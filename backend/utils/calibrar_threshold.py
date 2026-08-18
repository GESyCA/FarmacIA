"""
calibrar_threshold.py
─────────────────────
Roda queries representativas do dataset contra o ChromaDB e imprime a
distribuição de scores de relevância por query.

Use isso para escolher um bom valor de similarity_threshold no YAML
antes de rodar experimentos completos.

Uso:
    cd FarmacIA/Paciente/app
    python utils/calibrar_threshold.py

Parâmetros configuráveis (seção CONFIG abaixo):
    COLLECTION_NAME  : nome da coleção ChromaDB a inspecionar
    EMBEDDING_MODEL  : modelo de embedding usado na coleção
    CHROMA_PATH      : caminho para o banco ChromaDB
    K                : quantos chunks buscar por query (upper bound)
    DATASET_CSV      : CSV do dataset para extrair queries reais
                       (deixe None para usar as queries embutidas)
"""

import sys
import os
import io

# Força UTF-8 no terminal Windows para evitar UnicodeEncodeError com
# caracteres especiais presentes nos textos das bulas (PDFs)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import pandas as pd

# ─────────────────────────────────────────────
# CONFIG — ajuste aqui antes de rodar
# ─────────────────────────────────────────────
COLLECTION_NAME = "bulas_bge_m3"          # ou "bulas" para a coleção padrão
EMBEDDING_MODEL = "BAAI/bge-m3"           # deve ser o mesmo usado na ingestão
CHROMA_PATH     = "./chroma_bulas"
K               = 15                       # máx de chunks por query
DATASET_CSV     = "dataset/perguntas_respostas_dificeis.csv"  # None = usa queries embutidas
# ─────────────────────────────────────────────

# Queries embutidas (usadas se DATASET_CSV=None ou o arquivo não existir)
QUERIES_EMBUTIDAS = [
    ("amoxil",    "Como Amoxil® pode afetar o tratamento com varfarina?"),
    ("amoxil",    "Posso tomar amoxicilina grávida?"),
    ("amoxil",    "Qual a dose máxima diária de amoxicilina?"),
    ("rivotril",  "Rivotril tem contraindicação para apneia do sono?"),
    ("rivotril",  "O que acontece se parar de tomar Rivotril de repente?"),
    ("rivotril",  "Posso tomar Rivotril com álcool?"),
    ("tylenol",   "Qual a dose máxima de Tylenol por dia?"),
    ("tylenol",   "Tylenol pode ser usado em crianças menores de 12 anos?"),
    ("tylenol",   "Tylenol faz mal para o fígado?"),
    # Queries negativas (irrelevante — score deve ser baixo)
    ("amoxil",    "Qual o horário de funcionamento da farmácia?"),
    ("rivotril",  "Receita de bolo de chocolate"),
]


def carregar_queries_do_dataset(csv_path: str) -> list:
    """Lê o CSV do dataset e retorna lista de (medicamento, pergunta)."""
    try:
        df = pd.read_csv(csv_path)
        col_med = "nome_remedio" if "nome_remedio" in df.columns else "medicamento"
        queries = [
            (str(row[col_med]).strip().lower(), str(row["pergunta"]).strip())
            for _, row in df.iterrows()
        ]
        print(f"[Dataset] {len(queries)} queries carregadas de '{csv_path}'.\n")
        return queries
    except FileNotFoundError:
        print(f"[AVISO] '{csv_path}' não encontrado. Usando queries embutidas.\n")
        return []


def linha_score(score: float, max_bar: int = 40) -> str:
    """Barra visual proporcional ao score."""
    filled = int(score * max_bar)
    return "|" * filled + "." * (max_bar - filled)


def inspecionar_scores(vs: Chroma, queries: list, k: int):
    """Roda cada query e imprime os scores de relevância."""
    todos_os_scores = []

    for i, (medicamento, pergunta) in enumerate(queries, 1):
        print(f"\n{'=' * 70}")
        print(f"Query {i}/{len(queries)}")
        print(f"  Medicamento : {medicamento.upper()}")
        print(f"  Pergunta    : {pergunta[:90]}{'...' if len(pergunta) > 90 else ''}")
        print(f"{'-' * 70}")

        filtro = {"medicamento": medicamento.lower()}

        try:
            pairs = vs.similarity_search_with_relevance_scores(
                query=pergunta,
                filter=filtro,
                k=k,
            )
        except Exception as e:
            print(f"  [ERRO] {e}")
            continue

        if not pairs:
            print("  Nenhum chunk encontrado para este medicamento.")
            continue

        scores = [score for _, score in pairs]
        todos_os_scores.extend(scores)

        print(f"  {'#':<4} {'Score':>6}  {'Barra':<42}  Secao / Inicio do chunk")
        print(f"  {'-'*4} {'-'*6}  {'-'*42}  {'-'*30}")

        for j, (doc, score) in enumerate(pairs, 1):
            secao = doc.metadata.get("section") or doc.metadata.get("tipo_secao", "?")
            trecho = doc.page_content[:60].replace("\n", " ")
            barra = linha_score(max(0.0, min(1.0, score)))
            print(f"  {j:<4} {score:>6.4f}  {barra}  [{secao}] {trecho}...")

        print(f"\n  Resumo: min={min(scores):.4f}  max={max(scores):.4f}  "
              f"média={sum(scores)/len(scores):.4f}  "
              f"mediana={sorted(scores)[len(scores)//2]:.4f}")

    return todos_os_scores


def sugerir_threshold(todos_os_scores: list):
    """Analisa a distribuição global e sugere faixas de threshold."""
    if not todos_os_scores:
        return

    n = len(todos_os_scores)
    s_sorted = sorted(todos_os_scores)
    media = sum(s_sorted) / n
    mediana = s_sorted[n // 2]
    p25 = s_sorted[int(n * 0.25)]
    p75 = s_sorted[int(n * 0.75)]

    print(f"\n{'=' * 70}")
    print("DISTRIBUICAO GLOBAL DOS SCORES")
    print(f"{'-' * 70}")
    print(f"  Total de chunks avaliados : {n}")
    print(f"  Mínimo                    : {s_sorted[0]:.4f}")
    print(f"  Percentil 25              : {p25:.4f}")
    print(f"  Mediana (P50)             : {mediana:.4f}")
    print(f"  Média                     : {media:.4f}")
    print(f"  Percentil 75              : {p75:.4f}")
    print(f"  Máximo                    : {s_sorted[-1]:.4f}")

    # Histograma em texto
    print(f"\n  Histograma (cada '*' ≈ {max(1, n // 20)} chunk(s)):")
    bins = 10
    bin_size = (s_sorted[-1] - s_sorted[0] + 1e-9) / bins
    for b in range(bins):
        lo = s_sorted[0] + b * bin_size
        hi = lo + bin_size
        count = sum(1 for s in s_sorted if lo <= s < hi)
        bar = "*" * (count * 20 // max(n, 1))
        print(f"  [{lo:.2f}-{hi:.2f}]  {bar} ({count})")

    print(f"\n{'-' * 70}")
    print("SUGESTOES DE THRESHOLD")
    print(f"{'-' * 70}")
    print(f"  Conservador  (filtra pouco)  -> similarity_threshold: {p25:.2f}")
    print(f"  Moderado     (recomendado)   -> similarity_threshold: {mediana:.2f}")
    print(f"  Agressivo    (filtra muito)  -> similarity_threshold: {p75:.2f}")
    print(f"\n  Dica: comece com o valor Moderado ({mediana:.2f}) e ajuste")
    print(f"     observando o section_recall nos resultados dos experimentos.")
    print(f"     Se o recall cair muito, reduza o threshold; se o contexto")
    print(f"     ficar sujo com chunks irrelevantes, aumente-o.")
    print(f"{'=' * 70}\n")


def main():
    print("=" * 70)
    print("  CALIBRADOR DE SIMILARITY THRESHOLD — FarmacIA")
    print("=" * 70)
    print(f"  Coleção     : {COLLECTION_NAME}")
    print(f"  Embedding   : {EMBEDDING_MODEL}")
    print(f"  ChromaDB    : {CHROMA_PATH}")
    print(f"  K por query : {K}")
    print("=" * 70)

    print("\n[1/3] Carregando modelo de embedding...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print("[2/3] Conectando ao ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        col = client.get_collection(COLLECTION_NAME)
        print(f"      Coleção '{COLLECTION_NAME}' encontrada — {col.count()} chunks.")
    except Exception as e:
        print(f"      [ERRO] Coleção não encontrada: {e}")
        print("      Verifique COLLECTION_NAME e CHROMA_PATH no topo do script.")
        sys.exit(1)

    vs = Chroma(collection_name=COLLECTION_NAME, client=client, embedding_function=embeddings)

    print("[3/3] Carregando queries...\n")
    queries = []
    if DATASET_CSV:
        queries = carregar_queries_do_dataset(DATASET_CSV)
    if not queries:
        queries = QUERIES_EMBUTIDAS
        print(f"  Usando {len(queries)} queries embutidas.\n")

    todos_os_scores = inspecionar_scores(vs, queries, K)
    sugerir_threshold(todos_os_scores)


if __name__ == "__main__":
    main()
