from pydantic import BaseModel, Field
from typing import List, Optional

class MetricResult(BaseModel):
    metric_name: str
    score: int
    normalized_score: float
    critical_failure: bool
    reason: str
    failure_type: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)

class EvaluationResult(BaseModel):
    question_id: str
    pipeline_name: str
    difficulty: str
    drug_name: str
    
    # Context metrics
    contextual_recall: Optional[MetricResult] = None
    contextual_precision: Optional[MetricResult] = None
    evidence_sufficiency: Optional[MetricResult] = None
    
    # Response metrics
    faithfulness: Optional[MetricResult] = None
    answer_relevancy: Optional[MetricResult] = None
    response_completeness: Optional[MetricResult] = None
    unsupported_claims: Optional[MetricResult] = None
    
    # Bula metrics
    clinical_safety: Optional[MetricResult] = None
    warning_preservation: Optional[MetricResult] = None
    patient_comprehensibility: Optional[MetricResult] = None
    inference_control: Optional[MetricResult] = None
    
    # Final Score
    final_score: float = 0.0
    overall_critical_failure: bool = False
