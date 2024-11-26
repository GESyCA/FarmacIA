from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

def topic_classify(llm, query):
    
    # Títulos dos tópicos
    section_titles = [
        "IDENTIFICAÇÃO DO MEDICAMENTO", 
        "PARA QUE ESTE MEDICAMENTO É INDICADO?", 
        "COMO ESTE MEDICAMENTO FUNCIONA?", 
        "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?",
        "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?", 
        "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?",
        "COMO DEVO USAR ESTE MEDICAMENTO?", 
        "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?",
        "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?", 
        "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?",
    ]

    # Template do prompt
    template = """
    Você é um assistente farmacêutico especializado em medicamentos. Abaixo estão os tópicos possíveis de uma bula de remédio:

    {topics}

    Sua tarefa é identificar o tópico (da lista acima) mais relevante para a frase fornecida. Escolha apenas um dos tópicos listados.
    
    Caso não encontre um tópico adequado, escolha o tópico que mais se aproxima do contexto da frase. Se a pergunta estiver fora do contexto de um Assistente farmacêutico, informe que sua resposta não está disponível. 
    
    Passo a passo:
    1. Leia a frase fornecida.
    2. Identifique e escolha o tópico listado que mais se encaixa no contexto da frase.
    3. Informe o tópico encontrado no passo 2.

    ### Exemplos:
    Frase: "Quais são os efeitos colaterais do medicamento?"
    Tópico mais relevante: "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?"

    Frase: "Como devo armazenar o remédio?"
    Tópico mais relevante: "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?"

    Frase: "Para que serve este remédio?"
    Tópico mais relevante: "PARA QUE ESTE MEDICAMENTO É INDICADO?"

    Agora, classifique a frase fornecida:

    Frase: "{question}"
    Tópico mais relevante:
    """

    prompt = PromptTemplate(
        input_variables=["topics", "question"],
        template=template
    )

    # Função para identificar o tópico
    def identify_topic_with_model(question: str) -> str:
        """
        Pergunta ao modelo qual é o tópico mais relevante para a pergunta fornecida.

        Args:
            question (str): A pergunta feita pelo usuário.

        Returns:
            str: O título do tópico mais relevante.
        """
        # Formatando os tópicos como uma string
        topics_formatted = "\n".join(f"- {topic}" for topic in section_titles)
        
        # Criando a cadeia do LLM
        chain = (prompt | llm | StrOutputParser())
        
        # Gerando a resposta do modelo
        response = chain.invoke({"topics": topics_formatted, "question": question})
        return response.strip()

    matched_topic = identify_topic_with_model(query)
    
    # Regex para capturar o tópico entre aspas duplas
    pattern = r'Tópico mais relevante:\s*"([^"]+)"'
    result = re.search(pattern, matched_topic)
    
    return result.group(1) if result else None