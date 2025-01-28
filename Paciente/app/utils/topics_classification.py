from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

def topic_classify(llm, query):
    
    # Títulos dos tópicos com descrições detalhadas
    section_titles = {
        "IDENTIFICAÇÃO DO MEDICAMENTO": "Informações básicas sobre o medicamento, como nome, fabricante, composição e forma farmacêutica.",
        "PARA QUE ESTE MEDICAMENTO É INDICADO?": "Indicações terapêuticas, ou seja, para quais condições ou doenças o medicamento é recomendado.",
        "COMO ESTE MEDICAMENTO FUNCIONA?": "Mecanismo de ação do medicamento, explicando como ele age no organismo para produzir o efeito desejado.",
        "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?": "Contraindicações, listando situações ou condições em que o medicamento não deve ser utilizado.",
        "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?": "Precauções e informações importantes que o paciente deve saber antes de iniciar o uso do medicamento.",
        "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?": "Instruções sobre armazenamento, incluindo temperatura, local e prazo de validade.",
        "COMO DEVO USAR ESTE MEDICAMENTO?": "Posologia e modo de uso, explicando como e quando o medicamento deve ser administrado.",
        "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?": "Orientações sobre o que fazer caso o paciente esqueça de tomar uma dose do medicamento.",
        "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?": "Efeitos colaterais ou reações adversas que o medicamento pode causar.",
        "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?": "Orientações sobre overdose, incluindo sintomas e o que fazer em caso de uso excessivo.",
    }

    # Template do prompt
    template = """
    Você é um assistente farmacêutico especializado em medicamentos. Abaixo estão os tópicos possíveis de uma bula de remédio, com suas respectivas descrições:

    {topics}

    Sua tarefa é identificar três dos tópicos (da lista acima) mais relevantes para a frase fornecida.
    
    Caso não encontre um tópico adequado, escolha o tópico que mais se aproxima do contexto da frase. Se a pergunta estiver fora do contexto de um Assistente farmacêutico, informe que sua resposta não está disponível. 
    
    Passo a passo (não precisa escrever os passos):
    1. Leia a frase fornecida.
    2. Identifique e escolha os tópicos listados que mais se encaixam no contexto da frase, considerando as descrições fornecidas.
    3. Informe somente os tópicos encontrados no passo 2, entre aspas duplas ("").

    ### Exemplos:
    Frase: "Quais são os efeitos colaterais do medicamento?"
    Tópicos mais relevantes: "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?"

    Frase: "Como devo armazenar o remédio?"
    Tópicos mais relevantes: "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?"

    Frase: "Para que serve este remédio?"
    Tópicos mais relevantes: "PARA QUE ESTE MEDICAMENTO É INDICADO?"

    Agora, classifique a frase fornecida:

    Frase: "{question}"
    Tópicos mais relevantes:
    """

    prompt = PromptTemplate(
        input_variables=["topics", "question"],
        template=template
    )

    # Função para identificar o tópico
    def identify_topic_with_model(question: str) -> str:
        # Formatando os tópicos e suas descrições como uma string
        topics_formatted = "\n".join(f"- {topic}: {description}" for topic, description in section_titles.items())
        
        # Criando a cadeia do LLM
        chain = (prompt | llm | StrOutputParser())
        
        # Gerando a resposta do modelo
        response = chain.invoke({"topics": topics_formatted, "question": question})
        return response.strip()

    matched_topic = identify_topic_with_model(query)
    print("Classificação do Tópico: ", matched_topic)
    # Regex para capturar o tópico entre aspas duplas
    pattern = r'["\'](.*?)["\']'
    result = re.findall(pattern, matched_topic)
    
    return result if result else None