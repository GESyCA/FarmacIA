import os
import json
from typing import Dict, Any
from pydantic import BaseModel

from deepeval.metrics import ContextualRecallMetric, ContextualPrecisionMetric
from deepeval.test_case import LLMTestCase

from eval_deepeval.schemas import MetricResult

# We will use litellm or openai directly for the custom G-Evals to guarantee structured JSON output.
import litellm

class EvidenceSufficiencyEvaluation(BaseModel):
    score: int
    critical_failure: bool
    reason: str
    failure_type: str | None

def evaluate_contextual_recall(test_case: LLMTestCase, deepeval_model=None) -> MetricResult:
    # DeepEval native Contextual Recall
    metric = ContextualRecallMetric(
        threshold=0.5,
        model=deepeval_model,
        include_reason=True
    )
    
    try:
        metric.measure(test_case)
        score = metric.score
        reason = metric.reason
        # Map 0-1 to 1-5
        score_1_to_5 = int(round(score * 4 + 1))
        
        return MetricResult(
            metric_name="contextual_recall",
            score=score_1_to_5,
            normalized_score=score,
            critical_failure=score_1_to_5 <= 2,
            reason=reason,
            failure_type=None,
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="contextual_recall",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )

def evaluate_contextual_precision(test_case: LLMTestCase, deepeval_model=None) -> MetricResult:
    # DeepEval native Contextual Precision
    metric = ContextualPrecisionMetric(
        threshold=0.5,
        model=deepeval_model,
        include_reason=True
    )
    
    try:
        metric.measure(test_case)
        score = metric.score
        reason = metric.reason
        # Map 0-1 to 1-5
        score_1_to_5 = int(round(score * 4 + 1))
        
        return MetricResult(
            metric_name="contextual_precision",
            score=score_1_to_5,
            normalized_score=score,
            critical_failure=score_1_to_5 <= 2,
            reason=reason,
            failure_type=None,
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="contextual_precision",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )

def evaluate_evidence_sufficiency(test_case: LLMTestCase, model: str = "gpt-4o") -> MetricResult:
    """
    Custom GEval metric for Evidence Sufficiency.
    """
    prompt = f"""Você é um especialista em avaliação médica (LLM-as-a-judge).
Avalie se os trechos recuperados da bula contêm evidência suficiente para responder corretamente à pergunta do usuário. 
Considere que a resposta deve ser baseada apenas nos trechos fornecidos, sem conhecimento externo.

PERGUNTA: {test_case.input}
CONTEXTO RECUPERADO: {test_case.retrieval_context}

Passos de avaliação:
1. Identifique a intenção da pergunta do usuário.
2. Identifique quais informações seriam necessárias para responder corretamente.
3. Leia os trechos recuperados.
4. Verifique se os trechos contêm evidência direta ou inferência claramente suportada.
5. Penalize se a resposta depender de informação ausente.
6. Penalize se houver contexto irrelevante que possa induzir resposta errada.

Rubrica:
5 = O contexto contém toda a evidência necessária, de forma direta ou claramente sustentada.
4 = O contexto é suficiente, mas há pequena omissão ou ruído irrelevante.
3 = O contexto permite uma resposta parcial, mas falta informação relevante.
2 = O contexto é insuficiente para responder com segurança.
1 = O contexto não contém evidência adequada ou induz resposta incorreta.

Você deve retornar um JSON com a seguinte estrutura:
{{
    "score": <inteiro 1 a 5>,
    "critical_failure": <booleano, true se score <= 2>,
    "reason": "<explicação detalhada justificando a nota>",
    "failure_type": "<um dos seguintes: 'missing_evidence', 'irrelevant_context', ou null se não houver falha>"
}}
"""
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
            num_retries=3
        )
        
        result_json = json.loads(response.choices[0].message.content)
        score = result_json.get("score", 1)
        critical_failure = result_json.get("critical_failure", score <= 2)
        reason = result_json.get("reason", "")
        failure_type = result_json.get("failure_type")
        
        normalized_score = (score - 1) / 4.0
        
        return MetricResult(
            metric_name="evidence_sufficiency",
            score=score,
            normalized_score=normalized_score,
            critical_failure=critical_failure,
            reason=reason,
            failure_type=failure_type,
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="evidence_sufficiency",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )
