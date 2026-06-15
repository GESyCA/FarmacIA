import os
import time
import json
import re
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from utils.vectorstore import bula_exists
from utils.process import processar_bula
from utils.topics_classification import topic_classify
from bulagraph.formatter import SAFETY_NOTE, SEEK_PROFESSIONAL_NOTE

def apply_safety_note(pergunta: str, resposta: str) -> str:
    high_risk_keywords = ["gravid", "lacta", "pediatr", "crianc", "bebe", "idos", "contraindic", "interac", "superdos", "overdose", "renal", "hepatic", "figado", "rim"]
    safety_note = SAFETY_NOTE
    if any(kw in pergunta.lower() for kw in high_risk_keywords):
        safety_note += SEEK_PROFESSIONAL_NOTE
    return f"{resposta}\n\n---\n*{safety_note}*"

def extract_answer(raw_output: str) -> str:
    if not isinstance(raw_output, str):
        return raw_output
    # Remove blocos de raciocínio (<think>...</think>)
    cleaned = re.sub(r"<think>.*?</think>", "", raw_output, flags=re.DOTALL | re.IGNORECASE)
    # Tenta parsear JSON diretamente
    try:
        data = json.loads(cleaned)
        return data.get("answer", "").strip()
    except json.JSONDecodeError:
        pass
    # Fallback: tenta encontrar um objeto JSON dentro do texto (ex: { "answer": "..." })
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return data.get("answer", "").strip()
        except json.JSONDecodeError:
            pass
    # Último fallback: retorna o texto limpo
    return cleaned.strip()


SECOES_DISPONIVEIS = {
    "IDENTIFICAÇÃO DO MEDICAMENTO": "Informações básicas sobre o medicamento, como nome, fabricante, composição e forma farmacêutica.",
    "PARA QUE ESTE MEDICAMENTO É INDICADO?": "Indicações terapêuticas, ou seja, para quais condições ou doenças o medicamento é recomendado.",
    "COMO ESTE MEDICAMENTO FUNCIONA?": "Mecanismo e tempo de ação do medicamento, explicando em quanto tempo e como ele age no organismo para produzir o efeito desejado.",
    "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?": "Contraindicações, listando situações ou condições em que o medicamento não deve ser utilizado.",
    "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?": "Precauções e informações importantes que o paciente deve saber antes de iniciar o uso do medicamento.",
    "ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?": "Instruções sobre armazenamento, incluindo temperatura, local e prazo de validade.",
    "COMO DEVO USAR ESTE MEDICAMENTO?": "Posologia (dosagem) e modo de uso, explicando como e quando o medicamento deve ser administrado.",
    "O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?": "Orientações sobre o que fazer caso o paciente esqueça de tomar uma dose do medicamento.",
    "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?": "Reações adversas que o medicamento pode causar, como diarreia, enjoo e alergias, incluindo a frequência e gravidade.",
    "O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?": "Orientações sobre overdose, incluindo sintomas e o que fazer em caso de uso excessivo."
}

def _search_with_threshold(vectorstore, query, filter_dict, k, threshold=None, min_chunks=1):
    """
    Wrapper de similarity_search com filtragem opcional por limiar de relevância.

    Se threshold=None, comportamento idêntico ao similarity_search padrão (k fixo).
    Quando ativado, retorna apenas docs com score >= threshold, garantindo ao menos
    `min_chunks` resultados para evitar contexto vazio.

    Os scores do LangChain/Chroma são relevância (0–1, maior = mais similar).
    """
    if threshold is None:
        return vectorstore.similarity_search(query=query, filter=filter_dict, k=k)

    pairs = vectorstore.similarity_search_with_relevance_scores(
        query=query, filter=filter_dict, k=k
    )

    above = [doc for doc, score in pairs if score >= threshold]

    if len(above) < min_chunks and pairs:
        # Fallback: garante min_chunks do topo mesmo abaixo do limiar
        above = [doc for doc, _ in pairs[:min_chunks]]

    return above


def formatar_historico(historico_db):
    """Converte o histórico do formato do DB para o formato LangChain."""
    mensagens = []
    for msg in historico_db:
        if msg['role'] == 'user':
            mensagens.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'llm':
            mensagens.append(AIMessage(content=msg['content']))
    return mensagens

class PipelineFactory:
    @staticmethod
    def get_pipeline(pipeline_type):
        if pipeline_type == "standard_rag":
            return StandardRAGPipeline()
        elif pipeline_type == "agentic_rag":
            return AgenticRAGPipeline()
        elif pipeline_type == "hybrid_agentic_rag":
            return HybridAgenticRAGPipeline()
        elif pipeline_type == "fusion_rag":
            return FusionRAGPipeline()
        elif pipeline_type == "graph_rag":
            return GraphRAGPipeline()
        elif pipeline_type == "naive_rag":
            return NaiveRAGPipeline()
        else:
            raise ValueError(f"Pipeline desconhecido: {pipeline_type}")


class BasePipeline:
    def execute(self, nome_remedio, pergunta, historico_conversa, llm, vectorstore, return_metadata=False):
        raise NotImplementedError("Implemente o método execute.")

class NaiveRAGPipeline(BasePipeline):
    def execute(self, nome_remedio, pergunta, historico_conversa, llm, vectorstore,
                return_metadata=False, similarity_threshold=None, min_chunks=1):
        
        # 1. Recuperação (Retrieval)
        start_retrieval = time.time()
        
        # Faz uma consulta vetorial buscando a pergunta em toda a bula (sem filtro de seção)
        contexto_docs = _search_with_threshold(
            vectorstore=vectorstore,
            query=pergunta,
            filter_dict={
                "medicamento": nome_remedio.lower()
            },
            k=15,
            threshold=similarity_threshold,
            min_chunks=min_chunks,
        )
        context_list = [doc.page_content for doc in contexto_docs]

        # Busca obrigatória por identificação
        identificacao_docs = vectorstore.similarity_search(
            query="", 
            filter={"$and": [{"medicamento": nome_remedio.lower()}, {"section": "IDENTIFICAÇÃO DO MEDICAMENTO"}]}
        )
        identificacao_medicamento = "\n".join([doc.page_content for doc in identificacao_docs])

        end_retrieval = time.time()
        
        # 2. Geração (Inference)
        start_inference = time.time()
        
        context_llm = "\n".join(context_list) if context_list else "Sem contexto específico encontrado."

        SYSTEM_PROMPT = """Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.

Regras fundamentais:
1. Toda resposta DEVE ser estritamente fundamentada no contexto fornecido. Não invente nenhuma informação.
2. Se o contexto não contiver nenhuma informação relevante para responder a pelo menos parte da pergunta, use para a resposta final: "Na bula consultada de {medicamento}, não constam informações sobre essa pergunta."
3. Sua resposta final DEVE iniciar obrigatoriamente seguindo este padrão exato:
   "De acordo com a bula do medicamento {medicamento}, consta a seguinte informação: "
4. Não faça diagnósticos ou prescrições. Mantenha um tom profissional, clínico e objetivo.
5. Escreva a sua resposta diretamente em formato de texto simples, sem utilizar formatos estruturados como JSON ou XML."""
        
        RAG_TEMPLATE = """
        Passo a passo para responder a pergunta:
        1. Leia o nome do remédio e identificação fornecidas.
        2. Leia o contexto.
        3. Leia a pergunta.
        4. Responda à pergunta de forma clara e objetiva com base no contexto fornecido.
        5. Releia a resposta e verifique se inclui todos os detalhes relevantes do contexto para responder completamente à pergunta.

        Medicamento:
        nome = {medicamento}

        Identificação do medicamento:
        {identificacao_medicamento}

        Contexto:
        {contexto}

        Pergunta:
        {pergunta}

        Resposta:
        """

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", RAG_TEMPLATE),
        ])
        
        historico_formatado_lc = formatar_historico(historico_conversa)
        
        chain = (rag_prompt | llm | StrOutputParser())
        
        resposta = chain.invoke({
            "medicamento": nome_remedio,
            "contexto": context_llm, 
            "identificacao_medicamento": identificacao_medicamento,
            "pergunta": pergunta,
            "chat_history": historico_formatado_lc
        })
        
        end_inference = time.time()
        
        resposta_limpa = extract_answer(resposta)
        resposta_final = apply_safety_note(pergunta, resposta_limpa)

        if return_metadata:
            chunk_ids = [
                doc.metadata.get("id") or doc.metadata.get("chunk_id", "")
                for doc in contexto_docs
            ]
            metadata = {
                "tempo_recuperacao": round(end_retrieval - start_retrieval, 3),
                "tempo_inferencia": round(end_inference - start_inference, 3),
                "secoes_recuperadas": ["TODAS (Naive)"],
                "chunk_ids_recuperados": chunk_ids, 
                "textos_recuperados": context_list, 
                "resposta_crua": resposta
            }
            return resposta_final, metadata
            
        return resposta_final

class StandardRAGPipeline(BasePipeline):
    def execute(self, nome_remedio, pergunta, historico_conversa, llm, vectorstore,
                return_metadata=False, similarity_threshold=None, min_chunks=1):
        
        # 1. Recuperação (Retrieval)
        start_retrieval = time.time()
        
        topic_llm = topic_classify(llm, pergunta)
        context_list = []
        secoes_recuperadas = []
        contexto_docs = []  # inicializado aqui para garantir referência no metadata
        
        if topic_llm:
            secoes_recuperadas = [topic.upper() for topic in topic_llm if topic.upper() in SECOES_DISPONIVEIS]
            
            # Faz uma única consulta vetorial buscando a pergunta DENTRO das seções classificadas
            contexto_docs = _search_with_threshold(
                vectorstore=vectorstore,
                query=pergunta,
                filter_dict={
                    "$and": [
                        {"medicamento": nome_remedio.lower()},
                        {"section": {"$in": secoes_recuperadas}}
                    ]
                },
                k=15,
                threshold=similarity_threshold,
                min_chunks=min_chunks,
            )
            context_list.extend([doc.page_content for doc in contexto_docs])

        # Busca obrigatória por identificação
        identificacao_docs = vectorstore.similarity_search(
            query="", 
            filter={"$and": [{"medicamento": nome_remedio.lower()}, {"section": "IDENTIFICAÇÃO DO MEDICAMENTO"}]}
        )
        identificacao_medicamento = "\n".join([doc.page_content for doc in identificacao_docs])

        end_retrieval = time.time()
        
        # 2. Geração (Inference)
        start_inference = time.time()
        
        context_llm = "\n".join(context_list) if context_list else "Sem contexto específico encontrado."

        SYSTEM_PROMPT = """Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.

Regras fundamentais:
1. Toda resposta DEVE ser estritamente fundamentada no contexto fornecido. Não invente nenhuma informação.
2. Se o contexto não contiver nenhuma informação relevante para responder a pelo menos parte da pergunta, use para a resposta final: "Na bula consultada de {medicamento}, não constam informações sobre essa pergunta."
3. Sua resposta final DEVE iniciar obrigatoriamente seguindo este padrão exato:
   "De acordo com a bula do medicamento {medicamento}, consta a seguinte informação: "
4. Não faça diagnósticos ou prescrições. Mantenha um tom profissional, clínico e objetivo.
5. Escreva a sua resposta diretamente em formato de texto simples, sem utilizar formatos estruturados como JSON ou XML."""
        
        RAG_TEMPLATE = """
        Passo a passo para responder a pergunta:
        1. Leia o nome do remédio e identificação fornecidas.
        2. Leia o contexto.
        3. Leia a pergunta.
        4. Responda à pergunta de forma clara e objetiva com base no contexto fornecido.
        5. Releia a resposta e verifique se inclui todos os detalhes relevantes do contexto para responder completamente à pergunta.

        Medicamento:
        nome = {medicamento}

        Identificação do medicamento:
        {identificacao_medicamento}

        Contexto:
        {contexto}

        Pergunta:
        {pergunta}

        Resposta:
        """

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", RAG_TEMPLATE),
        ])
        
        historico_formatado_lc = formatar_historico(historico_conversa)
        
        chain = (rag_prompt | llm | StrOutputParser())
        
        resposta = chain.invoke({
            "medicamento": nome_remedio,
            "contexto": context_llm, 
            "identificacao_medicamento": identificacao_medicamento,
            "pergunta": pergunta,
            "chat_history": historico_formatado_lc
        })
        
        end_inference = time.time()
        
        resposta_limpa = extract_answer(resposta)
        resposta_final = apply_safety_note(pergunta, resposta_limpa)

        if return_metadata:
            chunk_ids = [
                doc.metadata.get("id") or doc.metadata.get("chunk_id", "")
                for doc in contexto_docs
            ]
            metadata = {
                "tempo_recuperacao": round(end_retrieval - start_retrieval, 3),
                "tempo_inferencia": round(end_inference - start_inference, 3),
                "secoes_recuperadas": secoes_recuperadas,
                "chunk_ids_recuperados": chunk_ids, "textos_recuperados": [doc.page_content for doc in (contexto_docs if "contexto_docs" in locals() else (reranked if "reranked" in locals() else []))], 
                "resposta_crua": resposta
            }
            return resposta_final, metadata
            
        return resposta_final



class AgenticRAGPipeline(BasePipeline):
    def execute(self, nome_remedio, pergunta, historico_conversa, llm, vectorstore,
                return_metadata=False, similarity_threshold=None, min_chunks=1):
        start_total = time.time()
        
        # ETAPA 1: O Agente analisa a pergunta e decide QUAIS e QUANTAS seções consultar
        PLANNING_PROMPT = """
        Você é um agente planejador de busca farmacêutica.
        Sua tarefa é analisar a pergunta de um paciente e decidir quais seções da bula do medicamento '{medicamento}' devem ser consultadas para responder à pergunta de forma completa e segura.
        Você pode escolher uma ou mais seções da lista abaixo. Escolha apenas as seções estritamente necessárias.

        Seções disponíveis:
        {secoes_disponiveis}

        Pergunta do Paciente:
        "{pergunta}"

        Responda obrigatoriamente em formato JSON estruturado contendo a lista das seções escolhidas. Não escreva mais nada além do JSON.
        Exemplo de resposta:
        {{
            "secoes": ["COMO DEVO USAR ESTE MEDICAMENTO?", "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?"]
        }}
        """

        prompt_plan = PromptTemplate.from_template(PLANNING_PROMPT)
        chain_plan = prompt_plan | llm | StrOutputParser()
        
        t0_plan = time.time()
        planejamento_bruto = chain_plan.invoke({
            "medicamento": nome_remedio,
            "secoes_disponiveis": "\n".join([f"- {s}" for s in SECOES_DISPONIVEIS.keys()]),
            "pergunta": pergunta
        })
        t1_plan = time.time()
        
        # print(f"    [Agentic] Planejamento bruto:\n{planejamento_bruto}")
        
        # Parsing das seções escolhidas pelo Agente
        try:
            # Limpa possíveis blocos de código markdown do JSON
            json_str = planejamento_bruto.replace("```json", "").replace("```", "").strip()
            dados = json.loads(json_str)
            secoes_escolhidas = [s.upper() for s in dados.get("secoes", []) if s.upper() in SECOES_DISPONIVEIS]
        except Exception as e:
            print(f"    [Agentic] Falha no parsing do JSON: {e}")
            # Fallback caso o JSON falhe
            secoes_escolhidas = ["O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?"]
            
        print(f"    [Agentic] Seções escolhidas: {secoes_escolhidas}")

        # Se o agente não escolheu nada, coloca uma de fallback
        if not secoes_escolhidas:
            secoes_escolhidas = ["IDENTIFICAÇÃO DO MEDICAMENTO"]

        # ETAPA 2: Recuperação (Retrieval) no ChromaDB usando a pergunta e o filtro das seções planejadas
        t0_retrieval = time.time()
        
        contexto_docs = _search_with_threshold(
            vectorstore=vectorstore,
            query=pergunta,
            filter_dict={
                "$and": [
                    {"medicamento": nome_remedio.lower()},
                    {"section": {"$in": secoes_escolhidas}}
                ]
            },
            k=15,
            threshold=similarity_threshold,
            min_chunks=min_chunks,
        )
        
        # Garante a identificação básica do medicamento
        if "IDENTIFICAÇÃO DO MEDICAMENTO" not in secoes_escolhidas:
            id_docs = vectorstore.similarity_search(
                query="", 
                filter={"$and": [{"medicamento": nome_remedio.lower()}, {"section": "IDENTIFICAÇÃO DO MEDICAMENTO"}]}
            )
            contexto_docs.extend(id_docs)

        context_llm = "\n\n".join([doc.page_content for doc in contexto_docs])
        t1_retrieval = time.time()

        # ETAPA 3: Geração da Resposta Final
        t0_generation = time.time()
        SYSTEM_PROMPT = """Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.

Regras fundamentais:
1. Toda resposta DEVE ser estritamente fundamentada no contexto fornecido. Não invente nenhuma informação.
2. Se o contexto não contiver nenhuma informação relevante para responder a pelo menos parte da pergunta, use para a resposta final: "Na bula consultada de {medicamento}, não constam informações sobre essa pergunta."
3. Sua resposta final DEVE iniciar obrigatoriamente seguindo este padrão exato:
   "De acordo com a bula do medicamento {medicamento}, consta a seguinte informação: "
4. Não faça diagnósticos ou prescrições. Mantenha um tom profissional, clínico e objetivo.
5. Escreva a sua resposta diretamente em formato de texto simples, sem utilizar formatos estruturados como JSON ou XML."""
        
        RAG_TEMPLATE = """
        Responda à pergunta de forma clara e objetiva com base no contexto fornecido.

        Medicamento:
        nome = {medicamento}

        Contexto recuperado das seções ({secoes_usadas}):
        {contexto}

        Pergunta:
        {pergunta}

        Resposta:
        """

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", RAG_TEMPLATE),
        ])
        
        historico_formatado_lc = formatar_historico(historico_conversa)
        chain_rag = rag_prompt | llm | StrOutputParser()
        
        resposta = chain_rag.invoke({
            "medicamento": nome_remedio,
            "secoes_usadas": ", ".join(secoes_escolhidas),
            "contexto": context_llm,
            "pergunta": pergunta,
            "chat_history": historico_formatado_lc
        })
        t1_generation = time.time()
        
        resposta_limpa = extract_answer(resposta)
        resposta_final = apply_safety_note(pergunta, resposta_limpa)

        tempo_planejamento = t1_plan - t0_plan
        tempo_retrieval = t1_retrieval - t0_retrieval
        tempo_geracao = t1_generation - t0_generation
        
        # No Agentic RAG, o tempo de "recuperação" engloba o planejamento + a busca vetorial física
        tempo_rec_total = tempo_planejamento + tempo_retrieval

        if return_metadata:
            chunk_ids = [
                doc.metadata.get("id") or doc.metadata.get("chunk_id", "")
                for doc in contexto_docs
            ]
            return resposta_final, {
                "tempo_recuperacao": round(tempo_rec_total, 3),
                "tempo_inferencia": round(tempo_geracao, 3),
                "secoes_recuperadas": secoes_escolhidas,
                "chunk_ids_recuperados": chunk_ids, "textos_recuperados": [doc.page_content for doc in (contexto_docs if "contexto_docs" in locals() else (reranked if "reranked" in locals() else []))], 
                "resposta_crua": resposta
            }
        
        return resposta_final

class HybridAgenticRAGPipeline(BasePipeline):
    """
    Pipeline Agentic RAG Híbrido Dinâmico.

    Etapa 1: Planejamento enriquecido — LLM escolhe seções com base em nome + descrição.
    Etapa 2: Recuperação híbrida —
        - Lê o metadado `section_char_count` de cada seção planejada.
        - Se o total de chars cabe no limite configurado: traz TODOS os chunks (seção completa).
        - Caso contrário: fallback para similarity_search semântico (k=FALLBACK_K).
    Etapa 3: Geração — igual ao AgenticRAGPipeline.
    """

    def execute(self, nome_remedio, pergunta, historico_conversa, llm, vectorstore,
                return_metadata=False, context_size_limit=12000, fallback_k=15,
                similarity_threshold=None, min_chunks=1):

        # ------------------------------------------------------------------ #
        # ETAPA 1 — Planejamento Enriquecido                                  #
        # ------------------------------------------------------------------ #
        PLANNING_PROMPT = """
        Você é um agente planejador de busca farmacêutica especializado.
        Sua tarefa é analisar a pergunta de um paciente e decidir quais seções da bula do medicamento '{medicamento}' devem ser consultadas.
        Escolha apenas as seções estritamente necessárias para responder à pergunta de forma completa e segura.

        Seções disponíveis (nome: descrição):
        {secoes_com_descricao}

        Pergunta do Paciente:
        "{pergunta}"

        Responda obrigatoriamente em formato JSON. Não escreva mais nada além do JSON.
        Exemplo:
        {{
            "secoes": ["COMO DEVO USAR ESTE MEDICAMENTO?", "QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?"]
        }}
        """

        secoes_formatadas = "\n".join(
            [f"- {nome}: {desc}" for nome, desc in SECOES_DISPONIVEIS.items()]
        )

        prompt_plan = PromptTemplate.from_template(PLANNING_PROMPT)
        chain_plan = prompt_plan | llm | StrOutputParser()

        t0_plan = time.time()
        planejamento_bruto = chain_plan.invoke({
            "medicamento": nome_remedio,
            "secoes_com_descricao": secoes_formatadas,
            "pergunta": pergunta
        })
        t1_plan = time.time()

        # Parsing do JSON retornado pelo LLM
        try:
            json_str = planejamento_bruto.replace("```json", "").replace("```", "").strip()
            dados = json.loads(json_str)
            secoes_escolhidas = [
                s.upper() for s in dados.get("secoes", [])
                if s.upper() in SECOES_DISPONIVEIS
            ]
        except Exception:
            secoes_escolhidas = ["O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?"]

        if not secoes_escolhidas:
            secoes_escolhidas = ["IDENTIFICAÇÃO DO MEDICAMENTO"]

        # ------------------------------------------------------------------ #
        # ETAPA 2 — Recuperação Híbrida Dinâmica                            #
        # ------------------------------------------------------------------ #
        t0_retrieval = time.time()

        # 2a. Probe: busca 1 chunk de cada seção para ler o metadado section_char_count
        total_chars_estimado = 0
        for secao in secoes_escolhidas:
            probe = vectorstore.similarity_search(
                query="",
                filter={"$and": [
                    {"medicamento": nome_remedio.lower()},
                    {"section": secao}
                ]},
                k=1
            )
            if probe and "section_char_count" in probe[0].metadata:
                total_chars_estimado += probe[0].metadata["section_char_count"]
            else:
                # Metadado ausente (BD antigo): assume que a seção é grande e usa fallback
                total_chars_estimado += context_size_limit + 1
                break

        # 2b. Decide a estratégia de recuperação
        if total_chars_estimado <= context_size_limit:
            # ROTA A: Seção Completa — k grande para trazer todos os chunks das seções
            retrieval_mode = "full_section"
            contexto_docs = vectorstore.similarity_search(
                query=pergunta,
                filter={"$and": [
                    {"medicamento": nome_remedio.lower()},
                    {"section": {"$in": secoes_escolhidas}}
                ]},
                k=200  # Conservadoramente alto: 200 chunks * 1000 chars = 200k chars máximo
            )
        else:
            # ROTA B: Fallback semântico — busca por similaridade com k limitado e limiar opcional
            retrieval_mode = "semantic_fallback"
            contexto_docs = _search_with_threshold(
                vectorstore=vectorstore,
                query=pergunta,
                filter_dict={"$and": [
                    {"medicamento": nome_remedio.lower()},
                    {"section": {"$in": secoes_escolhidas}}
                ]},
                k=fallback_k,
                threshold=similarity_threshold,
                min_chunks=min_chunks,
            )

        # 2c. Identificação do medicamento (sempre incluída)
        if "IDENTIFICAÇÃO DO MEDICAMENTO" not in secoes_escolhidas:
            id_docs = vectorstore.similarity_search(
                query="",
                filter={"$and": [
                    {"medicamento": nome_remedio.lower()},
                    {"section": "IDENTIFICAÇÃO DO MEDICAMENTO"}
                ]},
                k=200
            )
            contexto_docs.extend(id_docs)

        context_llm = "\n\n".join([doc.page_content for doc in contexto_docs])
        t1_retrieval = time.time()

        # Loga o modo de recuperação no console para diagnóstico
        print(f"    [Hybrid] Seções: {secoes_escolhidas} | Modo: {retrieval_mode} | Chars estimados: {total_chars_estimado}")

        # ------------------------------------------------------------------ #
        # ETAPA 3 — Geração da Resposta Final                               #
        # ------------------------------------------------------------------ #
        t0_generation = time.time()

        SYSTEM_PROMPT = """Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.

Regras fundamentais:
1. Toda resposta DEVE ser estritamente fundamentada no contexto fornecido. Não invente nenhuma informação.
2. Se o contexto não contiver nenhuma informação relevante para responder a pelo menos parte da pergunta, use para a resposta final: "Na bula consultada de {medicamento}, não constam informações sobre essa pergunta."
3. Sua resposta final DEVE iniciar obrigatoriamente seguindo este padrão exato:
   "De acordo com a bula do medicamento {medicamento}, consta a seguinte informação: "
4. Não faça diagnósticos ou prescrições. Mantenha um tom profissional, clínico e objetivo.
5. Escreva a sua resposta diretamente em formato de texto simples, sem utilizar formatos estruturados como JSON ou XML."""

        RAG_TEMPLATE = """
        Passo a passo para responder a pergunta:
        1. Leia o nome do remédio fornecido.
        2. Leia o contexto (seções recuperadas da bula).
        3. Leia a pergunta.
        4. Responda à pergunta de forma clara e objetiva com base no contexto fornecido.
        5. Releia a resposta e verifique se inclui todos os detalhes relevantes para responder completamente.

        Medicamento:
        nome = {medicamento}

        Contexto recuperado das seções ({secoes_usadas}) — modo: {retrieval_mode}:
        {contexto}

        Pergunta:
        {pergunta}

        Resposta:
        """

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", RAG_TEMPLATE),
        ])

        historico_formatado_lc = formatar_historico(historico_conversa)
        chain_rag = rag_prompt | llm | StrOutputParser()

        resposta = chain_rag.invoke({
            "medicamento": nome_remedio,
            "secoes_usadas": ", ".join(secoes_escolhidas),
            "retrieval_mode": retrieval_mode,
            "contexto": context_llm,
            "pergunta": pergunta,
            "chat_history": historico_formatado_lc
        })
        t1_generation = time.time()
        
        resposta_limpa = extract_answer(resposta)
        resposta_final = apply_safety_note(pergunta, resposta_limpa)

        tempo_rec_total = (t1_plan - t0_plan) + (t1_retrieval - t0_retrieval)
        tempo_geracao = t1_generation - t0_generation

        if return_metadata:
            chunk_ids = [
                doc.metadata.get("id") or doc.metadata.get("chunk_id", "")
                for doc in contexto_docs
            ]
            return resposta_final, {
                "tempo_recuperacao": round(tempo_rec_total, 3),
                "tempo_inferencia": round(tempo_geracao, 3),
                "secoes_recuperadas": secoes_escolhidas,
                "retrieval_mode": retrieval_mode,
                "total_chars_contexto": total_chars_estimado,
                "chunk_ids_recuperados": chunk_ids, "textos_recuperados": [doc.page_content for doc in (contexto_docs if "contexto_docs" in locals() else (reranked if "reranked" in locals() else []))], 
                "resposta_crua": resposta
            }

        return resposta_final


class FusionRAGPipeline(BasePipeline):
    """
    Pipeline Fusion RAG:
      1. Classificação de intenção (LLM) → mapeia para tipos de seção
      2. Recuperação híbrida: BM25 (léxico) + Dense (semântico)
      3. Reciprocal Rank Fusion (RRF) para combinar e deduplicar
      4. CrossEncoder Reranker para reordenar os top candidatos
      5. LLM gera resposta com os top-K chunks rerankeados
    """

    # Mapeamento intent → tipos de seção (campo tipo_secao no ChromaDB)
    INTENT_TO_SECAO = {
        "contraindicacao": ["contraindicacao", "precaucao_interacao"],
        "interacao":       ["precaucao_interacao", "contraindicacao"],
        "posologia":       ["posologia", "dose_esquecida"],
        "reacao_adversa":  ["reacao_adversa"],
        "superdose":       ["superdose"],
        "indicacao":       ["indicacao", "mecanismo_acao"],
        "mecanismo_acao":  ["mecanismo_acao"],
        "armazenamento":   ["armazenamento"],
        "identificacao":   ["identificacao"],
        "gravidez":        ["precaucao_interacao", "contraindicacao"],
        "dose_esquecida":  ["dose_esquecida", "posologia"],
    }

    def __init__(self):
        self._reranker = None
        self._reranker_model_name = None

    def _get_reranker(self, model_name: str):
        """Carrega o CrossEncoder uma vez e reutiliza nas chamadas seguintes."""
        if self._reranker is None or self._reranker_model_name != model_name:
            from sentence_transformers import CrossEncoder
            print(f"    [Fusion] Carregando reranker: {model_name}")
            self._reranker = CrossEncoder(model_name)
            self._reranker_model_name = model_name
        return self._reranker

    # ------------------------------------------------------------------
    # Etapa 1: Classificação de Intenção
    # ------------------------------------------------------------------
    def _classify_intent(self, llm, nome_remedio: str, pergunta: str) -> tuple:
        """Retorna (intents_escolhidos, tipos_secao_alvo)."""
        intents_list = "\n".join([f"- {i}" for i in self.INTENT_TO_SECAO])

        INTENT_PROMPT = """
        Você é um classificador de intenção farmacêutica.
        Analise a pergunta sobre o medicamento '{medicamento}' e identifique quais intenções estão presentes.
        Escolha apenas da lista abaixo. Pode escolher mais de uma.

        Intenções disponíveis:
        {intents}

        Pergunta: "{pergunta}"

        Responda apenas em JSON. Exemplo:
        {{"intents": ["posologia", "reacao_adversa"]}}
        """

        prompt = PromptTemplate.from_template(INTENT_PROMPT)
        chain = prompt | llm | StrOutputParser()
        raw = chain.invoke({
            "medicamento": nome_remedio,
            "intents": intents_list,
            "pergunta": pergunta,
        })

        try:
            parsed = json.loads(raw.replace("```json", "").replace("```", "").strip())
            intents = [i for i in parsed.get("intents", []) if i in self.INTENT_TO_SECAO]
        except Exception:
            intents = ["identificacao"]

        if not intents:
            intents = ["identificacao"]

        # Expande intents em tipos_secao (removendo duplicatas, mantendo ordem)
        tipos_secao = []
        for intent in intents:
            for t in self.INTENT_TO_SECAO[intent]:
                if t not in tipos_secao:
                    tipos_secao.append(t)

        return intents, tipos_secao

    # ------------------------------------------------------------------
    # Etapa 3: Reciprocal Rank Fusion
    # ------------------------------------------------------------------
    @staticmethod
    def _rrf_fusion(ranked_lists: list, rrf_k: int = 60) -> list:
        """
        Combina múltiplas listas de documentos rankeados usando RRF.
        Retorna lista de Documents ordenados por score RRF decrescente.
        """
        scores = {}       # key (content hash) → score RRF acumulado
        doc_map = {}      # key → Document

        for ranked in ranked_lists:
            for rank, doc in enumerate(ranked):
                key = doc.page_content  # usa conteúdo completo como chave de dedup
                if key not in doc_map:
                    doc_map[key] = doc
                    scores[key] = 0.0
                scores[key] += 1.0 / (rrf_k + rank + 1)

        sorted_keys = sorted(scores, key=scores.get, reverse=True)
        return [doc_map[k] for k in sorted_keys]

    # ------------------------------------------------------------------
    # execute
    # ------------------------------------------------------------------
    def execute(
        self,
        nome_remedio,
        pergunta,
        historico_conversa,
        llm,
        vectorstore,
        return_metadata=False,
        reranker_model: str = "BAAI/bge-reranker-base",
        top_k_retrieval: int = 20,
        top_k_rerank: int = 5,
        rrf_k: int = 60,
        similarity_threshold: float = None,
        min_chunks: int = 1,
    ):
        import re
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError("Instale rank-bm25: `uv pip install rank-bm25`")

        # ----------------------------------------------------------------
        # ETAPA 1 — Classificação de Intenção
        # ----------------------------------------------------------------
        t0_intent = time.time()
        intents, tipos_secao = self._classify_intent(llm, nome_remedio, pergunta)
        t1_intent = time.time()

        print(f"    [Fusion] Intents: {intents} | Seções: {tipos_secao}")

        # ----------------------------------------------------------------
        # ETAPA 2A — Dense Retrieval (embedding)
        # ----------------------------------------------------------------
        t0_ret = time.time()

        filtro_secao = {
            "$and": [
                {"medicamento": nome_remedio.lower()},
                {"tipo_secao": {"$in": tipos_secao}},
            ]
        }

        dense_docs = _search_with_threshold(
            vectorstore=vectorstore,
            query=pergunta,
            filter_dict=filtro_secao,
            k=top_k_retrieval,
            threshold=similarity_threshold,
            min_chunks=min_chunks,
        )

        # ----------------------------------------------------------------
        # ETAPA 2B — BM25 Retrieval (léxico)
        # ----------------------------------------------------------------
        # Busca todos os chunks das seções alvo para construir índice BM25
        all_section_docs = vectorstore.similarity_search(
            query=pergunta,
            filter=filtro_secao,
            k=500,  # amplo o suficiente para pegar todos os chunks das seções
        )

        bm25_docs = []
        if all_section_docs:
            def tokenize(text: str) -> list:
                return re.findall(r'\w+', text.lower())

            corpus = [tokenize(d.page_content) for d in all_section_docs]
            # Verify if corpus actually has non-empty tokens to prevent division by zero in BM25 statistics
            if corpus and any(len(doc) > 0 for doc in corpus):
                bm25 = BM25Okapi(corpus)
                query_tokens = tokenize(pergunta)
                bm25_scores = bm25.get_scores(query_tokens)

                # Ordena por score BM25 decrescente e pega top-K
                ranked_bm25_idx = sorted(range(len(all_section_docs)), key=lambda i: bm25_scores[i], reverse=True)
                bm25_docs = [all_section_docs[i] for i in ranked_bm25_idx[:top_k_retrieval]]

        t1_ret = time.time()

        # ----------------------------------------------------------------
        # ETAPA 3 — Reciprocal Rank Fusion
        # ----------------------------------------------------------------
        fused_docs = self._rrf_fusion([dense_docs, bm25_docs], rrf_k=rrf_k)

        # ----------------------------------------------------------------
        # ETAPA 4 — Reranking com CrossEncoder
        # ----------------------------------------------------------------
        t0_rerank = time.time()
        reranked = []
        if fused_docs:
            reranker = self._get_reranker(reranker_model)
            pairs = [(pergunta, doc.page_content) for doc in fused_docs]
            rerank_scores = reranker.predict(pairs)

            reranked = [
                doc for _, doc in sorted(
                    zip(rerank_scores, fused_docs), key=lambda x: x[0], reverse=True
                )
            ][:top_k_rerank]
        t1_rerank = time.time()

        context_llm = "\n\n".join([doc.page_content for doc in reranked])
        
        # Extract the official section titles from document metadata and filter against SECOES_DISPONIVEIS
        secoes_recuperadas = list({
            doc.metadata.get("section", "").upper()
            for doc in reranked
            if doc.metadata.get("section", "").upper() in SECOES_DISPONIVEIS
        })

        print(f"    [Fusion] Dense={len(dense_docs)} | BM25={len(bm25_docs)} | Fused={len(fused_docs)} | Reranked={len(reranked)}")

        # ----------------------------------------------------------------
        # ETAPA 5 — Geração
        # ----------------------------------------------------------------
        t0_gen = time.time()

        SYSTEM_PROMPT = """Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é fornecer informações precisas, confiáveis e diretamente extraídas do contexto sobre um medicamento em específico.

Regras fundamentais:
1. Toda resposta DEVE ser estritamente fundamentada no contexto fornecido. Não invente nenhuma informação.
2. Se o contexto não contiver nenhuma informação relevante para responder a pelo menos parte da pergunta, use para a resposta final: "Na bula consultada de {medicamento}, não constam informações sobre essa pergunta."
3. Sua resposta final DEVE iniciar obrigatoriamente seguindo este padrão exato:
   "De acordo com a bula do medicamento {medicamento}, consta a seguinte informação: "
4. Não faça diagnósticos ou prescrições. Mantenha um tom profissional, clínico e objetivo.
5. Escreva a sua resposta diretamente em formato de texto simples, sem utilizar formatos estruturados como JSON ou XML."""

        RAG_TEMPLATE = """
        Passo a passo para responder a pergunta:
        1. Leia o nome do remédio fornecido.
        2. Leia o contexto (trechos da bula).
        3. Leia a pergunta.
        4. Responda à pergunta de forma clara e objetiva com base no contexto fornecido.
        5. Releia a resposta e verifique se inclui todos os detalhes relevantes do contexto para responder completamente à pergunta.

        Medicamento: {medicamento}
        Intenções identificadas: {intents}
        Seções consultadas: {secoes_usadas}

        Contexto (trechos rerankeados da bula):
        {contexto}

        Pergunta:
        {pergunta}

        Resposta:
        """

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", RAG_TEMPLATE),
        ])
        chain_rag = rag_prompt | llm | StrOutputParser()

        resposta = chain_rag.invoke({
            "medicamento": nome_remedio,
            "intents": ", ".join(intents),
            "secoes_usadas": ", ".join(secoes_recuperadas),
            "contexto": context_llm,
            "pergunta": pergunta,
            "chat_history": formatar_historico(historico_conversa),
        })
        t1_gen = time.time()
        
        resposta_limpa = extract_answer(resposta)
        resposta_final = apply_safety_note(pergunta, resposta_limpa)

        tempo_recuperacao = (t1_intent - t0_intent) + (t1_ret - t0_ret) + (t1_rerank - t0_rerank)
        tempo_inferencia  = t1_gen - t0_gen

        if return_metadata:
            chunk_ids = [
                doc.metadata.get("id") or doc.metadata.get("chunk_id", "")
                for doc in reranked
            ]
            return resposta_final, {
                "tempo_recuperacao": round(tempo_recuperacao, 3),
                "tempo_inferencia":  round(tempo_inferencia, 3),
                "secoes_recuperadas": secoes_recuperadas,
                "intents": intents,
                "n_chunks_dense": len(dense_docs),
                "n_chunks_bm25":  len(bm25_docs),
                "n_chunks_fused": len(fused_docs),
                "n_chunks_final": len(reranked),
                "chunk_ids_recuperados": chunk_ids, "textos_recuperados": [doc.page_content for doc in (contexto_docs if "contexto_docs" in locals() else (reranked if "reranked" in locals() else []))], 
                "resposta_crua": resposta
            }
        return resposta_final


class GraphRAGPipeline(BasePipeline):
    def execute(self, nome_remedio, pergunta, historico_conversa, llm, vectorstore, return_metadata=False, **kwargs):
        import os
        import time
        from bulagraph import BulaGraphStore, BulaGraphImporter, BulaGraphRetriever
        from bulagraph.formatter import HIGH_RISK_INTENTS, SAFETY_NOTE, SEEK_PROFESSIONAL_NOTE

        ACTIVE_INGREDIENTS_MAP = {
            "amoxil": ["amoxicilina"],
            "rivotril": ["clonazepam"],
            "tylenol": ["paracetamol"]
        }

        start_total = time.time()

        # 1. Carregar/Inicializar Grafo
        STORE_DIR = "./instance/bulagraph_store"
        if os.path.exists(STORE_DIR) and os.listdir(STORE_DIR):
            store = BulaGraphStore.load_jsonl(STORE_DIR)
        else:
            store = BulaGraphStore()

        # 2. Verificar se a bula específica está no grafo; se não, importar
        leaflet_id = store.find_leaflet(nome_remedio)
        if not leaflet_id:
            # Localizar PDF da bula
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            BULAS_PDF_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "bulas_pdf"))
            pdf_path = os.path.join(BULAS_PDF_DIR, f"bula_{nome_remedio.lower()}.pdf")
            
            if os.path.exists(pdf_path):
                from langchain_community.document_loaders import PyPDFLoader
                import re
                from utils.process import remover_referencias_entre_parenteses, cortar_no_historico, cortar_apos_primeira_bula
                
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                cleaned_documents = []
                for doc in documents:
                    cleaned_content = re.sub(r'\n{2,}', '\n', doc.page_content)
                    cleaned_content = re.sub(r'\s{2,}', ' ', cleaned_content)
                    cleaned_documents.append(cleaned_content)
                full_text = "\n".join(cleaned_documents)
                full_text = remover_referencias_entre_parenteses(full_text)
                full_text = cortar_no_historico(full_text)
                full_text = cortar_apos_primeira_bula(full_text)
                
                active_ingredients = ACTIVE_INGREDIENTS_MAP.get(nome_remedio.lower(), [nome_remedio.lower()])
                
                importer = BulaGraphImporter(store)
                importer.import_leaflet(
                    text=full_text,
                    medication_name=nome_remedio,
                    active_ingredients=active_ingredients,
                    leaflet_type="patient_leaflet",
                    source=os.path.basename(pdf_path)
                )
                
                # Salvar grafo persistido
                store.save_jsonl(STORE_DIR)

        # 3. Recuperação por Grafo (com busca vetorial integrada opcional)
        start_retrieval = time.time()
        retriever = BulaGraphRetriever(store, vectorstore=vectorstore)
        retrieval_result = retriever.retrieve(
            question=pergunta,
            medication=nome_remedio,
            leaflet_type="patient_leaflet",
            top_k=8
        )
        end_retrieval = time.time()

        # 4. Formatar e Processar Evidências
        evidence_texts = []
        cited_sections = []
        seen_sections = set()
        chunk_ids = []
        
        for i, item in enumerate(retrieval_result.evidence[:5]):
            evidence_texts.append(f"[{i+1}] Seção: {item.section_title}\nTexto: {item.text}")
            chunk_ids.append(item.chunk_id)
            section_title_upper = item.section_title.upper() if item.section_title else ""
            if section_title_upper in SECOES_DISPONIVEIS and section_title_upper not in seen_sections:
                cited_sections.append(section_title_upper)
                seen_sections.add(section_title_upper)
        
        context_llm = "\n\n".join(evidence_texts) if evidence_texts else "Sem contexto específico encontrado."
        
        if len(cited_sections) == 1:
            secoes_str = cited_sections[0]
            header_prefix = f"na seção \"{secoes_str}\""
        elif len(cited_sections) > 1:
            secoes_str = " e ".join([", ".join(cited_sections[:-1]), cited_sections[-1]])
            header_prefix = f"nas seções \"{secoes_str}\""
        else:
            secoes_str = "Identificação"
            header_prefix = "na seção \"IDENTIFICAÇÃO DO MEDICAMENTO\""

        # 5. Geração da Resposta pelo LLM
        start_inference = time.time()
        
        SYSTEM_PROMPT = """Você é um assistente farmacêutico especializado em medicamentos. Seu objetivo é responder perguntas de forma extremamente precisa e segura, baseando-se unicamente nas evidências textuais recuperadas da bula.

Regras fundamentais:
1. Toda resposta DEVE ser estritamente fundamentada no contexto fornecido. Não invente nenhuma informação.
2. Se o contexto não contiver nenhuma informação relevante para responder a pelo menos parte da pergunta, use para a resposta final: "Na bula consultada de {medicamento}, não constam informações sobre essa pergunta."
3. Sua resposta final DEVE iniciar obrigatoriamente seguindo este padrão exato:
   "De acordo com a bula do medicamento {medicamento}, {header_prefix}, consta a seguinte informação: "
4. Não faça diagnósticos ou prescrições. Mantenha um tom profissional, clínico e objetivo.
5. Escreva a sua resposta diretamente em formato de texto simples, sem utilizar formatos estruturados como JSON ou XML."""

        RAG_TEMPLATE = """Responda à pergunta do usuário baseando-se estritamente no contexto fornecido.

Medicamento: {medicamento}
Seções Citadas: {secoes}

Contexto (Evidências da Bula):
{contexto}

Pergunta do Usuário:
{pergunta}

Resposta:"""

        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", RAG_TEMPLATE),
        ])
        
        historico_formatado_lc = formatar_historico(historico_conversa)
        chain = (rag_prompt | llm | StrOutputParser())
        
        resposta = chain.invoke({
            "medicamento": nome_remedio,
            "header_prefix": header_prefix,
            "secoes": secoes_str,
            "contexto": context_llm,
            "pergunta": pergunta,
            "chat_history": historico_formatado_lc
        })
        
        resposta_limpa = extract_answer(resposta)
        
        # 6. Adicionar Nota de Segurança
        safety_note = SAFETY_NOTE
        if retrieval_result.intent in HIGH_RISK_INTENTS:
            safety_note += SEEK_PROFESSIONAL_NOTE
            
        resposta_limpa += f"\n\n---\n*{safety_note}*"
        
        end_inference = time.time()

        if return_metadata:
            metadata = {
                "tempo_recuperacao": round(end_retrieval - start_retrieval, 3),
                "tempo_inferencia": round(end_inference - start_inference, 3),
                "secoes_recuperadas": cited_sections,
                "chunk_ids_recuperados": chunk_ids,
                "textos_recuperados": [item.text for item in retrieval_result.evidence],
                "intent": retrieval_result.intent,
                "resposta_crua": resposta
            }
            return resposta_limpa, metadata
            
        return resposta_limpa


