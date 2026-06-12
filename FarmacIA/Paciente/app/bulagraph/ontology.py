"""
BulaGraph Ontology — tipos de nós, relações e mapeamentos de seção.

Ontologia fechada e orientada à estrutura regulatória de bulas ANVISA.
Todos os tipos são Enums para evitar criação arbitrária de entidades/relações.
"""

from enum import Enum


# ---------------------------------------------------------------------------
# Tipos de Nós
# ---------------------------------------------------------------------------
class NodeType(str, Enum):
    MEDICATION = "Medication"
    ACTIVE_INGREDIENT = "ActiveIngredient"
    LEAFLET = "Leaflet"
    SECTION = "Section"
    EVIDENCE_CHUNK = "EvidenceChunk"
    POPULATION = "Population"
    CLINICAL_CONDITION = "ClinicalCondition"
    ADVERSE_EVENT = "AdverseEvent"
    INTERACTING_SUBSTANCE = "InteractingSubstance"
    RECOMMENDATION = "Recommendation"
    DOSE = "Dose"
    ADMINISTRATION_ROUTE = "AdministrationRoute"
    FREQUENCY = "Frequency"
    STORAGE_CONDITION = "StorageCondition"
    MISSED_DOSE_INSTRUCTION = "MissedDoseInstruction"
    OVERDOSE_INSTRUCTION = "OverdoseInstruction"
    PATIENT_ACTION = "PatientAction"
    SAFETY_WARNING = "SafetyWarning"


# ---------------------------------------------------------------------------
# Tipos de Relação
# ---------------------------------------------------------------------------
class RelationType(str, Enum):
    MEDICATION_HAS_ACTIVE_INGREDIENT = "MEDICATION_HAS_ACTIVE_INGREDIENT"
    MEDICATION_HAS_LEAFLET = "MEDICATION_HAS_LEAFLET"
    LEAFLET_HAS_SECTION = "LEAFLET_HAS_SECTION"
    SECTION_HAS_CHUNK = "SECTION_HAS_CHUNK"
    CHUNK_MENTIONS_POPULATION = "CHUNK_MENTIONS_POPULATION"
    CHUNK_MENTIONS_CONDITION = "CHUNK_MENTIONS_CONDITION"
    CHUNK_MENTIONS_ADVERSE_EVENT = "CHUNK_MENTIONS_ADVERSE_EVENT"
    CHUNK_MENTIONS_INTERACTING_SUBSTANCE = "CHUNK_MENTIONS_INTERACTING_SUBSTANCE"
    CHUNK_EXPRESSES_RECOMMENDATION = "CHUNK_EXPRESSES_RECOMMENDATION"
    INDICATED_FOR = "INDICATED_FOR"
    CONTRAINDICATED_FOR = "CONTRAINDICATED_FOR"
    USE_WITH_CAUTION_IN = "USE_WITH_CAUTION_IN"
    INTERACTS_WITH = "INTERACTS_WITH"
    MAY_CAUSE = "MAY_CAUSE"
    REQUIRES_DOSE_ADJUSTMENT_IN = "REQUIRES_DOSE_ADJUSTMENT_IN"
    MONITOR_IN = "MONITOR_IN"
    HAS_DOSAGE = "HAS_DOSAGE"
    HAS_ADMINISTRATION_ROUTE = "HAS_ADMINISTRATION_ROUTE"
    HAS_FREQUENCY = "HAS_FREQUENCY"
    STORE_UNDER = "STORE_UNDER"
    IF_MISSED_DOSE_DO = "IF_MISSED_DOSE_DO"
    IN_OVERDOSE_DO = "IN_OVERDOSE_DO"
    SEEK_MEDICAL_HELP_IF = "SEEK_MEDICAL_HELP_IF"
    SAME_ACTIVE_INGREDIENT_AS = "SAME_ACTIVE_INGREDIENT_AS"


# ---------------------------------------------------------------------------
# Tipos de Seção (normalizados)
# ---------------------------------------------------------------------------
class SectionType(str, Enum):
    INDICATION = "indication"
    SIMPLIFIED_MECHANISM = "simplified_mechanism"
    CONTRAINDICATION = "contraindication"
    WARNING_PRECAUTION = "warning_precaution"
    STORAGE = "storage"
    DOSAGE = "dosage"
    MISSED_DOSE = "missed_dose"
    ADVERSE_REACTION = "adverse_reaction"
    OVERDOSE = "overdose"
    EFFICACY = "efficacy"
    PHARMACOLOGY = "pharmacology"
    INTERACTION = "interaction"
    IDENTIFICATION = "identification"


# ---------------------------------------------------------------------------
# Tipos de Bula
# ---------------------------------------------------------------------------
class LeafletType(str, Enum):
    PATIENT = "patient_leaflet"
    PROFESSIONAL = "professional_leaflet"


# ---------------------------------------------------------------------------
# Mapeamento de seções: título → SectionType
# ---------------------------------------------------------------------------

PATIENT_SECTION_MAP: dict[str, SectionType] = {
    "Para que este medicamento é indicado?": SectionType.INDICATION,
    "Como este medicamento funciona?": SectionType.SIMPLIFIED_MECHANISM,
    "Quando não devo usar este medicamento?": SectionType.CONTRAINDICATION,
    "O que devo saber antes de usar este medicamento?": SectionType.WARNING_PRECAUTION,
    "Onde, como e por quanto tempo posso guardar este medicamento?": SectionType.STORAGE,
    "Como devo usar este medicamento?": SectionType.DOSAGE,
    "O que devo fazer quando eu me esquecer de usar este medicamento?": SectionType.MISSED_DOSE,
    "Quais os males que este medicamento pode me causar?": SectionType.ADVERSE_REACTION,
    "O que fazer se alguém usar uma quantidade maior do que a indicada deste medicamento?": SectionType.OVERDOSE,
    # Compatibilidade com títulos em MAIÚSCULO (formato do PDF parser existente)
    "PARA QUE ESTE MEDICAMENTO É INDICADO?": SectionType.INDICATION,
    "COMO ESTE MEDICAMENTO FUNCIONA?": SectionType.SIMPLIFIED_MECHANISM,
    "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?": SectionType.CONTRAINDICATION,
    "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?": SectionType.WARNING_PRECAUTION,
    "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?": SectionType.STORAGE,
    "COMO DEVO USAR ESTE MEDICAMENTO?": SectionType.DOSAGE,
    "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?": SectionType.MISSED_DOSE,
    "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?": SectionType.ADVERSE_REACTION,
    "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?": SectionType.OVERDOSE,
    # Seção de identificação (presente nas bulas mas não na lista de seções padrão)
    "IDENTIFICAÇÃO DO MEDICAMENTO": SectionType.IDENTIFICATION,
    "Identificação do medicamento": SectionType.IDENTIFICATION,
}

PROFESSIONAL_SECTION_MAP: dict[str, SectionType] = {
    "Indicações": SectionType.INDICATION,
    "Resultados de eficácia": SectionType.EFFICACY,
    "Características farmacológicas": SectionType.PHARMACOLOGY,
    "Contraindicações": SectionType.CONTRAINDICATION,
    "Advertências e precauções": SectionType.WARNING_PRECAUTION,
    "Interações medicamentosas": SectionType.INTERACTION,
    "Cuidados de armazenamento do medicamento": SectionType.STORAGE,
    "Posologia e modo de usar": SectionType.DOSAGE,
    "Reações adversas": SectionType.ADVERSE_REACTION,
    "Superdose": SectionType.OVERDOSE,
    # Versões em MAIÚSCULO
    "INDICAÇÕES": SectionType.INDICATION,
    "RESULTADOS DE EFICÁCIA": SectionType.EFFICACY,
    "CARACTERÍSTICAS FARMACOLÓGICAS": SectionType.PHARMACOLOGY,
    "CONTRAINDICAÇÕES": SectionType.CONTRAINDICATION,
    "ADVERTÊNCIAS E PRECAUÇÕES": SectionType.WARNING_PRECAUTION,
    "INTERAÇÕES MEDICAMENTOSAS": SectionType.INTERACTION,
    "CUIDADOS DE ARMAZENAMENTO DO MEDICAMENTO": SectionType.STORAGE,
    "POSOLOGIA E MODO DE USAR": SectionType.DOSAGE,
    "REAÇÕES ADVERSAS": SectionType.ADVERSE_REACTION,
    "SUPERDOSE": SectionType.OVERDOSE,
}


# ---------------------------------------------------------------------------
# Intenções de consulta
# ---------------------------------------------------------------------------
class QueryIntent(str, Enum):
    INDICATION = "indication"
    CONTRAINDICATION = "contraindication"
    INTERACTION = "interaction"
    DOSAGE = "dosage"
    ADVERSE_REACTION = "adverse_reaction"
    WARNING_PRECAUTION = "warning_precaution"
    PREGNANCY_LACTATION = "pregnancy_lactation"
    ELDERLY = "elderly"
    PEDIATRIC = "pediatric"
    RENAL_HEPATIC = "renal_hepatic"
    STORAGE = "storage"
    MISSED_DOSE = "missed_dose"
    OVERDOSE = "overdose"
    COMPARISON = "comparison"
    GENERAL = "general"


# ---------------------------------------------------------------------------
# Mapeamento intenção → seções prioritárias
# ---------------------------------------------------------------------------
INTENT_TO_SECTIONS: dict[QueryIntent, list[SectionType]] = {
    QueryIntent.INDICATION: [SectionType.INDICATION],
    QueryIntent.CONTRAINDICATION: [SectionType.CONTRAINDICATION, SectionType.WARNING_PRECAUTION],
    QueryIntent.INTERACTION: [SectionType.INTERACTION, SectionType.WARNING_PRECAUTION],
    QueryIntent.DOSAGE: [SectionType.DOSAGE],
    QueryIntent.ADVERSE_REACTION: [SectionType.ADVERSE_REACTION],
    QueryIntent.WARNING_PRECAUTION: [SectionType.WARNING_PRECAUTION, SectionType.CONTRAINDICATION],
    QueryIntent.PREGNANCY_LACTATION: [SectionType.CONTRAINDICATION, SectionType.WARNING_PRECAUTION],
    QueryIntent.ELDERLY: [SectionType.WARNING_PRECAUTION, SectionType.DOSAGE],
    QueryIntent.PEDIATRIC: [SectionType.WARNING_PRECAUTION, SectionType.CONTRAINDICATION, SectionType.DOSAGE],
    QueryIntent.RENAL_HEPATIC: [SectionType.WARNING_PRECAUTION, SectionType.CONTRAINDICATION, SectionType.DOSAGE],
    QueryIntent.STORAGE: [SectionType.STORAGE],
    QueryIntent.MISSED_DOSE: [SectionType.MISSED_DOSE],
    QueryIntent.OVERDOSE: [SectionType.OVERDOSE],
    QueryIntent.COMPARISON: [SectionType.INDICATION, SectionType.CONTRAINDICATION, SectionType.ADVERSE_REACTION],
    QueryIntent.GENERAL: [
        SectionType.INDICATION,
        SectionType.DOSAGE,
        SectionType.CONTRAINDICATION,
        SectionType.WARNING_PRECAUTION,
        SectionType.ADVERSE_REACTION,
    ],
}


# ---------------------------------------------------------------------------
# Mapeamento intenção → tipos de relação prioritários
# ---------------------------------------------------------------------------
INTENT_TO_RELATIONS: dict[QueryIntent, list[RelationType]] = {
    QueryIntent.INDICATION: [RelationType.INDICATED_FOR],
    QueryIntent.CONTRAINDICATION: [
        RelationType.CONTRAINDICATED_FOR,
        RelationType.CHUNK_MENTIONS_POPULATION,
        RelationType.CHUNK_MENTIONS_CONDITION,
    ],
    QueryIntent.INTERACTION: [
        RelationType.INTERACTS_WITH,
        RelationType.CHUNK_MENTIONS_INTERACTING_SUBSTANCE,
    ],
    QueryIntent.DOSAGE: [
        RelationType.HAS_DOSAGE,
        RelationType.HAS_ADMINISTRATION_ROUTE,
        RelationType.HAS_FREQUENCY,
    ],
    QueryIntent.ADVERSE_REACTION: [
        RelationType.MAY_CAUSE,
        RelationType.CHUNK_MENTIONS_ADVERSE_EVENT,
    ],
    QueryIntent.WARNING_PRECAUTION: [
        RelationType.USE_WITH_CAUTION_IN,
        RelationType.SEEK_MEDICAL_HELP_IF,
        RelationType.MONITOR_IN,
    ],
    QueryIntent.PREGNANCY_LACTATION: [
        RelationType.CONTRAINDICATED_FOR,
        RelationType.USE_WITH_CAUTION_IN,
        RelationType.CHUNK_MENTIONS_POPULATION,
    ],
    QueryIntent.ELDERLY: [
        RelationType.REQUIRES_DOSE_ADJUSTMENT_IN,
        RelationType.USE_WITH_CAUTION_IN,
        RelationType.CHUNK_MENTIONS_POPULATION,
    ],
    QueryIntent.PEDIATRIC: [
        RelationType.CONTRAINDICATED_FOR,
        RelationType.USE_WITH_CAUTION_IN,
        RelationType.CHUNK_MENTIONS_POPULATION,
    ],
    QueryIntent.RENAL_HEPATIC: [
        RelationType.REQUIRES_DOSE_ADJUSTMENT_IN,
        RelationType.USE_WITH_CAUTION_IN,
        RelationType.CHUNK_MENTIONS_CONDITION,
    ],
    QueryIntent.STORAGE: [RelationType.STORE_UNDER],
    QueryIntent.MISSED_DOSE: [RelationType.IF_MISSED_DOSE_DO],
    QueryIntent.OVERDOSE: [RelationType.IN_OVERDOSE_DO],
    QueryIntent.COMPARISON: [RelationType.SAME_ACTIVE_INGREDIENT_AS],
    QueryIntent.GENERAL: [],
}
