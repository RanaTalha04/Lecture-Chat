"""FastAPI routes for the lecture-chat application."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.rag.service import DATA_DIR, RAGService
from src.logger import logging

router = APIRouter(prefix="/api", tags=["lecture-chat"])
service = RAGService()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)


@router.get("/health")
def health() -> dict:
    return {"status": "ok", **service.status()}


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    try:
        return service.ask(payload.question, payload.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/reindex")
def reindex() -> dict:
    try:
        return {"message": "Lecture index rebuilt.", **service.reindex()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files can be uploaded.")
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        target = DATA_DIR / Path(file.filename).name
        with target.open("wb") as output:
            shutil.copyfileobj(file.file, output)
        return {"message": f"Uploaded {target.name}. Reindex to include it in chat."}
    except OSError as exc:
        logging.exception("Could not save uploaded PDF")
        raise HTTPException(
            status_code=500,
            detail="The server could not save this file. Check the Render service logs.",
        ) from exc
    finally:
        await file.close()
