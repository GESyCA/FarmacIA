import os
import json
from typing import Dict, Any

from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from eval_deepeval.schemas import MetricResult
import litellm

def evaluate_faithfulness(test_case: LLMTestCase, deepeval_model=None) -> MetricResult:
    # DeepEval native Faithfulness
    metric = FaithfulnessMetric(
        threshold=0.5,
        model=deepeval_model,
        include_reason=True
    )
    
    try:
        metric.measure(test_case)
        score = metric.score
        reason = metric.reason
        score_1_to_5 = int(round(score * 4 + 1))
        
        return MetricResult(
            metric_name="faithfulness",
            score=score_1_to_5,
            normalized_score=score,
            critical_failure=score_1_to_5 <= 2,
            reason=reason,
            failure_type=None if score_1_to_5 > 2 else "contradiction",
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="faithfulness",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )

def evaluate_answer_relevancy(test_case: LLMTestCase, deepeval_model=None) -> MetricResult:
    # DeepEval native Answer Relevancy
    metric = AnswerRelevancyMetric(
        threshold=0.5,
        model=deepeval_model,
        include_reason=True
    )
    
    try:
        metric.measure(test_case)
        score = metric.score
        reason = metric.reason
        score_1_to_5 = int(round(score * 4 + 1))
        
        return MetricResult(
            metric_name="answer_relevancy",
            score=score_1_to_5,
            normalized_score=score,
            critical_failure=score_1_to_5 <= 2,
            reason=reason,
            failure_type=None,
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="answer_relevancy",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )

def evaluate_response_completeness(test_case: LLMTestCase, model: str = "gpt-4o") -> MetricResult:
    prompt = f"""Você é um especialista em avaliação médica (LLM-as-a-judge).
Avalie se a resposta cobre todos os aspectos clinicamente relevantes presentes nos trechos da bula para responder à pergunta. 
Penalize omissões importantes, especialmente contraindicações, advertências, posologia, modo de uso, reações adversas, restrições de população, gravidez, lactação, interações, superdose ou instruções sobre esquecimento de dose.

PERGUNTA: {test_case.input}
CONTEXTO RECUPERADO: {test_case.retrieval_context}
RESPOSTA GERADA: {test_case.actual_output}

Passos de avaliação:
1. Leia a pergunta do usuário.
2. Leia os trechos recuperados.
3. Identifique todos os pontos relevantes para responder à pergunta.
4. Compare esses pontos com a resposta gerada.
5. Penalize omissões clinicamente relevantes.
6. Não penalize a ausência de detalhes irrelevantes à pergunta.

Rubrica:
5 = A resposta cobre todos os pontos relevantes.
4 = A resposta omite apenas detalhe menor, sem impacto clínico.
3 = A resposta cobre o ponto principal, mas omite informação relevante.
2 = A resposta é superficial ou omite várias informações importantes.
1 = A resposta não responde adequadamente ou omite informação crítica.

Você deve retornar um JSON com a seguinte estrutura:
{{
    "score": <inteiro 1 a 5>,
    "critical_failure": <booleano, true se score <= 2>,
    "reason": "<explicação detalhada justificando a nota>",
    "failure_type": "<um dos seguintes: 'incomplete_answer', ou null se não houver falha>"
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
            metric_name="response_completeness",
            score=score,
            normalized_score=normalized_score,
            critical_failure=critical_failure,
            reason=reason,
            failure_type=failure_type,
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="response_completeness",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )

def evaluate_unsupported_claims(test_case: LLMTestCase, model: str = "gpt-4o") -> MetricResult:
    prompt = f"""Você é um especialista em avaliação médica (LLM-as-a-judge).
Avalie se a resposta contém qualquer afirmação médica, farmacológica, posológica, de segurança, contraindicação, interação, indicação ou reação adversa que não esteja sustentada pelos trechos recuperados. 
Penalize fortemente extrapolações, generalizações e uso de conhecimento externo.

PERGUNTA: {test_case.input}
CONTEXTO RECUPERADO: {test_case.retrieval_context}
RESPOSTA GERADA: {test_case.actual_output}

Passos de avaliação:
1. Extraia as principais afirmações clínicas da resposta.
2. Para cada afirmação, verifique se há suporte explícito ou inferência claramente permitida no contexto.
3. Marque afirmações sem suporte.
4. Penalize afirmações sem suporte proporcionalmente ao risco clínico.
5. Se houver afirmação perigosa ou contraditória, marque critical_failure como true.

Rubrica:
5 = Todas as afirmações estão suportadas.
4 = Há pequena formulação não literal, mas sem alteração de sentido.
3 = Há inferências fracas, mas sem risco clínico relevante.
2 = Há afirmações importantes sem suporte.
1 = Há alucinação, contradição ou afirmação clinicamente perigosa.

Você deve retornar um JSON com a seguinte estrutura:
{{
    "score": <inteiro 1 a 5>,
    "critical_failure": <booleano, true se score <= 2 ou afirmação perigosa>,
    "reason": "<explicação detalhada justificando a nota, listando as afirmações não suportadas se houver>",
    "failure_type": "<um dos seguintes: 'unsupported_claim', 'contradiction', ou null se não houver falha>"
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
            metric_name="unsupported_claims",
            score=score,
            normalized_score=normalized_score,
            critical_failure=critical_failure,
            reason=reason,
            failure_type=failure_type,
            evidence=[]
        )
    except Exception as e:
        return MetricResult(
            metric_name="unsupported_claims",
            score=0,
            normalized_score=0.0,
            critical_failure=True,
            reason=f"Failed to evaluate: {str(e)}",
            failure_type="evaluation_error",
            evidence=[]
        )
