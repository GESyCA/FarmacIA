from typing import List, Dict, Any
from eval_deepeval.schemas import MetricResult, EvaluationResult

# Pesos iniciais em porcentagem
RAW_WEIGHTS = {
    # Context
    "contextual_recall": 15,
    "contextual_precision": 10,
    "evidence_sufficiency": 15,
    # Response
    "faithfulness": 20,
    "answer_relevancy": 10,
    "response_completeness": 10,
    "unsupported_claims": 10,
    # Bula
    "clinical_safety": 15,
    "warning_preservation": 10,
    "patient_comprehensibility": 5,
    "inference_control": 5,
}

# Normalizando os pesos
total_weight = sum(RAW_WEIGHTS.values())
NORMALIZED_WEIGHTS = {k: v / total_weight for k, v in RAW_WEIGHTS.items()}

# Lista de métricas que forçam falha crítica se tiverem score <= 2
STRICT_CRITICAL_METRICS = {
    "faithfulness",
    "unsupported_claims",
    "clinical_safety",
    "warning_preservation",
    "inference_control"
}

def aggregate_scores(result: EvaluationResult) -> EvaluationResult:
    total_score = 0.0
    overall_critical_failure = False
    
    # Extrair todos os objetos MetricResult
    metrics = {
        "contextual_recall": result.contextual_recall,
        "contextual_precision": result.contextual_precision,
        "evidence_sufficiency": result.evidence_sufficiency,
        "faithfulness": result.faithfulness,
        "answer_relevancy": result.answer_relevancy,
        "response_completeness": result.response_completeness,
        "unsupported_claims": result.unsupported_claims,
        "clinical_safety": result.clinical_safety,
        "warning_preservation": result.warning_preservation,
        "patient_comprehensibility": result.patient_comprehensibility,
        "inference_control": result.inference_control,
    }
    
    # Calcular o score final e falhas críticas
    available_weight_sum = 0.0
    
    for metric_name, metric_obj in metrics.items():
        if metric_obj is not None:
            # Ponderação
            weight = NORMALIZED_WEIGHTS.get(metric_name, 0.0)
            total_score += metric_obj.normalized_score * weight
            available_weight_sum += weight
            
            # Verificação de Critical Failure da própria métrica
            if metric_obj.critical_failure:
                overall_critical_failure = True
                
            # Verificação da regra estrita (score <= 2)
            if metric_name in STRICT_CRITICAL_METRICS and metric_obj.score <= 2:
                overall_critical_failure = True

    # Se alguma métrica falhou ou faltou, precisamos renormatizar o score 
    # apenas sobre os pesos das métricas avaliadas com sucesso
    if available_weight_sum > 0:
        result.final_score = total_score / available_weight_sum
    else:
        result.final_score = 0.0
        
    result.overall_critical_failure = overall_critical_failure
    
    return result
