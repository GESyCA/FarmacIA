import os
import warnings
import logging

# Desabilita a telemetria do ChromaDB e silencia avisos do LiteLLM antes de qualquer importação
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["LITELLM_LOG"] = "ERROR"

# Configura o nível de logs para silenciar LiteLLM e ChromaDB
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("litellm").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import sys
import argparse
import re
import json
import pandas as pd
from dotenv import load_dotenv

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

# Configura o path e variáveis de ambiente
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import load_config
from services.pipelines import PipelineFactory, extract_answer
from rodar_experimentos import load_models
from eval_deepeval.run_deepeval import run_evaluation as run_deepeval_eval

def main():
    parser = argparse.ArgumentParser(description="Testar uma única pergunta nos pipelines")
    parser.add_argument("--medicamento", type=str, default="Aspirina", help="Nome do medicamento")
    parser.add_argument("--pergunta", type=str, default="Quais são as contraindicações?", help="Pergunta a ser feita")
    parser.add_argument("--resposta_esperada", type=str, default="O ácido acetilsalicílico (Aspirina) é contraindicado em caso de hipersensibilidade a salicilatos, asma, úlceras gastrointestinais, diátese hemorrágica, insuficiência renal, hepática ou cardíaca graves, e no último trimestre de gravidez.", help="Resposta esperada (gabarito) para avaliação")
    parser.add_argument("--generation_llm", type=str, default=None, help="Modelo de geração (se omitido, usa o do YAML)")
    parser.add_argument("--judge_llm", type=str, default=None, help="Modelo juiz para LLM as a Judge (se omitido, usa o do YAML)")
    args = parser.parse_args()

    configs = [
        ("Standard RAG", "configs/exp_compare_01_standard.yaml"),
        ("Agentic RAG", "configs/exp_compare_02_agentic.yaml"),
        ("Hybrid Agentic RAG", "configs/exp_compare_03_hybrid_agent.yaml"),
        ("Fusion RAG", "configs/exp_compare_04_fusion.yaml"),
        ("Graph RAG", "configs/exp_compare_05_graph.yaml"),
        ("Naive RAG", "configs/exp_compare_06_naive.yaml"),
    ]

    print("="*80)
    print(f" Testando pergunta única com avaliação LLM as a Judge")
    print(f" Medicamento: {args.medicamento}")
    print(f" Pergunta: '{args.pergunta}'")
    print(f" Modelo de Geração (CLI Override): {args.generation_llm}")
    print(f" Modelo Juiz (CLI Override): {args.judge_llm}")
    print("="*80)

    # Carrega os modelos uma única vez usando o primeiro arquivo de configuração válido
    embeddings = None
    vectorstore = None
    llm = None
    
    for name, config_path in configs:
        actual_path = config_path
        if not os.path.exists(actual_path) and os.path.exists(os.path.join("app", config_path)):
            actual_path = os.path.join("app", config_path)
            
        if os.path.exists(actual_path):
            first_config = load_config(actual_path)
            if args.generation_llm:
                first_config['models']['generation_llm'] = args.generation_llm
            try:
                embeddings, vectorstore, llm = load_models(first_config)
                break
            except Exception as e:
                print(f"[Erro] Falha ao carregar modelos com {actual_path}: {e}")
                
    if not llm:
        print("\n[ERRO CRÍTICO] Não foi possível carregar os modelos e inicializar a execução.")
        return

    resultados_rodadas = []
    test_cases_data = []

    for name, config_path in configs:
        actual_path = config_path
        if not os.path.exists(actual_path) and os.path.exists(os.path.join("app", config_path)):
            actual_path = os.path.join("app", config_path)
            
        if not os.path.exists(actual_path):
            print(f"\n[AVISO] Configuração {actual_path} não encontrada. Pulando {name}.")
            continue
        
        print(f"\n{'='*30} {name} {'='*30}")
        config = load_config(actual_path)
        if args.generation_llm:
            config['models']['generation_llm'] = args.generation_llm
        
        try:
            pipeline_type = config.get('pipeline_type', 'standard_rag')
            pipeline = PipelineFactory.get_pipeline(pipeline_type)


            # Extra kwargs para os pipelines avançados
            extra_kwargs = {}
            if pipeline_type == "hybrid_agentic_rag":
                hybrid_cfg = config.get('hybrid_retrieval', {})
                extra_kwargs["context_size_limit"] = hybrid_cfg.get('context_size_limit', 12000)
                extra_kwargs["fallback_k"] = hybrid_cfg.get('fallback_k', 15)
            elif pipeline_type == "fusion_rag":
                fusion_cfg = config.get('fusion_retrieval', {})
                extra_kwargs["top_k_retrieval"] = fusion_cfg.get('top_k_retrieval', 20)
                extra_kwargs["top_k_rerank"] = fusion_cfg.get('top_k_rerank', 5)
                extra_kwargs["rrf_k"] = fusion_cfg.get('rrf_k', 60)
                extra_kwargs["reranker_model"] = fusion_cfg.get('reranker_model', 'BAAI/bge-reranker-base')

            # Executa o pipeline
            resposta, metadata = pipeline.execute(
                nome_remedio=args.medicamento,
                pergunta=args.pergunta,
                historico_conversa=[],
                llm=llm,
                vectorstore=vectorstore,
                return_metadata=True,
                **extra_kwargs
            )
            
            # Limpa a saída para manter apenas a resposta direta
            resposta_limpa = limpar_saida_generica(resposta)
            resposta_crua_limpa = extract_answer(metadata.get("resposta_crua", resposta))
            
            tempo_recuperacao = metadata.get('tempo_recuperacao', 0)
            tempo_inferencia = metadata.get('tempo_inferencia', 0)
            secoes_str = ", ".join(metadata.get("secoes_recuperadas", []))
            ids_str = ", ".join(str(i) for i in metadata.get("chunk_ids_recuperados", []) if i)
            textos_recuperados = metadata.get("textos_recuperados", [])
            
            print(f"\n[RESPOSTA FINAL]\n{resposta_limpa}")
            print(f"\nTempo de Recuperação: {tempo_recuperacao}s | Tempo de Inferência: {tempo_inferencia}s")
            
            # Armazena os dados para o CSV
            resultados_rodadas.append({
                "pipeline": name,
                "modelo": args.generation_llm,
                "nome_remedio": args.medicamento,
                "pergunta": args.pergunta,
                "resposta_esperada": args.resposta_esperada,
                "resposta_gerada": resposta_limpa,
                "resposta_crua": resposta_crua_limpa,
                "secoes_recuperadas": secoes_str,
                "chunk_ids_recuperados": ids_str,
                "textos_recuperados": json.dumps(textos_recuperados, ensure_ascii=False),
                "tempo_recuperacao_segundos": tempo_recuperacao,
                "tempo_inferencia_segundos": tempo_inferencia
            })

            # Prepara caso para o DeepEval
            test_cases_data.append({
                "question_id": f"pergunta_unica_{pipeline_type}",
                "pipeline_name": name,
                "difficulty": "easy",
                "drug_name": args.medicamento,
                "input": args.pergunta,
                "actual_output": resposta_limpa,
                "expected_output": args.resposta_esperada,
                "retrieval_context": textos_recuperados
            })

        except Exception as e:
            print(f"Erro ao executar {name}: {e}")

    # Salva os resultados das saídas dos pipelines em CSV
    os.makedirs("resultados", exist_ok=True)
    csv_output_path = "resultados/pergunta_unica_todos_pipelines_output.csv"
    df_output = pd.DataFrame(resultados_rodadas)
    df_output.to_csv(csv_output_path, index=False, encoding='utf-8')
    print(f"\n[OK] Saídas dos pipelines salvas em: {csv_output_path}")

    # Roda a avaliação com LLM as a judge (DeepEval)
    deepeval_output_path = "resultados/pergunta_unica_todos_pipelines_deepeval.jsonl"
    if os.path.exists(deepeval_output_path):
        os.remove(deepeval_output_path)

    judge_model_fullname = args.judge_llm
    if not judge_model_fullname:
        # Tenta buscar do primeiro YAML válido, caso contrário usa o fallback padrão
        judge_model_fullname = 'gemini-3.1-flash-lite'
        for name, config_path in configs:
            actual_path = config_path
            if not os.path.exists(actual_path) and os.path.exists(os.path.join("app", config_path)):
                actual_path = os.path.join("app", config_path)
            if os.path.exists(actual_path):
                try:
                    temp_config = load_config(actual_path)
                    if 'models' in temp_config and 'judge_llm' in temp_config['models']:
                        judge_model_fullname = temp_config['models']['judge_llm']
                        break
                except Exception:
                    pass

    if not judge_model_fullname.startswith("gemini/"):
        judge_model_fullname = f"gemini/{judge_model_fullname}"

    print(f"\n[DeepEval] Iniciando avaliação com o modelo juiz: {judge_model_fullname}")
    print(f"\n[INFO] Geração concluída. O DeepEval local foi ignorado para poupar limite de API.")
    print(f"Envie o arquivo '{csv_output_path}' para avaliação via ChatGPT usando o prompt.")
    #try:
    #    run_deepeval_eval(test_cases_data, deepeval_output_path, model=judge_model_fullname)
    #    print(f"[OK] Avaliação finalizada. Resultados detalhados salvos em: {deepeval_output_path}")
    #except Exception as e:
    #    print(f"[Erro] Falha ao rodar avaliação DeepEval: {e}")

if __name__ == '__main__':
    main()

