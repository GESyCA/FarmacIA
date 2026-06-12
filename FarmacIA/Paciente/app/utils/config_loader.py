import yaml
import os

def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
