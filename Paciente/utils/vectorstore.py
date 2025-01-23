import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# Inicializa o cliente ChromaDB com persistência local
chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
vectorstore = Chroma(collection_name="bulas", client=chroma_client, embedding_function=embeddings)

# Verifica se a bula de um medicamento já está armazenada localmente
def bula_exists(nome_remedio):
    documentos_existentes = vectorstore.similarity_search(query="", filter={"medicamento": nome_remedio.lower()})
    return (documentos_existentes != [])

# Busca por similaridade na bula específica
def search_bula(nome_remedio, query):
    return vectorstore.similarity_search(query=query, filter={"medicamento": nome_remedio.lower()})
