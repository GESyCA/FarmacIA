import json
import csv
import os
import time
from pathlib import Path
from tqdm import tqdm

from deepeval.test_case import LLMTestCase
from eval_deepeval.schemas import EvaluationResult
from metrics.context_metrics import (
    evaluate_contextual_recall, 
    evaluate_contextual_precision, 
    evaluate_evidence_sufficiency
)
from metrics.response_metrics import (
    evaluate_faithfulness, 
    evaluate_answer_relevancy, 
    evaluate_response_completeness, 
    evaluate_unsupported_claims
)
from metrics.bula_metrics import (
    evaluate_clinical_safety,
    evaluate_warning_preservation,
    evaluate_patient_comprehensibility,
    evaluate_inference_control
)
from metrics.score_aggregator import aggregate_scores
from utils.deepeval_gemini import GeminiDeepEvalModel

def run_evaluation(test_cases_data: list, output_file: str, model: str = "gemini/gemini-2.5-flash"):
    """
    Executa a pipeline de avaliação do DeepEval para uma lista de casos de teste.
    Cada item em test_cases_data deve ser um dicionário com:
    - question_id
    - pipeline_name
    - difficulty
    - drug_name
    - input (pergunta)
    - actual_output (resposta)
    - expected_output (gabarito)
    - retrieval_context (lista de chunks textuais)
    """
    
    results = []
    deepeval_model = GeminiDeepEvalModel(model_name=model)
    
    for data in tqdm(test_cases_data, desc="Avaliando casos de teste"):
        
        # Criação do LLMTestCase do DeepEval
        test_case = LLMTestCase(
            input=data.get("input", ""),
            actual_output=data.get("actual_output", ""),
            expected_output=data.get("expected_output", ""),
            retrieval_context=data.get("retrieval_context", [])
        )
        
        # Inicializando o resultado
        eval_result = EvaluationResult(
            question_id=str(data.get("question_id", "")),
            pipeline_name=data.get("pipeline_name", "unknown"),
            difficulty=data.get("difficulty", "unknown"),
            drug_name=data.get("drug_name", "unknown")
        )
        
        # ==========================================
        # 1. CAMADA DE CONTEXTO
        # ==========================================
        eval_result.contextual_recall = evaluate_contextual_recall(test_case, deepeval_model)
        time.sleep(2)
        eval_result.contextual_precision = evaluate_contextual_precision(test_case, deepeval_model)
        time.sleep(2)
        eval_result.evidence_sufficiency = evaluate_evidence_sufficiency(test_case, model=model)
        time.sleep(2)
        
        # ==========================================
        # 2. CAMADA DE RESPOSTA
        # ==========================================
        eval_result.faithfulness = evaluate_faithfulness(test_case, deepeval_model)
        time.sleep(2)
        eval_result.answer_relevancy = evaluate_answer_relevancy(test_case, deepeval_model)
        time.sleep(2)
        eval_result.response_completeness = evaluate_response_completeness(test_case, model=model)
        time.sleep(2)
        eval_result.unsupported_claims = evaluate_unsupported_claims(test_case, model=model)
        time.sleep(2)
        
        # ==========================================
        # 3. CAMADA DA BULA
        # ==========================================
        eval_result.clinical_safety = evaluate_clinical_safety(test_case, model=model)
        time.sleep(2)
        eval_result.warning_preservation = evaluate_warning_preservation(test_case, model=model)
        time.sleep(2)
        eval_result.patient_comprehensibility = evaluate_patient_comprehensibility(test_case, model=model)
        time.sleep(2)
        eval_result.inference_control = evaluate_inference_control(test_case, model=model)
        
        # Agregar notas e aplicar falhas críticas
        eval_result = aggregate_scores(eval_result)
        results.append(eval_result.model_dump())
        
        # Salvamento incremental (JSONL)
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(eval_result.model_dump(), ensure_ascii=False) + "\n")
            
    print(f"Avaliação concluída. Resultados salvos em {output_file}")
    return results

if __name__ == "__main__":
    from dotenv import load_dotenv
    # Carrega as variáveis de ambiente (ex: GOOGLE_API_KEY) do arquivo .env na raiz
    load_dotenv()
    
    sample_dataset = [
        {
            "question_id": "test_1",
            "pipeline_name": "Standard RAG",
            "difficulty": "medium",
            "drug_name": "Paracetamol",
            "input": "Posso tomar paracetamol se estiver grávida?",
            "actual_output": "O paracetamol pode ser usado durante a gravidez. No entanto, você deve usar a menor dose efetiva pelo menor tempo possível.",
            "expected_output": "O paracetamol pode ser usado durante a gravidez. No entanto, você deve usar a menor dose efetiva pelo menor tempo possível e sempre procurar orientação médica.",
            "retrieval_context": [
                "Gravidez e lactação: O paracetamol pode ser usado durante a gravidez. No entanto, você deve usar a menor dose efetiva pelo menor tempo possível e com a menor frequência possível."
            ],
            "retrieved_metadata": [],
            "expected_sections": ["Gravidez e lactação"]
        }
    ]
    
    output_path = "resultados/deepeval_results.jsonl"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Limpa arquivo existente
    if os.path.exists(output_path):
        os.remove(output_path)
        
    run_evaluation(sample_dataset, output_path, model="gemini/gemini-3.1-flash-lite")
