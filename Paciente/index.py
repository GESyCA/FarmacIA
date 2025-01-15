from utils.bulario import buscar_remedio, salvar_pdf, verificar_arquivo
from utils.process import processar_bula, format_docs
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from utils.vectorstore import bula_exists, search_bula
from utils.topics_classification import topic_classify
from langsmith import Client
from langsmith import traceable
from dotenv import load_dotenv
import streamlit as st

# Carregar variáveis de ambiente
load_dotenv()

# Setup do Streamlit
st.title("FarmacIA - Assistente Farmacêutico")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Inicializa o cliente ChromaDB com persistência local
chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
vectorstore = Chroma(collection_name="bulas", client=chroma_client, embedding_function=embeddings)

llm = ChatOllama(
    model = "llama3.2:3b",
    temperature=0
)

# Inicializar histórico
if "historico" not in st.session_state:
    st.session_state["historico"] = ""
    
# Entrada do nome do remédio
nome_remedio = st.text_input("Digite o nome do remédio:")

if nome_remedio:
    caminho_arquivo = f"bulas_pdf/bula_{nome_remedio.lower()}.pdf"
    bula_existe = bula_exists(nome_remedio)

    if bula_existe:
        st.info(f"A bula de '{nome_remedio}' já está armazenada localmente.")
    else:
        st.warning("Bula não encontrada localmente. Clique para baixar.")
        if st.button("Baixar Bula"):
            resultado = buscar_remedio(nome_remedio, 1)
            if resultado and resultado['status'] != 'not_found':
                pdf_buffer = resultado['pdf']['data']
                salvar_pdf(pdf_buffer, caminho_arquivo)
                vectorstore, _ = processar_bula(caminho_arquivo, nome_remedio)
                st.success("Bula processada e adicionada ao banco!")
            else:
                st.error("Bula do remédio não encontrada na ANVISA.")
                
caminho_arquivo = f"bulas_pdf/bula_{nome_remedio.lower()}.pdf"

# Entrada para perguntas ao assistente
pergunta = st.text_input("Pergunte algo sobre o medicamento:")

if pergunta:
    # Classifica o tópico e busca contexto
    topic_llm = topic_classify(llm, pergunta)
    context_list = []
    for topic in topic_llm:
        filtros = {"$and": [{"medicamento": nome_remedio.lower()}, {"section": topic.upper()}]}
        contexto = vectorstore.similarity_search(query="", filter=filtros)
        context_list.extend([doc.page_content for doc in contexto])
    
    context_llm = "".join(context_list) if context_list else "Sem contexto"
    
    # Prompt
    RAG_TEMPLATE = """
    Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.
    
    Se a pergunta estiver fora do escopo da bula ou a informação não for encontrada, informe que os dados não estão disponíveis na seção fornecida. Seja preciso e detalhado em suas respostas.
    
    Sua resposta deve iniciar com: "De acordo com a bula do medicamento..." e fornecer a resposta completa à pergunta.
    
    Converse de maneira natural e mantenha o contexto das interações anteriores. Aqui estão as conversas anteriores:

    {historico}

    Agora, continue a conversa.
    
    Passo a passo para responder a pergunta:
    1. Leia o nome do remédio fornecido.
    2. Leia o contexto especifico e o contexto geral.
    3. Leia a pergunta.
    4. Responda à pergunta com base no contexto fornecido.
    5. Releia a resposta e verifique se inclui todos os detalhes relevantes do contexto para responder completamente à pergunta.

    Siga os exemplos abaixo para responder às perguntas:
    ### Exemplo 1 ###
    Medicamento: Dramin
    Pergunta:
    "Quais as contraindicações do medicamento?"
    Resposta:
    "De acordo com a bula do medicamento, as contraindicações do medicamento DRAMIN B6 são as seguintes:

    * Não deve ser tomado por pacientes com alergia ao dimenidrinato, à piridoxina ou aos outros componentes da fórmula.
    * Pacientes com porfiria (distúrbio caracterizado por quantidades excessivas dos pigmentos porfirina no sangue e na urina) não devem tomar DRAMIN B6.      
    * Este medicamento é contraindicado para menores de 12 anos.

    Além disso, é importante lembrar que, caso você esqueça de tomar uma dose, ela deve ser tomada tão logo seja lembrada. No entanto, se estiver muito perto da administração da próxima dose, não a tome; tome somente a dose seguinte e continue com o esquema posológico regular. Não tome uma dose dupla para compensar a dose esquecida.

    É importante consultar um farmacêutico ou um médico ou cirurgião-dentista em caso de dúvidas sobre o uso do medicamento DRAMIN B6."
    
    ### Exemplo 2 ###
    Medicamento: Dramin
    Pergunta:
    "Me faça um Poema sobre o remédio"
    Resposta:
    "Somente posso responder perguntas relacionadas à bula do medicamento DRAMIN B6. Por favor, faça uma pergunta relevante sobre o medicamento para obter informações precisas e confiáveis."
    
    ### Fim dos Exemplos ###
    
    Medicamento:
    nome = {medicamento}
    
    Contexto especifico:
    {contexto_esp}
    
    Contexto Geral:
    {contexto}
    
    Pergunta:
    {pergunta}
    
    Resposta: 
    """
    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
    # Cadeia de Operações que processa a entrada e gera uma resposta
    chain = (
        RunnablePassthrough.assign(context=lambda input: format_docs(input["contexto"])) # Atribui o resultado de format_docs(input["contexto"]) a context
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    
    # Busca resposta
    docs = search_bula(nome_remedio, pergunta)
    resposta = chain.invoke({"contexto": docs, "contexto_esp": context_llm, "pergunta": pergunta, "medicamento": nome_remedio, "historico": st.session_state["historico"]})
    
    # Atualizar histórico
    historico_atual = f"Usuário: {pergunta}\nAssistente: {resposta}\n"
    st.session_state["historico"] += historico_atual
    
    # Exibir resposta
    st.markdown(f"**Assistente:** {resposta}")

# Exibir histórico
st.subheader("Histórico de Conversa")
st.text_area("Histórico", value=st.session_state["historico"], height=300)