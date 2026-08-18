import os, json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'figure.titlesize': 22,
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

JUDGE_ATTRS = [
    "contextual_recall", "contextual_precision", "evidence_sufficiency",
    "faithfulness", "answer_relevancy", "response_completeness",
    "unsupported_claims", "clinical_safety", "warning_preservation",
    "patient_comprehensibility", "inference_control",
]
JUDGE_LABELS = {
    "contextual_recall":        "Recall Contextual",
    "contextual_precision":     "Precisão Contextual",
    "evidence_sufficiency":     "Suficiência de Evidência",
    "faithfulness":             "Fidelidade",
    "answer_relevancy":         "Relevância da Resposta",
    "response_completeness":    "Completude",
    "unsupported_claims":       "Sem Afirmações Não Suportadas",
    "clinical_safety":          "Segurança Clínica",
    "warning_preservation":     "Preservação de Alertas",
    "patient_comprehensibility":"Compreensibilidade",
    "inference_control":        "Controle de Inferência",
}

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
                m = data[key]
                row = {
                    "Model": model_name,
                    "Pipeline_Raw": pipe,
                    "Pipeline": PIPE_NAMES.get(pipe, pipe),
                    "Difficulty_Raw": diff,
                    "Dificuldade": DIFF_LABELS.get(diff, diff),
                    "Final Score": m.get("final_score", 0.0)
                }
                for attr in JUDGE_ATTRS:
                    row[attr] = m.get(attr, 0.0)
                rows.append(row)

df_all = pd.DataFrame(rows)

if not df_all.empty:
    model_order = [m for m, _, _ in MODELS if m in df_all["Model"].unique()]

    # Identificar melhor pipeline por modelo (maior final_score médio geral)
    best_pipeline = {}
    for model in model_order:
        sub = df_all[df_all["Model"] == model].groupby("Pipeline_Raw")["Final Score"].mean()
        best_pipeline[model] = sub.idxmax()

    cat_short = [JUDGE_LABELS[a].replace(" ", "\n") if len(JUDGE_LABELS[a]) > 14 else JUDGE_LABELS[a]
                 for a in JUDGE_ATTRS]

    def radar_chart(ax, values_dict, categories, title, cat_labels):
        N = len(categories)
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(cat_labels, size=13, weight='bold')
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0.25","0.50","0.75","1.00"], size=11, color='#555555')
        ax.yaxis.grid(True, linestyle='--', alpha=0.5)

        for model, vals in values_dict.items():
            v = list(vals) + [vals[0]]
            color = MODEL_COLORS[model]
            ax.plot(angles, v, 'o-', linewidth=2.0, color=color, label=model)
            ax.fill(angles, v, alpha=0.10, color=color)

        ax.set_title(title, size=20, pad=25, weight='bold')

    fig, axes = plt.subplots(1, 3, figsize=(26, 9), subplot_kw=dict(polar=True))

    legend_labels_stored = {}

    for i, diff_raw in enumerate(DIFFICULTIES):
        ax = axes[i]
        diff_label = DIFF_LABELS[diff_raw]
        
        values_dict = {}
        for model in model_order:
            bp = best_pipeline[model]
            row = df_all[(df_all["Model"] == model) & (df_all["Pipeline_Raw"] == bp) & (df_all["Difficulty_Raw"] == diff_raw)]
            if not row.empty:
                values_dict[model] = [float(row.iloc[0][a]) for a in JUDGE_ATTRS]
                legend_labels_stored[model] = f"{model} ({PIPE_NAMES[bp]})"

        radar_chart(ax, values_dict, JUDGE_ATTRS, f"Dificuldade: {diff_label}", cat_short)

    handles, _ = axes[0].get_legend_handles_labels()
    custom_labels = [legend_labels_stored.get(model, model) for model in model_order if model in legend_labels_stored]
    fig.legend(handles, custom_labels, loc='upper center', bbox_to_anchor=(0.5, -0.04), ncol=len(model_order), fontsize=16, title="Modelo (Melhor Pipeline)", title_fontsize=18)

    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.15)
    
    out_path = os.path.join(OUTPUT_DIR, "radar_llm_judge_por_dificuldade.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Gráfico gerado com sucesso: {out_path}")
else:
    print("Nenhum dado encontrado.")
