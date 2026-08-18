"""
BulaGraph Formatter — formatação de respostas estruturadas com evidência.

Gera respostas no formato padronizado, garantindo:
  - Toda resposta cita evidência textual
  - Nenhuma afirmação sem base na bula
  - Safety notes automáticos para populações de risco
  - Orientação profissional quando apropriado
"""

from typing import Optional
from bulagraph.retriever import RetrievalResult, EvidenceItem
from bulagraph.ontology import QueryIntent


# ---------------------------------------------------------------------------
# Intenções que requerem safety note reforçada
# ---------------------------------------------------------------------------
HIGH_RISK_INTENTS = {
    QueryIntent.PREGNANCY_LACTATION.value,
    QueryIntent.PEDIATRIC.value,
    QueryIntent.ELDERLY.value,
    QueryIntent.CONTRAINDICATION.value,
    QueryIntent.INTERACTION.value,
    QueryIntent.OVERDOSE.value,
    QueryIntent.RENAL_HEPATIC.value,
}

SAFETY_NOTE = (
    "Esta resposta se baseia apenas nos trechos da bula recuperados "
    "e não substitui orientação médica ou farmacêutica."
)

SEEK_PROFESSIONAL_NOTE = (
    " É recomendável consultar um profissional de saúde para orientação individualizada."
)


# ---------------------------------------------------------------------------
# Formatador principal
# ---------------------------------------------------------------------------

def format_response(
    result: RetrievalResult,
    max_evidence: int = 5,
) -> dict:
    """
    Formata o resultado da recuperação em um objeto estruturado.
    
    Args:
        result: RetrievalResult do BulaGraphRetriever
        max_evidence: Número máximo de evidências no output
        
    Returns:
        dict com answer, intent, medication, leaflet_type, evidence, safety_note
    """
    evidence_items = result.evidence[:max_evidence]
    
    # Gera resposta textual
    answer = _generate_answer_text(result, evidence_items)
    
    # Safety note
    safety_note = SAFETY_NOTE
    if result.intent in HIGH_RISK_INTENTS:
        safety_note += SEEK_PROFESSIONAL_NOTE
    
    # Evidências formatadas
    formatted_evidence = [
        {
            "section_title": item.section_title,
            "section_type": item.section_type,
            "text": item.text,
            "source": item.source,
            "score": item.score,
        }
        for item in evidence_items
    ]
    
    return {
        "answer": answer,
        "intent": result.intent,
        "medication": result.medication,
        "leaflet_type": result.leaflet_type,
        "evidence": formatted_evidence,
        "safety_note": safety_note,
    }


def _generate_answer_text(
    result: RetrievalResult,
    evidence_items: list[EvidenceItem],
) -> str:
    """Gera o texto da resposta baseado nas evidências."""
    
    if not evidence_items:
        return (
            "Na bula consultada, não foi encontrado trecho suficiente para "
            "responder a esta pergunta. Recomenda-se consultar a bula completa "
            "ou um profissional de saúde."
        )
    
    # Seções citadas (únicas)
    cited_sections = []
    seen = set()
    for item in evidence_items:
        if item.section_title and item.section_title not in seen:
            cited_sections.append(item.section_title)
            seen.add(item.section_title)
    
    sections_str = ", ".join(f'"{s}"' for s in cited_sections) if cited_sections else "seção não identificada"
    
    # Monta resposta
    medication_label = result.medication if result.medication else "do medicamento"
    
    intro = f"Na bula consultada de {medication_label}"
    
    if len(cited_sections) == 1:
        intro += f", na seção {sections_str}"
    elif len(cited_sections) > 1:
        intro += f", nas seções {sections_str}"
    
    # Resumo baseado na intenção
    intent_prefix = _get_intent_prefix(result.intent)
    
    # Trecho principal de evidência
    main_evidence = evidence_items[0].text.strip()
    # Limita tamanho do trecho na resposta
    if len(main_evidence) > 500:
        main_evidence = main_evidence[:497] + "..."
    
    answer = f"{intro}, {intent_prefix}: \"{main_evidence}\""
    
    # Adiciona orientação para buscar profissional quando relevante
    if result.intent in HIGH_RISK_INTENTS:
        answer += (
            "\n\nÉ importante consultar um médico ou farmacêutico "
            "para orientação personalizada sobre esta questão."
        )
    
    return answer


def _get_intent_prefix(intent: str) -> str:
    """Retorna um prefixo contextual baseado na intenção."""
    prefixes = {
        "indication": "consta a seguinte informação sobre indicação",
        "contraindication": "consta a seguinte informação sobre contraindicação",
        "interaction": "consta a seguinte informação sobre interações",
        "dosage": "consta a seguinte informação sobre posologia e modo de uso",
        "adverse_reaction": "constam as seguintes informações sobre reações adversas",
        "warning_precaution": "consta a seguinte informação sobre advertências e precauções",
        "pregnancy_lactation": "consta a seguinte informação sobre uso na gravidez/amamentação",
        "elderly": "consta a seguinte informação sobre uso em idosos",
        "pediatric": "consta a seguinte informação sobre uso pediátrico",
        "renal_hepatic": "consta a seguinte informação sobre uso em pacientes com condições renais/hepáticas",
        "storage": "consta a seguinte informação sobre armazenamento",
        "missed_dose": "consta a seguinte informação sobre dose esquecida",
        "overdose": "consta a seguinte informação sobre superdose",
        "comparison": "constam as seguintes informações para comparação",
        "general": "constam as seguintes informações",
    }
    return prefixes.get(intent, "constam as seguintes informações")
