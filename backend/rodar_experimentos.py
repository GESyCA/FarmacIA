import os
import warnings
# Desabilita a telemetria do ChromaDB e silencia avisos de depreciação antes de qualquer importação
os.environ["ANONYMIZED_TELEMETRY"] = "False"
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
import time
import sys
import json
import argparse
import re
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def limpar_saida_generica(texto):
    if not isinstance(texto, str):
        return texto
    texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
    prefixos = [
        r"aqui est[áa].*?:", 
        r"com base.*?bula.*?[:,\.]",
        r"com base.*?texto.*?[:,\.]",
        r"resposta:",
        r"a resposta é:"
    ]
    for prefixo in prefixos:
        texto = re.sub(r'^\s*(?:' + prefixo + r')\s*', '', texto, flags=re.IGNORECASE)
    return texto.strip()

# Carrega as variáveis de ambiente (ex: GOOGLE_API_KEY) do arquivo .env na raiz
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Adiciona o diretório atual ao path para garantir que os módulos sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import load_config
from services.pipelines import PipelineFactory, extract_answer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from langchain_chroma import Chroma

def load_models(config):
    # Inicializa Embedding
    emb_model_name = config['models']['embedding_model']
    try:
        embeddings = HuggingFaceEmbeddings(model_name=emb_model_name, model_kwargs={"local_files_only": True})
    except Exception:
        embeddings = HuggingFaceEmbeddings(model_name=emb_model_name)
    
    # Nome da coleção ChromaDB (permite coleções separadas por modelo de embedding)
    collection_name = config.get('chroma_collection', 'bulas')
    
    # Inicializa Vectorstore
    chroma_client = chromadb.PersistentClient(path="./chroma_bulas")
    vectorstore = Chroma(collection_name=collection_name, client=chroma_client, embedding_function=embeddings)
    
    # Inicializa LLM de Geração
    gen_llm_name = config['models']['generation_llm']
    
    if gen_llm_name.startswith("ollama:"):
        from langchain_ollama import ChatOllama
        ollama_model_name = gen_llm_name.replace("ollama:", "")
        
        # Ajusta num_ctx dinamicamente com base no pipeline se não estiver no YAML
        pipeline_type = config.get('pipeline_type', 'standard_rag')
        default_ctx = 16384 if pipeline_type in ["guarded_hybrid_agentic_fusion_rag", "graph_rag"] else 4096
        num_ctx = config.get('models', {}).get('num_ctx', default_ctx)
        
        print(f"[Ollama] Carregando modelo local: {ollama_model_name} com num_ctx={num_ctx}")
        llm = ChatOllama(model=ollama_model_name, temperature=0, num_ctx=num_ctx)
    elif gen_llm_name.startswith("llama_cpp:"):
        from langchain_openai import ChatOpenAI
        llama_cpp_model_name = gen_llm_name.replace("llama_cpp:", "")
        print(f"[Llama.cpp] Carregando modelo local (OpenAI compatible): {llama_cpp_model_name}")
        # A porta padrão do server llama.cpp é 8080
        llm = ChatOpenAI(
            base_url="http://localhost:8080/v1",
            api_key="sk-no-key-required",
            model=llama_cpp_model_name,
            temperature=0
        )
    elif "gemini" in gen_llm_name.lower() or "gemma" in gen_llm_name.lower():
        llm = ChatGoogleGenerativeAI(model=gen_llm_name, temperature=0)
    else:
        # Placeholder para modelos locais no futuro
        raise ValueError(f"LLM {gen_llm_name} ainda não suportado nativamente no script.")
        
    return embeddings, vectorstore, llm

def run_experiments(config_path, gen_llm_override=None, judge_llm_override=None, output_dir="resultados"):
    config = load_config(config_path)
    
    if gen_llm_override:
        config['models']['generation_llm'] = gen_llm_override
        print(f"[Override] Modelo de geração sobrescrito para: {gen_llm_override}")
    if judge_llm_override:
        config['models']['judge_llm'] = judge_llm_override
        print(f"[Override] Modelo juiz sobrescrito para: {judge_llm_override}")
    
    print(f"=== Iniciando Experimento: {config['experiment_name']} ===")

    # Regenerar o banco vetorial se solicitado no YAML
    if config.get('run_flags', {}).get('generate_vector_db', False):
        from utils.process import processar_bula
        collection_name = config.get('chroma_collection', 'bulas')
        emb_model_name = config['models']['embedding_model']
        print(f"\n[generate_vector_db=true] Re-processando PDFs -> coleção='{collection_name}', embedding='{emb_model_name}'...")
        try:
            ingest_embeddings = HuggingFaceEmbeddings(model_name=emb_model_name, model_kwargs={"local_files_only": True})
        except Exception:
            ingest_embeddings = HuggingFaceEmbeddings(model_name=emb_model_name)
        bulas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bulas_pdf")
        if os.path.isdir(bulas_dir):
            for pdf_file in Path(bulas_dir).glob("*.pdf"):
                nome_remedio = pdf_file.stem.lower().removeprefix("bula_")
                print(f"  Processando: {pdf_file.name} -> medicamento='{nome_remedio}'")
                try:
                    processar_bula(str(pdf_file), nome_remedio,
                                   embeddings=ingest_embeddings, collection_name=collection_name)
                except Exception as e:
                    print(f"  Erro ao processar {pdf_file.name}: {e}")
        else:
            print(f"  [AVISO] Diretório de bulas não encontrado: {bulas_dir}")
    
    embeddings, vectorstore, llm = load_models(config)
    pipeline_type = config.get('pipeline_type', 'standard_rag')
    pipeline = PipelineFactory.get_pipeline(pipeline_type)
    
    # Parâmetros específicos do pipeline híbrido (lidos do YAML, com defaults)
    hybrid_cfg = config.get('hybrid_retrieval', {})
    hybrid_context_limit = hybrid_cfg.get('context_size_limit', 12000)
    hybrid_fallback_k = hybrid_cfg.get('fallback_k', 15)

    # Parâmetros específicos do Fusion RAG
    fusion_cfg = config.get('fusion_retrieval', {})
    fusion_top_k_retrieval = fusion_cfg.get('top_k_retrieval', 20)
    fusion_top_k_rerank    = fusion_cfg.get('top_k_rerank', 5)
    fusion_rrf_k           = fusion_cfg.get('rrf_k', 60)
    fusion_reranker_model  = fusion_cfg.get('reranker_model', 'BAAI/bge-reranker-base')

    # Parâmetros globais de limiar de similaridade (opcionais)
    retrieval_cfg = config.get('retrieval', {})
    similarity_threshold = retrieval_cfg.get('similarity_threshold', None)
    min_chunks = retrieval_cfg.get('min_chunks', 1)
    if similarity_threshold is not None:
        print(f"[Retrieval] Limiar de similaridade ativado: similarity_threshold={similarity_threshold}, min_chunks={min_chunks}")

    datasets = config.get('datasets', [])
    for dataset_file in datasets:
        actual_dataset_file = dataset_file
        if not os.path.exists(actual_dataset_file) and os.path.exists(os.path.join("app", dataset_file)):
            actual_dataset_file = os.path.join("app", dataset_file)
            
        print(f"\nCarregando dataset de {actual_dataset_file}...")
        try:
            df = pd.read_csv(actual_dataset_file)
        except FileNotFoundError:
            print(f"Erro: Arquivo {actual_dataset_file} não encontrado.")
            continue

        respostas_geradas = []
        respostas_cruas = []
        tempos_recuperacao = []
        tempos_inferencia = []
        secoes_recuperadas_list = []
        chunk_ids_list = []
        textos_recuperados_list = []
        
        # Colunas adicionais de depuração para o pipeline Guarded RAG
        guarded_planner_primary = []
        guarded_planner_secondary = []
        guarded_planner_safety = []
        guarded_expanded_sections = []
        guarded_confidence = []
        guarded_fallback_triggered = []
        guarded_debug_trace_list = []

        print(f"Processando {len(df)} perguntas do dataset...")

        for index, row in df.iterrows():
            medicamento = row.get("nome_remedio") or row.get("medicamento")
            pergunta = row.get("pergunta")
            
            print(f"[{index+1}/{len(df)}] Medicamento: {medicamento} | Pergunta: {pergunta}")
            
            try:
                # Constrói kwargs extras para pipelines que aceitam parâmetros adicionais
                run_generation = config.get('run_flags', {}).get('run_generation', True)
                extra_kwargs = {
                    "similarity_threshold": similarity_threshold,
                    "min_chunks": min_chunks,
                    "run_generation": run_generation,
                }
                if pipeline_type == "hybrid_agentic_rag":
                    extra_kwargs["context_size_limit"] = hybrid_context_limit
                    extra_kwargs["fallback_k"] = hybrid_fallback_k
                elif pipeline_type == "fusion_rag":
                    extra_kwargs["top_k_retrieval"] = fusion_top_k_retrieval
                    extra_kwargs["top_k_rerank"]    = fusion_top_k_rerank
                    extra_kwargs["rrf_k"]           = fusion_rrf_k
                    extra_kwargs["reranker_model"]  = fusion_reranker_model
                elif pipeline_type == "guarded_hybrid_agentic_fusion_rag":
                    guarded_cfg = config.get('guarded_retrieval', {})
                    guarded_params = [
                        "primary_vector_top_k", "primary_bm25_top_k",
                        "secondary_vector_top_k", "secondary_bm25_top_k",
                        "safety_vector_top_k", "safety_bm25_top_k",
                        "expanded_vector_top_k", "expanded_bm25_top_k",
                        "global_vector_top_k", "global_bm25_top_k",
                        "fallback_global_vector_top_k", "fallback_global_bm25_top_k",
                        "fallback_safety_top_k",
                        "rrf_k", "reranker_model", "reranker_top_n",
                        "fallback_reranker_top_n",
                        "context_size_limit", "max_full_primary_sections",
                        "max_full_secondary_sections",
                        "enable_fallback", "enable_section_expansion",
                        "enable_full_section_inclusion",
                    ]
                    for param in guarded_params:
                        if param in guarded_cfg:
                            extra_kwargs[param] = guarded_cfg[param]

                # Chama o pipeline com os modelos carregados
                resposta, metadata = pipeline.execute(
                    nome_remedio=medicamento,
                    pergunta=pergunta,
                    historico_conversa=[],
                    llm=llm,
                    vectorstore=vectorstore,
                    return_metadata=True,
                    **extra_kwargs
                )
                
                # Limpa a saída para manter apenas a resposta direta
                resposta_limpa = limpar_saida_generica(resposta)
                
                respostas_geradas.append(resposta_limpa)
                # Salva apenas a resposta final extraída do modelo (sem o JSON, sem o think, e sem a nota de segurança)
                respostas_cruas.append(extract_answer(metadata.get("resposta_crua", resposta)))
                tempos_recuperacao.append(metadata.get("tempo_recuperacao", 0))
                tempos_inferencia.append(metadata.get("tempo_inferencia", 0))
                # Junta a lista de seções com vírgula para salvar no CSV
                secoes_str = ", ".join(metadata.get("secoes_recuperadas", []))
                secoes_recuperadas_list.append(secoes_str)
                ids_str = ", ".join(str(i) for i in metadata.get("chunk_ids_recuperados", []) if i)
                chunk_ids_list.append(ids_str)
                
                textos = metadata.get("textos_recuperados", [])
                textos_recuperados_list.append(json.dumps(textos, ensure_ascii=False))
                
                # Extrai dados adicionais do pipeline Guarded (se disponíveis)
                trace = metadata.get("guarded_debug_trace", {})
                guarded_planner_primary.append(", ".join(trace.get("planner_primary", [])))
                guarded_planner_secondary.append(", ".join(trace.get("planner_secondary", [])))
                guarded_planner_safety.append(", ".join(trace.get("planner_safety", [])))
                guarded_expanded_sections.append(", ".join(trace.get("expanded_sections", [])))
                guarded_confidence.append(trace.get("evidence_confidence", ""))
                guarded_fallback_triggered.append(trace.get("fallback_triggered", False))
                guarded_debug_trace_list.append(json.dumps(trace, ensure_ascii=False))
                
                print(f"  Recuperação: {metadata.get('tempo_recuperacao', 0)}s | Inferência: {metadata.get('tempo_inferencia', 0)}s")
                
            except Exception as e:
                print(f"Erro ao processar: {e}")
                respostas_geradas.append(f"ERRO: {str(e)}")
                respostas_cruas.append(f"ERRO: {str(e)}")
                tempos_recuperacao.append(0)
                tempos_inferencia.append(0)
                secoes_recuperadas_list.append("")
                chunk_ids_list.append("")
                textos_recuperados_list.append("[]")
                guarded_planner_primary.append("")
                guarded_planner_secondary.append("")
                guarded_planner_safety.append("")
                guarded_expanded_sections.append("")
                guarded_confidence.append("")
                guarded_fallback_triggered.append(False)
                guarded_debug_trace_list.append("{}")
 
            # Salva o progresso parcial incrementalmente a cada iteração para evitar perdas
            os.makedirs(output_dir, exist_ok=True)
            dataset_basename = Path(actual_dataset_file).stem
            
            # Remove prefixo "compare_" do nome do experimento
            exp_name = config['experiment_name'].replace("compare_", "")
            # Limpa o nome do modelo para usar no nome do arquivo
            model_name_raw = config['models']['generation_llm']
            model_name_clean = model_name_raw.replace("ollama:", "").replace("llama_cpp:", "")
            model_name_clean = re.sub(r'[^a-zA-Z0-9_]', '_', model_name_clean).lower()
            model_name_clean = re.sub(r'_+', '_', model_name_clean).strip('_')
            
            # Limpa o nome do modelo de embedding para usar no nome do arquivo
            emb_name_raw = config['models']['embedding_model']
            emb_name_clean = re.sub(r'[^a-zA-Z0-9_]', '_', emb_name_raw).lower()
            emb_name_clean = re.sub(r'_+', '_', emb_name_clean).strip('_')
            
            # Remove "perguntas_respostas_" do dataset_basename
            ds_name = dataset_basename.replace("perguntas_respostas_", "")
            
            output_file = os.path.join(output_dir, f"{exp_name}_{model_name_clean}_{emb_name_clean}_{ds_name}_output.csv")
            # Copia o dataframe original até a linha atual
            partial_df = df.iloc[:len(respostas_geradas)].copy()
            
            # Adiciona colunas extras
            partial_df['pipeline'] = pipeline_type
            partial_df['modelo'] = config['models']['generation_llm']
            
            # Tenta inferir a dificuldade pelo nome do arquivo caso não exista
            if 'dificuldade' not in partial_df.columns:
                basename_lower = dataset_basename.lower()
                if 'faceis' in basename_lower or 'facil' in basename_lower:
                    partial_df['dificuldade'] = 'facil'
                elif 'medias' in basename_lower or 'medio' in basename_lower:
                    partial_df['dificuldade'] = 'medio'
                elif 'dificeis' in basename_lower or 'dificil' in basename_lower:
                    partial_df['dificuldade'] = 'dificil'
                else:
                    partial_df['dificuldade'] = 'desconhecido'
                    
            partial_df['resposta_gerada'] = respostas_geradas
            partial_df['resposta_crua'] = respostas_cruas
            partial_df['secoes_recuperadas'] = secoes_recuperadas_list
            partial_df['chunk_ids_recuperados'] = chunk_ids_list
            partial_df['textos_recuperados'] = textos_recuperados_list
            partial_df['tempo_recuperacao_segundos'] = tempos_recuperacao
            partial_df['tempo_inferencia_segundos'] = tempos_inferencia
            partial_df['guarded_planner_primary'] = guarded_planner_primary
            partial_df['guarded_planner_secondary'] = guarded_planner_secondary
            partial_df['guarded_planner_safety'] = guarded_planner_safety
            partial_df['guarded_expanded_sections'] = guarded_expanded_sections
            partial_df['guarded_confidence'] = guarded_confidence
            partial_df['guarded_fallback_triggered'] = guarded_fallback_triggered
            partial_df['guarded_debug_trace'] = guarded_debug_trace_list
            
            # Reordena colunas para colocar pipeline e modelo e dificuldade no começo se possível
            cols = partial_df.columns.tolist()
            # Mover pipeline e modelo para o início
            for col in ['modelo', 'pipeline']:
                if col in cols:
                    cols.remove(col)
                    cols.insert(0, col)
            
            # Move dificuldade logo depois da pergunta se a pergunta existir
            if 'dificuldade' in cols:
                cols.remove('dificuldade')
                if 'pergunta' in cols:
                    pergunta_idx = cols.index('pergunta')
                    cols.insert(pergunta_idx + 1, 'dificuldade')
                else:
                    cols.insert(2, 'dificuldade')
                    
            partial_df = partial_df[cols]
            partial_df.to_csv(output_file, index=False, encoding='utf-8')

            # Rate limiting para evitar 429 na conta gratuita (limite de 15 RPM)
            # Só aplicamos a pausa se o modelo não for local (Ollama) e se houver chamadas ao LLM
            if not config['models']['generation_llm'].startswith('ollama:'):
                if run_generation:
                    time.sleep(4)
                elif pipeline_type in ["standard_rag", "agentic_rag", "hybrid_agentic_rag", "fusion_rag", "guarded_hybrid_agentic_fusion_rag"]:
                    # Planejamento/classificação na recuperação ainda faz 1 chamada ao LLM
                    time.sleep(2)
 
        print(f"\nResultados salvos com sucesso em: {output_file}")
        
        if config.get('run_flags', {}).get('run_evaluation', False):
            from evaluation import run_evaluation
            run_evaluation(output_file, config)
        
    print("\nExperimentos concluídos com sucesso!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rodar experimentos de RAG")
    parser.add_argument("--config", type=str, required=True, help="Caminho para o arquivo YAML de configuração")
    parser.add_argument("--generation_llm", type=str, default=None, help="Sobrescrever o modelo de inferência/geração")
    parser.add_argument("--judge_llm", type=str, default=None, help="Sobrescrever o modelo juiz")
    parser.add_argument("--output_dir", type=str, default="resultados", help="Diretório onde os arquivos de saída serão salvos")
    args = parser.parse_args()
    
    run_experiments(args.config, gen_llm_override=args.generation_llm, judge_llm_override=args.judge_llm, output_dir=args.output_dir)
