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

def split_leaflets(texto: str) -> list:
    """
    Divide o texto completo em sub-bulas usando 'IDENTIFICAÇÃO DO MEDICAMENTO'.
    Retorna uma lista de tuplas (texto_sub_bula, is_profissional).
    """
    matches = list(re.finditer(r"IDENTIFICAÇÃO DO MEDICAMENTO", texto, flags=re.IGNORECASE))
    if not matches:
        is_prof = "profissional" in texto[:1500].lower() or "vps" in texto[:1500].lower()
        return [(texto.strip(), is_prof)]
        
    leaflets = []
    for i in range(len(matches)):
        start_idx = 0 if i == 0 else matches[i].start()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(texto)
        sub_text = texto[start_idx:end_idx].strip()
        
        # Para classificar, olha os primeiros 1500 caracteres a partir do início real da identificação
        match_relative_start = matches[i].start() - start_idx
        classification_text = sub_text[match_relative_start:match_relative_start + 1500].lower()
        is_prof = "profissional" in classification_text or "vps" in classification_text
        leaflets.append((sub_text, is_prof))
        
    return leaflets

def detectar_apresentacao(texto: str) -> str:
    """
    Detecta a forma farmacêutica (apresentação) da sub-bula com base nos primeiros 1500 caracteres.
    """
    prefix = texto[:1500].lower()
    
    if "comprimido sublingual" in prefix or "comprimidos sublinguais" in prefix:
        return "comprimido sublingual"
    elif "suspensão" in prefix or "suspensao" in prefix:
        return "suspensão oral"
    elif "cápsula" in prefix or "capsula" in prefix:
        return "cápsula"
    elif "comprimido" in prefix or "comprimidos" in prefix:
        return "comprimido"
    elif "gotas" in prefix:
        return "gotas"
    elif "solução oral" in prefix or "solucao oral" in prefix:
        return "solução oral"
    elif "injetável" in prefix or "injetavel" in prefix:
        return "injetável"
        
    return "geral"

def cortar_no_historico(texto: str) -> str:
    splitado = re.split(r"hist[oó]rico d[ae] altera[cç][aã]o de bula", texto, flags=re.IGNORECASE)
    return splitado[0].strip()

# ---------------------------------------------------------------------------
# Função principal de processamento de bula
def extrair_texto_pdf(pdf_path: str) -> str:
    """
    Extrai o texto de um PDF usando pymupdf4llm para obter markdown formatado,
    com fallbacks para fitz (PyMuPDF) e PyPDFLoader se falhar.
    """
    full_text = ""
    try:
        import pymupdf4llm
        full_text = pymupdf4llm.to_markdown(pdf_path)
    except Exception as e:
        print(f"Erro ao extrair markdown com pymupdf4llm: {e}. Usando fallback fitz/pypdf...")
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n\n"
            doc.close()
        except Exception as e_fitz:
            print(f"Erro no fallback fitz: {e_fitz}. Usando fallback PyPDFLoader...")
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            full_text = "\n\n".join(page.page_content for page in pages)
    return full_text


# ---------------------------------------------------------------------------
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
    Lê um PDF de bula ou carrega chunks determinísticos do grafo, cria chunks e indexa no ChromaDB.

    Metadados gravados por chunk:
        medicamento        – nome do medicamento (ex: "amoxil")
        principio_ativo    – princípio ativo (ex: "amoxicilina tri-hidratada")
        tipo_bula          – "bula_paciente" | "bula_profissional"
        titulo_secao       – título completo da seção conforme a bula
        tipo_secao         – tipo normalizado (ex: "contraindicacao", "posologia")
        section_char_count – tamanho total da seção em caracteres
        indice_chunk       – índice do chunk dentro da sua seção (0-based)
        fonte              – nome do arquivo PDF de origem
        apresentacao       – forma farmacêutica (ex: "cápsula", "suspensão oral", "geral")
    """
    import json
    import hashlib
    
    all_texts = []
    all_metadatas = []
    all_ids = []
    loaded_from_store = False
    
    # Determinar diretório do bulagraph_store dinamicamente
    possible_dirs = [
        "./instance/bulagraph_store",
        "./app/instance/bulagraph_store",
        "../instance/bulagraph_store",
        "../../instance/bulagraph_store",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "instance", "bulagraph_store"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "instance", "bulagraph_store")
    ]
    
    store_dir = None
    for p in possible_dirs:
        if os.path.exists(os.path.join(p, "chunks.jsonl")):
            store_dir = p
            break
            
    if store_dir:
        try:
            print(f"  [processar_bula] Carregando chunks determinísticos do grafo de: {store_dir}")
            chunks = []
            sections = {}
            leaflets = {}
            
            with open(os.path.join(store_dir, "sections.jsonl"), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        sections[item["id"]] = item
                        
            with open(os.path.join(store_dir, "leaflets.jsonl"), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        leaflets[item["id"]] = item
                        
            with open(os.path.join(store_dir, "chunks.jsonl"), 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunks.append(json.loads(line))
            
            # Encontrar as sub-bulas/leaflets do medicamento
            matched_leaflet_ids = []
            for leaf_id, leaf in leaflets.items():
                med_name = leaf.get("medication_name", "")
                if med_name.lower() == nome_remedio.lower():
                    matched_leaflet_ids.append(leaf_id)
            
            # Selecionar chunks desse medicamento
            matched_chunks = []
            for chunk in chunks:
                chunk_med = chunk.get("metadata", {}).get("medication", "").lower()
                if chunk.get("leaflet_id") in matched_leaflet_ids or chunk_med == nome_remedio.lower():
                    matched_chunks.append(chunk)
            
            if matched_chunks:
                for chunk in matched_chunks:
                    chunk_id = chunk["id"]
                    text = chunk["text"]
                    
                    sec_id = chunk.get("section_id")
                    sec = sections.get(sec_id, {})
                    sec_title = chunk.get("section_title") or sec.get("raw_title", "")
                    sec_char_count = len(sec.get("text", "")) if sec else len(text)
                    
                    leaf_id = chunk.get("leaflet_id")
                    leaf = leaflets.get(leaf_id, {})
                    active_ingredients = leaf.get("active_ingredients", [])
                    p_ativo = active_ingredients[0] if active_ingredients else principio_ativo
                    
                    ind_chunk = chunk.get("metadata", {}).get("chunk_index", 0)
                    src_pdf = chunk.get("source_pdf") or f"bula_{nome_remedio.lower()}.pdf"
                    apres = chunk.get("apresentacao") or "geral"
                    t_secao = TIPO_SECAO_MAP.get(sec_title, "outro")
                    
                    metadata = {
                        "id":                 chunk_id,
                        "chunk_id":           chunk_id,
                        "medicamento":        nome_remedio.lower(),
                        "principio_ativo":    p_ativo.lower(),
                        "tipo_bula":          tipo_bula,
                        "titulo_secao":       sec_title,
                        "section":            sec_title,
                        "tipo_secao":         t_secao,
                        "section_char_count": sec_char_count,
                        "indice_chunk":       ind_chunk,
                        "fonte":              src_pdf,
                        "apresentacao":       apres,
                    }
                    
                    all_texts.append(text)
                    all_metadatas.append(metadata)
                    all_ids.append(chunk_id)
                
                loaded_from_store = True
                print(f"  [processar_bula] Sucesso! Carregados {len(all_texts)} chunks do grafo para {nome_remedio}.")
        except Exception as store_err:
            print(f"  [AVISO] Erro ao carregar chunks do bulagraph_store: {store_err}. Usando processamento de PDF...")
            
    if not loaded_from_store:
        from langchain_text_splitters import MarkdownTextSplitter
        
        # Extrai o texto completo já formatado como Markdown (ou texto puro de fallback)
        full_text = extrair_texto_pdf(pdf_path)
        
        # Divide o texto completo em sub-bulas
        leaflets = split_leaflets(full_text)
        
        # Filtra apenas bulas de paciente (VP)
        patient_leaflets = [l for l, is_prof in leaflets if not is_prof]
        if not patient_leaflets:
            # Fallback se não encontrar nenhuma com classificação VP
            patient_leaflets = [l for l, _ in leaflets]
            
        section_titles = list(TIPO_SECAO_MAP.keys())
        splitter = MarkdownTextSplitter(chunk_size=1600, chunk_overlap=300)
        fonte = os.path.basename(pdf_path)
        
        for sub_text in patient_leaflets:
            # Limpezas específicas para cada sub-bula (para evitar descartar sub-bulas subsequentes)
            sub_text = remover_referencias_entre_parenteses(sub_text)
            sub_text = cortar_no_historico(sub_text)
            
            apresentacao = detectar_apresentacao(sub_text)
            
            # Detecta posições de cada seção no sub-texto
            section_matches = []
            for title in section_titles:
                words = title.split()
                pattern_str = r"(?:\d+\.\s*)?" + r"\s+".join(re.escape(w) for w in words)
                pattern = re.compile(pattern_str, flags=re.IGNORECASE)
                match = pattern.search(sub_text)
                if match:
                    section_matches.append((match.start(), title))
            section_matches.sort()

            # Extrai o texto completo de cada seção
            sections = []
            for i, (start_idx, title) in enumerate(section_matches):
                end_idx = section_matches[i + 1][0] if i + 1 < len(section_matches) else len(sub_text)
                content = sub_text[start_idx:end_idx].strip()
                sections.append((title, content))

            for titulo_secao, content in sections:
                tipo_secao = TIPO_SECAO_MAP.get(titulo_secao, "outro")
                section_char_count = len(content)

                # Divide apenas esta seção — sem risco de mistura
                section_doc = Document(page_content=content, metadata={})
                chunks = splitter.split_documents([section_doc])

                for indice_chunk, chunk in enumerate(chunks):
                    # Gera um ID determinístico baseado no hash MD5 do texto
                    text_hash = hashlib.md5(chunk.page_content.encode('utf-8')).hexdigest()[:12]
                    chunk_id = f"chunk_{text_hash}"
                    
                    all_texts.append(chunk.page_content)
                    all_metadatas.append({
                        "id":                 chunk_id,
                        "chunk_id":           chunk_id,
                        "medicamento":        nome_remedio.lower(),
                        "principio_ativo":    principio_ativo.lower(),
                        "tipo_bula":          tipo_bula,
                        "titulo_secao":       titulo_secao,
                        "section":            titulo_secao,          # mantido por compatibilidade
                        "tipo_secao":         tipo_secao,
                        "section_char_count": section_char_count,
                        "indice_chunk":       indice_chunk,
                        "fonte":              fonte,
                        "apresentacao":       apresentacao,
                    })
                    all_ids.append(chunk_id)

    # Salva debug de chunks
    paciente_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    chunks_txt_path = os.path.join(paciente_root, "chunks.txt")
    with open(chunks_txt_path, "w", encoding="utf-8") as f:
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
        ids=all_ids,
        embeddings=embeddings
    )

    print(f"Bula processada com sucesso! ({len(all_texts)} chunks)")
    return vectorstore


# ---------------------------------------------------------------------------
# Utilitário
# ---------------------------------------------------------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)