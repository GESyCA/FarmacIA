# Usa uma imagem base do Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências para o diretório de trabalho
COPY app/requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copia o restante do código da aplicação
COPY app/ .

# Expõe a porta que a aplicação vai rodar
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "main.py"]