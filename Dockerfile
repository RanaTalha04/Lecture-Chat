FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/storage/chroma /app/uploads
# Bake Chroma's lightweight ONNX embedding model into the image. This prevents
# the first /api/reindex request from waiting for a model download on Render.
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()(['warmup'])"
EXPOSE 8000
CMD ["python", "main.py"]
