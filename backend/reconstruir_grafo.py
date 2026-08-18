import os
import sys
import re
import shutil
from pathlib import Path

# Configura o path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from bulagraph import BulaGraphStore, BulaGraphImporter
from utils.process import remover_referencias_entre_parenteses, cortar_no_historico, split_leaflets, extrair_texto_pdf

ACTIVE_INGREDIENTS_MAP = {
    "amoxil": ["amoxicilina"],
    "amoxicilina": ["amoxicilina"],
    "rivotril": ["clonazepam"],
    "tylenol": ["paracetamol"],
    "paracetamol": ["paracetamol"],
    "dramin": ["dimenidrato", "cloridrato de piridoxina"],
}

def main():
    STORE_DIR = os.path.join(BASE_DIR, "instance", "bulagraph_store")
    BULAS_MD_DIR = os.path.join(BASE_DIR, "bulas_markdown")

    print("=" * 80)
    print("                RECONSTRUINDO O GRAFO DE CONHECIMENTO (BULAGRAPH)                ")
    print("=" * 80)

    # 1. Limpar os arquivos de destino se existirem
    if os.path.exists(STORE_DIR):
        print(f"Limpando arquivos do grafo em: {STORE_DIR}")
        for file_name in ["nodes.jsonl", "edges.jsonl", "chunks.jsonl", "sections.jsonl", "leaflets.jsonl"]:
            file_path = os.path.join(STORE_DIR, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"  [AVISO] Não foi possível remover {file_name}: {e}")
    else:
        os.makedirs(STORE_DIR, exist_ok=True)

    # 2. Inicializar o Store
    store = BulaGraphStore()
    importer = BulaGraphImporter(store)

    # 3. Listar e processar todas as bulas Markdown limpas
    if not os.path.isdir(BULAS_MD_DIR):
        print(f"[ERRO] Diretório de Markdowns não encontrado em: {BULAS_MD_DIR}")
        return

    md_files = list(Path(BULAS_MD_DIR).glob("*_raw.md"))
    if not md_files:
        print(f"[AVISO] Nenhum arquivo Markdown bruto encontrado em: {BULAS_MD_DIR}")
        return

    print(f"Encontrados {len(md_files)} arquivos Markdown brutos para processar.")

    for md_path in md_files:
        nome_remedio = md_path.name.lower().removeprefix("bula_").removesuffix("_raw.md")
        print(f"\n- Processando {md_path.name} (medicamento: '{nome_remedio}')...")
        
        try:
            # Carregar texto do Markdown
            with open(md_path, "r", encoding="utf-8") as f:
                full_text = f.read()
            
            # Separar sub-bulas/apresentações
            leaflets = split_leaflets(full_text)
            patient_leaflets = [l for l, is_prof in leaflets if not is_prof]
            
            # Se não encontrar nenhuma VP explicitamente classificada, importa tudo
            if not patient_leaflets:
                patient_leaflets = [l for l, _ in leaflets]
            
            active_ingredients = ACTIVE_INGREDIENTS_MAP.get(nome_remedio, [nome_remedio])
            
            print(f"  Encontradas {len(patient_leaflets)} apresentações/sub-bulas de paciente.")
            
            for idx, sub_text in enumerate(patient_leaflets):
                cleaned_sub = remover_referencias_entre_parenteses(sub_text)
                cleaned_sub = cortar_no_historico(cleaned_sub)
                
                stats = importer.import_leaflet(
                    text=cleaned_sub,
                    medication_name=nome_remedio,
                    active_ingredients=active_ingredients,
                    leaflet_type="patient_leaflet",
                    source=f"bula_{nome_remedio}.pdf"
                )
                print(f"    Sub-bula {idx+1} importada com sucesso! Chunks criados: {stats.get('chunks_created', 0)}")
                
        except Exception as e:
            print(f"  [ERRO] Falha ao processar {md_path.name}: {e}")

    # 4. Salvar o grafo persistido
    print("\nSalvando grafo...")
    store.save_jsonl(STORE_DIR)
    
    print("\nEstatísticas do Grafo Final Reconstruído:")
    for key, val in store.stats().items():
        print(f"  - {key}: {val}")
        
    print("=" * 80)
    print(" Grafo reconstruído e salvo com sucesso em ./instance/bulagraph_store!")
    print("=" * 80)

if __name__ == "__main__":
    main()
