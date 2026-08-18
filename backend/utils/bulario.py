import subprocess
import json, os
import requests

# Verifica se o arquivo existe
def verificar_arquivo(caminho_arquivo):
    if os.path.isfile(caminho_arquivo):
        return True
    else:
        return False

# Busca o remédio no servidor
def buscar_server(nome, pagina=1):
    try:
        remedio = requests.get(f'http://localhost:3000/buscar/{nome}')
        return remedio.json()
    except Exception as e:
        print(f"Erro ao buscar o remédio: {e}")
        return None

def pdf_server(id):
    try:
        pdf = requests.get(f'http://localhost:3000/bula/{id}')
        return pdf.content
    except Exception as e:
        print(f"Erro ao buscar o PDF: {e}")
        return None
"""
def buscar_remedio(nome, pagina=1):
    try:
        # Executa o script JavaScript passando o nome do remédio e a página como argumentos
        result = subprocess.run(
            ['node', 'utils/bulario.js', nome, str(pagina)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Verifica se houve erros na execução
        if result.returncode != 0:
            raise Exception(f"Erro: {result.stderr}")
        
        # Converte a saída JSON para um dicionário Python
        resultado = json.loads(result.stdout)
        return resultado
    
    except Exception as e:
        print(f"Erro ao buscar o remédio: {e}")
        return None

def salvar_pdf(buffer_data, filename):
    try:
        print("Salvando o PDF da bula...")
        # Converte a lista de inteiros de volta para bytes
        pdf_bytes = bytes(buffer_data)
        
        # Escreve o conteúdo binário no arquivo
        with open(f'bulas_pdf/{filename}', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"PDF salvo como {filename}")
    
    except Exception as e:
        print(f"Erro ao salvar o PDF: {e}")
"""