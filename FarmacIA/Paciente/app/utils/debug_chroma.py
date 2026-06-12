import sys, os
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv('../.env')
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path='./chroma_bulas')
vs = Chroma(collection_name='bulas', client=client, embedding_function=embeddings)

# Busca 3 chunks do Rivotril na seção de contraindicação
results = vs.similarity_search(
    query='contraindicação clonazepam',
    filter={"$and": [{"medicamento": "rivotril"}, {"tipo_secao": "contraindicacao"}]},
    k=3
)

for i, doc in enumerate(results):
    print(f"\n--- Chunk {i+1} ---")
    print(f"Metadata: {doc.metadata}")
    print(f"Conteúdo: {doc.page_content[:200]}...")
