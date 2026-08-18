"""
BulaGraph Normalizer — normalização de linguagem leiga para termos clínicos.

Implementa um dicionário expansível que mapeia expressões populares do
português brasileiro para termos clínicos padronizados, permitindo:
  - Normalização de entidades extraídas de bulas
  - Normalização de termos da pergunta do usuário
  - Expansão de sinônimos para melhorar recall na busca
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Dicionário de normalização leigo → clínico
# Chaves em minúsculo. Ordem: mais específico primeiro (multiword antes).
# ---------------------------------------------------------------------------
LAY_TO_CLINICAL: dict[str, str] = {
    # Condições hepáticas/renais
    "problemas no fígado": "doença hepática",
    "problema no fígado": "doença hepática",
    "problemas hepáticos": "doença hepática",
    "doença no fígado": "doença hepática",
    "insuficiência hepática": "doença hepática",
    "hepatopatia": "doença hepática",
    "hepatopatias": "doença hepática",
    "comprometimento hepático": "doença hepática",
    "problemas nos rins": "doença renal",
    "problema nos rins": "doença renal",
    "problemas renais": "doença renal",
    "doença nos rins": "doença renal",
    "insuficiência renal": "doença renal",
    "nefropatia": "doença renal",
    "nefropatias": "doença renal",
    # Cardiovascular
    "pressão alta": "hipertensão",
    "pressão arterial alta": "hipertensão",
    # Glicemia
    "açúcar no sangue": "glicemia",
    "nível de açúcar": "glicemia",
    "taxa de glicose": "glicemia",
    # Diabetes (já é termo clínico, mas normaliza para consistência)
    "diabetes": "diabetes",
    # Substâncias / medicamentos
    "remédio para afinar o sangue": "anticoagulante",
    "remédio para afinar sangue": "anticoagulante",
    "afinador de sangue": "anticoagulante",
    "bebidas alcoólicas": "álcool",
    "bebida alcoólica": "álcool",
    "álcool": "álcool",
    # Populações
    "grávida": "gestante",
    "gravidez": "gestante",
    "gestação": "gestante",
    "mulher grávida": "gestante",
    "mulheres grávidas": "gestante",
    "amamentando": "lactante",
    "amamentação": "lactante",
    "aleitamento": "lactante",
    "mulher que amamenta": "lactante",
    # Faixas etárias
    "idoso": "idoso",
    "idosos": "idoso",
    "pessoa idosa": "idoso",
    "paciente idoso": "idoso",
    "pacientes idosos": "idoso",
    "terceira idade": "idoso",
    "criança": "criança",
    "crianças": "criança",
    "menor de idade": "criança",
    "menores de 12 anos": "criança",
    "menores de idade": "criança",
    "pediátrico": "criança",
    "pediatria": "criança",
    "lactente": "lactente",
    "lactentes": "lactente",
    "bebê": "lactente",
    "bebês": "lactente",
    "recém-nascido": "lactente",
    "recém-nascidos": "lactente",
    # Reações comuns em linguagem popular
    "enjoo": "náusea",
    "enjoos": "náusea",
    "vontade de vomitar": "náusea",
    "ânsia": "náusea",
    "vômito": "vômito",
    "diarreia": "diarreia",
    "diarréia": "diarreia",
    "coceira": "prurido",
    "alergia": "reação alérgica",
    "reação alérgica": "reação alérgica",
    "erupção na pele": "erupção cutânea",
    "manchas na pele": "erupção cutânea",
    "vermelhidão": "eritema",
    "sonolência": "sonolência",
    "sono": "sonolência",
    "tontura": "tontura",
    "dor de cabeça": "cefaleia",
    # Formas farmacêuticas
    "comprimido": "comprimido",
    "cápsula": "cápsula",
    "suspensão": "suspensão oral",
    "xarope": "suspensão oral",
    "gotas": "solução oral",
    "injeção": "injetável",
}

# ---------------------------------------------------------------------------
# Dicionário reverso: canônico → lista de aliases
# Construído automaticamente a partir de LAY_TO_CLINICAL
# ---------------------------------------------------------------------------
_CLINICAL_TO_ALIASES: dict[str, set[str]] = {}
for _lay, _clin in LAY_TO_CLINICAL.items():
    _CLINICAL_TO_ALIASES.setdefault(_clin, set()).add(_lay)
    _CLINICAL_TO_ALIASES[_clin].add(_clin)  # o próprio termo canônico é alias


def get_aliases(canonical: str) -> list[str]:
    """Retorna todos os aliases conhecidos para um termo canônico."""
    return sorted(_CLINICAL_TO_ALIASES.get(canonical.lower(), {canonical.lower()}))


# ---------------------------------------------------------------------------
# Funções de normalização
# ---------------------------------------------------------------------------

def normalize_entity(text: str) -> str:
    """
    Normaliza uma entidade individual (ex: "problemas no fígado" → "doença hepática").
    Retorna o texto original em minúsculo se não houver correspondência.
    """
    lower = text.strip().lower()
    return LAY_TO_CLINICAL.get(lower, lower)


def normalize_text(text: str) -> str:
    """
    Aplica normalização em um texto completo, substituindo todas as ocorrências
    de termos leigos por seus equivalentes clínicos.
    
    A substituição é feita dos termos mais longos para os mais curtos,
    evitando substituições parciais incorretas.
    """
    result = text.lower()
    # Ordena chaves por comprimento decrescente para evitar substituições parciais
    sorted_terms = sorted(LAY_TO_CLINICAL.keys(), key=len, reverse=True)
    for lay_term in sorted_terms:
        clinical_term = LAY_TO_CLINICAL[lay_term]
        if lay_term != clinical_term:
            # Usa word boundaries para evitar substituições dentro de palavras
            pattern = re.compile(re.escape(lay_term), re.IGNORECASE)
            result = pattern.sub(clinical_term, result)
    return result


def extract_normalized_entities(text: str) -> list[dict]:
    """
    Extrai todas as entidades normalizáveis encontradas em um texto.
    
    Returns:
        Lista de dicts com:
          - original: texto original encontrado
          - canonical: termo normalizado
          - start: posição inicial no texto
          - end: posição final no texto
    """
    found: list[dict] = []
    lower_text = text.lower()
    # Ordena chaves por comprimento decrescente
    sorted_terms = sorted(LAY_TO_CLINICAL.keys(), key=len, reverse=True)
    
    used_positions: set[int] = set()
    
    for lay_term in sorted_terms:
        pattern = re.compile(re.escape(lay_term), re.IGNORECASE)
        for match in pattern.finditer(lower_text):
            start, end = match.start(), match.end()
            # Evita sobreposição de entidades
            if any(pos in used_positions for pos in range(start, end)):
                continue
            for pos in range(start, end):
                used_positions.add(pos)
            found.append({
                "original": text[start:end],
                "canonical": LAY_TO_CLINICAL[lay_term],
                "start": start,
                "end": end,
            })
    
    # Ordena por posição no texto
    found.sort(key=lambda x: x["start"])
    return found


def add_synonym(lay_term: str, clinical_term: str) -> None:
    """
    Adiciona um novo par leigo→clínico ao dicionário de normalização.
    
    Uso:
        add_synonym("remédio para pressão", "anti-hipertensivo")
    """
    key = lay_term.strip().lower()
    value = clinical_term.strip().lower()
    LAY_TO_CLINICAL[key] = value
    _CLINICAL_TO_ALIASES.setdefault(value, set()).add(key)
    _CLINICAL_TO_ALIASES[value].add(value)
