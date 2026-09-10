"""Index lecture PDFs, retrieve relevant passages, and optionally generate answers."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from threading import Lock
from typing import Any

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv
from groq import Groq

from src.chunking.chunker import Chunking
from src.ingestion.loader import Loader

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "uploads"
CHROMA_DIR = ROOT / "data" / "chroma"
# Changing embedding models requires a new collection; uploaded PDFs remain in
# ``uploads/`` and can be rebuilt from the UI.
COLLECTION_NAME = "uploaded_lecture_chunks_onnx"


class RAGService:
    """Single-process RAG service with a persistent Chroma collection."""

    def __init__(self) -> None:
        load_dotenv(ROOT / ".env")
        self.embedding_function = DefaultEmbeddingFunction()
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_function,
        )
        self._lock = Lock()

    def status(self) -> dict[str, int]:
        return {"documents": len(list(DATA_DIR.glob("*.pdf"))), "chunks": self.collection.count()}

    def reindex(self) -> dict[str, int]:
        """Recreate the collection from PDFs the user uploaded to ``uploads/``."""
        with self._lock:
            documents = Loader(DATA_DIR).load_document()
            chunks = Chunking().create_chunks(documents)
            if not chunks:
                raise ValueError("No readable text was found in the lecture PDFs.")

            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.embedding_function,
            )
            for start in range(0, len(chunks), 100):
                batch = chunks[start : start + 100]
                texts = [chunk.page_content for chunk in batch]
                metadata = [self._metadata(chunk.metadata) for chunk in batch]
                ids = [
                    self._chunk_id(text, meta, start + offset)
                    for offset, (text, meta) in enumerate(zip(texts, metadata))
                ]
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadata,
                )
            return self.status()

    def ask(self, question: str, top_k: int = 4) -> dict[str, Any]:
        if not question.strip():
            raise ValueError("A question is required.")
        if self.collection.count() == 0:
            self.reindex()

        result = self.collection.query(
            query_texts=[question],
            n_results=min(max(top_k, 1), self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        sources = [
            {
                "text": text,
                "source": Path(metadata.get("source", "Unknown")).name,
                "page": int(metadata.get("page", 0)) + 1,
                "relevance": round(1 - float(distance), 3),
            }
            for text, metadata, distance in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0])
        ]
        return {"answer": self._generate_answer(question, sources), "sources": sources}

    @staticmethod
    def _metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
        return {key: value for key, value in metadata.items() if isinstance(value, (str, int, float, bool))}

    @staticmethod
    def _chunk_id(text: str, metadata: dict[str, Any], index: int) -> str:
        raw = f"{metadata.get('source', '')}:{metadata.get('page', '')}:{index}:{text}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _generate_answer(self, question: str, sources: list[dict[str, Any]]) -> str:
        context = "\n\n".join(
            f"[{index + 1}] {source['source']}, page {source['page']}: {source['text']}"
            for index, source in enumerate(sources)
        )
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return (
                "I found the passages below, but answer generation is not configured. "
                "Add `GROQ_API_KEY` to `.env` to receive a synthesized answer."
            )
        completion = Groq(api_key=api_key).chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            temperature=0.2,
            max_tokens=700,
            messages=[
                {"role": "system", "content": "Answer only from the lecture context. If it lacks the answer, say so. Cite source numbers such as [1]."},
                {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
            ],
        )
        return completion.choices[0].message.content or "No answer was generated."
