# Dockerfile
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código da aplicação para o diretório de trabalho
COPY . .

# Define o comando padrão para executar a aplicação
CMD ["python", "aws_audit.py"]
