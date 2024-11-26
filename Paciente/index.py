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

    # Cria uma instância de 'ChatPromptTemplate' e Permite que o template de prompt seja preenchido com diferentes valores de {contexto}, {pergunta}...
    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
    
    # Classifica o tópico
    topic_llm = topic_classify(llm, query)
    if topic_llm:
        filtros = { "$and": [{"medicamento": nome_remedio.lower()}, {"section": topic_llm.upper()}]}
        context_llm = vectorstore.similarity_search(
            query="", 
            filter=filtros
        )
        '''print("Tópico específico: ", context_llm)'''
    else:
        context_llm = "Sem contexto"
    
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