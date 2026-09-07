FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelos de spaCy
RUN python -m spacy download es_core_news_sm
RUN python -m spacy download en_core_web_sm

# Copiar código fuente
COPY . .

# Crear directorio para datos
RUN mkdir -p /data

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python"]
CMD ["scripts/run_analysis.py"]
