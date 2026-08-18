import pandas as pd
import json
import os
import transformers
transformers.logging.set_verbosity_error()
from evaluate import load
from bert_score import score as bert_score
from nltk.translate.bleu_score import sentence_bleu
import nltk

def evaluate_section_retrieval(df, k=None):
    """
    Avalia a recuperação de seções comparando secoes_esperadas com secoes_recuperadas.
    Calcula Precision, Recall, F1-score, e as novas métricas: Hit, Exact Match, All Required e Coverage.
    Se k for fornecido, restringe a avaliação às K primeiras seções recuperadas.
    """
    precisions = []
    recalls = []
    f1s = []
    
    hits = []
    exact_matches = []
    all_required = []
    for _, row in df.iterrows():
        # Previne que a vírgula de "ONDE, COMO..." seja tratada como separador de seções
        storage_placeholder = "ONDE_COMO_E_POR_QUANTO_TEMPO_POSSO_GUARDAR_ESTE_MEDICAMENTO"
        
        esperadas_raw = str(row.get('secoes_esperadas', '')).replace('\n', ',').replace('/', ',')
        esperadas_raw = esperadas_raw.replace("ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO", storage_placeholder)
        
        recuperadas_raw = str(row.get('secoes_recuperadas', '')).replace('\n', ',').replace('/', ',')
        recuperadas_raw = recuperadas_raw.replace("ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO", storage_placeholder)
        
        esperadas_list = esperadas_raw.split(',')
        recuperadas_list = recuperadas_raw.split(',')
        
        # Limpar strings, normalizar subseções e reverter placeholders
        esperadas_limpas = []
        for s in esperadas_list:
            s_clean = s.strip().upper()
            if s_clean in [storage_placeholder, "ONDE", "COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO", "COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?"]:
                s_clean = "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?"
            elif s_clean in ["APRESENTAÇÕES", "COMPOSIÇÃO", "APRESENTACÕES", "APRESENTACAO", "APRESENTACOES", "COMPOSICAO"]:
                s_clean = "IDENTIFICAÇÃO DO MEDICAMENTO"
            if s_clean:
                esperadas_limpas.append(s_clean)
        esperadas = set(esperadas_limpas)
        
        # Manter a ordem original para permitir o corte K
        rec_limpas = []
        for s in recuperadas_list:
            s_clean = s.strip().upper()
            if s_clean in [storage_placeholder, "ONDE", "COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO", "COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?"]:
                s_clean = "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?"
            elif s_clean in ["APRESENTAÇÕES", "COMPOSIÇÃO", "APRESENTACÕES", "APRESENTACAO", "APRESENTACOES", "COMPOSICAO"]:
                s_clean = "IDENTIFICAÇÃO DO MEDICAMENTO"
            if s_clean and s_clean not in rec_limpas:
                rec_limpas.append(s_clean)
                
        # Aplica o corte top-K nas seções recuperadas
        if k is not None:
            rec_limpas = rec_limpas[:k]
            
        recuperadas = set(rec_limpas)
        
        if not esperadas and not recuperadas:
            precisions.append(1.0)
            recalls.append(1.0)
            f1s.append(1.0)
            hits.append(1.0)
            exact_matches.append(1.0)
            all_required.append(1.0)
            continue
        elif not esperadas:
            precisions.append(0.0)
            recalls.append(1.0)
            f1s.append(0.0)
            hits.append(0.0)
            exact_matches.append(0.0)
            all_required.append(1.0)
            continue
        elif not recuperadas:
            precisions.append(0.0)
            recalls.append(0.0)
            f1s.append(0.0)
            hits.append(0.0)
            exact_matches.append(0.0)
            all_required.append(0.0)
            continue
            
        true_positives = len(esperadas.intersection(recuperadas))
        
        precision = true_positives / len(recuperadas) if recuperadas else 0.0
        recall = true_positives / len(esperadas) if esperadas else 0.0
        
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        
        # Novas Métricas
        hits.append(1.0 if true_positives > 0 else 0.0)
        exact_matches.append(1.0 if esperadas == recuperadas else 0.0)
        all_required.append(1.0 if esperadas.issubset(recuperadas) else 0.0)
        
    k_suffix = f"@{k}" if k is not None else ""
        
    return {
        f"section_precision{k_suffix}": sum(precisions) / len(precisions),
        f"section_recall{k_suffix}": sum(recalls) / len(recalls),
        f"section_f1{k_suffix}": sum(f1s) / len(f1s),
        f"section_hit{k_suffix}": sum(hits) / len(hits),
        f"exact_section_match{k_suffix}": sum(exact_matches) / len(exact_matches),
        f"all_required_sections_retrieved{k_suffix}": sum(all_required) / len(all_required),
        f"required_section_coverage{k_suffix}": sum(recalls) / len(recalls) # Matematicamente equivalente ao Recall
    }

def evaluate_generation(df, metrics_config):
    """
    Avalia a qualidade do texto gerado comparando resposta_gerada com resposta_esperada.
    """
    results = {}
    
    respostas_esperadas = df['resposta_esperada'].fillna("").tolist()
    respostas_geradas = df['resposta_gerada'].fillna("").tolist()
    
    if "rouge" in metrics_config:
        print("Calculando ROUGE...")
        rouge = load('rouge')
        rouge_results = rouge.compute(predictions=respostas_geradas, references=respostas_esperadas)
        results["rouge"] = rouge_results
        
    if "bertscore" in metrics_config:
        print("Calculando BERTScore...")
        P, R, F1 = bert_score(respostas_geradas, respostas_esperadas, lang="pt", verbose=False)
        results["bertscore_f1"] = F1.mean().item()
        
    if "bleu" in metrics_config:
        print("Calculando BLEU...")
        bleu_scores = []
        for gerada, esperada in zip(respostas_geradas, respostas_esperadas):
            ref = [esperada.split()]
            cand = gerada.split()
            if not cand or not ref[0]:
                bleu_scores.append(0.0)
            else:
                bleu_scores.append(sentence_bleu(ref, cand))
        results["bleu"] = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0
        
    return results


def evaluate_corpus_coverage(df, chroma_collection_size: int):
    """
    Calcula a fração de chunks únicos do corpus que foram recuperados
    ao longo de todo o dataset (corpus coverage).

    Args:
        df: DataFrame com coluna 'chunk_ids_recuperados'
            (IDs separados por vírgula por linha).
        chroma_collection_size: total de documentos na coleção ChromaDB.

    Returns:
        dict com:
          - corpus_coverage (float 0-1)
          - unique_chunks_retrieved (int)
          - total_chunks_in_corpus (int)
    """
    all_retrieved_ids = set()

    for _, row in df.iterrows():
        ids_str = str(row.get('chunk_ids_recuperados', ''))
        ids = [i.strip() for i in ids_str.split(',') if i.strip()]
        all_retrieved_ids.update(ids)

    # Remove string vazia se presente (chunks sem ID)
    all_retrieved_ids.discard('')

    unique_retrieved = len(all_retrieved_ids)
    coverage = unique_retrieved / chroma_collection_size if chroma_collection_size > 0 else 0.0

    return {
        "corpus_coverage": round(coverage, 4),
        "unique_chunks_retrieved": unique_retrieved,
        "total_chunks_in_corpus": chroma_collection_size,
    }

def run_evaluation(csv_path, yaml_config):
    """
    Lê o CSV de saída e calcula todas as métricas solicitadas no YAML.
    """
    print(f"\nIniciando Avaliação para: {csv_path}")
    df = pd.read_csv(csv_path)
    metrics_config = yaml_config.get('metrics', {})
    
    final_metrics = {}
    
    if metrics_config.get('section_retrieval'):
        print("Avaliando Section Retrieval...")
        final_metrics.update(evaluate_section_retrieval(df))
        
    if metrics_config.get('generation'):
        final_metrics.update(evaluate_generation(df, metrics_config['generation']))

    if metrics_config.get('corpus_coverage', False):
        print("Calculando Corpus Coverage...")
        import chromadb
        chroma_path = yaml_config.get('chroma_path', './chroma_bulas')
        collection_name = yaml_config.get('chroma_collection', 'bulas')
        chroma_client = chromadb.PersistentClient(path=chroma_path)
        try:
            collection = chroma_client.get_collection(collection_name)
            corpus_size = collection.count()
        except Exception as e:
            print(f"  [AVISO] Não foi possível acessar a coleção '{collection_name}': {e}")
            corpus_size = 0
        final_metrics.update(evaluate_corpus_coverage(df, corpus_size))

    if metrics_config.get('deepeval', False):
        print("Avaliando com DeepEval (LLM-as-a-judge)...")
        from eval_deepeval.run_deepeval import run_evaluation as run_deepeval_eval
        
        test_cases_data = []
        for index, row in df.iterrows():
            medicamento = row.get("nome_remedio") or row.get("medicamento", "unknown")
            pergunta = row.get("pergunta", "")
            
            # Tentar pegar os textos recuperados
            textos_raw = row.get("textos_recuperados", "[]")
            try:
                retrieval_context = json.loads(textos_raw)
            except Exception:
                retrieval_context = []
            
            test_cases_data.append({
                "question_id": str(index),
                "pipeline_name": yaml_config.get('pipeline_type', 'unknown'),
                "difficulty": row.get("dificuldade", "unknown"),
                "drug_name": medicamento,
                "input": pergunta,
                "actual_output": str(row.get("resposta_gerada", "")),
                "expected_output": str(row.get("resposta_esperada", "")),
                "retrieval_context": retrieval_context
            })
            
        deepeval_output_path = csv_path.replace('_output.csv', '_deepeval.jsonl')
        # Obtemos o modelo judge_llm configurado no YAML, com fallback seguro para gemini-3.1-flash-lite
        judge_model = yaml_config.get('models', {}).get('judge_llm', 'gemini-3.1-flash-lite')
        if not judge_model.startswith('gemini/'):
            judge_model = f"gemini/{judge_model}"
        
        print(f"  Iniciando DeepEval com o modelo juiz: {judge_model}")
        run_deepeval_eval(test_cases_data, deepeval_output_path, model=judge_model)
        print(f"  Resultados detalhados do DeepEval salvos em: {deepeval_output_path}")

    # Salvar métricas em JSON
    metrics_output_path = csv_path.replace('_output.csv', '_metrics.json')
    with open(metrics_output_path, 'w', encoding='utf-8') as f:
        json.dump(final_metrics, f, indent=4, ensure_ascii=False)
        
    print(f"Métricas salvas em: {metrics_output_path}")
    return final_metrics

if __name__ == "__main__":
    import argparse
    from utils.config_loader import load_config
    
    parser = argparse.ArgumentParser(description="Rodar avaliação de métricas")
    parser.add_argument("--csv", type=str, required=True, help="Caminho para o CSV gerado pelo experimento")
    parser.add_argument("--config", type=str, required=True, help="Caminho para o arquivo YAML de configuração")
    args = parser.parse_args()
    
    config = load_config(args.config)
    metrics = run_evaluation(args.csv, config)
    
    print("\nResumo das Métricas:")
    for k, v in metrics.items():
        print(f" - {k}: {v}")
