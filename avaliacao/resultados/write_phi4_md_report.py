import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "phi4-mini", "phi4_compiled_results.json")
local_artifact_path = os.path.join(BASE_DIR, "phi4_mini_comparison.md")

# Determine dynamic brain path by finding the latest folder in brain dir
def get_latest_brain_dir():
    base = r"C:\Users\silvi\.gemini\antigravity-ide\brain"
    if not os.path.exists(base):
        return None
    dirs = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    if not dirs:
        return None
    dirs.sort(key=os.path.getmtime, reverse=True)
    return dirs[0]

brain_dir = get_latest_brain_dir()
if brain_dir:
    brain_artifact_path = os.path.join(brain_dir, "phi4_mini_comparison.md")
else:
    brain_artifact_path = r"C:\Users\silvi\.gemini\antigravity-ide\brain\05ce8a65-516e-47e2-9e7e-235ac724cc0e\phi4_mini_comparison.md"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

pipelines = ["06_naive", "01_standard", "02_agentic", "03_hybrid_agent", "04_fusion", "05_graph", "07_guarded"]
pipeline_names = {
    "06_naive": "Naive RAG",
    "01_standard": "Standard RAG",
    "02_agentic": "Agentic RAG",
    "03_hybrid_agent": "Hybrid Agent RAG",
    "04_fusion": "Fusion RAG",
    "05_graph": "Graph RAG",
    "07_guarded": "Guarded RAG"
}

difficulties = ["faceis", "medias", "dificeis"]
difficulty_names = {
    "faceis": "Fáceis (Easy)",
    "medias": "Médias (Medium)",
    "dificeis": "Difáceis (Hard)"
}

judge_metrics = [
    ("contextual_recall", "Recall"),
    ("contextual_precision", "Precision"),
    ("evidence_sufficiency", "Sufficiency"),
    ("faithfulness", "Faithfulness"),
    ("answer_relevancy", "Relevancy"),
    ("response_completeness", "Completeness"),
    ("unsupported_claims", "No-Unsupp-Claims"),
    ("clinical_safety", "Safety"),
    ("warning_preservation", "Warning-Pres"),
    ("patient_comprehensibility", "Comprehensibility"),
    ("inference_control", "Inference-Ctrl")
]

# Order of metrics in difficulty tables:
# (key, is_higher_better)
table_metrics = [
    ("final_score", True),
    ("critical_failure_rate", False),
    ("contextual_recall", True),
    ("contextual_precision", True),
    ("chunk_recall_at_3", True),
    ("chunk_recall_at_10", True),
    ("chunk_mrr_at_10", True),
    ("section_recall", True),
    ("section_precision", True),
    ("rougeL", True),
    ("bleu", True),
    ("avg_retrieval_time", False),
    ("avg_inference_time", False)
]

md = []
md.append("# Comparação Intramodelo - Phi4 Mini (ollama:phi4-mini)")
md.append("")
md.append("Este relatório compara de forma objetiva o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG** na recuperação e na geração de respostas, além de reportar os tempos médios de execução obtidos com o modelo **Phi4 Mini**.")
md.append("")
md.append("> [!NOTE]")
md.append("> **Destaque Visual:** Os melhores resultados em cada coluna estão destacados em **negrito** (maiores valores para pontuações de acurácia/recuperação e menores valores para taxas de falhas e tempos de latência).")
md.append("")
md.append("## Glossário de Métricas")
md.append("*   **Final Score (Judge):** Média aritmética (de 0.0 a 1.0) das avaliações do LLM-as-a-judge (ChatGPT / Gemini) nos 11 critérios individuais listados na seção 3.")
md.append("*   **Falhas Críticas (%):** Proporção de respostas que continham erros severos sob a ótica de segurança ou alucinação.")
md.append("*   **Context Recall / Precision:** Revocação e precisão do contexto selecionado pelo RAG em relação às informações necessárias para a resposta.")
md.append("*   **Chunk Recall@K / MRR@K:** Métricas de recuperação no nível de chunk. Medem a proporção de trechos do gabarito recuperados e a posição (ranking) em que aparecem.")
md.append("*   **Section Recall / Precision:** Grau de correspondência entre as seções formais da bula recuperadas pelo pipeline (ex: Posologia, Contraindicação) e aquelas esperadas no gabarito.")
md.append("*   **ROUGE-L / BLEU:** Métricas léxicas automáticas comparando o texto da resposta gerada com a resposta de referência.")
md.append("*   **Tempo Rec. (s):** Tempo médio gasto no processo de busca e recuperação de contexto (vetorial, agente ou grafo).")
md.append("*   **Tempo Inf. (s):** Tempo médio gasto pelo LLM local para inferência/geração da resposta final.")
md.append("")
md.append("---")
md.append("")
md.append("## 1. Resultados Detalhados por Dificuldade")
md.append("")

for diff in difficulties:
    md.append(f"### Perguntas {difficulty_names[diff]}")
    md.append("| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |")
    md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    
    # First pass: collect raw values
    raw_rows = []
    for pipe in pipelines:
        key = f"{pipe}|{diff}"
        metrics = data.get(key, {})
        raw_rows.append((pipe, metrics))
        
    # Find best values for each metric column
    best_vals = {}
    for mkey, is_higher_better in table_metrics:
        vals = [r[1].get(mkey, 0.0) for r in raw_rows if mkey in r[1]]
        if vals and max(vals) != min(vals):
            best_vals[mkey] = max(vals) if is_higher_better else min(vals)
        else:
            best_vals[mkey] = None

    # Format rows
    for pipe, metrics in raw_rows:
        row_cells = [pipeline_names[pipe]]
        for mkey, is_higher_better in table_metrics:
            val = metrics.get(mkey, 0.0)
            
            # Format value string
            if mkey == 'critical_failure_rate':
                val_str = f"{val*100:.1f}%"
            elif mkey in ['avg_retrieval_time', 'avg_inference_time']:
                val_str = f"{val:.2f}s"
            else:
                val_str = f"{val:.4f}"
                
            # Check if best (allowing tolerance)
            is_best = False
            if best_vals[mkey] is not None:
                if is_higher_better:
                    is_best = (val >= best_vals[mkey] - 1e-9)
                else:
                    is_best = (val <= best_vals[mkey] + 1e-9)
                    
            if is_best:
                row_cells.append(f"**{val_str}**")
            else:
                row_cells.append(val_str)
                
        md.append("| " + " | ".join(row_cells) + " |")
    md.append("")

md.append("---")
md.append("")
md.append("## 2. Comparativo Consolidado por Pipeline (Média Geral)")
md.append("")
md.append("A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline, unindo todas as dificuldades de perguntas:")
md.append("")
md.append("| Pipeline | Média Final Score | Média Falhas Críticas | Média Chunk Recall@3 | Média Chunk Recall@10 | Média Chunk MRR@10 | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |")
md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")

# Calculate averages for all pipelines
pipe_averages = {}
for pipe in pipelines:
    averages = {}
    for mkey, _ in table_metrics:
        val_list = []
        for diff in difficulties:
            key = f"{pipe}|{diff}"
            metrics = data.get(key, {})
            if mkey in metrics:
                val_list.append(metrics[mkey])
        averages[mkey] = sum(val_list)/len(val_list) if val_list else 0.0
    pipe_averages[pipe] = averages

# Find best consolidated values
best_consolidated = {}
for mkey, is_higher_better in table_metrics:
    vals = [pipe_averages[pipe][mkey] for pipe in pipelines]
    if vals and max(vals) != min(vals):
        best_consolidated[mkey] = max(vals) if is_higher_better else min(vals)
    else:
        best_consolidated[mkey] = None

# Format consolidated rows
for pipe in pipelines:
    row_cells = [pipeline_names[pipe]]
    averages = pipe_averages[pipe]
    
    # Columns in order of the consolidated table header
    consolidated_cols = [
        ("final_score", True),
        ("critical_failure_rate", False),
        ("chunk_recall_at_3", True),
        ("chunk_recall_at_10", True),
        ("chunk_mrr_at_10", True),
        ("contextual_recall", True),
        ("contextual_precision", True),
        ("rougeL", True),
        ("bleu", True),
        ("avg_retrieval_time", False),
        ("avg_inference_time", False)
    ]
    
    for mkey, is_higher_better in consolidated_cols:
        val = averages[mkey]
        
        # Format string
        if mkey == 'critical_failure_rate':
            val_str = f"{val*100:.1f}%"
        elif mkey in ['avg_retrieval_time', 'avg_inference_time']:
            val_str = f"{val:.2f}s"
        else:
            val_str = f"{val:.4f}"
            
        # Check if best
        is_best = False
        if best_consolidated[mkey] is not None:
            if is_higher_better:
                is_best = (val >= best_consolidated[mkey] - 1e-9)
            else:
                is_best = (val <= best_consolidated[mkey] + 1e-9)
                
        if is_best:
            row_cells.append(f"**{val_str}**")
        else:
            row_cells.append(val_str)
            
    md.append("| " + " | ".join(row_cells) + " |")

md.append("")
md.append("---")
md.append("")
md.append("## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge")
md.append("")
md.append("Detalhamento das médias obtidas em cada um dos **11 critérios individuais** avaliados pelo juiz (escala de 0.0 a 1.0):")
md.append("")

for diff in difficulties:
    md.append(f"### Critérios - Perguntas {difficulty_names[diff]}")
    md.append("")
    header_cols = ["Pipeline"] + [col_label for _, col_label in judge_metrics]
    md.append("| " + " | ".join(header_cols) + " |")
    md.append("| " + " | ".join(["---"] * len(header_cols)) + " |")
    
    # Calculate best criteria for this difficulty
    best_crit = {}
    for metric_key, _ in judge_metrics:
        vals = []
        for pipe in pipelines:
            key = f"{pipe}|{diff}"
            val = data.get(key, {}).get(metric_key, 0.0)
            vals.append(val)
        if vals and max(vals) != min(vals):
            best_crit[metric_key] = max(vals)
        else:
            best_crit[metric_key] = None

    for pipe in pipelines:
        row_cells = [pipeline_names[pipe]]
        for metric_key, _ in judge_metrics:
            key = f"{pipe}|{diff}"
            val = data.get(key, {}).get(metric_key, 0.0)
            val_str = f"{val:.4f}"
            
            is_best = (best_crit[metric_key] is not None and val >= best_crit[metric_key] - 1e-9)
            if is_best:
                row_cells.append(f"**{val_str}**")
            else:
                row_cells.append(val_str)
        md.append("| " + " | ".join(row_cells) + " |")
    md.append("")

# Consolidated Criteria
md.append("### Critérios - Média Geral (Consolidado de Todas as Dificuldades)")
md.append("")
header_cols = ["Pipeline"] + [col_label for _, col_label in judge_metrics]
md.append("| " + " | ".join(header_cols) + " |")
md.append("| " + " | ".join(["---"] * len(header_cols)) + " |")

# Precalculate consolidated values for criteria
consolidated_crit = {}
for pipe in pipelines:
    consolidated_crit[pipe] = {}
    for metric_key, _ in judge_metrics:
        vals = []
        for diff in difficulties:
            key = f"{pipe}|{diff}"
            if metric_key in data.get(key, {}):
                vals.append(data[key][metric_key])
        consolidated_crit[pipe][metric_key] = sum(vals)/len(vals) if vals else 0.0

best_con_crit = {}
for metric_key, _ in judge_metrics:
    vals = [consolidated_crit[pipe][metric_key] for pipe in pipelines]
    if vals and max(vals) != min(vals):
        best_con_crit[metric_key] = max(vals)
    else:
        best_con_crit[metric_key] = None

for pipe in pipelines:
    row_cells = [pipeline_names[pipe]]
    for metric_key, _ in judge_metrics:
        val = consolidated_crit[pipe][metric_key]
        val_str = f"{val:.4f}"
        
        is_best = (best_con_crit[metric_key] is not None and val >= best_con_crit[metric_key] - 1e-9)
        if is_best:
            row_cells.append(f"**{val_str}**")
        else:
            row_cells.append(val_str)
    md.append("| " + " | ".join(row_cells) + " |")

md.append("")
md.append("---")
md.append("")
md.append("## 4. Notas Técnicas sobre o Pipeline \"Naive RAG\"")
md.append("")
md.append("O **Naive RAG** apresenta valor `0.0000` em **Section Recall** e **Section Precision**.")
md.append("")
md.append("### Explicação Técnica:")
md.append("1. **Indexação Direta:** O Naive RAG fatia e indexa os textos de forma sequencial pura, sem estruturar o banco de dados vetorial por seções lógicas da bula (como fazem os outros pipelines). Por isso, ele não preenche a coluna de metadados `secoes_recuperadas` na saída CSV.")
md.append("2. **Impacto de Avaliação:** A ausência dessa marcação estrutural faz com que os testes formais de seção computem revocação e precisão zeradas. Contudo, isso **não** afeta o conteúdo textual recuperado. O **Context Recall** geral avaliado pelo juiz atesta que a informação de contexto requerida é efetivamente entregue ao modelo para formulação da resposta.")
md.append("")
md.append("---")

with open(local_artifact_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(md))

with open(brain_artifact_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(md))

print("Phi4 Markdown report successfully generated!")
