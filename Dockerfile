FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
    sentence-transformers==2.2.2 \
    huggingface-hub==0.14.1 && \
    pip install --no-cache-dir -r requirements.txt
COPY . .

RUN python -m backend.init_users && \
    python -m preprocessing.preprocess_all && \
    python -m vector_db.embedding_engine

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
