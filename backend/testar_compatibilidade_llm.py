"""
Teste mínimo de compatibilidade de saída de LLM.
Roda APENAS o pipeline Guarded Hybrid Agentic Fusion RAG com 2 perguntas
(1 fácil, 1 difícil) para validar se o modelo gera respostas compatíveis.
"""
import os
import sys
import re
import warnings

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["LITELLM_LOG"] = "ERROR"
warnings.filterwarnings("ignore", category=FutureWarning)

import logging
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("litellm").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from utils.config_loader import load_config
from services.pipelines import PipelineFactory, extract_answer
from rodar_experimentos import load_models

# ── Configuração do teste ────────────────────────────────────────────────────
GENERATION_LLM = "ollama:qwen3.5:4b"   # modelo a testar
CONFIG_PATH    = "configs/exp_compare_01_standard.yaml"
PIPELINE_NAME  = "Standard RAG"

PERGUNTAS = [
    {
        "nivel": "FÁCIL",
        "medicamento": "amoxil",
        "pergunta": "Quais são as contraindicações do Amoxil?",
        "resposta_esperada": (
            "Amoxil é contraindicado em pacientes com histórico de reações alérgicas "
            "a penicilinas, cefalosporinas ou outros alérgenos."
        ),
    },
    {
        "nivel": "DIFÍCIL",
        "medicamento": "rivotril",
        "pergunta": (
            "Quais são os riscos de dependência e os sintomas de abstinência "
            "associados ao uso prolongado do Rivotril (clonazepam)?"
        ),
        "resposta_esperada": (
            "O uso prolongado de Rivotril pode causar dependência física e psíquica. "
            "A retirada abrupta pode provocar sintomas de abstinência como ansiedade, "
            "tremores, sudorese, insônia, convulsões e psicose. A descontinuação deve "
            "ser gradual e sob orientação médica."
        ),
    },
]
# ─────────────────────────────────────────────────────────────────────────────

def limpar_saida(texto):
    if not isinstance(texto, str):
        return texto
    texto = re.sub(r'<think>.*?</think>', '', texto, flags=re.DOTALL)
    for prefixo in [r"aqui est[áa].*?:", r"com base.*?bula.*?[:,\.]",
                    r"resposta:", r"a resposta é:"]:
        texto = re.sub(r'^\s*(?:' + prefixo + r')\s*', '', texto, flags=re.IGNORECASE)
    return texto.strip()

def main():
    # Resolve path do config
    actual_path = CONFIG_PATH
    if not os.path.exists(actual_path):
        actual_path = os.path.join("app", CONFIG_PATH)
    if not os.path.exists(actual_path):
        print(f"[ERRO] Config não encontrada: {CONFIG_PATH}")
        sys.exit(1)

    config = load_config(actual_path)
    config['models']['generation_llm'] = GENERATION_LLM

    print("=" * 70)
    print(f" TESTE DE COMPATIBILIDADE — {PIPELINE_NAME}")
    print(f" LLM Gerador : {GENERATION_LLM}")
    print(f" Embedding   : {config['models']['embedding_model']}")
    print("=" * 70)

    embeddings, vectorstore, llm = load_models(config)

    pipeline_type = config.get('pipeline_type', 'standard_rag')
    pipeline = PipelineFactory.get_pipeline(pipeline_type)

    # Standard RAG não precisa de kwargs extras
    extra_kwargs = {}

    resultados = []

    for q in PERGUNTAS:
        print(f"\n{'─'*70}")
        print(f" [{q['nivel']}] Medicamento: {q['medicamento']}")
        print(f" Pergunta: {q['pergunta']}")
        print('─' * 70)

        try:
            resposta, metadata = pipeline.execute(
                nome_remedio=q['medicamento'],
                pergunta=q['pergunta'],
                historico_conversa=[],
                llm=llm,
                vectorstore=vectorstore,
                return_metadata=True,
                **extra_kwargs
            )

            resposta_limpa = limpar_saida(resposta)
            resposta_crua  = extract_answer(metadata.get("resposta_crua", resposta))
            t_rec = metadata.get('tempo_recuperacao', 0)
            t_inf = metadata.get('tempo_inferencia', 0)
            secoes = ", ".join(metadata.get("secoes_recuperadas", []))

            print(f"\n[RESPOSTA GERADA]\n{resposta_limpa}")
            print(f"\n[RESPOSTA CRUA (extract_answer)]\n{resposta_crua[:500]}{'...' if len(resposta_crua) > 500 else ''}")
            print(f"\nSeções recuperadas : {secoes or '(nenhuma)'}")
            print(f"Tempo recuperação  : {t_rec}s")
            print(f"Tempo inferência   : {t_inf}s")

            # Diagnóstico de compatibilidade
            ok_nao_vazia   = bool(resposta_limpa and resposta_limpa.strip())
            ok_nao_erro    = not resposta_limpa.startswith("ERRO")
            ok_crua_string = isinstance(resposta_crua, str)
            ok_secoes      = isinstance(secoes, str)

            print(f"\n[DIAGNÓSTICO]")
            print(f"  ✅ Resposta não vazia    : {ok_nao_vazia}")
            print(f"  ✅ Sem ERRO              : {ok_nao_erro}")
            print(f"  ✅ resposta_crua é str   : {ok_crua_string}")
            print(f"  ✅ secoes_recuperadas str: {ok_secoes}")

            resultados.append({
                "nivel": q['nivel'],
                "compativel": all([ok_nao_vazia, ok_nao_erro, ok_crua_string, ok_secoes])
            })

        except Exception as e:
            import traceback
            print(f"\n[ERRO] {e}")
            traceback.print_exc()
            resultados.append({"nivel": q['nivel'], "compativel": False})

    print(f"\n{'=' * 70}")
    print(" RESULTADO FINAL")
    print('=' * 70)
    todos_ok = True
    for r in resultados:
        status = "✅ COMPATÍVEL" if r['compativel'] else "❌ INCOMPATÍVEL"
        print(f"  {r['nivel']:10s}: {status}")
        if not r['compativel']:
            todos_ok = False

    if todos_ok:
        print(f"\n✅ Modelo '{GENERATION_LLM}' COMPATÍVEL — pode rodar os experimentos completos.")
    else:
        print(f"\n❌ Modelo '{GENERATION_LLM}' INCOMPATÍVEL — verifique os erros acima antes de prosseguir.")
    print('=' * 70)

if __name__ == '__main__':
    main()
