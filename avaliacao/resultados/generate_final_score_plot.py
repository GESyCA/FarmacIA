import os, json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'axes.edgecolor': '#cccccc',
    'grid.linestyle': '--',
    'figure.titlesize': 24,
    'axes.titlesize': 22,
    'axes.labelsize': 20,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16,
})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "graficos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_COLORS = {
    "Gemma 4:4b":       "#1F77B4",   
    "MedGemma 4b":      "#D62728",   
    "Phi4 Mini":        "#D4AC0D",   
    "MediPhi Instruct": "#2CA02C",   
}

PIPELINES = ["06_naive", "01_standard", "02_agentic", "03_hybrid_agent", "04_fusion", "05_graph", "07_guarded"]
PIPE_NAMES = {
    "06_naive": "Naive RAG", "01_standard": "Standard RAG", "02_agentic": "Agentic RAG",
    "03_hybrid_agent": "Hybrid Agent", "04_fusion": "Fusion RAG", "05_graph": "Graph RAG",
    "07_guarded": "Guarded RAG"
}
DIFFICULTIES = ["faceis", "medias", "dificeis"]
DIFF_LABELS = {"faceis": "Fáceis", "medias": "Médias", "dificeis": "Difíceis"}

MODELS = [
    ("Gemma 4:4b", "gemma_4_4b", "gemma_compiled_results.json"),
    ("MedGemma 4b", "medgemma_4b", "medgemma_compiled_results.json"),
    ("Phi4 Mini", "phi4-mini", "phi4_compiled_results.json"),
    ("MediPhi Instruct", "mediphi", "mediphi_compiled_results.json")
]

rows = []
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
                rows.append({
                    "Model": model_name,
                    "Pipeline_Raw": pipe,
                    "Pipeline": PIPE_NAMES.get(pipe, pipe),
                    "Difficulty_Raw": diff,
                    "Dificuldade": DIFF_LABELS.get(diff, diff),
                    "Final Score": data[key].get("final_score", 0.0)
                })

df_all = pd.DataFrame(rows)
if not df_all.empty:
    df_all['Pipeline_Raw'] = pd.Categorical(df_all['Pipeline_Raw'], categories=PIPELINES, ordered=True)

    fig, axes = plt.subplots(1, 3, figsize=(24, 10), sharey=True)
    # fig.suptitle("Comparativo: Final Score por Pipeline (Fácil, Média e Difícil)", fontsize=18, weight='bold', y=1.05)

    palette = [MODEL_COLORS[m] for m in df_all["Model"].unique()]
    model_order = [m for m, _, _ in MODELS if m in df_all["Model"].unique()]

    for i, diff in enumerate(DIFFICULTIES):
        ax = axes[i]
        sub = df_all[df_all["Difficulty_Raw"] == diff]
        
        sns.barplot(data=sub, x="Pipeline", y="Final Score", hue="Model", hue_order=model_order, palette=palette, ax=ax)
        
        ax.set_title(f"Dificuldade: {DIFF_LABELS[diff]}", fontsize=22)
        ax.set_xlabel("")
        if i == 0:
            ax.set_ylabel("Final Score (0 - 1)", fontsize=20)
        else:
            ax.set_ylabel("")
            
        ax.set_ylim(0, 1.1)
        ax.tick_params(axis='x', rotation=45, labelsize=16)
        
        # Add labels to bars
        for container in ax.containers:
            labels = [f"{val:.3f}" if val > 0 else "" for val in container.datavalues]
            ax.bar_label(container, labels=labels, padding=3, fontsize=14, color='#333333', rotation=90)
            
        # Remove individual legends
        ax.get_legend().remove()

    # Add a single legend at the bottom
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(model_order), fontsize=16, title="Modelos", title_fontsize=18)

    plt.tight_layout()
    # Add extra space at the bottom for the legend
    plt.subplots_adjust(top=0.9, bottom=0.15)
    
    out_path = os.path.join(OUTPUT_DIR, "final_score_por_dificuldade.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Gráfico gerado com sucesso: {out_path}")
else:
    print("Nenhum dado encontrado para gerar o gráfico.")
