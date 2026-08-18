"""
BulaGraph Retriever — recuperação por intenção, seções e caminhos de grafo.

Versão melhorada (Intent-Aware / Section-Aware):
  1. Classifica múltiplas intenções com score/confidence
  2. Normaliza entidades mencionadas na pergunta
  3. Cria QueryUnderstanding auditável
  4. Cria RetrievalPlan interno ao GraphRAG
  5. Recupera EvidenceChunks por seções, relações e entidades
  6. Opcionalmente combina com busca vetorial controlada pelo plano
  7. Faz reranking multi-fator orientado por plano
  8. Calcula intent_confidence, retrieval_confidence e answer_confidence

Importante:
  - Este módulo NÃO escolhe entre pipelines externos.
  - Ele melhora somente a recuperação interna do BulaGraph/GraphRAG.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, Any

from bulagraph.ontology import (
    NodeType,
    RelationType,
    SectionType,
    QueryIntent,
    INTENT_TO_SECTIONS,
    INTENT_TO_RELATIONS,
)
from bulagraph.normalizer import normalize_text, extract_normalized_entities
from bulagraph.store import BulaGraphStore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Modelo de resultado
# ---------------------------------------------------------------------------


@dataclass
class EvidenceItem:
    """Um trecho de evidência recuperado."""
    chunk_id: str
    section_type: str
    section_title: str
    text: str
    score: float
    leaflet_type: str = ""
    source: str = ""
    relations: list[str] = field(default_factory=list)
    apresentacao: str = ""


@dataclass
class IntentCandidate:
    """Uma intenção candidata detectada na pergunta."""
    intent: QueryIntent
    raw_score: float
    confidence: float
    matched_patterns: list[str] = field(default_factory=list)


@dataclass
class SectionCandidate:
    """Uma seção candidata derivada das intenções."""
    section_type: SectionType
    confidence: float
    source_intents: list[str] = field(default_factory=list)


@dataclass
class RetrievalPlan:
    """
    Plano interno de recuperação do GraphRAG.

    Não escolhe entre pipelines externos. Apenas decide como o BulaGraph
    deve consultar grafo, seções, relações, entidades e vetor complementar.
    """
    strategy: str
    use_graph_sections: bool
    use_graph_relations: bool
    use_graph_entities: bool
    use_vector: bool
    target_sections: list[SectionType] = field(default_factory=list)
    target_relations: list[RelationType] = field(default_factory=list)
    top_k_graph: int = 40
    top_k_vector: int = 0
    reason: str = ""


@dataclass
class QueryUnderstanding:
    """Interpretação auditável da pergunta antes da recuperação."""
    question: str
    normalized_question: str
    intent_candidates: list[IntentCandidate]
    section_candidates: list[SectionCandidate]
    normalized_entities: list[dict]
    retrieval_plan: RetrievalPlan
    intent_confidence: float
    entity_confidence: float
    ambiguity_score: float


@dataclass
class RetrievalResult:
    """Resultado completo de uma consulta ao BulaGraph."""
    question: str
    intent: str
    medication: str
    leaflet_type: str
    evidence: list[EvidenceItem]
    normalized_entities: list[dict]
    graph_stats: dict = field(default_factory=dict)

    # Novos campos opcionais para auditoria/avaliação
    query_understanding: Optional[QueryUnderstanding] = None
    confidence: dict = field(default_factory=dict)
    debug: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers defensivos
# ---------------------------------------------------------------------------

def _enum_value(value: Any) -> str:
    """Retorna .value quando existir; caso contrário, str(value)."""
    return value.value if hasattr(value, "value") else str(value)


def _safe_lower(value: Optional[str]) -> str:
    return (value or "").lower().strip()


def _text_hash(text: str) -> str:
    normalized = normalize_text(text or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


# ---------------------------------------------------------------------------
# Padrões para classificação de intenção — com pesos
# ---------------------------------------------------------------------------

INTENT_PATTERNS: dict[QueryIntent, list[tuple[re.Pattern, float]]] = {
    QueryIntent.INDICATION: [
        (re.compile(r"para\s+qu[eê]\s+(?:serve|é\s+indicad[oa])", re.IGNORECASE), 1.0),
        (re.compile(r"indica[çc][ãa]o", re.IGNORECASE), 0.9),
        (re.compile(r"indicad[oa]\s+para", re.IGNORECASE), 0.9),
        (re.compile(r"para\s+(?:que|qual)\s+(?:doença|condição)", re.IGNORECASE), 0.8),
        (re.compile(r"\bserve\s+para\b", re.IGNORECASE), 0.8),
    ],

    QueryIntent.CONTRAINDICATION: [
        (re.compile(r"contraindicad[oa]", re.IGNORECASE), 1.0),
        (re.compile(r"contraindica[çc][ãaõo]es?", re.IGNORECASE), 1.0),
        (re.compile(r"quando\s+não\s+(?:devo|posso|pode)", re.IGNORECASE), 0.9),
        (re.compile(r"quem\s+não\s+(?:deve|pode)", re.IGNORECASE), 1.0),
        (re.compile(r"não\s+(?:devo|posso|pode)\s+(?:usar|tomar)", re.IGNORECASE), 0.9),
        (re.compile(r"\bnão\s+é\s+recomendad[oa]\b", re.IGNORECASE), 0.8),
    ],

    QueryIntent.INTERACTION: [
        (re.compile(r"intera[çc][ãa]o|intera(?:ge|gir|gem)", re.IGNORECASE), 1.0),
        (re.compile(r"junto\s+com", re.IGNORECASE), 0.9),
        (re.compile(r"(?:tomar|usar)\s+com", re.IGNORECASE), 0.8),
        (re.compile(r"(?:misturar|combinar)\s+com", re.IGNORECASE), 0.8),
        (re.compile(r"uso\s+concomitante", re.IGNORECASE), 1.0),
        (re.compile(r"(?:com|e)\s+(?:álcool|alcool|anticoagulante|anti-inflamatório|antiinflamatório)", re.IGNORECASE), 0.9),
    ],

    QueryIntent.DOSAGE: [
        (re.compile(r"(?:qual|como)\s+(?:é\s+)?a?\s*dose", re.IGNORECASE), 1.0),
        (re.compile(r"posologia", re.IGNORECASE), 1.0),
        (re.compile(r"quantos?\s+(?:comprimidos?|cápsulas?|gotas?|ml)", re.IGNORECASE), 0.9),
        (re.compile(r"como\s+(?:devo\s+)?(?:usar|tomar|administrar)", re.IGNORECASE), 0.9),
        (re.compile(r"dose\s+(?:recomendada|padrão|máxima|diária)", re.IGNORECASE), 0.9),
        (re.compile(r"modo\s+de\s+us[ao]", re.IGNORECASE), 1.0),
        (re.compile(r"quantas\s+vezes", re.IGNORECASE), 0.8),
    ],

    QueryIntent.ADVERSE_REACTION: [
        (re.compile(r"(?:efeitos?\s+)?(?:colaterais?|adversos?|indesej[aá]veis?)", re.IGNORECASE), 1.0),
        (re.compile(r"rea[çc][ãa]o\s*(?:adversa|indesejável|alérgica)", re.IGNORECASE), 1.0),
        (re.compile(r"rea[çc][õo]es", re.IGNORECASE), 0.7),
        (re.compile(r"males?\s+que", re.IGNORECASE), 0.7),
        (re.compile(r"pode\s+causar", re.IGNORECASE), 0.8),
        (re.compile(r"caus[aar]?\s+(?:diarreia|enjoo|náusea|nausea|sonolência|sonolencia|tontura|alergia|coceira)", re.IGNORECASE), 0.9),
        (re.compile(r"\bd[áa]\s+sono\b", re.IGNORECASE), 0.9),
    ],

    QueryIntent.WARNING_PRECAUTION: [
        (re.compile(r"precau[çc][ãa]o", re.IGNORECASE), 1.0),
        (re.compile(r"advert[eê]ncia", re.IGNORECASE), 1.0),
        (re.compile(r"cuidado", re.IGNORECASE), 0.7),
        (re.compile(r"(?:o\s+que\s+)?devo\s+saber\s+antes", re.IGNORECASE), 1.0),
        (re.compile(r"antes\s+de\s+(?:usar|tomar)", re.IGNORECASE), 0.8),
        (re.compile(r"\bé\s+perigoso\b|\bfaz\s+mal\b|\bé\s+seguro\b", re.IGNORECASE), 0.7),
    ],

    QueryIntent.PREGNANCY_LACTATION: [
        (re.compile(r"gr[aá]vid[ao]", re.IGNORECASE), 1.0),
        (re.compile(r"gravidez", re.IGNORECASE), 1.0),
        (re.compile(r"gestante", re.IGNORECASE), 1.0),
        (re.compile(r"gesta[çc][ãa]o", re.IGNORECASE), 1.0),
        (re.compile(r"amament(?:ando|ação|acao)", re.IGNORECASE), 1.0),
        (re.compile(r"lactante", re.IGNORECASE), 1.0),
        (re.compile(r"lacta[çc][ãa]o", re.IGNORECASE), 1.0),
        (re.compile(r"aleitamento", re.IGNORECASE), 0.9),
    ],

    QueryIntent.ELDERLY: [
        (re.compile(r"idos[oa]s?", re.IGNORECASE), 1.0),
        (re.compile(r"terceira\s+idade", re.IGNORECASE), 1.0),
        (re.compile(r"pacientes?\s+idos[oa]s?", re.IGNORECASE), 1.0),
    ],

    QueryIntent.PEDIATRIC: [
        (re.compile(r"crian[çc]as?", re.IGNORECASE), 1.0),
        (re.compile(r"pedi[aá]tri", re.IGNORECASE), 1.0),
        (re.compile(r"menores?\s+de\s+\d+\s+anos", re.IGNORECASE), 1.0),
        (re.compile(r"beb[eê]s?", re.IGNORECASE), 0.9),
        (re.compile(r"rec[eé]m.nascid[oa]s?", re.IGNORECASE), 0.9),
    ],

    QueryIntent.RENAL_HEPATIC: [
        (re.compile(r"(?:doença|problema|insuficiência)\s+(?:hep[aá]tic|no\s+fígado|no\s+figado|renal|nos?\s+rins)", re.IGNORECASE), 1.0),
        (re.compile(r"\bf[ií]gado\b", re.IGNORECASE), 0.9),
        (re.compile(r"\brim\b|\brins\b|\brenal\b", re.IGNORECASE), 0.9),
        (re.compile(r"hepat[oó]pat|hep[aá]tic", re.IGNORECASE), 0.9),
        (re.compile(r"nefropat", re.IGNORECASE), 0.9),
    ],

    QueryIntent.STORAGE: [
        (re.compile(r"(?:como\s+)?(?:guardar|conservar|armazenar)", re.IGNORECASE), 1.0),
        (re.compile(r"armazenamento", re.IGNORECASE), 1.0),
        (re.compile(r"onde\s+(?:guardar|conservar)", re.IGNORECASE), 0.9),
        (re.compile(r"temperatura", re.IGNORECASE), 0.8),
        (re.compile(r"validade", re.IGNORECASE), 0.8),
    ],

    QueryIntent.MISSED_DOSE: [
        (re.compile(r"esquec(?:er|i|eu|ida)", re.IGNORECASE), 1.0),
        (re.compile(r"dose\s+esquecida", re.IGNORECASE), 1.0),
        (re.compile(r"pul(?:ar|ou|ei)\s+(?:uma\s+)?dose", re.IGNORECASE), 0.9),
        (re.compile(r"não\s+(?:tomei|usei|tomou)", re.IGNORECASE), 0.8),
    ],

    QueryIntent.OVERDOSE: [
        (re.compile(r"superdose", re.IGNORECASE), 1.0),
        (re.compile(r"superdosagem", re.IGNORECASE), 1.0),
        (re.compile(r"(?:tom|us|inger)[a-z]*\s+(?:demais|muito|mais\s+do\s+que|excesso)", re.IGNORECASE), 0.9),
        (re.compile(r"quantidade\s+maior", re.IGNORECASE), 0.9),
        (re.compile(r"excesso", re.IGNORECASE), 0.7),
        (re.compile(r"intoxica[çc][ãa]o", re.IGNORECASE), 0.9),
        (re.compile(r"acidental(?:mente)?", re.IGNORECASE), 0.7),
        (re.compile(r"por\s+acidente", re.IGNORECASE), 0.8),
        (re.compile(r"(?:caixa|cartela|frasco)\s+inteir[oa]", re.IGNORECASE), 0.9),
    ],

    QueryIntent.COMPARISON: [
        (re.compile(r"diferen[çc]a\s+entre", re.IGNORECASE), 1.0),
        (re.compile(r"compar(?:ar|ação|acao)", re.IGNORECASE), 1.0),
        (re.compile(r"mesmo\s+princ[ií]pio", re.IGNORECASE), 0.9),
        (re.compile(r"gen[eé]rico", re.IGNORECASE), 0.8),
        (re.compile(r"similar", re.IGNORECASE), 0.8),
    ],
}


AMBIGUOUS_QUESTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"^\s*pode\s+tomar\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*posso\s+tomar\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*é\s+perigoso\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*faz\s+mal\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*é\s+seguro\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*serve\s+para\s+isso\??\s*$", re.IGNORECASE),
]

# Padrões de boilerplate genérico para penalização no reranking
_BOILERPLATE_PATTERNS: list[re.Pattern] = [
    re.compile(r"^\s*este\s+é\s+um\s+medicamento", re.IGNORECASE),
    re.compile(r"^\s*leia\s+atentamente\s+esta\s+bula", re.IGNORECASE),
    re.compile(r"^\s*em\s+caso\s+de\s+dúvidas", re.IGNORECASE),
    re.compile(r"^\s*siga\s+corretamente\s+o\s+modo\s+de\s+usar", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------


class BulaGraphRetriever:
    """
    Recuperador de informações do BulaGraph.

    Uso:
        retriever = BulaGraphRetriever(graph_store)
        result = retriever.retrieve(
            question="Posso usar se estiver grávida?",
            medication="Tylenol",
            leaflet_type="patient_leaflet",
            debug=True,
        )
    """

    def __init__(self, store: BulaGraphStore, vectorstore: Any = None):
        """
        Args:
            store: BulaGraphStore com o grafo indexado
            vectorstore: Opcional — instância de vectorstore ChromaDB/LangChain
                         para busca vetorial complementar.
        """
        self.store = store
        self.vectorstore = vectorstore

    def retrieve(
        self,
        question: str,
        medication: Optional[str] = None,
        leaflet_type: Optional[str] = None,
        top_k: int = 8,
        debug: bool = False,
    ) -> RetrievalResult:
        """
        Ponto de entrada principal de consulta.

        Args:
            question: Pergunta do usuário.
            medication: Nome do medicamento, opcional, filtra resultados.
            leaflet_type: "patient_leaflet" ou "professional_leaflet", opcional.
            top_k: Número máximo de chunks a retornar.
            debug: Se True, inclui diagnóstico estruturado.

        Returns:
            RetrievalResult com evidências pontuadas.
        """
        normalized_question = normalize_text(question)
        normalized_entities = extract_normalized_entities(question)

        # 1. Múltiplas intenções
        intent_candidates = self._classify_intents(
            question=question,
            entities=normalized_entities,
        )

        # 2. Plano interno do GraphRAG
        plan = self._build_retrieval_plan(
            intent_candidates=intent_candidates,
            entities=normalized_entities,
            medication=medication,
            leaflet_type=leaflet_type,
        )

        # 3. QueryUnderstanding auditável
        query_understanding = self._build_query_understanding(
            question=question,
            normalized_question=normalized_question,
            intent_candidates=intent_candidates,
            entities=normalized_entities,
            plan=plan,
        )

        debug_info: dict[str, Any] = {
            "candidate_counts": {},
            "retrieval_plan": self._to_debug_dict(plan),
            "intent_candidates": [
                self._to_debug_dict(candidate) for candidate in intent_candidates
            ],
        } if debug else {}

        # 4. Recuperação por plano do grafo
        graph_candidates = self._retrieve_by_graph_plan(
            plan=plan,
            medication=medication,
            leaflet_type=leaflet_type,
            normalized_question=normalized_question,
            entities=normalized_entities,
        )
        candidates = graph_candidates

        if debug:
            debug_info["candidate_counts"]["graph"] = len(graph_candidates)

        # 5. Busca vetorial complementar, controlada pelo plano
        if self.vectorstore and medication and plan.use_vector:
            vector_candidates = self._retrieve_by_vector_plan(
                question=question,
                medication=medication,
                leaflet_type=leaflet_type,
                plan=plan,
            )
            candidates = self._merge_candidates(candidates, vector_candidates)

            if debug:
                debug_info["candidate_counts"]["vector"] = len(vector_candidates)
                debug_info["candidate_counts"]["merged"] = len(candidates)

        # 6. Reranking orientado por plano
        scored = self._rerank(
            candidates=candidates,
            intent_candidates=intent_candidates,
            plan=plan,
            question=question,
            normalized_question=normalized_question,
            entities=normalized_entities,
            leaflet_type=leaflet_type,
        )

        top_evidence = scored[:top_k]

        # 7. Confidence
        confidence = self._compute_confidence(
            query_understanding=query_understanding,
            evidence=top_evidence,
        )

        if debug:
            debug_info["confidence"] = confidence
            debug_info["top_evidence"] = [
                {
                    "chunk_id": item.chunk_id,
                    "section_type": item.section_type,
                    "section_title": item.section_title,
                    "score": item.score,
                    "source": item.source,
                    "relations": item.relations,
                    "text_preview": item.text[:250],
                }
                for item in top_evidence
            ]

        primary_intent = (
            intent_candidates[0].intent
            if intent_candidates
            else QueryIntent.GENERAL
        )

        return RetrievalResult(
            question=question,
            intent=_enum_value(primary_intent),
            medication=medication or "",
            leaflet_type=leaflet_type or "",
            evidence=top_evidence,
            normalized_entities=normalized_entities,
            graph_stats=self.store.stats(),
            query_understanding=query_understanding,
            confidence=confidence,
            debug=debug_info,
        )

    # ------------------------------------------------------------------
    # Backward-compatible alias for legacy single-intent callers
    # ------------------------------------------------------------------

    def _classify_intent(self, question: str) -> QueryIntent:
        """
        Backward-compatible wrapper: retorna a intenção principal.

        Delegações existentes (ex: testes) que chamam
        ``_classify_intent(question)`` continuam funcionando.
        """
        candidates = self._classify_intents(question, entities=[])
        return candidates[0].intent if candidates else QueryIntent.GENERAL

    # ===================================================================
    # 1. Classificação de múltiplas intenções
    # ===================================================================

    def _classify_intents(
        self,
        question: str,
        entities: list[dict],
    ) -> list[IntentCandidate]:
        """
        Classifica múltiplas intenções usando padrões regex ponderados.

        Retorna lista ranqueada de IntentCandidate.
        """
        candidates: list[IntentCandidate] = []
        normalized_question = normalize_text(question)

        for intent, patterns in INTENT_PATTERNS.items():
            raw_score = 0.0
            max_score = sum(weight for _, weight in patterns)
            matched_patterns: list[str] = []

            for pattern, weight in patterns:
                if pattern.search(question) or pattern.search(normalized_question):
                    raw_score += weight
                    matched_patterns.append(pattern.pattern)

            if raw_score <= 0:
                continue

            # Blend best-match strength with cumulative breadth:
            # - best_match_weight: the highest weight among matched patterns
            #   (one strong hit should still produce meaningful confidence)
            # - breadth_ratio: fraction of total weight matched
            #   (matching more patterns increases confidence further)
            best_match_weight = max(
                (weight for pattern, weight in patterns
                 if pattern.search(question) or pattern.search(normalized_question)),
                default=0.0,
            )
            breadth_ratio = raw_score / max_score if max_score else 0.0
            regex_confidence = 0.6 * best_match_weight + 0.4 * breadth_ratio

            entity_bonus = self._entity_bonus_for_intent(intent, entities)
            ambiguity_penalty = self._ambiguity_penalty(question)

            confidence = (
                0.75 * regex_confidence
                + 0.20 * entity_bonus
                - 0.15 * ambiguity_penalty
            )

            candidates.append(
                IntentCandidate(
                    intent=intent,
                    raw_score=round(raw_score, 3),
                    confidence=round(_clamp01(confidence), 3),
                    matched_patterns=matched_patterns,
                )
            )

        if not candidates:
            return [
                IntentCandidate(
                    intent=QueryIntent.GENERAL,
                    raw_score=0.0,
                    confidence=0.25,
                    matched_patterns=[],
                )
            ]

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates

    def _entity_bonus_for_intent(
        self,
        intent: QueryIntent,
        entities: list[dict],
    ) -> float:
        """Calcula bônus simples por compatibilidade entre entidades e intenção."""
        if not entities:
            return 0.0

        entity_types = {
            _safe_lower(e.get("type", ""))
            for e in entities
        }

        canonicals = {
            _safe_lower(e.get("canonical", ""))
            for e in entities
        }

        if intent == QueryIntent.INTERACTION:
            med_like = [
                e for e in entities
                if _safe_lower(e.get("type", "")) in {
                    "medication", "medicamento", "substance", "substancia",
                    "substância", "drug", "principle", "principio_ativo",
                    "princípio_ativo",
                }
            ]
            if len(med_like) >= 2:
                return 1.0
            if len(med_like) == 1:
                return 0.5
            return 0.0

        if intent == QueryIntent.PREGNANCY_LACTATION:
            terms = {
                "gestante", "gravida", "grávida", "gravidez",
                "lactante", "amamentacao", "amamentação",
                "lactacao", "lactação", "aleitamento",
            }
            return 1.0 if canonicals & {_safe_lower(t) for t in terms} else 0.0

        if intent == QueryIntent.RENAL_HEPATIC:
            terms = {
                "figado", "fígado", "hepatico", "hepático",
                "rim", "rins", "renal", "hepatica", "hepática",
                "doença hepática", "doença renal",
            }
            return 1.0 if canonicals & {_safe_lower(t) for t in terms} else 0.0

        if intent in {QueryIntent.ELDERLY, QueryIntent.PEDIATRIC}:
            population_like = {"population", "populacao", "população", "patient_group"}
            return 1.0 if entity_types & population_like else 0.3

        return 0.5

    def _ambiguity_penalty(self, question: str) -> float:
        """Penaliza perguntas muito vagas."""
        normalized_question = normalize_text(question)

        for pattern in AMBIGUOUS_QUESTION_PATTERNS:
            if pattern.search(question) or pattern.search(normalized_question):
                return 1.0

        word_count = len(re.findall(r"\w+", normalized_question))
        if word_count <= 3:
            return 0.7

        return 0.0

    # ===================================================================
    # 2. QueryUnderstanding e plano de recuperação
    # ===================================================================

    def _build_query_understanding(
        self,
        question: str,
        normalized_question: str,
        intent_candidates: list[IntentCandidate],
        entities: list[dict],
        plan: RetrievalPlan,
    ) -> QueryUnderstanding:
        section_candidates = self._build_section_candidates(intent_candidates)

        intent_confidence = intent_candidates[0].confidence if intent_candidates else 0.0
        entity_confidence = self._entity_confidence(entities)
        ambiguity_score = self._ambiguity_penalty(question)

        return QueryUnderstanding(
            question=question,
            normalized_question=normalized_question,
            intent_candidates=intent_candidates,
            section_candidates=section_candidates,
            normalized_entities=entities,
            retrieval_plan=plan,
            intent_confidence=round(intent_confidence, 3),
            entity_confidence=round(entity_confidence, 3),
            ambiguity_score=round(ambiguity_score, 3),
        )

    def _build_retrieval_plan(
        self,
        intent_candidates: list[IntentCandidate],
        entities: list[dict],
        medication: Optional[str],
        leaflet_type: Optional[str],
    ) -> RetrievalPlan:
        """
        Cria plano interno de recuperação do GraphRAG.

        Não escolhe entre pipelines externos; apenas decide como consultar
        o grafo, seções, relações, entidades e vetor complementar.
        """
        top_intent = intent_candidates[0] if intent_candidates else None
        intent_conf = top_intent.confidence if top_intent else 0.0

        strong_intents = [
            c for c in intent_candidates
            if c.confidence >= 0.50
        ]

        if not strong_intents and top_intent:
            strong_intents = [top_intent]

        target_sections = self._collect_sections_for_intents(strong_intents)
        target_relations = self._collect_relations_for_intents(strong_intents)

        has_entities = bool(entities)
        entity_conf = self._entity_confidence(entities)
        multi_intent = len(strong_intents) > 1

        if not target_sections:
            target_sections = self._critical_safety_sections()

        # Alta confiança: foco no grafo e em evidência textual ancorada
        if intent_conf >= 0.80 and entity_conf >= 0.50 and not multi_intent:
            return RetrievalPlan(
                strategy="graph_focused",
                use_graph_sections=True,
                use_graph_relations=True,
                use_graph_entities=True,
                use_vector=False,
                target_sections=target_sections,
                target_relations=target_relations,
                top_k_graph=30,
                top_k_vector=0,
                reason="intenção clara e entidades detectadas; priorizar grafo e seções esperadas",
            )

        # Média confiança ou múltiplas intenções: grafo + vetor filtrado
        if intent_conf >= 0.50:
            return RetrievalPlan(
                strategy="graph_hybrid_restricted",
                use_graph_sections=True,
                use_graph_relations=True,
                use_graph_entities=has_entities,
                use_vector=True,
                target_sections=target_sections,
                target_relations=target_relations,
                top_k_graph=40,
                top_k_vector=10,
                reason="intenção provável ou múltiplas intenções; usar grafo e vetor filtrado por seção",
            )

        # Baixa confiança: busca ampla, mas ainda dentro do GraphRAG
        return RetrievalPlan(
            strategy="graph_broad_safety",
            use_graph_sections=True,
            use_graph_relations=True,
            use_graph_entities=has_entities,
            use_vector=True,
            target_sections=self._critical_safety_sections(),
            target_relations=target_relations,
            top_k_graph=50,
            top_k_vector=15,
            reason="baixa confiança; ampliar busca em seções críticas",
        )

    def _build_section_candidates(
        self,
        intent_candidates: list[IntentCandidate],
    ) -> list[SectionCandidate]:
        """Gera seções candidatas a partir das intenções candidatas."""
        section_scores: dict[str, dict[str, Any]] = {}

        for candidate in intent_candidates:
            sections = INTENT_TO_SECTIONS.get(candidate.intent, [])

            for section in sections:
                key = _enum_value(section)

                if key not in section_scores:
                    section_scores[key] = {
                        "section": section,
                        "confidence": 0.0,
                        "source_intents": [],
                    }

                section_scores[key]["confidence"] = max(
                    section_scores[key]["confidence"],
                    candidate.confidence,
                )
                section_scores[key]["source_intents"].append(_enum_value(candidate.intent))

        results = [
            SectionCandidate(
                section_type=data["section"],
                confidence=round(data["confidence"], 3),
                source_intents=data["source_intents"],
            )
            for data in section_scores.values()
        ]

        results.sort(key=lambda s: s.confidence, reverse=True)
        return results

    def _collect_sections_for_intents(
        self,
        intent_candidates: list[IntentCandidate],
    ) -> list[SectionType]:
        """Coleta seções únicas associadas às intenções candidatas."""
        seen: set[str] = set()
        sections: list[SectionType] = []

        for candidate in intent_candidates:
            for section in INTENT_TO_SECTIONS.get(candidate.intent, []):
                key = _enum_value(section)
                if key not in seen:
                    seen.add(key)
                    sections.append(section)

        return sections

    def _collect_relations_for_intents(
        self,
        intent_candidates: list[IntentCandidate],
    ) -> list[RelationType]:
        """Coleta relações únicas associadas às intenções candidatas."""
        seen: set[str] = set()
        relations: list[RelationType] = []

        for candidate in intent_candidates:
            for relation in INTENT_TO_RELATIONS.get(candidate.intent, []):
                key = _enum_value(relation)
                if key not in seen:
                    seen.add(key)
                    relations.append(relation)

        return relations

    def _entity_confidence(self, entities: list[dict]) -> float:
        """Calcula confiança agregada simples das entidades detectadas."""
        if not entities:
            return 0.0

        confidences = []
        for entity in entities:
            value = entity.get("confidence")
            if isinstance(value, (int, float)):
                confidences.append(float(value))
            else:
                source = _safe_lower(entity.get("source", ""))
                if source == "exact_match":
                    confidences.append(1.0)
                elif source in {"normalized_match", "ontology_match", "synonym_match"}:
                    confidences.append(0.85)
                elif source == "fuzzy_match":
                    confidences.append(0.65)
                else:
                    confidences.append(0.7)

        return _clamp01(sum(confidences) / len(confidences))

    def _critical_safety_sections(self) -> list[SectionType]:
        """
        Retorna seções críticas de segurança.

        Usa nomes do SectionType enum, com fallback seguro.
        """
        candidates = [
            "CONTRAINDICATION",
            "WARNING_PRECAUTION",
            "INTERACTION",
            "ADVERSE_REACTION",
            "DOSAGE",
            "INDICATION",
        ]

        sections: list[SectionType] = []

        for name in candidates:
            if hasattr(SectionType, name):
                sections.append(getattr(SectionType, name))

        return sections

    # ===================================================================
    # 3. Recuperação por plano de grafo
    # ===================================================================

    def _retrieve_by_graph_plan(
        self,
        plan: RetrievalPlan,
        medication: Optional[str],
        leaflet_type: Optional[str],
        normalized_question: str,
        entities: list[dict],
    ) -> list[EvidenceItem]:
        """Recupera chunks seguindo o RetrievalPlan interno do GraphRAG."""
        candidates: list[EvidenceItem] = []

        if plan.use_graph_sections and plan.target_sections:
            candidates.extend(
                self._get_chunks_by_sections(
                    plan.target_sections,
                    medication,
                    leaflet_type,
                )
            )

        if plan.use_graph_relations and plan.target_relations:
            candidates.extend(
                self._get_chunks_by_relations(
                    plan.target_relations,
                    medication,
                    leaflet_type,
                )
            )

        if plan.use_graph_entities and entities:
            candidates.extend(
                self._get_chunks_by_entities(
                    entities,
                    medication,
                    leaflet_type,
                )
            )

        deduped = self._dedupe_candidates(candidates)
        return deduped[: plan.top_k_graph] if plan.top_k_graph else deduped

    def _get_chunks_by_sections(
        self,
        section_types: list[SectionType],
        medication: Optional[str],
        leaflet_type: Optional[str],
    ) -> list[EvidenceItem]:
        """Busca chunks de seções específicas."""
        items: list[EvidenceItem] = []

        for section_type in section_types:
            st_value = _enum_value(section_type)

            try:
                matching_sections = self.store.get_sections_by_type(st_value)
            except Exception as exc:
                logger.warning("Failed to get sections by type %s: %s", st_value, exc)
                continue

            for section in matching_sections:
                leaflet = None

                if leaflet_type or medication:
                    leaflet = self._safe_get_leaflet(section.get("leaflet_id"))

                if leaflet_type:
                    if not leaflet or leaflet.get("leaflet_type") != leaflet_type:
                        continue

                if medication:
                    leaflet_medication = _safe_lower(leaflet.get("medication_name", "") if leaflet else "")
                    if leaflet_medication != _safe_lower(medication):
                        continue

                try:
                    chunks = self.store.get_chunks_for_section(section["id"])
                except Exception as exc:
                    logger.warning("Failed to get chunks for section %s: %s", section.get("id"), exc)
                    continue

                for chunk in chunks:
                    metadata = chunk.get("metadata", {})

                    items.append(
                        EvidenceItem(
                            chunk_id=chunk["id"],
                            section_type=section.get("section_type", metadata.get("section_type", "")),
                            section_title=section.get("raw_title", ""),
                            text=chunk.get("text", ""),
                            score=0.0,
                            leaflet_type=metadata.get("leaflet_type", leaflet_type or ""),
                            source="graph_section",
                            relations=[],
                            apresentacao=metadata.get("apresentacao", ""),
                        )
                    )

        return items

    def _get_chunks_by_relations(
        self,
        relation_types: list[RelationType],
        medication: Optional[str],
        leaflet_type: Optional[str],
    ) -> list[EvidenceItem]:
        """Busca chunks conectados por relações específicas."""
        items: list[EvidenceItem] = []
        seen_chunks: set[str] = set()

        for rel_type in relation_types:
            rt_value = _enum_value(rel_type)

            try:
                edges = self.store.get_edges_by_type(rt_value)
            except Exception as exc:
                logger.warning("Failed to get edges by type %s: %s", rt_value, exc)
                continue

            for edge in edges:
                chunk_id = edge.get("evidence_chunk_id")
                if not chunk_id or chunk_id in seen_chunks:
                    continue

                meta = edge.get("metadata", {})

                if leaflet_type and meta.get("leaflet_type") and meta["leaflet_type"] != leaflet_type:
                    continue

                chunk = self._safe_get_evidence_chunk(chunk_id)
                if not chunk:
                    continue

                chunk_meta = chunk.get("metadata", {})

                if medication:
                    chunk_medication = _safe_lower(
                        chunk_meta.get("medication", "")
                        or chunk_meta.get("medicamento", "")
                    )
                    if chunk_medication != _safe_lower(medication):
                        continue

                section = self._safe_get_section(chunk.get("section_id"))

                seen_chunks.add(chunk_id)

                items.append(
                    EvidenceItem(
                        chunk_id=chunk_id,
                        section_type=meta.get(
                            "section_type",
                            chunk_meta.get("section_type", chunk_meta.get("tipo_secao", "")),
                        ),
                        section_title=section.get("raw_title", "") if section else "",
                        text=chunk.get("text", ""),
                        score=0.0,
                        leaflet_type=meta.get("leaflet_type", chunk_meta.get("leaflet_type", "")),
                        source="graph_relation",
                        relations=[rt_value],
                        apresentacao=chunk_meta.get("apresentacao", ""),
                    )
                )

        return items

    def _get_chunks_by_entities(
        self,
        entities: list[dict],
        medication: Optional[str],
        leaflet_type: Optional[str],
    ) -> list[EvidenceItem]:
        """
        Busca chunks que mencionam entidades específicas.

        Procura incoming e outgoing para cobertura completa.
        """
        items: list[EvidenceItem] = []
        seen_chunks: set[str] = set()

        for entity in entities:
            canonical = entity.get("canonical")
            if not canonical:
                continue

            try:
                node_id = self.store.find_node(canonical)
            except Exception as exc:
                logger.warning("Failed to find node for entity %s: %s", canonical, exc)
                continue

            if not node_id:
                continue

            neighbors = []
            for direction in ("incoming", "outgoing"):
                try:
                    neighbors.extend(self.store.get_neighbors(node_id, direction))
                except Exception as exc:
                    logger.debug("Could not get %s neighbors for node %s: %s", direction, node_id, exc)

            for neighbor in neighbors:
                edge = neighbor.get("edge", {})
                chunk_id = edge.get("evidence_chunk_id")

                if not chunk_id or chunk_id in seen_chunks:
                    continue

                chunk = self._safe_get_evidence_chunk(chunk_id)
                if not chunk:
                    continue

                chunk_meta = chunk.get("metadata", {})

                if medication:
                    chunk_medication = _safe_lower(
                        chunk_meta.get("medication", "")
                        or chunk_meta.get("medicamento", "")
                    )
                    if chunk_medication != _safe_lower(medication):
                        continue

                if leaflet_type:
                    chunk_leaflet_type = chunk_meta.get("leaflet_type") or chunk_meta.get("tipo_bula")
                    if chunk_leaflet_type and chunk_leaflet_type != leaflet_type:
                        continue

                section = self._safe_get_section(chunk.get("section_id"))
                seen_chunks.add(chunk_id)

                items.append(
                    EvidenceItem(
                        chunk_id=chunk_id,
                        section_type=chunk_meta.get("section_type", chunk_meta.get("tipo_secao", "")),
                        section_title=section.get("raw_title", "") if section else "",
                        text=chunk.get("text", ""),
                        score=0.0,
                        leaflet_type=chunk_meta.get("leaflet_type", chunk_meta.get("tipo_bula", "")),
                        source="graph_entity",
                        relations=[edge.get("type", "")],
                        apresentacao=chunk_meta.get("apresentacao", ""),
                    )
                )

        return items

    # ===================================================================
    # 4. Busca vetorial complementar por plano
    # ===================================================================

    def _retrieve_by_vector_plan(
        self,
        question: str,
        medication: str,
        leaflet_type: Optional[str],
        plan: RetrievalPlan,
    ) -> list[EvidenceItem]:
        """Busca complementar no vectorstore existente, controlada pelo RetrievalPlan."""
        if not self.vectorstore:
            return []

        try:
            section_types = [
                _enum_value(section)
                for section in plan.target_sections
            ]

            filters: list[dict] = [{"medicamento": medication.lower()}]

            if section_types:
                filters.append({"tipo_secao": {"$in": section_types}})

            if leaflet_type:
                filters.append({"tipo_bula": leaflet_type})

            filter_dict: dict
            if len(filters) == 1:
                filter_dict = filters[0]
            else:
                filter_dict = {"$and": filters}

            docs = self.vectorstore.similarity_search(
                query=question,
                filter=filter_dict,
                k=plan.top_k_vector or 10,
            )

            items: list[EvidenceItem] = []
            for doc in docs:
                items.append(
                    EvidenceItem(
                        chunk_id=f"vector_{hash(doc.page_content) % 10000}",
                        section_type=doc.metadata.get("tipo_secao", ""),
                        section_title=doc.metadata.get(
                            "titulo_secao", doc.metadata.get("section", "")
                        ),
                        text=doc.page_content,
                        score=0.0,
                        leaflet_type=doc.metadata.get("tipo_bula", ""),
                        source="vector",
                        relations=[],
                        apresentacao=doc.metadata.get("apresentacao", ""),
                    )
                )
            return items

        except Exception as exc:
            logger.warning("Vector search failed: %s", exc)
            return []

    # ===================================================================
    # Merge + Dedup
    # ===================================================================

    @staticmethod
    def _merge_candidates(
        graph_candidates: list[EvidenceItem],
        vector_candidates: list[EvidenceItem],
    ) -> list[EvidenceItem]:
        """Merge e dedup de candidatos de grafo e vetorial."""
        seen_texts: set[str] = set()
        merged: list[EvidenceItem] = []

        # Grafo tem prioridade
        for item in graph_candidates:
            text_key = _text_hash(item.text[:200])
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                merged.append(item)

        for item in vector_candidates:
            text_key = _text_hash(item.text[:200])
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                merged.append(item)

        return merged

    @staticmethod
    def _dedupe_candidates(candidates: list[EvidenceItem]) -> list[EvidenceItem]:
        """Remove duplicatas por chunk_id."""
        seen: set[str] = set()
        deduped: list[EvidenceItem] = []
        for item in candidates:
            if item.chunk_id not in seen:
                seen.add(item.chunk_id)
                deduped.append(item)
        return deduped

    # ===================================================================
    # 5. Reranking
    # ===================================================================

    def _rerank(
        self,
        candidates: list[EvidenceItem],
        intent_candidates: list[IntentCandidate],
        plan: RetrievalPlan,
        question: str,
        normalized_question: str,
        entities: list[dict],
        leaflet_type: Optional[str],
    ) -> list[EvidenceItem]:
        """
        Pontua e ordena candidatos usando critérios multi-fator orientados
        por múltiplas intenções e pelo plano de recuperação.

        Scoring:
          - seção compatível com intenção candidata: até +3 (proporcional à confidence)
          - relação clínica compatível: +3
          - evidência vinda de relação explícita do grafo: +1.5
          - entidade normalizada encontrada no texto: +2
          - mesmo tipo de bula solicitado: +2
          - overlap lexical com a pergunta: até +1
          - seção crítica de segurança: +1
          - penalidade por texto muito curto (<50 chars): -1.5
          - penalidade por texto muito longo (>2000 chars): -1
          - penalidade por texto genérico/boilerplate: -2
          - bonus por texto com tamanho ideal (100-1800 chars): +0.5
        """
        # Consolidar seções e relações alvo de TODAS as intenções candidatas
        target_section_values: dict[str, float] = {}
        target_relation_values: set[str] = set()

        for candidate in intent_candidates:
            sections = INTENT_TO_SECTIONS.get(candidate.intent, [])
            for s in sections:
                key = _enum_value(s)
                # Armazena a maior confidence associada a cada seção
                target_section_values[key] = max(
                    target_section_values.get(key, 0.0),
                    candidate.confidence,
                )

            relations = INTENT_TO_RELATIONS.get(candidate.intent, [])
            for r in relations:
                target_relation_values.add(_enum_value(r))

        # Seções críticas para bônus extra
        critical_section_values = {
            _enum_value(s) for s in self._critical_safety_sections()
        }

        entity_canonicals = {_safe_lower(e.get("canonical", "")) for e in entities}

        question_words = set(re.findall(r'\w{3,}', question.lower()))

        for item in candidates:
            score = 0.0

            # Seção compatível com intenção (proporcional à confidence)
            section_conf = target_section_values.get(item.section_type, 0.0)
            if section_conf > 0:
                score += 3.0 * section_conf

            # Relação clínica compatível
            for rel in item.relations:
                if rel in target_relation_values:
                    score += 3.0
                    break

            # Evidência vinda de relação explícita do grafo
            if item.source == "graph_relation":
                score += 1.5

            # Entidade normalizada encontrada
            item_text_lower = item.text.lower()
            for entity_canonical in entity_canonicals:
                if entity_canonical and entity_canonical in item_text_lower:
                    score += 2.0
                    break

            # Mesmo tipo de bula
            if leaflet_type and item.leaflet_type == leaflet_type:
                score += 2.0

            # Overlap lexical com a pergunta
            matching_words = sum(1 for w in question_words if w in item_text_lower)
            score += min(matching_words * 0.3, 1.0)

            # Seção crítica de segurança
            if item.section_type in critical_section_values:
                score += 1.0

            # Penalizações por tamanho
            text_len = len(item.text)
            if text_len < 50:
                score -= 1.5
            elif text_len > 2000:
                score -= 1.0

            # Bonus: texto com tamanho ideal
            if 100 < text_len < 1800:
                score += 0.5

            # Penalização por boilerplate genérico
            if self._is_boilerplate(item.text):
                score -= 2.0

            item.score = round(score, 2)

        # Ordena por score decrescente
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates

    @staticmethod
    def _is_boilerplate(text: str) -> bool:
        """Detecta texto genérico/boilerplate de bula."""
        for pattern in _BOILERPLATE_PATTERNS:
            if pattern.search(text):
                return True
        return False

    # ===================================================================
    # 6. Confidence
    # ===================================================================

    def _compute_confidence(
        self,
        query_understanding: QueryUnderstanding,
        evidence: list[EvidenceItem],
    ) -> dict:
        """
        Calcula confiança em 3 camadas:
          - intent_confidence: confiança na classificação de intenção
          - retrieval_confidence: cobertura de seções/relações esperadas
          - answer_confidence: capacidade de responder com base na evidência
        """
        intent_conf = query_understanding.intent_confidence

        # Retrieval confidence: proporção de seções esperadas cobertas
        expected_sections = {
            _enum_value(sc.section_type)
            for sc in query_understanding.section_candidates
        }
        covered_sections = {
            item.section_type
            for item in evidence
            if item.section_type
        }

        if expected_sections:
            section_coverage = len(expected_sections & covered_sections) / len(expected_sections)
        else:
            section_coverage = 0.5 if evidence else 0.0

        # Fator de qualidade da evidência
        if evidence:
            avg_score = sum(item.score for item in evidence) / len(evidence)
            max_possible = 12.0  # score máximo teórico aproximado
            evidence_quality = _clamp01(avg_score / max_possible)
        else:
            evidence_quality = 0.0

        retrieval_conf = _clamp01(
            0.6 * section_coverage + 0.4 * evidence_quality
        )

        # Answer confidence: combinação de ambos
        answer_conf = _clamp01(
            min(intent_conf, retrieval_conf)
            * (0.5 + 0.5 * evidence_quality)
        )

        return {
            "intent_confidence": round(intent_conf, 3),
            "retrieval_confidence": round(retrieval_conf, 3),
            "answer_confidence": round(answer_conf, 3),
        }

    # ===================================================================
    # Helpers defensivos para acesso ao store
    # ===================================================================

    def _safe_get_leaflet(self, leaflet_id: Optional[str]) -> Optional[dict]:
        """Busca leaflet com tratamento de erro."""
        if not leaflet_id:
            return None
        try:
            return self.store.get_leaflet(leaflet_id)
        except Exception as exc:
            logger.warning("Failed to get leaflet %s: %s", leaflet_id, exc)
            return None

    def _safe_get_evidence_chunk(self, chunk_id: Optional[str]) -> Optional[dict]:
        """Busca evidence chunk com tratamento de erro."""
        if not chunk_id:
            return None
        try:
            return self.store.get_evidence_chunk(chunk_id)
        except Exception as exc:
            logger.warning("Failed to get evidence chunk %s: %s", chunk_id, exc)
            return None

    def _safe_get_section(self, section_id: Optional[str]) -> Optional[dict]:
        """Busca section com tratamento de erro."""
        if not section_id:
            return None
        try:
            return self.store.get_section(section_id)
        except Exception as exc:
            logger.warning("Failed to get section %s: %s", section_id, exc)
            return None

    @staticmethod
    def _to_debug_dict(obj: Any) -> dict:
        """Converte dataclass ou objeto para dict serializável."""
        if hasattr(obj, "__dataclass_fields__"):
            result = {}
            for field_name in obj.__dataclass_fields__:
                value = getattr(obj, field_name)
                if hasattr(value, "value"):  # enum
                    result[field_name] = value.value
                elif isinstance(value, list):
                    result[field_name] = [
                        BulaGraphRetriever._to_debug_dict(v)
                        if hasattr(v, "__dataclass_fields__")
                        else (v.value if hasattr(v, "value") else v)
                        for v in value
                    ]
                else:
                    result[field_name] = value
            return result
        return {"value": str(obj)}
