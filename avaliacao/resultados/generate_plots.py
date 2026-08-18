import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set design styles for premium look
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 0.8,
    'grid.color': '#eeeeee',
    'grid.linestyle': '--',
    'figure.titlesize': 16,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10
})

def label_bars(ax, fmt_type='float'):
    # Expand vertical limit dynamically to prevent clipping of labels at the top
    y_min, y_max = ax.get_ylim()
    if fmt_type == 'percent':
        ax.set_ylim(y_min, max(112.0, y_max * 1.12))
    elif fmt_type == 'score':
        ax.set_ylim(y_min, max(1.12, y_max * 1.12))
    else:
        ax.set_ylim(y_min, y_max * 1.12)
        
    for container in ax.containers:
        labels = []
        for val in container.datavalues:
            if pd.isna(val) or val == 0.0:
                labels.append("")
            elif fmt_type == 'percent':
                labels.append(f"{val:.1f}%")
            elif fmt_type == 'time':
                if val < 0.1:
                    labels.append(f"{val:.3f}s")
                elif val < 1.0:
                    labels.append(f"{val:.2f}s")
                else:
                    labels.append(f"{val:.1f}s")
            elif fmt_type == 'score':
                labels.append(f"{val:.3f}")
            else:
                labels.append(f"{val:.2f}")
        ax.bar_label(container, labels=labels, padding=3, fontsize=7, weight='bold')

# Color palettes
gemma_palette = sns.color_palette("viridis", 3)
medgemma_palette = sns.color_palette("magma", 3)
comparison_palette = ["#4285F4", "#EA4335"]  # Google blue vs Google red/coral

# Paths
base_dir = os.path.dirname(os.path.abspath(__file__))
gemma_json = os.path.join(base_dir, "gemma_4_4b", "gemma_compiled_results.json")
medgemma_json = os.path.join(base_dir, "medgemma_4b", "medgemma_compiled_results.json")
output_plots_dir = os.path.join(base_dir, "graficos")

os.makedirs(output_plots_dir, exist_ok=True)

# Load data
with open(gemma_json, 'r', encoding='utf-8') as f:
    gemma_data = json.load(f)

with open(medgemma_json, 'r', encoding='utf-8') as f:
    medgemma_data = json.load(f)

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
    "faceis": "Fáceis",
    "medias": "Médias",
    "dificeis": "Difáceis"
}

# ----------------------------------------------------
# 1. Prepare Dataframes
# ----------------------------------------------------
def build_df(data, model_name):
    rows = []
    for pipe in pipelines:
        for diff in difficulties:
            key = f"{pipe}|{diff}"
            if key in data:
                metrics = data[key]
                rows.append({
                    "Model": model_name,
                    "Pipeline_Raw": pipe,
                    "Pipeline": pipeline_names[pipe],
                    "Difficulty_Raw": diff,
                    "Dificuldade": difficulty_names[diff],
                    "Final Score": metrics.get("final_score", 0.0),
                    "Critical Failure Rate": metrics.get("critical_failure_rate", 0.0) * 100.0,
                    "Context Recall": metrics.get("contextual_recall", 0.0),
                    "Context Precision": metrics.get("contextual_precision", 0.0),
                    "Retrieval Time (s)": metrics.get("avg_retrieval_time", 0.0),
                    "Inference Time (s)": metrics.get("avg_inference_time", 0.0),
                    "Chunk Recall@3": metrics.get("chunk_recall_at_3", 0.0),
                    "Chunk Recall@10": metrics.get("chunk_recall_at_10", 0.0),
                    "Chunk MRR@10": metrics.get("chunk_mrr_at_10", 0.0)
                })
    return pd.DataFrame(rows)

df_gemma = build_df(gemma_data, "Gemma 4:4b")
df_medgemma = build_df(medgemma_data, "MedGemma 4b")
df_all = pd.concat([df_gemma, df_medgemma], ignore_index=True)

# Save dataframes as csv for record
df_all.to_csv(os.path.join(output_plots_dir, "compiled_data.csv"), index=False, encoding='utf-8')

# ----------------------------------------------------
# 2. Gemma 4:4b Intra-model plots
# ----------------------------------------------------
# 2.1 Final Score
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_gemma,
    x="Pipeline",
    y="Final Score",
    hue="Dificuldade",
    palette="Blues_d"
)
plt.title("Gemma 4:4b - Final Score por Pipeline e Dificuldade", pad=15)
plt.ylabel("Final Score (Média, escala 0-1)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 1.05)
label_bars(ax, 'score')
plt.legend(title="Dificuldade", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "gemma_final_scores.png"), dpi=300)
plt.close()

# 2.2 Critical Failure Rate
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_gemma,
    x="Pipeline",
    y="Critical Failure Rate",
    hue="Dificuldade",
    palette="Oranges_d"
)
plt.title("Gemma 4:4b - Taxa de Falhas Críticas (%)", pad=15)
plt.ylabel("Falhas Críticas (%)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 105)
label_bars(ax, 'percent')
plt.legend(title="Dificuldade", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "gemma_critical_failures.png"), dpi=300)
plt.close()

# ----------------------------------------------------
# 3. MedGemma 4b Intra-model plots
# ----------------------------------------------------
# 3.1 Final Score
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_medgemma,
    x="Pipeline",
    y="Final Score",
    hue="Dificuldade",
    palette="Purples_d"
)
plt.title("MedGemma 4b - Final Score por Pipeline e Dificuldade", pad=15)
plt.ylabel("Final Score (Média, escala 0-1)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 1.05)
label_bars(ax, 'score')
plt.legend(title="Dificuldade", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "medgemma_final_scores.png"), dpi=300)
plt.close()

# 3.2 Critical Failure Rate
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_medgemma,
    x="Pipeline",
    y="Critical Failure Rate",
    hue="Dificuldade",
    palette="Reds_d"
)
plt.title("MedGemma 4b - Taxa de Falhas Críticas (%)", pad=15)
plt.ylabel("Falhas Críticas (%)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 105)
label_bars(ax, 'percent')
plt.legend(title="Dificuldade", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "medgemma_critical_failures.png"), dpi=300)
plt.close()

# ----------------------------------------------------
# 4. Direct Model Comparison (Gemma 4:4b vs MedGemma 4b)
# ----------------------------------------------------
# Aggregate across difficulties to get a single score per pipeline per model
df_consolidated = df_all.groupby(["Model", "Pipeline", "Pipeline_Raw"], as_index=False).agg({
    "Final Score": "mean",
    "Critical Failure Rate": "mean",
    "Retrieval Time (s)": "mean",
    "Inference Time (s)": "mean",
    "Chunk Recall@3": "mean",
    "Chunk Recall@10": "mean",
    "Chunk MRR@10": "mean"
})
# Sort pipelines in correct logical order
df_consolidated['Pipeline_Raw'] = pd.Categorical(df_consolidated['Pipeline_Raw'], categories=pipelines, ordered=True)
df_consolidated = df_consolidated.sort_values('Pipeline_Raw')

# 4.1 Consolidated Final Score Comparison
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_consolidated,
    x="Pipeline",
    y="Final Score",
    hue="Model",
    palette=comparison_palette
)
plt.title("Comparação Consolidada: Gemma 4:4b vs MedGemma 4b (Média Final Score)", pad=15)
plt.ylabel("Média do Final Score (escala 0-1)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 1.05)
label_bars(ax, 'score')
plt.legend(title="Modelo")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "comparison_final_scores_consolidated.png"), dpi=300)
plt.close()

# 4.2 Consolidated Critical Failure Rate Comparison
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_consolidated,
    x="Pipeline",
    y="Critical Failure Rate",
    hue="Model",
    palette=comparison_palette
)
plt.title("Comparação Consolidada: Gemma 4:4b vs MedGemma 4b (Taxa de Falhas Críticas)", pad=15)
plt.ylabel("Média de Falhas Críticas (%)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 105)
label_bars(ax, 'percent')
plt.legend(title="Modelo")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "comparison_critical_failures_consolidated.png"), dpi=300)
plt.close()

# 4.3 Consolidated Retrieval Time Comparison
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_consolidated,
    x="Pipeline",
    y="Retrieval Time (s)",
    hue="Model",
    palette=comparison_palette
)
plt.title("Comparação Consolidada: Tempo Médio de Recuperação (s)", pad=15)
plt.ylabel("Tempo de Recuperação (segundos)")
plt.xlabel("Pipeline RAG")
label_bars(ax, 'time')
plt.legend(title="Modelo")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "comparison_retrieval_time_consolidated.png"), dpi=300)
plt.close()

# 4.4 Consolidated Inference Time Comparison
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_consolidated,
    x="Pipeline",
    y="Inference Time (s)",
    hue="Model",
    palette=comparison_palette
)
plt.title("Comparação Consolidada: Tempo Médio de Inferência (s)", pad=15)
plt.ylabel("Tempo de Inferência (segundos)")
plt.xlabel("Pipeline RAG")
label_bars(ax, 'time')
plt.legend(title="Modelo")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "comparison_inference_time_consolidated.png"), dpi=300)
plt.close()

# 4.5 Consolidated Chunk Recall@3 Comparison
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_consolidated,
    x="Pipeline",
    y="Chunk Recall@3",
    hue="Model",
    palette=comparison_palette
)
plt.title("Comparação Consolidada: Média de Chunk Recall@3", pad=15)
plt.ylabel("Chunk Recall@3 (Média)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 1.05)
label_bars(ax, 'score')
plt.legend(title="Modelo")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "comparison_chunk_recall_3_consolidated.png"), dpi=300)
plt.close()

# 4.6 Consolidated Chunk Recall@10 Comparison
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_consolidated,
    x="Pipeline",
    y="Chunk Recall@10",
    hue="Model",
    palette=comparison_palette
)
plt.title("Comparação Consolidada: Média de Chunk Recall@10", pad=15)
plt.ylabel("Chunk Recall@10 (Média)")
plt.xlabel("Pipeline RAG")
plt.ylim(0, 1.05)
label_bars(ax, 'score')
plt.legend(title="Modelo")
plt.tight_layout()
plt.savefig(os.path.join(output_plots_dir, "comparison_chunk_recall_10_consolidated.png"), dpi=300)
plt.close()

print("All plots successfully generated!")
