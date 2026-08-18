import os
import subprocess
import sys

def run_retrieval_comparison():
    # Resolve caminhos relativos ao diretório do script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Python executável do ambiente virtual
    venv_python = sys.executable

    configs = [
        ("MiniLM (all-MiniLM-L6-v2)", "configs/exp_compare_embeddings_retrieval_all-MiniLM.yaml"),
        ("BGE-M3 (BAAI/bge-m3)", "configs/exp_compare_embeddings_retrieval_BGE.yaml")
    ]

    print("="*80)
    print(" Iniciando Comparativo de Modelos de Embedding (Fase de Recuperação)")
    print("="*80)

    for name, config_rel_path in configs:
        config_path = os.path.join(base_dir, config_rel_path)
        if not os.path.exists(config_path):
            print(f"\n[ERRO] Arquivo de configuração não encontrado: {config_path}")
            continue

        print(f"\n>>> Executando experimento: {name} <<<")
        print(f"Configuração: {config_rel_path}")
        
        # Executa o script de experimentos passando o arquivo yaml correspondente e sobrescrevendo o LLM de classificação para usar Ollama local
        cmd = [venv_python, "-u", "rodar_experimentos.py", "--config", config_rel_path, "--generation_llm", "ollama:medgemma:4b"]
        
        try:
            # Roda e exibe os prints em tempo real
            result = subprocess.run(cmd, cwd=base_dir, check=True)
            print(f"\n[Sucesso] Experimento {name} concluído.")
        except subprocess.CalledProcessError as e:
            print(f"\n[Erro] Falha ao rodar experimento {name}: {e}")

    print("\n" + "="*80)
    print(" Execução do Comparativo Concluída!")
    print(" Os resultados (CSVs) foram salvos na pasta 'resultados/'.")
    print("="*80)

if __name__ == "__main__":
    run_retrieval_comparison()
