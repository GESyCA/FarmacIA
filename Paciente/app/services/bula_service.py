from utils.bulario import buscar_remedio, salvar_pdf
from utils.process import processar_bula
from utils.vectorstore import bula_exists
from utils.topics_classification import topic_classify
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
vectorstore = Chroma(collection_name="bulas", client=chroma_client, embedding_function=embeddings)

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)

def buscar_bula(nome_remedio):
    caminho_arquivo = f"bulas_pdf/bula_{nome_remedio.lower()}.pdf"
    bula_existe = bula_exists(nome_remedio)

    if bula_existe:
        return {"status": "exists", "message": f"A bula de '{nome_remedio}' já está armazenada localmente."}
    else:
        resultado = buscar_remedio(nome_remedio, 1)
        if resultado and resultado['status'] != 'not_found':
            pdf_buffer = resultado['pdf']['data']
            salvar_pdf(pdf_buffer, f'bula_{nome_remedio.lower()}.pdf')
            processar_bula(caminho_arquivo, nome_remedio)
            return {"status": "success", "message": "Bula processada e adicionada ao banco!"}
        else:
            return {"status": "error", "message": "Bula do remédio não encontrada na ANVISA."}

def perguntar_sobre_bula(nome_remedio, pergunta):
    caminho_arquivo = f"bulas_pdf/bula_{nome_remedio.lower()}.pdf"
    
    topic_llm = topic_classify(llm, pergunta)
    context_list = []
    for topic in topic_llm:
        filtros = {"$and": [{"medicamento": nome_remedio.lower()}, {"section": topic.upper()}]}
        contexto = vectorstore.similarity_search(query="", filter=filtros)
        context_list.extend([doc.page_content for doc in contexto])
    
    context_llm = "".join(context_list) if context_list else "Sem contexto"
    
    SYSTEM_PROMPT = """
Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.

Se a pergunta estiver fora do escopo da bula ou a informação não for encontrada, informe que os dados não estão disponíveis na seção fornecida. Seja preciso e detalhado em suas respostas.

Sua resposta deve iniciar com: "De acordo com a bula do medicamento..." e fornecer a resposta completa à pergunta.

Caso a pergunta não tenha nenhuma relação com a bula ou o medicamento, responda de forma educada que não pode fornecer informações sobre o assunto.

Converse de maneira natural e mantenha o contexto das interações anteriores.
"""
    RAG_TEMPLATE = """
Aqui estão as conversas anteriores:

{historico}

Agora, continue a conversa.

Passo a passo para responder a pergunta:
1. Leia o nome do remédio fornecido.
2. Leia o contexto.
3. Leia a pergunta.
4. Responda à pergunta com base no contexto fornecido.
5. Releia a resposta e verifique se inclui todos os detalhes relevantes do contexto para responder completamente à pergunta.

Medicamento:
nome = {medicamento}

Contexto:
{contexto}

Pergunta:
{pergunta}

Resposta:
"""
    
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", RAG_TEMPLATE)
    ])
    
    chain = (
        rag_prompt
        | llm
        | StrOutputParser()
    )
    
    resposta = chain.invoke({"contexto": context_llm, "pergunta": pergunta, "medicamento": nome_remedio, "historico": ""})
    
    return resposta