FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo spaCy
RUN python -m spacy download es_core_news_sm
RUN python -m spacy download en_core_web_sm

# Copiar código
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY examples/ ./examples/

CMD ["python", "scripts/run_naturalistic_analysis.py", "--help"]
