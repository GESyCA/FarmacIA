from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import chromadb, re, os
from langchain_chroma import Chroma

# ---------------------------------------------------------------------------
# Mapeamento: título da seção → tipo normalizado (para filtros de intenção)
# ---------------------------------------------------------------------------
TIPO_SECAO_MAP = {
    "IDENTIFICAÇÃO DO MEDICAMENTO":                                              "identificacao",
    "PARA QUE ESTE MEDICAMENTO É INDICADO?":                                     "indicacao",
    "COMO ESTE MEDICAMENTO FUNCIONA?":                                            "mecanismo_acao",
    "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?":                                    "contraindicacao",
    "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?":                          "precaucao_interacao",
    "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?":             "armazenamento",
    "COMO DEVO USAR ESTE MEDICAMENTO?":                                           "posologia",
    "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?":          "dose_esquecida",
    "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?":                       "reacao_adversa",
    "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?": "superdose",
}

# ---------------------------------------------------------------------------
# Funções auxiliares de limpeza e extração de texto
# ---------------------------------------------------------------------------
def assign_metadata(texts, section_titles):
    """Atribui metadados de seção a documentos (mantida por compatibilidade)."""
    sectioned_docs = []
    current_section = None
    for doc in texts:
        for title in section_titles:
            if title in doc.page_content:
                current_section = title
                break
        metadata = {"section": current_section} if current_section else {}
        sectioned_docs.append(Document(page_content=doc.page_content, metadata=metadata))
    return sectioned_docs

def limpar_titulo(titulo):
    return re.sub(r"^\d+\.\s*", "", titulo).strip().upper()

def remover_referencias_entre_parenteses(texto: str) -> str:
    padrao = r"\((?:vide|ver)[^\)]*\)"
    return re.sub(padrao, "", texto, flags=re.IGNORECASE)

def cortar_apos_primeira_bula(texto: str) -> str:
    ocorrencias = [m.start() for m in re.finditer(r"IDENTIFICAÇÃO DO MEDICAMENTO", texto, flags=re.IGNORECASE)]
    if len(ocorrencias) > 1:
        return texto[:ocorrencias[1]].strip()
    return texto.strip()

def cortar_no_historico(texto: str) -> str:
    splitado = re.split(r"hist[oó]rico d[ae] altera[cç][aã]o de bula", texto, flags=re.IGNORECASE)
    return splitado[0].strip()

# ---------------------------------------------------------------------------
# Função principal de processamento de bula
# ---------------------------------------------------------------------------
def processar_bula(
    pdf_path: str,
    nome_remedio: str,
    embeddings=None,
    collection_name: str = "bulas",
    principio_ativo: str = "",
    tipo_bula: str = "bula_paciente",
):
    """
    Lê um PDF de bula, extrai seções, cria chunks e indexa no ChromaDB.

    Metadados gravados por chunk:
        medicamento        – nome do medicamento (ex: "amoxil")
        principio_ativo    – princípio ativo (ex: "amoxicilina tri-hidratada")
        tipo_bula          – "bula_paciente" | "bula_profissional"
        titulo_secao       – título completo da seção conforme a bula
        tipo_secao         – tipo normalizado (ex: "contraindicacao", "posologia")
        section_char_count – tamanho total da seção em caracteres
        indice_chunk       – índice do chunk dentro da sua seção (0-based)
        fonte              – nome do arquivo PDF de origem
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    section_titles = list(TIPO_SECAO_MAP.keys())

    # Limpeza do texto bruto
    cleaned_documents = []
    for doc in documents:
        cleaned_content = re.sub(r'\n{2,}', '\n', doc.page_content)
        cleaned_content = re.sub(r'\s{2,}', ' ', cleaned_content)
        cleaned_documents.append(Document(page_content=cleaned_content))

    full_text = "\n".join([doc.page_content for doc in cleaned_documents])
    full_text = remover_referencias_entre_parenteses(full_text)
    full_text = cortar_no_historico(full_text)
    full_text = cortar_apos_primeira_bula(full_text)

    # Detecta posições de cada seção no texto
    section_matches = []
    for title in section_titles:
        pattern = re.compile(rf"(?:\d+\.\s*)?{re.escape(title)}", flags=re.IGNORECASE)
        match = pattern.search(full_text)
        if match:
            section_matches.append((match.start(), title))
    section_matches.sort()

    # Extrai o texto completo de cada seção
    sections = []
    for i, (start_idx, title) in enumerate(section_matches):
        end_idx = section_matches[i + 1][0] if i + 1 < len(section_matches) else len(full_text)
        content = full_text[start_idx:end_idx].strip()
        sections.append((title, content))

    # -----------------------------------------------------------------------
    # Chunking por seção (garante que nenhum chunk misture seções diferentes)
    # Alvo: ~400-500 tokens ≈ 1600 chars | overlap: ~75 tokens ≈ 300 chars
    # -----------------------------------------------------------------------
    splitter = RecursiveCharacterTextSplitter(chunk_size=1600, chunk_overlap=300)

    fonte = os.path.basename(pdf_path)
    all_texts = []
    all_metadatas = []

    for titulo_secao, content in sections:
        tipo_secao = TIPO_SECAO_MAP.get(titulo_secao, "outro")
        section_char_count = len(content)

        # Divide apenas esta seção — sem risco de mistura
        section_doc = Document(page_content=content, metadata={})
        chunks = splitter.split_documents([section_doc])

        for indice_chunk, chunk in enumerate(chunks):
            all_texts.append(chunk.page_content)
            all_metadatas.append({
                "medicamento":        nome_remedio.lower(),
                "principio_ativo":    principio_ativo.lower(),
                "tipo_bula":          tipo_bula,
                "titulo_secao":       titulo_secao,
                "section":            titulo_secao,          # mantido por compatibilidade com pipelines existentes
                "tipo_secao":         tipo_secao,
                "section_char_count": section_char_count,
                "indice_chunk":       indice_chunk,
                "fonte":              fonte,
            })

    # Salva debug de chunks
    with open("chunks.txt", "w", encoding="utf-8") as f:
        for i, (text, meta) in enumerate(zip(all_texts, all_metadatas)):
            f.write(f"--- Chunk {i + 1} ---\n")
            f.write(f"Metadata: {meta}\n")
            f.write(text.strip() + "\n\n")

    # Permite injetar embeddings externos (para suportar múltiplos modelos de embedding)
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
    vectorstore = Chroma(
        collection_name=collection_name,
        client=chroma_client,
        embedding_function=embeddings
    )

    vectorstore.add_texts(
        all_texts,
        metadatas=all_metadatas,
        embeddings=embeddings
    )

    print(f"Bula processada com sucesso! ({len(all_texts)} chunks | {len(sections)} seções)")
    return vectorstore


# ---------------------------------------------------------------------------
# Utilitário
# ---------------------------------------------------------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)