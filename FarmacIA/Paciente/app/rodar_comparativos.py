import os
import sys
import json
import subprocess
import pandas as pd
from pathlib import Path

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
    print_banner("ORQUESTRADOR DE EXPERIMENTOS COMPARATIVOS - FARMACIA RAG")
    
    configs = [
        ("Standard RAG", "compare_01_standard", "configs/exp_compare_01_standard.yaml"),
        ("Agentic RAG", "compare_02_agentic", "configs/exp_compare_02_agentic.yaml"),
        ("Hybrid Agentic RAG", "compare_03_hybrid_agent", "configs/exp_compare_03_hybrid_agent.yaml"),
        ("Fusion RAG", "compare_04_fusion", "configs/exp_compare_04_fusion.yaml"),
        ("Graph RAG (BulaGraph)", "compare_05_graph", "configs/exp_compare_05_graph.yaml"),
    ]
    
    dataset_name = "perguntas_respostas_dificeis"
    
    # 1. Executa cada pipeline sequencialmente (se os resultados não existirem)
    for name, exp_id, config_path in configs:
        csv_path = f"resultados/{exp_id}_{dataset_name}_output.csv"
        metrics_path = f"resultados/{exp_id}_{dataset_name}_metrics.json"
        
        if os.path.exists(csv_path) and os.path.exists(metrics_path):
            print(f"[INFO] Resultados para {name} já existem. Pulando execução.")
            continue
            
        print_banner(f"Executando Pipeline: {name}")
        try:
            # Invoca o script rodar_experimentos.py usando o interpretador atual
            subprocess.run(
                [sys.executable, "rodar_experimentos.py", "--config", config_path],
                check=True
            )
            print(f"\n[SUCESSO] Pipeline {name} concluído com êxito!\n")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERRO] Falha ao executar o pipeline {name}: {e}\n")
            # Continua para os próximos pipelines mesmo em caso de erro
    
    # 2. Consolida os resultados
    print_banner("CONSOLIDANDO RESULTADOS DOS EXPERIMENTOS")
    
    tabela_data = []
    
    for name, exp_id, config_path in configs:
        csv_path = f"resultados/{exp_id}_{dataset_name}_output.csv"
        metrics_path = f"resultados/{exp_id}_{dataset_name}_metrics.json"
        
        if not os.path.exists(csv_path) or not os.path.exists(metrics_path):
            print(f"[AVISO] Arquivos do pipeline {name} não encontrados. Pulando.")
            continue
            
        # Carrega métricas JSON
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            
        # Carrega tempos do CSV para calcular a média
        df = pd.read_csv(csv_path)
        avg_rec_time = df["tempo_recuperacao_segundos"].mean()
        avg_inf_time = df["tempo_inferencia_segundos"].mean()
        
        # Extração das métricas individuais com fallback
        sec_precision = metrics.get("section_precision", 0.0)
        sec_recall = metrics.get("section_recall", 0.0)
        sec_f1 = metrics.get("section_f1", 0.0)
        
        bleu = metrics.get("bleu", 0.0)
        
        # Rouge pode vir como dict do evaluate
        rouge_val = metrics.get("rouge", 0.0)
        if isinstance(rouge_val, dict):
            rouge_l = rouge_val.get("rougeL", 0.0)
        else:
            rouge_l = rouge_val
            
        bertscore = metrics.get("bertscore_f1", 0.0)
        corpus_coverage = metrics.get("corpus_coverage", 0.0)
        
        # Lê DeepEval se existir
        deepeval_path = f"resultados/{exp_id}_{dataset_name}_deepeval.jsonl"
        avg_deepeval = 0.0
        avg_context = 0.0
        avg_resp = 0.0
        avg_bula = 0.0
        
        if os.path.exists(deepeval_path):
            de_scores = []
            ctx_scores = []
            resp_scores = []
            bula_scores = []
            with open(deepeval_path, "r", encoding="utf-8") as de_file:
                for line in de_file:
                    try:
                        record = json.loads(line)
                        de_scores.append(record.get("final_score", 0.0) * 100)
                        
                        # Context Layer
                        ctx_metrics = ["contextual_recall", "contextual_precision", "evidence_sufficiency"]
                        ctx_scores_list = []
                        for m in ctx_metrics:
                            m_obj = record.get(m)
                            if m_obj and m_obj.get("failure_type") != "evaluation_error":
                                ctx_scores_list.append(m_obj.get("normalized_score", 0.0) * 100)
                        if ctx_scores_list:
                            ctx_scores.append(sum(ctx_scores_list) / len(ctx_scores_list))
                            
                        # Response Layer
                        resp_metrics = ["faithfulness", "answer_relevancy", "response_completeness", "unsupported_claims"]
                        resp_scores_list = []
                        for m in resp_metrics:
                            m_obj = record.get(m)
                            if m_obj and m_obj.get("failure_type") != "evaluation_error":
                                resp_scores_list.append(m_obj.get("normalized_score", 0.0) * 100)
                        if resp_scores_list:
                            resp_scores.append(sum(resp_scores_list) / len(resp_scores_list))
                            
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
            if ctx_scores:
                avg_context = sum(ctx_scores) / len(ctx_scores)
            if resp_scores:
                avg_resp = sum(resp_scores) / len(resp_scores)
            if bula_scores:
                avg_bula = sum(bula_scores) / len(bula_scores)
        
        tabela_data.append({
            "Pipeline": name,
            "Section Precision": f"{sec_precision:.4f}",
            "Section Recall": f"{sec_recall:.4f}",
            "Section F1": f"{sec_f1:.4f}",
            "BLEU": f"{bleu:.4f}",
            "ROUGE-L": f"{rouge_l:.4f}",
            "BERTScore": f"{bertscore:.4f}",
            "DeepEval Total": f"{avg_deepeval:.2f}/100",
            "DeepEval Ctx": f"{avg_context:.2f}/100",
            "DeepEval Resp": f"{avg_resp:.2f}/100",
            "DeepEval Bula": f"{avg_bula:.2f}/100",
            "Corpus Cover": f"{corpus_coverage * 100:.2f}%",
            "Média Rec. (s)": f"{avg_rec_time:.4f}s",
            "Média Inf. (s)": f"{avg_inf_time:.4f}s"
        })
        
    if not tabela_data:
        print("[ERRO] Ninguém gerou resultados com sucesso. Abortando consolidação.")
        return
        
    df_consolidado = pd.DataFrame(tabela_data)
    
    # 3. Cria o relatório consolidado em markdown
    output_report_path = "resultados/comparativo_consolidado.md"
    
    report_content = f"""# Relatório Comparativo de Pipelines de RAG

Relatório gerado automaticamente comparando a performance dos 5 pipelines sob as mesmas configurações e base de dados.

## Tabela Comparativa de Métricas

{to_markdown_simple(df_consolidado)}

## Análise e Insights Clínicos

1. **Section Retrieval (Precisão, Revocação e F1-Score)**:
   - Mede a precisão ao apontar para as seções reais recomendadas pela bula.
   - **Graph RAG (BulaGraph)** se destaca por possuir roteamento determinístico baseado na intenção e normalização clínico-leiga de alta precisão.

2. **Qualidade Textual da Geração (BLEU, ROUGE-L e BERTScore)**:
   - **ROUGE-L** e **BLEU** medem a sobreposição lexical.
   - **BERTScore** mede similaridade semântica.

3. **Qualidade Clínica (DeepEval LLM-as-a-Judge - Gemini 3.1 Pro)**:
   - **DeepEval Total**: Agregação das 3 camadas, com regras de falha crítica (Faithfulness, Warning Preservation).
   - **DeepEval Ctx**: Qualidade do retrieval (Contextual Recall/Precision, Evidence Sufficiency).
   - **DeepEval Resp**: Qualidade da resposta textual (Faithfulness, Completeness, etc).
   - **DeepEval Bula**: Domínio médico (Clinical Safety, Warning Preservation, Inference Control).

4. **Cobertura de Corpus e Performance (Tempo)**:
   - **Corpus Cover**: Diversidade de documentos e chunks buscados no ChromaDB.
   - **Tempo Médio de Recuperação / Inferência**: Mostram gargalos operacionais e do LLM.
   - **Tempo Médio de Recuperação (Rec.)**: Mede o gargalo do motor de busca (vetorial, grafo ou híbrido).
   - **Tempo Médio de Inferência (Inf.)**: Mede o tempo gasto na chamada ao LLM (Gemini).
"""
    
    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print_banner("RELATÓRIO CONSOLIDADO GERADO!")
    print(to_markdown_simple(df_consolidado))
    print(f"\nSalvo com sucesso em: {output_report_path}\n")

if __name__ == "__main__":
    main()
