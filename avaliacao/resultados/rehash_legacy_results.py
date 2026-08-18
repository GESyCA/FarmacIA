import os
import json
import hashlib
import pandas as pd

def recalculate_chunk_id(text: str) -> str:
    """Calcula o ID determinístico do chunk baseado no hash MD5 do texto."""
    if not isinstance(text, str):
        return ""
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:12]
    return f"chunk_{text_hash}"

def process_csv_file(file_path: str):
    print(f"Processando: {file_path}")
    try:
        df = pd.read_csv(file_path)
        if "chunk_ids_recuperados" in df.columns:
            df["chunk_ids_recuperados"] = df["chunk_ids_recuperados"].astype(object)
        else:
            df["chunk_ids_recuperados"] = None
            df["chunk_ids_recuperados"] = df["chunk_ids_recuperados"].astype(object)
        updated = False
        
        for index, row in df.iterrows():
            textos_str = row.get("textos_recuperados")
            if pd.isna(textos_str):
                continue
                
            try:
                textos_list = json.loads(textos_str)
                if isinstance(textos_list, list):
                    new_ids = []
                    for t in textos_list:
                        # Se o item for um dicionário (estrutura nova), extrai o texto ou id
                        if isinstance(t, dict):
                            text_content = t.get("text", t.get("page_content", ""))
                        else:
                            text_content = str(t)
                            
                        chunk_id = recalculate_chunk_id(text_content)
                        if chunk_id:
                            new_ids.append(chunk_id)
                            
                    if new_ids:
                        df.at[index, "chunk_ids_recuperados"] = ", ".join(new_ids)
                        updated = True
            except Exception as row_err:
                print(f"  [Erro na linha {index}]: {row_err}")
                
        if updated:
            df.to_csv(file_path, index=False, encoding='utf-8')
            print(f"  -> Sucesso! IDs de chunks recalculados e salvos.")
        else:
            print(f"  -> Nenhuma atualização necessária.")
            
    except Exception as e:
        print(f"  [ERRO ao processar arquivo]: {e}")

def main():
    # Diretório base dos resultados
    resultados_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Pastas dos modelos
    sub_dirs = ["medgemma_4b", "gemma_4_4b"]
    
    for sub in sub_dirs:
        target_path = os.path.join(resultados_dir, sub)
        if not os.path.exists(target_path):
            print(f"Diretório não encontrado: {target_path}")
            continue
            
        print(f"\n=== Varrendo diretório: {target_path} ===")
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith("_output.csv"):
                    csv_path = os.path.join(root, file)
                    process_csv_file(csv_path)

if __name__ == "__main__":
    main()
