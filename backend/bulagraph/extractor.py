"""
BulaGraph Extractor — extração rule-based de entidades e relações a partir de bulas.

Usa padrões regex e dicionários para detectar relações clínicas nos chunks de texto.
Não depende de LLM. Cada relação extraída preserva rastreabilidade completa:
  - source_node_id, target_node_id
  - relation_type
  - evidence_chunk_id
  - section_type, leaflet_type
  - confidence, extraction_method
"""

import re
from typing import Optional

from bulagraph.ontology import NodeType, RelationType, SectionType
from bulagraph.normalizer import normalize_entity, extract_normalized_entities


# ---------------------------------------------------------------------------
# Padrões regex para detecção de relações
# ---------------------------------------------------------------------------

# Contraindicação: "contraindicado", "não deve ser usado", "não use"
CONTRAINDICATION_PATTERNS = [
    re.compile(r"contraindicad[oa]", re.IGNORECASE),
    re.compile(r"não\s+dev[ae]\s+ser\s+usad[oa]", re.IGNORECASE),
    re.compile(r"não\s+dev[ae]\s+usar", re.IGNORECASE),
    re.compile(r"não\s+use", re.IGNORECASE),
    re.compile(r"não\s+(?:é\s+)?recomendad[oa]", re.IGNORECASE),
    re.compile(r"não\s+(?:deve|devem)\s+(?:tomar|utilizar|administrar)", re.IGNORECASE),
    re.compile(r"proibid[oa]", re.IGNORECASE),
]

# Cautela / monitoramento: "usar com cautela", "cuidado", "informe seu médico"
CAUTION_PATTERNS = [
    re.compile(r"usar?\s+com\s+cautela", re.IGNORECASE),
    re.compile(r"us[ae]\s+com\s+cuidado", re.IGNORECASE),
    re.compile(r"cuidado\s+(?:especial|ao)", re.IGNORECASE),
    re.compile(r"informe\s+(?:seu\s+|ao\s+)?médico", re.IGNORECASE),
    re.compile(r"avise\s+(?:seu\s+|ao\s+)?médico", re.IGNORECASE),
    re.compile(r"consulte\s+(?:seu\s+|o\s+)?médico", re.IGNORECASE),
    re.compile(r"procure\s+(?:seu\s+|o\s+|um\s+)?médico", re.IGNORECASE),
    re.compile(r"orientação\s+médica", re.IGNORECASE),
    re.compile(r"acompanhamento\s+médico", re.IGNORECASE),
    re.compile(r"monitoramento", re.IGNORECASE),
    re.compile(r"monitorar", re.IGNORECASE),
    re.compile(r"supervisão\s+médica", re.IGNORECASE),
]

# Reação adversa: "pode causar", "reações adversas", "efeitos"
ADVERSE_REACTION_PATTERNS = [
    re.compile(r"pode(?:m)?\s+causar", re.IGNORECASE),
    re.compile(r"pode(?:m)?\s+(?:ocorrer|acontecer|surgir|apresentar|provocar)", re.IGNORECASE),
    re.compile(r"rea[çc][ãa]o\s*(?:adversa|indesej[aá]vel|al[eé]rgica)", re.IGNORECASE),
    re.compile(r"rea[çc][õo]es\s*(?:adversas|indesej[aá]veis|al[eé]rgicas)", re.IGNORECASE),
    re.compile(r"efeitos?\s+(?:colaterais?|indesej[aá]veis?)", re.IGNORECASE),
    re.compile(r"males?\s+que", re.IGNORECASE),
]

# Interação: "interação", "não deve ser usado com", "uso concomitante"
INTERACTION_PATTERNS = [
    re.compile(r"intera[çc][ãa]o", re.IGNORECASE),
    re.compile(r"intera[çc][õo]es", re.IGNORECASE),
    re.compile(r"não\s+dev[ae]\s+ser\s+usad[oa]\s+com", re.IGNORECASE),
    re.compile(r"uso\s+concomitante", re.IGNORECASE),
    re.compile(r"junto\s+com", re.IGNORECASE),
    re.compile(r"associa[çc][ãa]o\s+com", re.IGNORECASE),
    re.compile(r"combinad[oa]\s+com", re.IGNORECASE),
    re.compile(r"quando\s+(?:usad[oa]|tomad[oa]|administrad[oa])\s+com", re.IGNORECASE),
]

# Ajuste de dose: "ajuste de dose", "redução da dose", "dose deve ser ajustada"
DOSE_ADJUSTMENT_PATTERNS = [
    re.compile(r"ajuste\s+d[eao]\s+dose", re.IGNORECASE),
    re.compile(r"redu[çc][ãa]o\s+d[eao]\s+dose", re.IGNORECASE),
    re.compile(r"dose\s+dev[ae]\s+ser\s+ajustad[oa]", re.IGNORECASE),
    re.compile(r"dose\s+mais\s+baixa", re.IGNORECASE),
    re.compile(r"menor\s+dose\s+possível", re.IGNORECASE),
    re.compile(r"dose\s+reduzida", re.IGNORECASE),
]

# Armazenamento: "conservar", "guardar", "temperatura", "proteger da luz/umidade"
STORAGE_PATTERNS = [
    re.compile(r"conservar?\s+(?:em|a|à)", re.IGNORECASE),
    re.compile(r"guardar?\s+(?:em|a|à)", re.IGNORECASE),
    re.compile(r"armazenar?\s+(?:em|a|à)", re.IGNORECASE),
    re.compile(r"temperatura\s+(?:ambiente|entre|de|inferior|m[aá]xima)", re.IGNORECASE),
    re.compile(r"proteg(?:er|ido)\s+d[aeo]\s+(?:luz|umidade)", re.IGNORECASE),
    re.compile(r"manter\s+(?:em|fora\s+do\s+alcance)", re.IGNORECASE),
]

# Dose esquecida: frases sobre esquecimento de dose
MISSED_DOSE_PATTERNS = [
    re.compile(r"esquec(?:er|eu|ida|ido)\s+(?:de\s+)?(?:tomar|usar|administrar)", re.IGNORECASE),
    re.compile(r"dose\s+esquecida", re.IGNORECASE),
    re.compile(r"se\s+(?:você\s+)?esquec", re.IGNORECASE),
    re.compile(r"n[ãa]o\s+tome?\s+(?:a\s+)?dose\s+dobrada", re.IGNORECASE),
]

# Superdose: intoxicação, quantidade maior
OVERDOSE_PATTERNS = [
    re.compile(r"superdose", re.IGNORECASE),
    re.compile(r"superdosagem", re.IGNORECASE),
    re.compile(r"quantidade\s+maior", re.IGNORECASE),
    re.compile(r"dose\s+(?:excessiva|acima)", re.IGNORECASE),
    re.compile(r"doses\s+excessivas", re.IGNORECASE),
    re.compile(r"intoxica[çc][ãa]o", re.IGNORECASE),
    re.compile(r"ingest[ãa]o\s+(?:excessiva|acidental)", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Dicionários de entidades para detecção
# ---------------------------------------------------------------------------

POPULATION_TERMS = {
    "gestante": NodeType.POPULATION,
    "lactante": NodeType.POPULATION,
    "grávida": NodeType.POPULATION,
    "gravidez": NodeType.POPULATION,
    "amamentando": NodeType.POPULATION,
    "amamentação": NodeType.POPULATION,
    "idoso": NodeType.POPULATION,
    "idosos": NodeType.POPULATION,
    "criança": NodeType.POPULATION,
    "crianças": NodeType.POPULATION,
    "lactente": NodeType.POPULATION,
    "lactentes": NodeType.POPULATION,
    "recém-nascido": NodeType.POPULATION,
    "recém-nascidos": NodeType.POPULATION,
    "menores de 12 anos": NodeType.POPULATION,
    "mulheres grávidas": NodeType.POPULATION,
    "pacientes idosos": NodeType.POPULATION,
    "bebê": NodeType.POPULATION,
    "bebês": NodeType.POPULATION,
}

CONDITION_TERMS = {
    "doença hepática": NodeType.CLINICAL_CONDITION,
    "doença renal": NodeType.CLINICAL_CONDITION,
    "insuficiência hepática": NodeType.CLINICAL_CONDITION,
    "insuficiência renal": NodeType.CLINICAL_CONDITION,
    "nefropatia": NodeType.CLINICAL_CONDITION,
    "hepatopatia": NodeType.CLINICAL_CONDITION,
    "hipertensão": NodeType.CLINICAL_CONDITION,
    "diabetes": NodeType.CLINICAL_CONDITION,
    "alergia": NodeType.CLINICAL_CONDITION,
    "hipersensibilidade": NodeType.CLINICAL_CONDITION,
    "epilepsia": NodeType.CLINICAL_CONDITION,
    "asma": NodeType.CLINICAL_CONDITION,
    "glaucoma": NodeType.CLINICAL_CONDITION,
    "apneia do sono": NodeType.CLINICAL_CONDITION,
    "fenilcetonúria": NodeType.CLINICAL_CONDITION,
    "problemas no fígado": NodeType.CLINICAL_CONDITION,
    "problemas nos rins": NodeType.CLINICAL_CONDITION,
    "problema no fígado": NodeType.CLINICAL_CONDITION,
    "problema nos rins": NodeType.CLINICAL_CONDITION,
    "comprometimento hepático": NodeType.CLINICAL_CONDITION,
}


# ---------------------------------------------------------------------------
# Classe principal de extração
# ---------------------------------------------------------------------------

class ExtractionResult:
    """Resultado de uma extração de relação."""
    __slots__ = (
        "source_node_type", "source_canonical",
        "target_node_type", "target_canonical",
        "relation_type", "evidence_text",
        "section_type", "leaflet_type",
        "confidence", "extraction_method",
    )

    def __init__(
        self,
        source_node_type: str,
        source_canonical: str,
        target_node_type: str,
        target_canonical: str,
        relation_type: str,
        evidence_text: str = "",
        section_type: str = "",
        leaflet_type: str = "",
        confidence: float = 0.8,
        extraction_method: str = "rule",
    ):
        self.source_node_type = source_node_type
        self.source_canonical = source_canonical
        self.target_node_type = target_node_type
        self.target_canonical = target_canonical
        self.relation_type = relation_type
        self.evidence_text = evidence_text
        self.section_type = section_type
        self.leaflet_type = leaflet_type
        self.confidence = confidence
        self.extraction_method = extraction_method

    def to_dict(self) -> dict:
        return {
            "source_node_type": self.source_node_type,
            "source_canonical": self.source_canonical,
            "target_node_type": self.target_node_type,
            "target_canonical": self.target_canonical,
            "relation_type": self.relation_type,
            "evidence_text": self.evidence_text,
            "section_type": self.section_type,
            "leaflet_type": self.leaflet_type,
            "confidence": self.confidence,
            "extraction_method": self.extraction_method,
        }


class RuleBasedExtractor:
    """
    Extrator rule-based de relações clínicas a partir de texto de bula.
    
    Uso:
        extractor = RuleBasedExtractor()
        results = extractor.extract_from_chunk(
            text="Este medicamento é contraindicado para gestantes.",
            medication_name="Tylenol",
            section_type="contraindication",
            leaflet_type="patient_leaflet",
        )
    """

    def extract_from_chunk(
        self,
        text: str,
        medication_name: str,
        section_type: str = "",
        leaflet_type: str = "",
    ) -> list[ExtractionResult]:
        """
        Extrai todas as relações detectáveis em um chunk de texto.
        
        Returns:
            Lista de ExtractionResult com as relações encontradas.
        """
        results: list[ExtractionResult] = []
        
        # Detectar menções a populações e condições no texto
        mentioned_populations = self._detect_populations(text)
        mentioned_conditions = self._detect_conditions(text)
        mentioned_substances = self._detect_substances(text)
        
        # 1. Contraindicações
        if self._matches_any(text, CONTRAINDICATION_PATTERNS):
            for pop in mentioned_populations:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.POPULATION,
                    target_canonical=pop,
                    relation_type=RelationType.CONTRAINDICATED_FOR,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.9,
                    extraction_method="rule",
                ))
            for cond in mentioned_conditions:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.CLINICAL_CONDITION,
                    target_canonical=cond,
                    relation_type=RelationType.CONTRAINDICATED_FOR,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.9,
                    extraction_method="rule",
                ))
        
        # 2. Cautela / Monitoramento / Procure médico
        if self._matches_any(text, CAUTION_PATTERNS):
            for pop in mentioned_populations:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.POPULATION,
                    target_canonical=pop,
                    relation_type=RelationType.USE_WITH_CAUTION_IN,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.8,
                    extraction_method="rule",
                ))
            for cond in mentioned_conditions:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.CLINICAL_CONDITION,
                    target_canonical=cond,
                    relation_type=RelationType.USE_WITH_CAUTION_IN,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.8,
                    extraction_method="rule",
                ))
            # SEEK_MEDICAL_HELP_IF para padrões específicos de "procure médico"
            seek_patterns = [p for p in CAUTION_PATTERNS if "procure" in p.pattern or "orientação" in p.pattern]
            if self._matches_any(text, seek_patterns):
                for pop in mentioned_populations:
                    results.append(ExtractionResult(
                        source_node_type=NodeType.EVIDENCE_CHUNK,
                        source_canonical=text[:80],
                        target_node_type=NodeType.PATIENT_ACTION,
                        target_canonical=f"procurar médico ({pop})",
                        relation_type=RelationType.SEEK_MEDICAL_HELP_IF,
                        evidence_text=text,
                        section_type=section_type,
                        leaflet_type=leaflet_type,
                        confidence=0.7,
                        extraction_method="rule",
                    ))
        
        # 3. Reações adversas
        if self._matches_any(text, ADVERSE_REACTION_PATTERNS):
            # Tenta detectar eventos adversos específicos no texto
            adverse_events = self._detect_adverse_events(text)
            for event in adverse_events:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.ADVERSE_EVENT,
                    target_canonical=event,
                    relation_type=RelationType.MAY_CAUSE,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.8,
                    extraction_method="rule",
                ))
        
        # 4. Interações
        if self._matches_any(text, INTERACTION_PATTERNS):
            for subst in mentioned_substances:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.INTERACTING_SUBSTANCE,
                    target_canonical=subst,
                    relation_type=RelationType.INTERACTS_WITH,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.85,
                    extraction_method="rule",
                ))
        
        # 5. Ajuste de dose
        if self._matches_any(text, DOSE_ADJUSTMENT_PATTERNS):
            for pop in mentioned_populations:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.POPULATION,
                    target_canonical=pop,
                    relation_type=RelationType.REQUIRES_DOSE_ADJUSTMENT_IN,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.85,
                    extraction_method="rule",
                ))
            for cond in mentioned_conditions:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.CLINICAL_CONDITION,
                    target_canonical=cond,
                    relation_type=RelationType.REQUIRES_DOSE_ADJUSTMENT_IN,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.85,
                    extraction_method="rule",
                ))
        
        # 6. Armazenamento
        if self._matches_any(text, STORAGE_PATTERNS):
            storage_info = self._extract_storage_info(text)
            if storage_info:
                results.append(ExtractionResult(
                    source_node_type=NodeType.EVIDENCE_CHUNK,
                    source_canonical=text[:80],
                    target_node_type=NodeType.STORAGE_CONDITION,
                    target_canonical=storage_info,
                    relation_type=RelationType.STORE_UNDER,
                    evidence_text=text,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                    confidence=0.9,
                    extraction_method="rule",
                ))
        
        # 7. Dose esquecida
        if self._matches_any(text, MISSED_DOSE_PATTERNS):
            results.append(ExtractionResult(
                source_node_type=NodeType.EVIDENCE_CHUNK,
                source_canonical=text[:80],
                target_node_type=NodeType.MISSED_DOSE_INSTRUCTION,
                target_canonical=self._extract_instruction_summary(text, "dose esquecida"),
                relation_type=RelationType.IF_MISSED_DOSE_DO,
                evidence_text=text,
                section_type=section_type,
                leaflet_type=leaflet_type,
                confidence=0.9,
                extraction_method="rule",
            ))
        
        # 8. Superdose
        if self._matches_any(text, OVERDOSE_PATTERNS):
            results.append(ExtractionResult(
                source_node_type=NodeType.EVIDENCE_CHUNK,
                source_canonical=text[:80],
                target_node_type=NodeType.OVERDOSE_INSTRUCTION,
                target_canonical=self._extract_instruction_summary(text, "superdose"),
                relation_type=RelationType.IN_OVERDOSE_DO,
                evidence_text=text,
                section_type=section_type,
                leaflet_type=leaflet_type,
                confidence=0.9,
                extraction_method="rule",
            ))
        
        # 9. Menções a populações (sempre, independente do tipo de relação detectada)
        for pop in mentioned_populations:
            results.append(ExtractionResult(
                source_node_type=NodeType.EVIDENCE_CHUNK,
                source_canonical=text[:80],
                target_node_type=NodeType.POPULATION,
                target_canonical=pop,
                relation_type=RelationType.CHUNK_MENTIONS_POPULATION,
                evidence_text=text,
                section_type=section_type,
                leaflet_type=leaflet_type,
                confidence=0.95,
                extraction_method="dictionary",
            ))
        
        # 10. Menções a condições (sempre)
        for cond in mentioned_conditions:
            results.append(ExtractionResult(
                source_node_type=NodeType.EVIDENCE_CHUNK,
                source_canonical=text[:80],
                target_node_type=NodeType.CLINICAL_CONDITION,
                target_canonical=cond,
                relation_type=RelationType.CHUNK_MENTIONS_CONDITION,
                evidence_text=text,
                section_type=section_type,
                leaflet_type=leaflet_type,
                confidence=0.95,
                extraction_method="dictionary",
            ))
        
        return results

    # ===================================================================
    # Detectores de entidades
    # ===================================================================

    def _detect_populations(self, text: str) -> list[str]:
        """Detecta populações mencionadas no texto."""
        found: set[str] = set()
        lower = text.lower()
        # Ordena por comprimento decrescente para evitar match parcial
        for term in sorted(POPULATION_TERMS.keys(), key=len, reverse=True):
            if term.lower() in lower:
                canonical = normalize_entity(term)
                found.add(canonical)
        return list(found)

    def _detect_conditions(self, text: str) -> list[str]:
        """Detecta condições clínicas mencionadas no texto."""
        found: set[str] = set()
        lower = text.lower()
        for term in sorted(CONDITION_TERMS.keys(), key=len, reverse=True):
            if term.lower() in lower:
                canonical = normalize_entity(term)
                found.add(canonical)
        return list(found)

    def _detect_substances(self, text: str) -> list[str]:
        """Detecta substâncias interagentes mencionadas no texto."""
        found: set[str] = set()
        lower = text.lower()
        
        # Dicionário de substâncias comuns
        substance_terms = {
            "álcool": "álcool",
            "bebidas alcoólicas": "álcool",
            "bebida alcoólica": "álcool",
            "varfarina": "varfarina",
            "anticoagulante": "anticoagulante",
            "anticoagulantes": "anticoagulante",
            "flucloxacilina": "flucloxacilina",
            "penicilina": "penicilina",
            "cefalosporina": "cefalosporina",
            "cefalosporinas": "cefalosporina",
            "derivados cumarínicos": "cumarínicos",
            "cumarínicos": "cumarínicos",
            "anti-inflamatório": "anti-inflamatório",
            "anti-inflamatórios": "anti-inflamatório",
            "suco de toranja": "suco de toranja",
            "depressores do snc": "depressores do SNC",
            "depressores do sistema nervoso central": "depressores do SNC",
            "benzodiazepínicos": "benzodiazepínicos",
            "analgésico": "analgésico",
            "analgésicos": "analgésico",
            "antibiótico": "antibiótico",
            "antibióticos": "antibiótico",
            "inibidor da bomba de prótons": "inibidor da bomba de prótons",
        }
        
        for term, canonical in sorted(substance_terms.items(), key=lambda x: len(x[0]), reverse=True):
            if term in lower:
                found.add(canonical)
        
        return list(found)

    def _detect_adverse_events(self, text: str) -> list[str]:
        """Detecta eventos adversos mencionados no texto."""
        found: set[str] = set()
        lower = text.lower()
        
        adverse_event_terms = {
            "diarreia": "diarreia",
            "diarréia": "diarreia",
            "náusea": "náusea",
            "enjoo": "náusea",
            "vômito": "vômito",
            "vômitos": "vômito",
            "sonolência": "sonolência",
            "tontura": "tontura",
            "cefaleia": "cefaleia",
            "dor de cabeça": "cefaleia",
            "urticária": "urticária",
            "coceira": "prurido",
            "prurido": "prurido",
            "erupção cutânea": "erupção cutânea",
            "erupções cutâneas": "erupção cutânea",
            "vermelhidão": "eritema",
            "eritema": "eritema",
            "reação alérgica": "reação alérgica",
            "reações alérgicas": "reação alérgica",
            "bolhas": "bolhas",
            "insônia": "insônia",
            "ansiedade": "ansiedade",
            "constipação": "constipação",
            "candidíase": "candidíase",
            "aumento das transaminases": "aumento das transaminases",
            "erupção fixa medicamentosa": "erupção fixa medicamentosa",
        }
        
        for term, canonical in sorted(adverse_event_terms.items(), key=lambda x: len(x[0]), reverse=True):
            if term in lower:
                found.add(canonical)
        
        return list(found)

    # ===================================================================
    # Helpers
    # ===================================================================

    @staticmethod
    def _matches_any(text: str, patterns: list[re.Pattern]) -> bool:
        """Verifica se o texto corresponde a algum dos padrões."""
        return any(p.search(text) for p in patterns)

    @staticmethod
    def _extract_storage_info(text: str) -> str:
        """Extrai informação resumida de armazenamento."""
        parts: list[str] = []
        
        # Temperatura
        temp_match = re.search(
            r"temperatura\s+(?:ambiente\s+)?\(?(?:entre\s+)?(\d+\s*°?\s*C?\s*(?:e|a)\s*\d+\s*°?\s*C?)\)?",
            text, re.IGNORECASE
        )
        if temp_match:
            parts.append(f"temperatura {temp_match.group(1).strip()}")
        elif "temperatura ambiente" in text.lower():
            parts.append("temperatura ambiente")
        
        if "proteg" in text.lower() and "luz" in text.lower():
            parts.append("proteger da luz")
        if "proteg" in text.lower() and "umidade" in text.lower():
            parts.append("proteger da umidade")
        
        return "; ".join(parts) if parts else "condições específicas (ver bula)"

    @staticmethod
    def _extract_instruction_summary(text: str, context: str) -> str:
        """Extrai um resumo curto de uma instrução."""
        # Pega as primeiras 120 chars relevantes como resumo
        clean = text.strip()
        if len(clean) > 120:
            clean = clean[:117] + "..."
        return f"instrução de {context}: {clean}"
