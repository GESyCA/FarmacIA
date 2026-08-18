import os
import time
import subprocess
import re
import threading
from pyngrok import ngrok
from flask import Flask

# Configurações
FLASK_PORT = 5000  # Porta da API Flask
OLLAMA_COMMAND = "ollama serve"  # Comando para iniciar o Ollama

# Função para iniciar o Ollama
def start_ollama():
    print("Iniciando Ollama...")
    # Inicia o Ollama em um processo separado
    subprocess.Popen(OLLAMA_COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # Aguarda alguns segundos para o Ollama inicializar
    print("Ollama iniciado.")

# Função para iniciar o ngrok
def start_ngrok(port):
    print("Iniciando ngrok...")
    # Conecta o ngrok à porta do Flask
    public_url = ngrok.connect(port).public_url
    print(f"\n ====================== \n ngrok URL: {public_url} \n ====================== \n ")
    return public_url


# Função para iniciar a API Flask
def start_flask():
    from main import create_app  # Importa a API Flask do arquivo main.py
    print("Iniciando API Flask...")
    app = create_app()
    app.run(host='0.0.0.0', port=FLASK_PORT)

if __name__ == "__main__":
    # Inicia o Ollama
    start_ollama()

    # Inicia o ngrok
    public_url = start_ngrok(FLASK_PORT)

    # Inicia a API Flask
    start_flask()