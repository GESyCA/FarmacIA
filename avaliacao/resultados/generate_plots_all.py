"""
generate_plots_all.py
Gera todos os gráficos comparativos entre os 4 modelos.
Não requer align_all_chunks.py - lê diretamente dos compiled_results.json.
"""

import os, json, glob, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from math import pi
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# Configuração visual global
# ─────────────────────────────────────────────
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 1.0,
    'grid.color': '#eeeeee',
    'grid.linestyle': '--',
    'figure.titlesize': 22,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
})

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
GUARDED_DIR   = os.path.join(BASE_DIR, "Comparativo Guarded")
OUTPUT_DIR    = os.path.join(BASE_DIR, "graficos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

import matplotlib.colors as mcolors

def darken_color(hex_color, factor=0.65):
    """Retorna uma versão mais escura da cor HEX fornecida."""
    rgb = mcolors.to_rgb(hex_color)
    return mcolors.to_hex(tuple(c * factor for c in rgb))

MODEL_COLORS = {
    "Gemma 4:4b":       "#1F77B4",   # Azul escuro
    "MedGemma 4b":      "#D62728",   # Vermelho queimado
    "Phi4 Mini":        "#D4AC0D",   # Amarelo/Mostarda
    "MediPhi Instruct": "#2CA02C",   # Verde
}

PIPELINES = ["06_naive","01_standard","02_agentic","03_hybrid_agent","04_fusion","05_graph","07_guarded"]
PIPE_NAMES = {
    "06_naive":        "Naive RAG",
    "01_standard":     "Standard RAG",
    "02_agentic":      "Agentic RAG",
    "03_hybrid_agent": "Hybrid Agent",
    "04_fusion":       "Fusion RAG",
    "05_graph":        "Graph RAG",
    "07_guarded":      "Guarded RAG",
}
DIFFICULTIES = ["faceis", "medias", "dificeis"]
DIFF_LABELS  = {"faceis": "Fáceis", "medias": "Médias", "dificeis": "Difíceis"}

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

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def label_bars(ax, fmt='score', fontsize=11, rotation=90, weight='bold'):
    """Adiciona rótulo no topo de TODAS as barras, incluindo zeros."""
    y_min, y_max = ax.get_ylim()
    pad = (y_max - y_min) * 0.04
    for container in ax.containers:
        labels = []
        for val in container.datavalues:
            if pd.isna(val):
                labels.append("")
            elif fmt == 'percent':
                labels.append(f"{val:.1f}%")
            elif fmt == 'time':
                labels.append(f"{val:.1f}s" if val >= 1 else f"{val:.3f}s")
            else:
                labels.append(f"{val:.3f}")
        ax.bar_label(container, labels=labels, padding=3,
                     fontsize=fontsize, weight=weight, color='#333333', rotation=rotation)
    # expand ylim
    if rotation != 0:
        pad *= 2.5 # Dar mais espaco no topo se estiver rotacionado
    ax.set_ylim(y_min, y_max + pad * 3)


def load_compiled(json_path, model_name):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    rows = []
    for pipe in PIPELINES:
        for diff in DIFFICULTIES:
            key = f"{pipe}|{diff}"
            if key in data:
                m = data[key]
                rows.append({
                    "Model":        model_name,
                    "Pipeline_Raw": pipe,
                    "Pipeline":     PIPE_NAMES[pipe],
                    "Diff_Raw":     diff,
                    "Difficulty":   DIFF_LABELS[diff],
                    # Retrieval
                    "Chunk Recall@3":   m.get("chunk_recall_at_3", 0.0),
                    "Chunk Recall@10":  m.get("chunk_recall_at_10", 0.0),
                    "Chunk MRR@10":     m.get("chunk_mrr_at_10", 0.0),
                    "Ctx Recall":       m.get("contextual_recall", 0.0),
                    "Ctx Precision":    m.get("contextual_precision", 0.0),
                    # Generation
                    "Final Score":      m.get("final_score", 0.0),
                    "Critical Fail %":  m.get("critical_failure_rate", 0.0) * 100,
                    "ROUGE-1":          m.get("rouge1", 0.0),
                    "BERTScore":        m.get("bertscore_f1", 0.0),
                    # Times
                    "Retrieval Time":   m.get("avg_retrieval_time", 0.0),
                    "Inference Time":   m.get("avg_inference_time", 0.0),
                    "Total Time":       m.get("avg_retrieval_time", 0.0) + m.get("avg_inference_time", 0.0),
                    # Judge subscores
                    **{k: m.get(k, 0.0) for k in JUDGE_ATTRS},
                })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
dfs = []
for model_name, folder, fname in [
    ("Gemma 4:4b",       "gemma_4_4b",  "gemma_compiled_results.json"),
    ("MedGemma 4b",      "medgemma_4b", "medgemma_compiled_results.json"),
    ("Phi4 Mini",        "phi4-mini",   "phi4_compiled_results.json"),
    ("MediPhi Instruct", "mediphi",     "mediphi_compiled_results.json"),
]:
    path = os.path.join(BASE_DIR, folder, fname)
    if os.path.exists(path):
        dfs.append(load_compiled(path, model_name))
    else:
        print(f"AVISO: {path} não encontrado.")

df_all = pd.concat(dfs, ignore_index=True)
df_all['Pipeline_Raw'] = pd.Categorical(df_all['Pipeline_Raw'], categories=PIPELINES, ordered=True)

# Consolidated (média das 3 dificuldades)
df_cons = df_all.groupby(["Model","Pipeline","Pipeline_Raw"], as_index=False).mean(numeric_only=True)
df_cons = df_cons.sort_values('Pipeline_Raw')

palette = [MODEL_COLORS[m] for m in ["Gemma 4:4b","MedGemma 4b","Phi4 Mini","MediPhi Instruct"]]
model_order = ["Gemma 4:4b","MedGemma 4b","Phi4 Mini","MediPhi Instruct"]

print("Dados carregados. Iniciando geração dos gráficos...")

# ═══════════════════════════════════════════════════════════════
# 1. BARRAS: também mostrar zero (já garantido por label_bars)
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# 2. Métricas de Recuperação — todos os modelos, consolidado
# ═══════════════════════════════════════════════════════════════
RETRIEVAL_COLS = ["Chunk Recall@3","Chunk Recall@10","Chunk MRR@10","Ctx Recall","Ctx Precision"]
RETRIEVAL_LABELS = ["Chunk\nRecall@3","Chunk\nRecall@10","Chunk\nMRR@10","Recall\nContextual","Precisão\nContextual"]

for col, lbl in zip(RETRIEVAL_COLS, RETRIEVAL_LABELS):
    fig, ax = plt.subplots(figsize=(12, 7))
    lbl_title = lbl.replace('\n', ' ')
    fig.suptitle(f"Comparativo: {lbl_title} — Todos os Modelos (Média Consolidada)", fontsize=18, weight='bold')

    sub = df_cons[["Model","Pipeline","Pipeline_Raw", col]].copy()
    sns.barplot(data=sub, x="Pipeline", y=col, hue="Model",
                hue_order=model_order, palette=palette, ax=ax)
    ax.set_xlabel("Pipeline RAG", fontsize=15, weight='bold')
    ax.set_ylabel("Score (0–1)", fontsize=15, weight='bold')
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis='x', rotation=45, labelsize=13)
    ax.tick_params(axis='y', labelsize=13)
    ax.legend(title="Modelo", fontsize=12, title_fontsize=13,
              bbox_to_anchor=(1.02, 1), loc='upper left')
    label_bars(ax, 'score', fontsize=10)

    plt.tight_layout()
    safe_col_name = col.replace("@", "_").replace(" ", "_").lower()
    save_path = os.path.join(OUTPUT_DIR, f"all_models_retrieval_metrics_{safe_col_name}.png")
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [OK] all_models_retrieval_metrics_{safe_col_name}.png")

# ═══════════════════════════════════════════════════════════════
# 3. Métricas de Geração — todos os modelos, consolidado
# ═══════════════════════════════════════════════════════════════
GEN_COLS   = ["Final Score","Critical Fail %","ROUGE-1","BERTScore"]
GEN_FMTS   = ['score','percent','score','score']
GEN_YLIMS  = [(0,1.05),(0,115),(0,0.7),(0,1.05)]
GEN_LABELS = ["Final Score","Taxa de Falhas\nCríticas (%)","ROUGE-1","BERTScore F1"]

for col, fmt, ylim, lbl in zip(GEN_COLS, GEN_FMTS, GEN_YLIMS, GEN_LABELS):
    fig, ax = plt.subplots(figsize=(12, 7))
    lbl_title = lbl.replace('\n', ' ')
    fig.suptitle(f"Comparativo: {lbl_title} — Todos os Modelos (Média Consolidada)", fontsize=18, weight='bold')

    sns.barplot(data=df_cons, x="Pipeline", y=col, hue="Model",
                hue_order=model_order, palette=palette, ax=ax)
    ax.set_xlabel("Pipeline RAG", fontsize=15, weight='bold')
    ax.set_ylabel(lbl_title, fontsize=15, weight='bold')
    ax.set_ylim(*ylim)
    ax.tick_params(axis='x', rotation=45, labelsize=13)
    ax.tick_params(axis='y', labelsize=13)
    ax.legend(title="Modelo", fontsize=12, title_fontsize=13,
              bbox_to_anchor=(1.02, 1), loc='upper left')
    label_bars(ax, fmt, fontsize=10)

    plt.tight_layout()
    safe_col_name = col.replace("%", "pct").replace(" ", "_").replace("-", "_").lower()
    save_path = os.path.join(OUTPUT_DIR, f"all_models_generation_metrics_{safe_col_name}.png")
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [OK] all_models_generation_metrics_{safe_col_name}.png")

# ═══════════════════════════════════════════════════════════════
# 4. Tempos de Recuperação e Inferência — todos os modelos (Barras Empilhadas com fontes maiores)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(18, 9))
fig.suptitle("Comparativo: Tempos de Recuperação (Sólido Escuro) e Inferência (Hachurado Claro)", fontsize=22, weight='bold')

pipelines = PIPELINES
x = np.arange(len(pipelines))
width = 0.2

for i, model in enumerate(model_order):
    sub = df_cons[df_cons["Model"] == model].set_index("Pipeline_Raw").reindex(pipelines)
    offset = (i - 1.5) * width
    color = MODEL_COLORS[model]
    dark_c = darken_color(color, 0.65)
    
    # Bottom bar (Retrieval) - Cor escura
    ax.bar(x + offset, sub["Retrieval Time"], width, label=model, color=dark_c, edgecolor='black', linewidth=0.5)
    # Top bar (Inference) - Cor clara com hachura
    ax.bar(x + offset, sub["Inference Time"], width, bottom=sub["Retrieval Time"], color=color, alpha=0.35, hatch='////', edgecolor='black', linewidth=0.5)
    
    # Labels
    for j, val in enumerate(sub["Total Time"]):
        if pd.notna(val):
            lbl = f"{val:.1f}s" if val >= 1 else f"{val:.3f}s"
            ax.text(x[j] + offset, val + (val * 0.02), lbl, ha='center', va='bottom', fontsize=11, weight='bold', rotation=45, color='#333333')

ax.set_title("Todos os Modelos (Média Consolidada)", fontsize=18, pad=15)
ax.set_xticks(x)
ax.set_xticklabels([PIPE_NAMES[p] for p in pipelines], fontsize=14, rotation=45, weight='bold')
ax.set_xlabel("Pipeline RAG", fontsize=16, weight='bold')
ax.set_ylabel("Segundos", fontsize=16, weight='bold')
ax.tick_params(axis='y', labelsize=14)

from matplotlib.patches import Patch
handles = [Patch(facecolor=MODEL_COLORS[m], edgecolor='white', label=m) for m in model_order]
handles.append(Patch(facecolor='#444444', edgecolor='black', hatch='', label='Recuperação (Retrieval Escuro)'))
handles.append(Patch(facecolor='#cccccc', edgecolor='black', hatch='////', label='Inferência (Generation Claro)'))
ax.legend(handles=handles, title="Legenda", fontsize=14, title_fontsize=16, loc='upper right')

y_max = df_cons["Total Time"].max()
ax.set_ylim(0, y_max * 1.25)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "all_models_times_comparison.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  [OK] all_models_times_comparison.png (Barras empilhadas com fontes maiores)")

# ═══════════════════════════════════════════════════════════════
# 5a. Scatter: Tempo Total vs Final Score — Versão 1: Textos Direcionados sem Sobreposição (adjustText)
# ═══════════════════════════════════════════════════════════════
from adjustText import adjust_text

fig, ax = plt.subplots(figsize=(15, 9))

texts_scatter = []
for model in model_order:
    sub = df_cons[df_cons["Model"] == model]
    color = MODEL_COLORS[model]
    ax.scatter(sub["Total Time"], sub["Final Score"],
               color=color, s=180, zorder=3, label=model, edgecolors='black', linewidths=1.0)
    for _, row in sub.iterrows():
        lbl = f"{row['Pipeline']}"
        txt = ax.text(row["Total Time"], row["Final Score"], lbl,
                      fontsize=13, color=color, fontweight='bold')
        texts_scatter.append(txt)

adjust_text(texts_scatter, ax=ax,
            arrowprops=dict(arrowstyle='->', color='#777777', lw=0.9, alpha=0.8),
            expand_text=(1.2, 1.4), expand_points=(1.3, 1.5),
            force_text=(0.6, 0.8), force_points=(0.6, 0.8))

ax.set_xlabel("Tempo Total Médio (Recuperação + Inferência, segundos)", fontsize=16, weight='bold')
ax.set_ylabel("Final Score Médio (escala 0–1)", fontsize=16, weight='bold')
ax.set_title("Relação entre Tempo Total e Score Final (Textos Direcionados)", fontsize=20, weight='bold')
ax.tick_params(axis='both', which='major', labelsize=14)
ax.legend(title="Modelo", fontsize=14, title_fontsize=15, loc='lower right')
ax.set_ylim(0, 1.05)
ax.grid(True, alpha=0.4, linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "all_models_time_vs_score_scatter_directed.png"), dpi=200, bbox_inches='tight')
plt.savefig(os.path.join(OUTPUT_DIR, "all_models_time_vs_score_scatter.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  [OK] all_models_time_vs_score_scatter.png (Versão 1 - Textos Direcionados)")

# ═══════════════════════════════════════════════════════════════
# 5b. Scatter: Tempo Total vs Final Score — Versão 2: Símbolos por Estratégia RAG e Cores por Modelo
# ═══════════════════════════════════════════════════════════════
PIPE_MARKERS = {
    "Naive RAG":     "o",   # Círculo
    "Standard RAG":  "s",   # Quadrado
    "Agentic RAG":   "^",   # Triângulo
    "Hybrid Agent":  "D",   # Diamante
    "Fusion RAG":    "*",   # Estrela
    "Graph RAG":     "P",   # Mais/Cruz
    "Guarded RAG":   "h",   # Hexágono
}

fig, ax = plt.subplots(figsize=(16, 9))
fig.suptitle("Relação entre Tempo Total e Score Final — Símbolos por Estratégia RAG e Cores por Modelo", fontsize=20, weight='bold')

for model in model_order:
    color = MODEL_COLORS[model]
    sub = df_cons[df_cons["Model"] == model]
    for _, row in sub.iterrows():
        pipe = row["Pipeline"]
        marker = PIPE_MARKERS.get(pipe, "o")
        ax.scatter(row["Total Time"], row["Final Score"],
                   color=color, marker=marker, s=220, zorder=3,
                   edgecolors='black', linewidths=1.0)

ax.set_xlabel("Tempo Total Médio (Recuperação + Inferência, segundos)", fontsize=16, weight='bold')
ax.set_ylabel("Final Score Médio (escala 0–1)", fontsize=16, weight='bold')
ax.tick_params(axis='both', which='major', labelsize=14)
ax.set_ylim(0, 1.05)
ax.grid(True, alpha=0.4, linestyle='--')

from matplotlib.lines import Line2D
model_handles = [Line2D([0], [0], marker='o', color='w', label=m,
                        markerfacecolor=MODEL_COLORS[m], markeredgecolor='black', markersize=12)
                 for m in model_order]

pipe_handles = [Line2D([0], [0], marker=PIPE_MARKERS[p], color='w', label=p,
                       markerfacecolor='#555555', markeredgecolor='black', markersize=12)
                for p in PIPE_NAMES.values()]

leg1 = ax.legend(handles=model_handles, title="Modelo (Cores)", fontsize=13, title_fontsize=14,
                 loc='upper left', bbox_to_anchor=(1.02, 1.0))
ax.add_artist(leg1)
ax.legend(handles=pipe_handles, title="Estratégia RAG (Símbolos)", fontsize=13, title_fontsize=14,
          loc='upper left', bbox_to_anchor=(1.02, 0.55))

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "all_models_time_vs_score_scatter_symbols.png"), dpi=200, bbox_inches='tight')
plt.close()
print("  [OK] all_models_time_vs_score_scatter_symbols.png (Versão 2 - Símbolos RAG)")

# ═══════════════════════════════════════════════════════════════
# 7. Gráfico Combinado para Artigo: Tempos de Execução (Esq) + Scatter Tempo vs Score (Dir)
# ═══════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(28, 10))

# ── Subplot A (Esquerda): Barras Empilhadas de Tempos ──
pipelines = PIPELINES
x = np.arange(len(pipelines))
width = 0.2

for i, model in enumerate(model_order):
    sub = df_cons[df_cons["Model"] == model].set_index("Pipeline_Raw").reindex(pipelines)
    offset = (i - 1.5) * width
    color = MODEL_COLORS[model]
    dark_c = darken_color(color, 0.65)
    
    # Bottom bar (Retrieval) - Cor escura
    ax1.bar(x + offset, sub["Retrieval Time"], width, color=dark_c, edgecolor='black', linewidth=0.5)
    # Top bar (Inference) - Cor clara com hachura
    ax1.bar(x + offset, sub["Inference Time"], width, bottom=sub["Retrieval Time"], color=color, alpha=0.35, hatch='////', edgecolor='black', linewidth=0.5)
    
    # Labels sobre as barras: 90 graus, fonte um pouco maior (12.5), sem negrito
    for j, val in enumerate(sub["Total Time"]):
        if pd.notna(val):
            lbl = f"{val:.1f}s" if val >= 1 else f"{val:.3f}s"
            ax1.text(x[j] + offset, val + (val * 0.02), lbl, ha='center', va='bottom', fontsize=12.5, weight='normal', rotation=90, color='#333333')

ax1.set_xticks(x)
ax1.set_xticklabels([PIPE_NAMES[p] for p in pipelines], fontsize=14, rotation=45, weight='bold')
ax1.set_xlabel("Pipeline RAG", fontsize=16, weight='bold', labelpad=10)
ax1.set_ylabel("Segundos", fontsize=16, weight='bold')
ax1.tick_params(axis='y', labelsize=14)
y_max = df_cons["Total Time"].max()
ax1.set_ylim(0, y_max * 1.25)
ax1.grid(True, alpha=0.4, linestyle='--')

# Legenda do Subplot A posicionada do lado DIREITO para não sobrepor valores
from matplotlib.patches import Patch
time_handles = [
    Patch(facecolor='#444444', edgecolor='black', hatch='', label='Recuperação (Retrieval Escuro)'),
    Patch(facecolor='#cccccc', edgecolor='black', hatch='////', label='Inferência (Generation Claro)')
]
ax1.legend(handles=time_handles, title="Fase", fontsize=13, title_fontsize=14, loc='upper right')

# Título do Subplot A ABAIXO do gráfico
ax1.text(0.5, -0.32, "(A) Tempos Médios de Recuperação e Inferência por Pipeline RAG",
         transform=ax1.transAxes, ha='center', va='top', fontsize=18, weight='bold')

# ── Subplot B (Direita): Scatter Tempo Total vs Final Score (Símbolos RAG + Cores Modelo) ──
for model in model_order:
    color = MODEL_COLORS[model]
    sub = df_cons[df_cons["Model"] == model]
    for _, row in sub.iterrows():
        pipe = row["Pipeline"]
        marker = PIPE_MARKERS.get(pipe, "o")
        ax2.scatter(row["Total Time"], row["Final Score"],
                    color=color, marker=marker, s=220, zorder=3,
                    edgecolors='black', linewidths=1.0)

ax2.set_xlabel("Tempo Total Médio (segundos)", fontsize=16, weight='bold', labelpad=10)
ax2.set_ylabel("Final Score Médio (escala 0–1)", fontsize=16, weight='bold')
ax2.tick_params(axis='both', which='major', labelsize=14)
ax2.set_ylim(0, 1.05)
ax2.grid(True, alpha=0.4, linestyle='--')

from matplotlib.lines import Line2D
model_handles = [Line2D([0], [0], marker='o', color='w', label=m,
                        markerfacecolor=MODEL_COLORS[m], markeredgecolor='black', markersize=12)
                 for m in model_order]

pipe_handles = [Line2D([0], [0], marker=PIPE_MARKERS[p], color='w', label=p,
                       markerfacecolor='#555555', markeredgecolor='black', markersize=12)
                for p in PIPE_NAMES.values()]

leg_m = ax2.legend(handles=model_handles, title="Modelo (Cores)", fontsize=13, title_fontsize=14,
                   loc='upper left', bbox_to_anchor=(1.02, 1.0))
ax2.add_artist(leg_m)
ax2.legend(handles=pipe_handles, title="Estratégia RAG (Símbolos)", fontsize=13, title_fontsize=14,
           loc='upper left', bbox_to_anchor=(1.02, 0.55))

# Título do Subplot B ABAIXO do gráfico
ax2.text(0.5, -0.32, "(B) Relação entre Tempo Total e Score Final",
         transform=ax2.transAxes, ha='center', va='top', fontsize=18, weight='bold')

plt.tight_layout()
plt.subplots_adjust(wspace=0.25, bottom=0.25)

combined_path = os.path.join(OUTPUT_DIR, "article_times_and_scatter_combined.png")
plt.savefig(combined_path, dpi=300, bbox_inches='tight')
plt.close()
print("  [OK] article_times_and_scatter_combined.png (Figura combinada para artigo)")

# ═══════════════════════════════════════════════════════════════
# 8. Gráfico Unificado com 2 Eixos Y Compartilhando Eixo X (Tempo em Segundos)
#    Eixo Y1 (Esquerda): Final Score (0.0 - 1.0)
#    Eixo Y2 (Direita): Estratégia RAG (Categorias)
# ═══════════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(figsize=(19, 10))

# Criar eixo Y2 (Direita) compartilhado com X
ax2 = ax1.twinx()

# ── Eixo Y1 (Esquerda): Final Score Médio (0.0 - 1.0) ──
ax1.set_ylabel("Final Score Médio (escala 0.0 – 1.0)", fontsize=16, weight='bold', color='#111111', labelpad=12)
ax1.set_ylim(0, 1.05)
ax1.tick_params(axis='y', labelsize=14)

# ── Eixo Y2 (Direita): Estratégia RAG (Categorias) ──
y_labels = list(reversed(list(PIPE_NAMES.values())))
y_positions = {p: i for i, p in enumerate(y_labels)}
ax2.set_yticks(range(len(y_labels)))
ax2.set_yticklabels(y_labels, fontsize=14, weight='bold')
ax2.set_ylabel("Estratégia RAG", fontsize=16, weight='bold', color='#222222', labelpad=12)
ax2.set_ylim(-0.6, len(y_labels) - 0.4)

# Plotar barras/segmentos horizontais de tempo por Modelo e RAG Strategy em ax2
offsets = np.linspace(-0.25, 0.25, len(model_order))
bar_height = 0.11

for i, model in enumerate(model_order):
    color = MODEL_COLORS[model]
    dark_c = darken_color(color, 0.65)
    sub = df_cons[df_cons["Model"] == model]
    offset = offsets[i]
    
    for _, row in sub.iterrows():
        pipe = row["Pipeline"]
        y_base = y_positions[pipe] + offset
        
        # Barra horizontal de Recuperação (Solid Escuro)
        ax2.barh(y_base, row["Retrieval Time"], height=bar_height,
                 color=dark_c, alpha=0.95, edgecolor='black', linewidth=0.5)
        # Barra horizontal de Inferência (Hatched Claro)
        ax2.barh(y_base, row["Inference Time"], left=row["Retrieval Time"], height=bar_height,
                 color=color, hatch='////', alpha=0.30, edgecolor='black', linewidth=0.5)
        
        # Marcador de ponto final do tempo total na barra horizontal
        marker = PIPE_MARKERS.get(pipe, "o")
        ax2.scatter(row["Total Time"], y_base, color=color, marker=marker,
                    s=130, zorder=3, edgecolors='black', linewidths=0.8)

# ── Eixo Y1 (Esquerda): Pontos de Final Score (SEM LINHAS TRACEJADAS) ──
texts_dual = []
for model in model_order:
    color = MODEL_COLORS[model]
    sub = df_cons[df_cons["Model"] == model]
    
    # Apenas os pontos de Final Score (SEM ax1.plot de linha tracejada)
    for _, row in sub.iterrows():
        marker = PIPE_MARKERS.get(row["Pipeline"], "o")
        ax1.scatter(row["Total Time"], row["Final Score"], color=color, marker=marker,
                    s=200, zorder=6, edgecolors='black', linewidths=1.2)
        
        # Rótulo de texto do valor numérico de Score
        lbl = f"{row['Final Score']:.2f}"
        txt = ax1.text(row["Total Time"], row["Final Score"] + 0.015, lbl,
                       fontsize=11, color=color, fontweight='bold', ha='center', va='bottom')
        texts_dual.append(txt)

# adjustText para evitar colisão de rótulos dos Scores
from adjustText import adjust_text
adjust_text(texts_dual, ax=ax1,
            arrowprops=dict(arrowstyle='->', color='#777777', lw=0.8, alpha=0.7),
            expand_text=(1.1, 1.3), expand_points=(1.2, 1.4))

# Configuração do Eixo X Compartilhado
ax1.set_xlabel("Tempo de Execução Médio (Segundos)", fontsize=16, weight='bold', labelpad=10)
ax1.tick_params(axis='x', labelsize=14)
max_t = df_cons["Total Time"].max()
ax1.set_xlim(0, max_t * 1.08)
ax1.grid(True, alpha=0.35, linestyle='--')

# Legendas externas posicionadas à direita de ax2
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

model_handles = [Line2D([0], [0], marker='o', color='w', label=m,
                        markerfacecolor=MODEL_COLORS[m], markeredgecolor='black', markersize=12)
                 for m in model_order]

pipe_handles = [Line2D([0], [0], marker=PIPE_MARKERS[p], color='w', label=p,
                       markerfacecolor='#555555', markeredgecolor='black', markersize=12)
                for p in PIPE_NAMES.values()]

phase_handles = [
    Patch(facecolor='#444444', edgecolor='black', hatch='', label='Tempo Recuperação (Escuro)'),
    Patch(facecolor='#cccccc', edgecolor='black', hatch='////', label='Tempo Inferência (Claro)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#666666', markeredgecolor='black', label='Final Score (Ponto)')
]

leg_m = ax2.legend(handles=model_handles, title="Modelo (Cores)", fontsize=12, title_fontsize=13,
                   loc='upper left', bbox_to_anchor=(1.10, 1.0))
ax2.add_artist(leg_m)

leg_p = ax2.legend(handles=pipe_handles, title="Estratégia RAG (Símbolos)", fontsize=12, title_fontsize=13,
                   loc='upper left', bbox_to_anchor=(1.10, 0.62))
ax2.add_artist(leg_p)

ax2.legend(handles=phase_handles, title="Componentes de Tempo / Score", fontsize=12, title_fontsize=13,
           loc='upper left', bbox_to_anchor=(1.10, 0.22))

# Sub-título/Legenda explicativa abaixo do gráfico
ax1.text(0.5, -0.22, "Figura: Análise Integrada — Final Score (Eixo Esquerdo), Estratégia RAG (Eixo Direito) e Tempo Total (Eixo X Compartilhado)",
         transform=ax1.transAxes, ha='center', va='top', fontsize=16, weight='bold')

plt.tight_layout()
plt.subplots_adjust(right=0.76, bottom=0.22)

dual_path = os.path.join(OUTPUT_DIR, "article_time_score_rag_dual_axis.png")
plt.savefig(dual_path, dpi=300, bbox_inches='tight')
plt.close()
print("  [OK] article_time_score_rag_dual_axis.png (Gráfico unificado com eixos Y invertidos e sem linhas tracejadas)")

# ═══════════════════════════════════════════════════════════════
# 9. Gráfico Separado Lado a Lado: (A) Final Score vs Tempo (Esq) + (B) Barras Horizontais RAG vs Tempo (Dir)
# ═══════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(26, 10))

max_t = df_cons["Total Time"].max() * 1.08

# ── Subplot A (Esquerda): Final Score Médio vs Tempo Total (Segundos) ──
texts_side = []
for model in model_order:
    color = MODEL_COLORS[model]
    sub = df_cons[df_cons["Model"] == model]
    for _, row in sub.iterrows():
        marker = PIPE_MARKERS.get(row["Pipeline"], "o")
        ax1.scatter(row["Total Time"], row["Final Score"], color=color, marker=marker,
                    s=200, zorder=5, edgecolors='black', linewidths=1.2)
        
        lbl = f"{row['Final Score']:.2f}"
        txt = ax1.text(row["Total Time"], row["Final Score"] + 0.015, lbl,
                       fontsize=11, color=color, fontweight='bold', ha='center', va='bottom')
        texts_side.append(txt)

from adjustText import adjust_text
adjust_text(texts_side, ax=ax1,
            arrowprops=dict(arrowstyle='->', color='#777777', lw=0.8, alpha=0.7),
            expand_text=(1.1, 1.3), expand_points=(1.2, 1.4))

ax1.set_xlabel("Tempo de Execução Médio (Segundos)", fontsize=16, weight='bold', labelpad=10)
ax1.set_ylabel("Final Score Médio (escala 0.0 – 1.0)", fontsize=16, weight='bold', labelpad=10)
ax1.tick_params(axis='both', which='major', labelsize=14)
ax1.set_xlim(0, max_t)
ax1.set_ylim(0, 1.05)
ax1.grid(True, alpha=0.35, linestyle='--')

ax1.text(0.5, -0.28, "(A) Relação entre Final Score e Tempo Total de Execução",
         transform=ax1.transAxes, ha='center', va='top', fontsize=18, weight='bold')

# ── Subplot B (Direita): Estratégia RAG (Barras Horizontais) vs Tempo (Segundos) ──
y_labels = list(reversed(list(PIPE_NAMES.values())))
y_positions = {p: i for i, p in enumerate(y_labels)}
ax2.set_yticks(range(len(y_labels)))
ax2.set_yticklabels(y_labels, fontsize=14, weight='bold')
ax2.set_ylabel("Estratégia RAG", fontsize=16, weight='bold', labelpad=10)
ax2.set_ylim(-0.6, len(y_labels) - 0.4)

offsets = np.linspace(-0.25, 0.25, len(model_order))
bar_height = 0.11

for i, model in enumerate(model_order):
    color = MODEL_COLORS[model]
    dark_c = darken_color(color, 0.65)
    sub = df_cons[df_cons["Model"] == model]
    offset = offsets[i]
    
    for _, row in sub.iterrows():
        pipe = row["Pipeline"]
        y_base = y_positions[pipe] + offset
        
        # Barra horizontal de Recuperação (Solid Escuro)
        ax2.barh(y_base, row["Retrieval Time"], height=bar_height,
                 color=dark_c, alpha=0.95, edgecolor='black', linewidth=0.5)
        # Barra horizontal de Inferência (Hatched Claro)
        ax2.barh(y_base, row["Inference Time"], left=row["Retrieval Time"], height=bar_height,
                 color=color, hatch='////', alpha=0.30, edgecolor='black', linewidth=0.5)
        
        # Marcador no final do tempo total
        marker = PIPE_MARKERS.get(pipe, "o")
        ax2.scatter(row["Total Time"], y_base, color=color, marker=marker,
                    s=130, zorder=4, edgecolors='black', linewidths=0.8)

ax2.set_xlabel("Tempo de Execução Médio (Segundos)", fontsize=16, weight='bold', labelpad=10)
ax2.tick_params(axis='both', which='major', labelsize=14)
ax2.set_xlim(0, max_t)
ax2.grid(True, alpha=0.35, linestyle='--')

ax2.text(0.5, -0.28, "(B) Tempos de Recuperação e Inferência por Estratégia RAG",
         transform=ax2.transAxes, ha='center', va='top', fontsize=18, weight='bold')

# Legendas externas posicionadas à direita de ax2
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

model_handles = [Line2D([0], [0], marker='o', color='w', label=m,
                        markerfacecolor=MODEL_COLORS[m], markeredgecolor='black', markersize=12)
                 for m in model_order]

pipe_handles = [Line2D([0], [0], marker=PIPE_MARKERS[p], color='w', label=p,
                       markerfacecolor='#555555', markeredgecolor='black', markersize=12)
                for p in PIPE_NAMES.values()]

phase_handles = [
    Patch(facecolor='#444444', edgecolor='black', hatch='', label='Tempo Recuperação (Escuro)'),
    Patch(facecolor='#cccccc', edgecolor='black', hatch='////', label='Tempo Inferência (Claro)')
]

leg_m = ax2.legend(handles=model_handles, title="Modelo (Cores)", fontsize=12, title_fontsize=13,
                   loc='upper left', bbox_to_anchor=(1.02, 1.0))
ax2.add_artist(leg_m)

leg_p = ax2.legend(handles=pipe_handles, title="Estratégia RAG (Símbolos)", fontsize=12, title_fontsize=13,
                   loc='upper left', bbox_to_anchor=(1.02, 0.62))
ax2.add_artist(leg_p)

ax2.legend(handles=phase_handles, title="Fases de Tempo", fontsize=12, title_fontsize=13,
           loc='upper left', bbox_to_anchor=(1.02, 0.22))

plt.tight_layout()
plt.subplots_adjust(wspace=0.25, right=0.82, bottom=0.22)

split_path = os.path.join(OUTPUT_DIR, "article_score_and_rag_times_side_by_side.png")
plt.savefig(split_path, dpi=300, bbox_inches='tight')
plt.close()
print("  [OK] article_score_and_rag_times_side_by_side.png (Gráfico separado lado a lado)")

# ═══════════════════════════════════════════════════════════════
# 6. Final Score por Dificuldade — todos os modelos
# ═══════════════════════════════════════════════════════════════
# Consolida por dificuldade (média dos pipelines)
df_by_diff = df_all.groupby(["Model","Difficulty","Diff_Raw"], as_index=False).agg({"Final Score":"mean"})
diff_order_raw = ["faceis","medias","dificeis"]
df_by_diff["Diff_Raw"] = pd.Categorical(df_by_diff["Diff_Raw"], categories=diff_order_raw, ordered=True)
df_by_diff = df_by_diff.sort_values("Diff_Raw")

for diff_raw, diff_label in DIFF_LABELS.items():
    subset = df_all[df_all["Diff_Raw"] == diff_raw].copy()
    subset["Pipeline_Raw"] = pd.Categorical(subset["Pipeline_Raw"], categories=PIPELINES, ordered=True)
    subset = subset.sort_values("Pipeline_Raw")

    fig, ax = plt.subplots(figsize=(18, 8))
    sns.barplot(data=subset, x="Pipeline", y="Final Score", hue="Model",
                hue_order=model_order, palette=palette, ax=ax)
    ax.set_title(f"Final Score por Pipeline — Questões {diff_label} (Todos os Modelos)", fontsize=22)
    ax.set_xlabel("Pipeline RAG", fontsize=20)
    ax.set_ylabel("Final Score (0–1)", fontsize=20)
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis='x', rotation=45, labelsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.legend(title="Modelo", fontsize=16, title_fontsize=18, bbox_to_anchor=(1.01,1), loc='upper left')
    label_bars(ax, 'score', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"all_models_final_score_{diff_raw}.png"), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [OK] all_models_final_score_{diff_raw}.png")

# ═══════════════════════════════════════════════════════════════
# 7. Radar por dificuldade — melhor pipeline de cada modelo
# ═══════════════════════════════════════════════════════════════
def radar_chart(ax, values_dict, categories, title, cat_labels):
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cat_labels, size=7)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25","0.50","0.75","1.00"], size=6, color='grey')
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)

    for model, vals in values_dict.items():
        v = list(vals) + [vals[0]]
        color = MODEL_COLORS[model]
        ax.plot(angles, v, 'o-', linewidth=1.5, color=color, label=model)
        ax.fill(angles, v, alpha=0.08, color=color)

    ax.set_title(title, size=11, pad=15, weight='bold')

# Identificar melhor pipeline por modelo (maior final_score médio geral)
best_pipeline = {}
for model in model_order:
    sub = df_all[df_all["Model"] == model].groupby("Pipeline_Raw")["Final Score"].mean()
    best_pipeline[model] = sub.idxmax()

print(f"\n  Melhores pipelines por modelo: {best_pipeline}")

cat_short = [JUDGE_LABELS[a].replace(" ", "\n") if len(JUDGE_LABELS[a]) > 14 else JUDGE_LABELS[a]
             for a in JUDGE_ATTRS]

for diff_raw, diff_label in DIFF_LABELS.items():
    fig, ax = plt.subplots(1, 1, figsize=(9, 9), subplot_kw=dict(polar=True))

    values_dict = {}
    legend_labels = {}  # model -> "Model (Pipeline)"
    for model in model_order:
        bp = best_pipeline[model]
        key = f"{bp}|{diff_raw}"
        row = df_all[(df_all["Model"] == model) & (df_all["Pipeline_Raw"] == bp) & (df_all["Diff_Raw"] == diff_raw)]
        if not row.empty:
            values_dict[model] = [float(row.iloc[0][a]) for a in JUDGE_ATTRS]
            legend_labels[model] = f"{model}\n({PIPE_NAMES[bp]})"

    # Radar com labels de legenda customizados
    radar_chart(ax, values_dict, JUDGE_ATTRS,
                f"Radar LLM-as-Judge — {diff_label}\n(Melhor pipeline de cada modelo)",
                cat_short)
    # Substituir labels da legenda pelo formato "Modelo (Pipeline)"
    handles, _ = ax.get_legend_handles_labels()
    custom_labels = [legend_labels.get(model, model) for model in model_order if model in values_dict]
    ax.legend(handles=handles, labels=custom_labels,
              loc='upper right', bbox_to_anchor=(1.35, 1.15),
              fontsize=8, title="Modelo (Pipeline)", title_fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"radar_llm_judge_{diff_raw}.png"), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [OK] radar_llm_judge_{diff_raw}.png")

# ═══════════════════════════════════════════════════════════════
# 8. Comparativo Pipeline 7 Guarded — dados de rastreio de execução
# ═══════════════════════════════════════════════════════════════
MODEL_FILE_PATTERNS = {
    "Gemma 4:4b":       "gemma4_e4b",
    "MedGemma 4b":      "medgemma_4b",
    "Phi4 Mini":        "phi4_mini",
    "MediPhi Instruct": "mediphi_instruct",
}

guarded_rows = []
for model_name, pattern in MODEL_FILE_PATTERNS.items():
    for diff_raw, diff_label in DIFF_LABELS.items():
        csv_files = glob.glob(os.path.join(GUARDED_DIR, f"*{pattern}*{diff_raw}*output.csv"))
        if not csv_files:
            continue
        df_g = pd.read_csv(csv_files[0])
        n = len(df_g)
        # Contagens de confiança
        for conf in ["high","medium","low"]:
            cnt = (df_g["guarded_confidence"].str.lower() == conf).sum() if "guarded_confidence" in df_g.columns else 0
            guarded_rows.append({"Model": model_name, "Difficulty": diff_label, "Diff_Raw": diff_raw,
                                  "Metric": f"Confiança {conf.capitalize()}", "Value": cnt / n * 100})
        # Fallback triggered rate
        if "guarded_fallback_triggered" in df_g.columns:
            ft = df_g["guarded_fallback_triggered"].apply(
                lambda x: str(x).strip().lower() in ("true","1","yes","sim")).mean() * 100
        else:
            ft = 0.0
        guarded_rows.append({"Model": model_name, "Difficulty": diff_label, "Diff_Raw": diff_raw,
                              "Metric": "Fallback Acionado (%)", "Value": ft})
        # Nº médio de seções secundárias
        if "guarded_planner_secondary" in df_g.columns:
            avg_sec = df_g["guarded_planner_secondary"].apply(
                lambda x: len([s for s in str(x).split(",") if str(s).strip()]) if pd.notna(x) else 0).mean()
        else:
            avg_sec = 0.0
        guarded_rows.append({"Model": model_name, "Difficulty": diff_label, "Diff_Raw": diff_raw,
                              "Metric": "Seções Secundárias (média)", "Value": avg_sec})
        # Nº médio de seções expandidas
        if "guarded_expanded_sections" in df_g.columns:
            avg_exp = df_g["guarded_expanded_sections"].apply(
                lambda x: len([s for s in str(x).split(",") if str(s).strip()]) if pd.notna(x) else 0).mean()
        else:
            avg_exp = 0.0
        guarded_rows.append({"Model": model_name, "Difficulty": diff_label, "Diff_Raw": diff_raw,
                              "Metric": "Seções Expandidas (média)", "Value": avg_exp})

df_guarded = pd.DataFrame(guarded_rows)

if not df_guarded.empty:
    guarded_metrics = df_guarded["Metric"].unique().tolist()
    n_metrics = len(guarded_metrics)
    n_cols = 3
    n_rows = (n_metrics + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
    fig.suptitle("Pipeline 7 Guarded RAG — Rastreio de Execução: Comparativo entre Modelos", fontsize=13, weight='bold')
    axes = axes.flatten()

    for i, metric in enumerate(guarded_metrics):
        ax = axes[i]
        sub = df_guarded[df_guarded["Metric"] == metric].copy()
        sub["Diff_Raw"] = pd.Categorical(sub["Diff_Raw"], categories=["faceis","medias","dificeis"], ordered=True)
        sub = sub.sort_values("Diff_Raw")
        sns.barplot(data=sub, x="Difficulty", y="Value", hue="Model",
                    hue_order=model_order, palette=palette, ax=ax)
        ax.set_title(metric, fontsize=10, weight='bold')
        ax.set_xlabel("Dificuldade")
        ax.set_ylabel("%" if "%" in metric or "Confiança" in metric else "Média")
        if i < n_metrics - 1:
            ax.legend_.remove()
        else:
            ax.legend(title="Modelo", fontsize=8, bbox_to_anchor=(1.01,1), loc='upper left')
        label_bars(ax, 'percent' if "%" in metric or "Confiança" in metric else 'score', fontsize=7)

    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "guarded_trace_comparison.png"), dpi=200, bbox_inches='tight')
    plt.close()
    print("  [OK] guarded_trace_comparison.png")
else:
    print("  [AVISO] Nenhum dado do Comparativo Guarded foi carregado.")

print(f"\n[OK] Todos os graficos gerados em: {OUTPUT_DIR}")
