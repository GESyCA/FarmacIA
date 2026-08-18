from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

def topic_classify(llm, query):
    
    # Títulos dos tópicos com descrições detalhadas
    section_titles = {
        "IDENTIFICAÇÃO DO MEDICAMENTO": "Informações básicas sobre o medicamento, como nome, fabricante, composição e forma farmacêutica.",
        "PARA QUE ESTE MEDICAMENTO É INDICADO?": "Indicações terapêuticas, ou seja, para quais condições ou doenças o medicamento é recomendado.",
        "COMO ESTE MEDICAMENTO FUNCIONA?": "Mecanismo e tempo de ação do medicamento, explicando em quanto tempo e como ele age no organismo para produzir o efeito desejado.",
        "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?": "Contraindicações, listando situações ou condições em que o medicamento não deve ser utilizado.",
        "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?": "Precauções e informações importantes que o paciente deve saber antes de iniciar o uso do medicamento.",
        "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?": "Instruções sobre armazenamento, incluindo temperatura, local e prazo de validade.",
        "COMO DEVO USAR ESTE MEDICAMENTO?": "Posologia (dosagem) e modo de uso, explicando como e quando o medicamento deve ser administrado.",
        "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?": "Orientações sobre o que fazer caso o paciente esqueça de tomar uma dose do medicamento.",
        "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?": "Reações adversas que o medicamento pode causar, como diarreia, enjoo e alergias, incluindo a frequência, gravidade e, às vezes, formas de amenizá-las.",
        "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?": "Orientações sobre overdose, incluindo sintomas e o que fazer em caso de uso excessivo.",
    }

    SYSTEM_PROMPT = """
    Você é um assistente farmacêutico especializado em medicamentos. Você vai receber do usuário, os tópicos possíveis de uma bula de remédio, com suas respectivas descrições.

    Sua tarefa é identificar os tópicos mais relevantes para a frase fornecida.
    
    Caso não encontre os tópicos adequados, escolha (entre os tópicos listados) os tópicos que mais se aproximam do contexto da frase. Se a pergunta estiver fora do contexto de um Assistente farmacêutico, informe que sua resposta não está disponível. 
    
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

    Frase: "Por que é recomendável tomar Amoxil® no início das refeições em caso de diarreia?"
    Tópicos mais relevantes: "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?" e "COMO DEVO USAR ESTE MEDICAMENTO?"

    """
    # Template do prompt
    PROMPT_TEMPLATE = """
    Classifique a frase fornecida com base nos tópicos listados abaixo.
    
    Tópicos: {topics}

    Frase: "{question}"
    
    Tópicos mais relevantes:
    """
    
    # Criando o prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", PROMPT_TEMPLATE)
    ])
    
    # Função para identificar o tópico
    def identify_topic_with_model(question: str) -> str:
        # Formatando os tópicos e suas descrições como uma string
        topics_formatted = "\n".join(f"- {topic}: {description}\n" for topic, description in section_titles.items())

        # Criando a cadeia do LLM
        chain = (prompt | llm | StrOutputParser())
        
        # Gerando a resposta do modelo
        response = chain.invoke({"topics": topics_formatted, "question": question})
        return response.strip()

    response = identify_topic_with_model(query)
    
    import unicodedata
    def normalizar(texto):
        # Converte para maiúsculo
        texto = texto.upper()
        # Remove acentos
        texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        # Remove caracteres especiais como ? e pontuações
        texto = re.sub(r'[^\w\s]', '', texto)
        # Remove múltiplos espaços
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    matched_sections = []
    
    # 1. Correspondência direta de substring normalizada
    normalized_response = normalizar(response)
    for title in section_titles:
        normalized_title = normalizar(title)
        if normalized_title in normalized_response:
            matched_sections.append(title)
            
    # 2. Fallback: se não achou por substring, tenta regex original de aspas
    if not matched_sections:
        matched_topic = ' "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?" ' + response
        pattern = r'["\'](.*?)["\']'
        raw_matches = re.findall(pattern, matched_topic)
        for match in raw_matches:
            match_upper = match.upper().strip()
            if match_upper in section_titles and match_upper not in matched_sections:
                matched_sections.append(match_upper)
                
    # Garante a presença do fallback padrão
    if "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?" not in matched_sections:
        matched_sections.insert(0, "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?")
        
    return matched_sections