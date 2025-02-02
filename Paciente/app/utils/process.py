from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
import chromadb, re
from langchain_chroma import Chroma

# Atribuir metadados
def assign_metadata(texts, section_titles):
    sectioned_docs = []
    current_section = None

    for doc in texts:
        for title in section_titles:
            # Verificar se o título da seção está presente no texto
            if title in doc.page_content:
                current_section = title
                break
        
        # Atribui o título da seção como metadado
        metadata = {"section": current_section} if current_section else {}
        
        # Adiciona o documento com os metadados
        sectioned_docs.append(Document(page_content=doc.page_content, metadata=metadata))
    
    return sectioned_docs
    
# Carregar a bula em PDF e dividir o texto
def processar_bula(pdf_path, nome_remedio):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Definindo títulos das seções
    section_titles = [
        "IDENTIFICAÇÃO DO MEDICAMENTO", "PARA QUE ESTE MEDICAMENTO É INDICADO?", "COMO ESTE MEDICAMENTO FUNCIONA?", "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?",
        "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?", "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?",
        "COMO DEVO USAR ESTE MEDICAMENTO?", "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?",
        "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?", "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?",
    ]

    # Limpeza inicial para remover quebras de linha extras
    cleaned_documents = []
    for doc in documents:
        cleaned_content = re.sub(r'\n{2,}', '\n', doc.page_content)  # Reduz múltiplas quebras de linha
        cleaned_content = re.sub(r'\s{2,}', ' ', cleaned_content)  # Reduz múltiplos espaços
        cleaned_documents.append(cleaned_content)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n"] + section_titles
    )
    
    # Dividir o texto
    texts = text_splitter.split_documents(documents)
    
    # Atribuir metadados
    sectioned_docs = assign_metadata(texts, section_titles) # Ex: "metadata={'section': 'POSOLOGIA'}"
    
    # Criando as embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Inicializa o cliente ChromaDB com persistência local
    chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
    vectorstore = Chroma(collection_name="bulas", client=chroma_client, embedding_function=embeddings)
    
    # Adicione as embeddings e documentos ao VectorStore
    vectorstore.add_texts([doc.page_content for doc in sectioned_docs], metadatas=[{"medicamento": nome_remedio.lower(), **doc.metadata} for doc in sectioned_docs], embeddings=embeddings)
    
    print("Bula processada com sucesso!")
    
    return vectorstore

# Converte os documentos em texto formatado
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)