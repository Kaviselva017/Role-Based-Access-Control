FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# ✅ ONLY install from requirements (no manual override)
RUN pip install --no-cache-dir -r requirements.txt



CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}