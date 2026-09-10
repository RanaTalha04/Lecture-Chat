"""Local embedding model used by the retrieval pipeline."""

import os


from langchain_huggingface import HuggingFaceEmbeddings


class Embedding:
    """Create a reusable, local sentence-transformer embedding model."""

    def get_embedding_model(self) -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            # This public model needs no Hugging Face token. Explicitly disabling
            # token lookup also avoids a stale endpoint token in a user's .env.
            model_kwargs={"device": "cpu", "token": False},
            encode_kwargs={"normalize_embeddings": True},
        )
