import os
import subprocess
import sys

def main():
    # Diretório dos resultados
    resultados_dir = os.path.dirname(os.path.abspath(__file__))
    paciente_dir = os.path.dirname(resultados_dir)
    
    # Path para o python e scripts
    python_exe = os.path.join(paciente_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable  # Fallback
        
    evaluation_py = os.path.join(paciente_dir, "app", "evaluation.py")
    configs_dir = os.path.join(paciente_dir, "app", "configs")
    
    # Mapeamento do prefixo do arquivo para a config correspondente
    config_mapping = {
        "01_standard": "exp_compare_01_standard.yaml",
        "02_agentic": "exp_compare_02_agentic.yaml",
        "03_hybrid_agent": "exp_compare_03_hybrid_agent.yaml",
        "04_fusion": "exp_compare_04_fusion.yaml",
        "05_graph": "exp_compare_05_graph.yaml",
        "06_naive": "exp_compare_06_naive.yaml",
        "07_guarded": "exp_compare_07_guarded.yaml"
    }
    
    sub_dirs = ["medgemma_4b", "gemma_4_4b", "phi4-mini", "mediphi"]
    
    for sub in sub_dirs:
        target_path = os.path.join(resultados_dir, sub)
        if not os.path.exists(target_path):
            print(f"Diretório não encontrado: {target_path}")
            continue
            
        print(f"\n=== Varrendo diretório para re-avaliação: {target_path} ===")
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith("_output.csv"):
                    csv_path = os.path.join(root, file)
                    basename = os.path.basename(file)
                    
                    # Identificar o prefixo do arquivo
                    prefix = None
                    for k in config_mapping.keys():
                        if basename.startswith(k):
                            prefix = k
                            break
                            
                    if not prefix:
                        print(f"Ignorando (sem mapeamento de config): {file}")
                        continue
                        
                    config_name = config_mapping[prefix]
                    config_path = os.path.join(configs_dir, config_name)
                    
                    if not os.path.exists(config_path):
                        print(f"Configuração não encontrada: {config_path}")
                        continue
                        
                    # Para rodar o evaluation.py corretamente, precisamos executar de dentro de Paciente/
                    # e passar caminhos relativos ou absolutos apropriados
                    print(f"\n[EXEC] Executando evaluation para {file} com config {config_name}...")
                    
                    cmd = [
                        python_exe, 
                        evaluation_py, 
                        "--csv", csv_path, 
                        "--config", config_path
                    ]
                    
                    try:
                        result = subprocess.run(
                            cmd, 
                            cwd=paciente_dir
                        )
                        if result.returncode == 0:
                            print(f"  -> Sucesso ao atualizar métricas de {file}.")
                        else:
                            print(f"  -> ERRO ao rodar evaluation.py (exit code: {result.returncode})")
                    except Exception as e:
                        print(f"  -> Falha de execução: {e}")

if __name__ == "__main__":
    main()
