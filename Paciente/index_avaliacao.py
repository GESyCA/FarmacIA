from langsmith import Client, evaluate
from langsmith.evaluation import LangChainStringEvaluator
from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do cliente LangSmith
client = Client()

# Configuração do modelo e prompt
llm = ChatOllama(
    model="Llama3.2:3b",
    temperature=0
)

# Template do prompt com uso de contexto
RAG_TEMPLATE = """
    Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.
    
    Se a pergunta estiver fora do escopo da bula ou a informação não for encontrada, informe que os dados não estão disponíveis na seção fornecida. Seja preciso e detalhado em suas respostas.
    
    Sua resposta deve iniciar com: "De acordo com a bula do medicamento..." e fornecer a resposta completa à pergunta, sem inventar nada.
    
    Passo a passo para responder a pergunta:
    1. Leia o nome do remédio fornecido.
    2. Leia o contexto.
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
    nome = Dramin B6
    
    Contexto:
    {context}
    
    Pergunta:
    {query}
    
    Resposta: 
    """

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

# Funções de predição do RAG
@traceable
def predict_rag_answer(example: dict):
    """Use this for answer evaluation"""
    chain = (
        RunnablePassthrough.assign(context=lambda _: example["context"])
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    response = chain.invoke({"query": example["query"], "context": example["context"]})
    return {"answer": response}

# Configuração do modelo Mistral
llm_judge = ChatOllama(
    model="Mistral",
    temperature=0
)

# Configuração dos avaliadores

# Avaliador de perguntas e respostas
qa_evaluator = [
    LangChainStringEvaluator(
        "cot_qa",
        config={"llm": llm_judge},
        prepare_data=lambda run, example: {
            "prediction": run.outputs["answer"],
            "reference": example.outputs["expected"],
            "input": example.inputs["query"],
        },
    )
]

# Avaliador de alucinação
answer_hallucination_evaluator = LangChainStringEvaluator(
    "labeled_score_string",
    config={
        "llm": llm_judge,
        "criteria": {
            "accuracy": """Is the Assistant's Answer grounded in the Ground Truth documentation? A score of [[1]] means that the
            Assistant answer contains is not at all based upon / grounded in the Groun Truth documentation. A score of [[5]] means
            that the Assistant answer contains some information (e.g., a hallucination) that is not captured in the Ground Truth
            documentation. A score of [[10]] means that the Assistant answer is fully based upon the in the Ground Truth documentation."""
        },
        "normalize_by": 10,
    },
    prepare_data=lambda run, example: {
        "prediction": run.outputs["answer"],
        "reference": example.inputs["context"],
        "input": example.inputs["query"],
    },
)

# Dataset de teste
dataset_name = "RAG_FarmacIA_Test"
test_cases = [
    {
        "query": "Qual a posologia do medicamento?",
        "context": "6. COMO DEVO USAR ESTE MEDICAMENTO? DRAMIN® B6 deve ser engolido com uma quantidade de água suficiente. DRAMIN® B6 pode ser tomado imediatamente antes ou durante as refeições.  Em caso de viagem, tomar a medicação de maneira preventiva com pelo menos meia hora de antecedência.  Posologia:   Adultos acima de 12 anos: um a dois comprimidos (50 a 100 mg de dimenidrinato), a cada quatro horas, não excedendo oito comprimidos (400 mg de dimenidrinato) em 24 horas. Na insuficiência hepática: Caso você tenha insuficiência hepática (fígado), avise seu médico, pois ele pode considerar reduzir a dose de DRAMIN® B6. Siga a orientação de seu médico, respeitando sempre os horários, as doses e a duração do tratamento. Não interrompa o tratamento sem o conhecimento do seu médico. Este medicamento não deve ser partido, aberto ou mastigado. ",
        "expected": "De acordo com a bula do medicamento Dramin: A posologia para adultos acima de 12 anos é de um a dois comprimidos (50 a 100 mg de dimenidrinato) a cada quatro horas, não excedendo oito comprimidos (400 mg de dimenidrinato) em 24 horas. Em caso de insuficiência hepática, o paciente deve informar ao médico, pois pode ser necessário ajustar a dose.",
    },
    {
        "query": "Quais as contraindicações do medicamento?",
        "context": "3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO? Você não deve tomar DRAMIN® B6 se tiver alergia ao dimenidrinato, à piridoxina ou aos outros componentes da fórmula. Pacientes com porfiria (distúrbio caracterizado por quantidades excessivas dos pigmentos porfirina no sangue e na urina) não devem tomar DRAMIN® B6. Este medicamento é contraindicado para menores de 12 anos.",
        "expected": "De acordo com a bula do medicamento Dramin: As contraindicações incluem: Alergia ao dimenidrinato, à piridoxina ou a outros componentes da fórmula Pacientes com porfiria, um distúrbio caracterizado por quantidades excessivas de porfirina no sangue e na urina. Uso por menores de 12 anos, para os quais o medicamento é contraindicado. Se houver dúvida, consulte sempre um médico antes de utilizar o medicamento.",
    },
    {
        "query": "Qual a melhor forma de conservar o medicamento?",
        "context": "5. ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO? Conserve o produto à temperatura ambiente (15°C a 30°C) e protegido da luz e da umidade. Número de lote e datas de fabricação e validade: vide embalagem.  Não use medicamento com o prazo de validade vencido. Guarde-o em sua embalagem original. DRAMIN® B6 é apresentado como comprimidos revestidos, de cor rosa, com vinco e a gravação DR B6 em uma de suas faces. Antes de usar, observe o aspecto do medicamento. Caso ele esteja no prazo de validade e você observe alguma mudança no aspecto, consulte o farmacêutico para saber se poderá utilizá-lo.  Todo medicamento deve ser mantido fora do alcance das crianças. ",
        "expected": "De acordo com a bula do medicamento Dramin: A melhor forma de conservar o medicamento é: Temperatura ambiente entre 15°C e 30°CMantê-lo protegido da luz e da umidade. Guardá-lo em sua embalagem original. Além disso, é importante: Não usar o medicamento com o prazo de validade vencido. Observar o aspecto do medicamento antes de utilizá-lo e, caso esteja dentro do prazo, mas com alteração no aspecto, consultar"
    },
]

inputs = [{"query": case["query"], "context": case["context"]} for case in test_cases]
outputs = [{"expected": case["expected"]} for case in test_cases]

# Cria o dataset
dataset = client.create_dataset(dataset_name, description="RAG QA FarmacIA Dataset")
client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)

# Avaliação
experiment_results = evaluate(
    predict_rag_answer,
    data=dataset_name, 
    evaluators=qa_evaluator, 
    experiment_prefix="rag-Teste-Completo-FarmacIA",  # Nome do experimento
    metadata={"variant": "Testes, Llama"},  # Metadados do experimento
)

# Resultado da avaliação
print(experiment_results)
