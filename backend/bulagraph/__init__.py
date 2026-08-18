"""
BulaGraph — módulo GraphRAG leve para bulas de medicamentos.

Exporta as classes principais para uso direto:

    from bulagraph import BulaGraphStore, BulaGraphImporter, BulaGraphRetriever
    from bulagraph import format_response
"""

from bulagraph.store import BulaGraphStore
from bulagraph.importer import BulaGraphImporter
from bulagraph.retriever import (
    BulaGraphRetriever,
    RetrievalResult,
    EvidenceItem,
    IntentCandidate,
    SectionCandidate,
    RetrievalPlan,
    QueryUnderstanding,
)
from bulagraph.formatter import format_response
from bulagraph.normalizer import normalize_entity, normalize_text, add_synonym
from bulagraph.ontology import (
    NodeType, RelationType, SectionType, LeafletType, QueryIntent,
    PATIENT_SECTION_MAP, PROFESSIONAL_SECTION_MAP,
    INTENT_TO_SECTIONS, INTENT_TO_RELATIONS,
)

__all__ = [
    # Core classes
    "BulaGraphStore",
    "BulaGraphImporter",
    "BulaGraphRetriever",
    # Results
    "RetrievalResult",
    "EvidenceItem",
    # Query understanding (v2)
    "IntentCandidate",
    "SectionCandidate",
    "RetrievalPlan",
    "QueryUnderstanding",
    # Formatter
    "format_response",
    # Normalizer
    "normalize_entity",
    "normalize_text",
    "add_synonym",
    # Ontology
    "NodeType",
    "RelationType",
    "SectionType",
    "LeafletType",
    "QueryIntent",
    "PATIENT_SECTION_MAP",
    "PROFESSIONAL_SECTION_MAP",
    "INTENT_TO_SECTIONS",
    "INTENT_TO_RELATIONS",
]
