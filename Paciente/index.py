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


nome_remedio = str(input("Digite o nome do remédio: "))
caminho_arquivo = f"bulas_pdf/bula_{nome_remedio.lower()}.pdf"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Inicializa o cliente ChromaDB com persistência local
chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
vectorstore = Chroma(collection_name="bulas", client=chroma_client, embedding_function=embeddings)

# Verifica se o medicamento já está no banco
bula_existe = bula_exists(nome_remedio)

if bula_existe:
    print(f"A bula de '{nome_remedio}' já está armazenada localmente.")
else:
    # Realiza o processo de download e adição da bula caso não exista no banco
    resultado = buscar_remedio(nome_remedio, 1)
    
    if resultado and resultado['status'] != 'not_found':
        pdf_buffer = resultado['pdf']['data']
        
        # Salva o PDF
        salvar_pdf(pdf_buffer, f'bula_{nome_remedio.lower()}.pdf')
        
        # Processa a bula
        vectorstore, sectioned_docs = processar_bula(caminho_arquivo, nome_remedio)
    else:
        print("Bula do Remédio não encontrada!")
        exit()


llm = ChatOllama(
    model = "llama3.2:3b",
    temperature=0.2
)

print("====== Assistente Farmacêutico - Chat ======")
while True:
    # Consulta
    query = input("Você: ")
    
    if query == "sair":
        print("Até mais!")
        break
    
    # Prompt
    RAG_TEMPLATE = """
    Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.
    
    Se a pergunta estiver fora do escopo da bula ou a informação não for encontrada, informe que os dados não estão disponíveis na seção fornecida. Seja preciso e detalhado em suas respostas.
    
    Sua resposta deve iniciar com: "De acordo com a bula do medicamento..." e fornecer a resposta completa à pergunta.
    
    Passo a passo para responder a pergunta:
    1. Leia o nome do remédio fornecido.
    2. Leia o contexto especifico e o contexto geral.
    3. Leia a pergunta.
    4. Responda à pergunta com base no contexto fornecido.
    5. Releia a resposta e verifique se inclui todos os detalhes relevantes do contexto para responder completamente à pergunta.

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

    # Cria uma instância de 'ChatPromptTemplate' e Permite que o template de prompt seja preenchido com diferentes valores de {contexto}, {pergunta}...
    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
    
    # Classifica o tópico
    topic_llm = topic_classify(llm, query)
    
    filtros = { "$and": [{"medicamento": nome_remedio.lower()}, {"section": topic_llm.upper()}]}
    context_llm = vectorstore.similarity_search(
        query="",  # Pode ser vazio, pois queremos filtrar por metadados, não por embeddings.
        filter=filtros
    )
    '''print("Tópico específico: ", context_llm)'''
    
    # Cadeia de Operações que processa a entrada e gera uma resposta
    chain = (
        RunnablePassthrough.assign(context=lambda input: format_docs(input["contexto"])) # Atribui o resultado de format_docs(input["contexto"]) a context
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    
    # Busca a similaridade
    docs = search_bula(nome_remedio, query)
    '''print(" BUSCA POR SIMILARIDADE : \n", docs, "\n\n")'''
    
    # Resposta
    print("Assistente: " + chain.invoke({"contexto": docs, "contexto_esp": context_llm,"pergunta": query, "medicamento": nome_remedio}) + "\n")