import os
import json
import glob
import pandas as pd

# Path to results
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(BASE_DIR, "gemma_4_4b")

# Find files
metrics_files = glob.glob(os.path.join(results_dir, "*_metrics.json"))
eval_files = glob.glob(os.path.join(results_dir, "*_avaliacoes.jsonl"))

# Data structure to hold results
results = {}

pipelines_mapping = {
    "01_standard": "Standard RAG",
    "02_agentic": "Agentic RAG",
    "03_hybrid_agent": "Hybrid Agent RAG",
    "04_fusion": "Fusion RAG",
    "05_graph": "Graph RAG",
    "06_naive": "Naive RAG",
    "07_guarded": "Guarded RAG"
}

difficulty_mapping = {
    "faceis": "Fáceis",
    "medias": "Médias",
    "dificeis": "Difíceis"
}

def parse_filename(filename):
    basename = os.path.basename(filename)
    pipeline = None
    for p_key in pipelines_mapping:
        if basename.startswith(p_key):
            pipeline = p_key
            break
            
    difficulty = None
    for d_key in difficulty_mapping:
        if f"_{d_key}_" in basename:
            difficulty = d_key
            break
            
    return pipeline, difficulty

# Process metrics.json
for f in metrics_files:
    pipeline, difficulty = parse_filename(f)
    if not pipeline or not difficulty:
        continue
        
    key = (pipeline, difficulty)
    if key not in results:
        results[key] = {}
        
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            results[key]['section_precision'] = data.get('section_precision', 0.0)
            results[key]['section_recall'] = data.get('section_recall', 0.0)
            results[key]['section_f1'] = data.get('section_f1', 0.0)
            results[key]['all_required_sections_retrieved'] = data.get('all_required_sections_retrieved', 0.0)
            results[key]['rouge1'] = data.get('rouge', {}).get('rouge1', 0.0)
            results[key]['rougeL'] = data.get('rouge', {}).get('rougeL', 0.0)
            results[key]['bertscore_f1'] = data.get('bertscore_f1', 0.0)
            results[key]['bleu'] = data.get('bleu', 0.0)
            results[key]['unique_chunks_retrieved'] = data.get('unique_chunks_retrieved', 0)
            # Chunks retrieval metrics
            results[key]['chunk_recall_at_1'] = data.get('chunk_retrieval_overall', {}).get('recall@1', 0.0)
            results[key]['chunk_recall_at_3'] = data.get('chunk_retrieval_overall', {}).get('recall@3', 0.0)
            results[key]['chunk_recall_at_5'] = data.get('chunk_retrieval_overall', {}).get('recall@5', 0.0)
            results[key]['chunk_recall_at_10'] = data.get('chunk_retrieval_overall', {}).get('recall@10', 0.0)
            results[key]['chunk_mrr_at_10'] = data.get('chunk_retrieval_overall', {}).get('mrr@10', 0.0)
            results[key]['chunk_ndcg_at_10'] = data.get('chunk_retrieval_overall', {}).get('ndcg@10', 0.0)
    except Exception as e:
        print(f"Error parsing metrics file {f}: {e}")

# Process avaliacoes.jsonl
for f in eval_files:
    pipeline, difficulty = parse_filename(f)
    if not pipeline or not difficulty:
        continue
        
    key = (pipeline, difficulty)
    if key not in results:
        results[key] = {}
        
    try:
        scores = []
        with open(f, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    scores.append(json.loads(line))
        
        if scores:
            df = pd.DataFrame(scores)
            
            # Helper to extract normalized_score from deep eval sub-objects
            def get_mean_subscore(col):
                if col in df.columns:
                    return df[col].apply(lambda x: x.get('normalized_score', 0.0) if isinstance(x, dict) else 0.0).mean()
                return 0.0

            results[key]['contextual_recall'] = get_mean_subscore('contextual_recall')
            results[key]['contextual_precision'] = get_mean_subscore('contextual_precision')
            results[key]['evidence_sufficiency'] = get_mean_subscore('evidence_sufficiency')
            results[key]['faithfulness'] = get_mean_subscore('faithfulness')
            results[key]['answer_relevancy'] = get_mean_subscore('answer_relevancy')
            results[key]['response_completeness'] = get_mean_subscore('response_completeness')
            results[key]['unsupported_claims'] = get_mean_subscore('unsupported_claims')
            results[key]['clinical_safety'] = get_mean_subscore('clinical_safety')
            results[key]['warning_preservation'] = get_mean_subscore('warning_preservation')
            results[key]['patient_comprehensibility'] = get_mean_subscore('patient_comprehensibility')
            results[key]['inference_control'] = get_mean_subscore('inference_control')
            
            if 'final_score' in df.columns:
                results[key]['final_score'] = df['final_score'].mean()
            else:
                results[key]['final_score'] = 0.0
                
            if 'overall_critical_failure' in df.columns:
                # overall_critical_failure is boolean, let's calculate rate of failure
                results[key]['critical_failure_rate'] = df['overall_critical_failure'].mean()
            else:
                results[key]['critical_failure_rate'] = 0.0
    except Exception as e:
        print(f"Error parsing eval file {f}: {e}")

# Process csv files for times
csv_files = glob.glob(os.path.join(results_dir, "*_output.csv"))
for f in csv_files:
    pipeline, difficulty = parse_filename(f)
    if not pipeline or not difficulty:
        continue
    key = (pipeline, difficulty)
    if key not in results:
        results[key] = {}
    try:
        df = pd.read_csv(f)
        if 'tempo_recuperacao_segundos' in df.columns:
            results[key]['avg_retrieval_time'] = float(df['tempo_recuperacao_segundos'].mean())
        else:
            results[key]['avg_retrieval_time'] = 0.0
            
        if 'tempo_inferencia_segundos' in df.columns:
            results[key]['avg_inference_time'] = float(df['tempo_inferencia_segundos'].mean())
        else:
            results[key]['avg_inference_time'] = 0.0
    except Exception as e:
        print(f"Error parsing CSV file {f}: {e}")

# Flatten data for printing
flattened = []
for (pipeline, difficulty), metrics in results.items():
    row = {
        'Pipeline': pipelines_mapping.get(pipeline, pipeline),
        'Pipeline_Raw': pipeline,
        'Dificuldade': difficulty_mapping.get(difficulty, difficulty),
        'Dificuldade_Raw': difficulty,
    }
    row.update(metrics)
    flattened.append(row)

df_all = pd.DataFrame(flattened)

# Let's save a summary json to check
output_json_path = os.path.join(results_dir, "gemma_compiled_results.json")
with open(output_json_path, 'w', encoding='utf-8') as out_f:
    # Convert keys to string for JSON serialization
    serializable = {f"{k[0]}|{k[1]}": v for k, v in results.items()}
    json.dump(serializable, out_f, indent=4, ensure_ascii=False)

print("Compilation successful! Summary saved to JSON.")

