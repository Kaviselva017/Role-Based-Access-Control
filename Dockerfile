FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# ✅ ONLY install from requirements (no manual override)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ⚠️ TEMP: comment embedding step to avoid crash
# RUN python -m backend.init_users && \
#     python -m preprocessing.preprocess_all && \
#     python -m vector_db.embedding_engine

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}