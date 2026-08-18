"""
Script utilitário para limpar e re-indexar o banco ChromaDB.
Execute sempre que houver mudanças no utils/process.py que alterem metadados ou chunking.

Uso:
    uv run python utils/reset_chroma.py
    uv run python utils/reset_chroma.py --collection bulas_bge_m3 --embedding BAAI/bge-m3
"""
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from utils.process import processar_bula

CHROMA_PATH = "./chroma_bulas"
BULAS_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bulas_pdf")

# ---------------------------------------------------------------------------
# Lookup: nome do medicamento → princípio ativo
# Adicione novos medicamentos aqui ao processar novos PDFs.
# ---------------------------------------------------------------------------
PRINCIPIO_ATIVO_MAP = {
    "amoxil":        "amoxicilina tri-hidratada",
    "amoxicilina":   "amoxicilina tri-hidratada",
    "rivotril":      "clonazepam",
    "dramin":        "dimenidrinato",
    "paracetamol":   "paracetamol",
    "tylenol":       "paracetamol",
}

# ---------------------------------------------------------------------------
# Lookup: nome do medicamento → tipo de bula
# Padrão: "bula_paciente". Altere para "bula_profissional" quando aplicável.
# ---------------------------------------------------------------------------
TIPO_BULA_MAP = {
    # todos os PDFs atuais são bulas de paciente
}

def reset_and_reindex(collection_name: str = "bulas", embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
    print(f"=== Limpando coleção '{collection_name}' no ChromaDB ===")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(collection_name)
        print(f"  Coleção '{collection_name}' deletada com sucesso.")
    except Exception as e:
        print(f"  Coleção não existia ou erro ao deletar: {e}")

    print(f"\n=== Re-indexando PDFs ===")
    print(f"  Embedding : {embedding_model}")
    print(f"  Coleção   : {collection_name}\n")

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    bulas_path = Path(BULAS_DIR)
    if not bulas_path.is_dir():
        print(f"  [ERRO] Diretório de bulas não encontrado: {BULAS_DIR}")
        return

    pdfs = list(bulas_path.glob("*.pdf"))
    if not pdfs:
        print(f"  [AVISO] Nenhum PDF encontrado em: {BULAS_DIR}")
        return

    for pdf_file in pdfs:
        nome_remedio = pdf_file.stem.lower().removeprefix("bula_")
        principio_ativo = PRINCIPIO_ATIVO_MAP.get(nome_remedio, "")
        tipo_bula = TIPO_BULA_MAP.get(nome_remedio, "bula_paciente")

        print(f"  Processando: {pdf_file.name}")
        print(f"    medicamento     = {nome_remedio}")
        print(f"    principio_ativo = {principio_ativo or '(não mapeado)'}")
        print(f"    tipo_bula       = {tipo_bula}")
        try:
            processar_bula(
                str(pdf_file),
                nome_remedio,
                embeddings=embeddings,
                collection_name=collection_name,
                principio_ativo=principio_ativo,
                tipo_bula=tipo_bula,
            )
        except Exception as e:
            print(f"    ERRO: {e}")
        print()

    print("=== Re-indexação concluída! ===")
    print("Metadados gravados: medicamento, principio_ativo, tipo_bula,")
    print("  titulo_secao, tipo_secao, section_char_count, indice_chunk, fonte")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset e re-indexação do ChromaDB")
    parser.add_argument("--collection", default="bulas", help="Nome da coleção ChromaDB")
    parser.add_argument("--embedding", default="sentence-transformers/all-MiniLM-L6-v2", help="Modelo de embedding")
    args = parser.parse_args()

    resposta = input(
        f"Isso irá APAGAR e re-criar a coleção '{args.collection}' "
        f"com embedding '{args.embedding}'. Confirmar? [s/N]: "
    ).strip().lower()
    if resposta == "s":
        reset_and_reindex(collection_name=args.collection, embedding_model=args.embedding)
    else:
        print("Operação cancelada.")
