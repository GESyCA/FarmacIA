import os, json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "graficos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODELS = [
    ("Gemma 4:4b", "gemma_4_4b", "gemma_compiled_results.json"),
    ("MedGemma 4b", "medgemma_4b", "medgemma_compiled_results.json"),
    ("Phi4 Mini", "phi4-mini", "phi4_compiled_results.json"),
    ("MediPhi Instruct", "mediphi", "mediphi_compiled_results.json")
]

PIPELINES = ["06_naive", "01_standard", "02_agentic", "03_hybrid_agent", "04_fusion", "05_graph", "07_guarded"]
PIPE_NAMES = {
    "06_naive": "Naive RAG", "01_standard": "Standard RAG", "02_agentic": "Agentic RAG",
    "03_hybrid_agent": "Hybrid Agent RAG", "04_fusion": "Fusion RAG", "05_graph": "Graph RAG",
    "07_guarded": "Guarded RAG"
}
DIFFICULTIES = ["faceis", "medias", "dificeis"]
DIFF_LABELS = {"faceis": "Fáceis", "medias": "Médias", "dificeis": "Difíceis"}

retrieval_rows = []
generation_rows = []

for model_name, folder, fname in MODELS:
    path = os.path.join(BASE_DIR, folder, fname)
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for pipe in PIPELINES:
        for diff in DIFFICULTIES:
            key = f"{pipe}|{diff}"
            if key in data:
                m = data[key]
                
                # Base Info
                base = {
                    "Model": model_name,
                    "Pipeline_Raw": pipe,
                    "Pipeline": PIPE_NAMES.get(pipe, pipe),
                    "Difficulty_Raw": diff,
                    "Dificuldade": DIFF_LABELS.get(diff, diff)
                }
                
                # Retrieval
                ret = base.copy()
                ret["Section Precision"] = m.get("section_precision", 0.0)
                ret["Section Recall"] = m.get("section_recall", 0.0)
                ret["F1-Score"] = m.get("section_f1", 0.0)
                ret["Section Hit"] = m.get("section_hit", 0.0)
                ret["Exact Match"] = m.get("exact_section_match", 0.0)
                ret["All Required"] = m.get("all_required_sections_retrieved", 0.0)
                ret["Hit@10"] = m.get("chunk_recall_at_10", 0.0)
                ret["Evidence Set Recall@10"] = m.get("evidence_set_recall_at_10", 0.0)
                ret["MRR@10"] = m.get("chunk_mrr_at_10", 0.0)
                ret["nDCG@10"] = m.get("chunk_ndcg_at_10", 0.0)
                ret["Retrieval Time (s)"] = m.get("avg_retrieval_time", 0.0)
                retrieval_rows.append(ret)
                
                # Generation
                gen = base.copy()
                gen["BLEU"] = m.get("bleu", 0.0)
                gen["ROUGE"] = m.get("rougeL", 0.0)  # Utilizando ROUGE-L como principal ROUGE geral
                gen["BERTScore"] = m.get("bertscore_f1", 0.0)
                
                gen["Contextual Recall"] = m.get("contextual_recall", 0.0)
                gen["Contextual Precision"] = m.get("contextual_precision", 0.0)
                gen["Evidence Sufficiency"] = m.get("evidence_sufficiency", 0.0)
                
                gen["Faithfulness"] = m.get("faithfulness", 0.0)
                gen["Answer Relevancy"] = m.get("answer_relevancy", 0.0)
                gen["Response Completeness"] = m.get("response_completeness", 0.0)
                gen["Unsupported Claims"] = m.get("unsupported_claims", 0.0)
                
                gen["Clinical Safety"] = m.get("clinical_safety", 0.0)
                gen["Warning Preservation"] = m.get("warning_preservation", 0.0)
                gen["Inference Control"] = m.get("inference_control", 0.0)
                
                gen["Inference Time (s)"] = m.get("avg_inference_time", 0.0)
                generation_rows.append(gen)

df_retrieval = pd.DataFrame(retrieval_rows)
df_generation = pd.DataFrame(generation_rows)

retrieval_path = os.path.join(OUTPUT_DIR, "compiled_retrieval_data.csv")
generation_path = os.path.join(OUTPUT_DIR, "compiled_generation_data.csv")

df_retrieval.to_csv(retrieval_path, index=False)
df_generation.to_csv(generation_path, index=False)

print(f"Salvo: {retrieval_path}")
print(f"Salvo: {generation_path}")
