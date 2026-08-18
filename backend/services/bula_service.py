from utils.process import processar_bula
from utils.vectorstore import bula_exists
from utils.topics_classification import topic_classify
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import chromadb, os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
vectorstore = Chroma(collection_name="bulas", client=chroma_client, embedding_function=embeddings)

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
# )

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
)

def formatar_historico(historico_db):
    """Converte o histórico do formato do DB para o formato LangChain."""
    mensagens = []
    for msg in historico_db:
        if msg['role'] == 'user':
            mensagens.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'llm':
            mensagens.append(AIMessage(content=msg['content']))
    return mensagens

def perguntar_sobre_bula(nome_remedio, pergunta, historico_conversa, return_metadata=False):
    # Obtém o diretório onde o script atual está localizado
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BULAS_PDF_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "bulas_pdf"))
    caminho_arquivo = os.path.join(BULAS_PDF_DIR, f"bula_{nome_remedio.lower()}.pdf")
    
    # Processa a bula se não existir no BD vetorial
    if not bula_exists(nome_remedio):
        processar_bula(caminho_arquivo, nome_remedio)

    from services.pipelines import PipelineFactory
    pipeline = PipelineFactory.get_pipeline("standard_rag")
    
    return pipeline.execute(
        nome_remedio=nome_remedio,
        pergunta=pergunta,
        historico_conversa=historico_conversa,
        llm=llm,
        vectorstore=vectorstore,
        return_metadata=return_metadata
    )

def topicos_bula(nome_remedio, pergunta):
    # Obtém o diretório onde o script atual está localizado
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BULAS_PDF_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "bulas_pdf"))
    caminho_arquivo = os.path.join(BULAS_PDF_DIR, f"bula_{nome_remedio.lower()}.pdf")
    
    if not bula_exists(nome_remedio):
        processar_bula(caminho_arquivo, nome_remedio)
    
    topic_llm = topic_classify(llm, pergunta)
    return topic_llm