import os
import sys
import json
import re
import subprocess
import pandas as pd
from pathlib import Path

# Adiciona o diretório atual do script ao sys.path para importar utils
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils.config_loader import load_config

def print_banner(text):
    print("=" * 80)
    print(f" {text:^78} ")
    print("=" * 80)

def to_markdown_simple(df):
    headers = list(df.columns)
    markdown_lines = []
    markdown_lines.append("| " + " | ".join(headers) + " |")
    markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        row_str = " | ".join(str(row[h]) for h in headers)
        markdown_lines.append("| " + row_str + " |")
    return "\n".join(markdown_lines)

def main():
    print_banner("COMPARATIVO DE MODELOS NO PIPELINE GUARDED RAG (7)")
    
    # Determinar caminhos relativos ao CWD
    # Se rodado a partir de Paciente, o CWD contém 'app'
    if os.path.exists("app") and os.path.isdir("app"):
        base_dir = "app"
        output_dir = "resultados"
    else:
        base_dir = "."
        output_dir = "../resultados"
        
    config_path = os.path.join(base_dir, "configs", "exp_compare_07_guarded.yaml")
    script_path = os.path.join(base_dir, "rodar_experimentos.py")
    
    if not os.path.exists(config_path):
        print(f"[ERRO] Arquivo de configuração não encontrado em: {config_path}")
        return
        
    config = load_config(config_path)
    
    models = [
        # ("MedGemma 4B", "ollama:medgemma:4b"),
        # ("Gemma4 E4B", "ollama:gemma4:e4b"),
        ("Phi4 Mini", "ollama:phi4-mini"),
        ("MediPhi Instruct", "ollama:mediphi-instruct")
    ]
    
    datasets = config.get('datasets', [])
    exp_name = config.get('experiment_name', '07_guarded').replace("compare_", "")
    
    # 1. Executa para cada modelo sequencialmente
    for model_name, model_uri in models:
        print_banner(f"Executando Guarded RAG com o modelo: {model_name}")
        try:
            # Invoca o script rodar_experimentos.py
            subprocess.run(
                [sys.executable, script_path, "--config", config_path, "--generation_llm", model_uri, "--output_dir", output_dir],
                check=True
            )
            print(f"\n[SUCESSO] Execução concluída para {model_name}!\n")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERRO] Falha ao executar o modelo {model_name}: {e}\n")
            
    # 2. Consolidação dos resultados por dataset
    print_banner("CONSOLIDANDO RESULTADOS DOS EXPERIMENTOS")
    
    report_content = f"""# Relatório Comparativo de Modelos - Pipeline Guarded RAG (07)

Relatório gerado automaticamente comparando a performance do pipeline **Guarded Hybrid Agentic Fusion RAG** executado sob diferentes modelos LLM geradores locais no Ollama.

"""

    emb_model_raw = config['models']['embedding_model']
    emb_name_clean = re.sub(r'[^a-zA-Z0-9_]', '_', emb_model_raw).lower()
    emb_name_clean = re.sub(r'_+', '_', emb_name_clean).strip('_')

    for dataset_file in datasets:
        dataset_basename = Path(dataset_file).stem
        ds_name = dataset_basename.replace("perguntas_respostas_", "")
        
        print(f"\nConsolidando resultados para o dataset: {ds_name}...")
        tabela_data = []
        
        for name, model_uri in models:
            model_name_clean = model_uri.replace("ollama:", "").replace("llama_cpp:", "")
            model_name_clean = re.sub(r'[^a-zA-Z0-9_]', '_', model_name_clean).lower()
            model_name_clean = re.sub(r'_+', '_', model_name_clean).strip('_')
            
            csv_path = os.path.join(output_dir, f"{exp_name}_{model_name_clean}_{emb_name_clean}_{ds_name}_output.csv")
            metrics_path = csv_path.replace('_output.csv', '_metrics.json')
            deepeval_path = csv_path.replace('_output.csv', '_deepeval.jsonl')
            
            if not os.path.exists(csv_path) or not os.path.exists(metrics_path):
                print(f"  [AVISO] Arquivos para {name} ({ds_name}) não encontrados. Pulando.")
                continue
                
            # Carrega métricas JSON
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
                
            # Carrega CSV para calcular médias de tempos e métricas Guarded
            df = pd.read_csv(csv_path)
            avg_rec_time = df["tempo_recuperacao_segundos"].mean()
            avg_inf_time = df["tempo_inferencia_segundos"].mean()
            
            # Guarded metrics
            fallback_rate = 0.0
            conf_high_rate = 0.0
            if "guarded_fallback_triggered" in df.columns:
                fallback_rate = df["guarded_fallback_triggered"].astype(bool).mean() * 100
            if "guarded_confidence" in df.columns:
                conf_counts = df["guarded_confidence"].str.lower().value_counts(normalize=True)
                conf_high_rate = conf_counts.get("high", 0.0) * 100
                
            # Extração das métricas individuais com fallback
            sec_precision = metrics.get("section_precision", 0.0)
            sec_recall = metrics.get("section_recall", 0.0)
            sec_f1 = metrics.get("section_f1", 0.0)
            bleu = metrics.get("bleu", 0.0)
            
            rouge_val = metrics.get("rouge", 0.0)
            if isinstance(rouge_val, dict):
                rouge_l = rouge_val.get("rougeL", 0.0)
            else:
                rouge_l = rouge_val
                
            bertscore = metrics.get("bertscore_f1", 0.0)
            
            # Lê DeepEval se existir
            avg_deepeval = 0.0
            avg_bula = 0.0
            
            if os.path.exists(deepeval_path):
                de_scores = []
                bula_scores = []
                with open(deepeval_path, "r", encoding="utf-8") as de_file:
                    for line in de_file:
                        try:
                            record = json.loads(line)
                            de_scores.append(record.get("final_score", 0.0) * 100)
                            
                            # Bula Layer
                            bula_metrics = ["clinical_safety", "warning_preservation", "patient_comprehensibility", "inference_control"]
                            bula_scores_list = []
                            for m in bula_metrics:
                                m_obj = record.get(m)
                                if m_obj and m_obj.get("failure_type") != "evaluation_error":
                                    bula_scores_list.append(m_obj.get("normalized_score", 0.0) * 100)
                            if bula_scores_list:
                                bula_scores.append(sum(bula_scores_list) / len(bula_scores_list))
                        except:
                            pass
                if de_scores:
                    avg_deepeval = sum(de_scores) / len(de_scores)
                if bula_scores:
                    avg_bula = sum(bula_scores) / len(bula_scores)
            
            tabela_data.append({
                "Modelo": name,
                "Sec. Precision": f"{sec_precision:.4f}",
                "Sec. Recall": f"{sec_recall:.4f}",
                "Sec. F1": f"{sec_f1:.4f}",
                "ROUGE-L": f"{rouge_l:.4f}",
                "BERTScore": f"{bertscore:.4f}",
                "DeepEval Total": f"{avg_deepeval:.2f}/100",
                "DeepEval Bula": f"{avg_bula:.2f}/100",
                "Confiança Alta (%)": f"{conf_high_rate:.1f}%",
                "Fallback (%)": f"{fallback_rate:.1f}%",
                "Média Rec. (s)": f"{avg_rec_time:.4f}s",
                "Média Inf. (s)": f"{avg_inf_time:.4f}s"
            })
            
        if tabela_data:
            df_consolidado = pd.DataFrame(tabela_data)
            report_content += f"## Dataset: {ds_name.upper()}\n\n"
            report_content += to_markdown_simple(df_consolidado) + "\n\n"
            
            print(f"\nTabela Comparativa para {ds_name}:")
            print(to_markdown_simple(df_consolidado))
            
    output_report_path = os.path.join(output_dir, "comparativo_guarded_consolidado.md")
    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print_banner("RELATÓRIO CONSOLIDADO GERADO!")
    print(f"Salvo com sucesso em: {output_report_path}\n")

if __name__ == "__main__":
    main()
