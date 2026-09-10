# Lecture Chat

Ask questions about PDFs you upload. The application splits PDFs into passages, embeds them locally with `all-MiniLM-L6-v2`, stores those vectors in ChromaDB, retrieves the best matches for a question, and asks Groq to write an answer grounded only in those passages. Each response includes the source text and page number.

## Run locally

1. Install dependencies with `uv sync` (or `pip install -r requirements.txt`).
2. Copy `.env.example` to `.env` and set `GROQ_API_KEY`. The key is optional: without it, the application still searches and shows relevant passages.
3. Start the application with `uv run python main.py`.
4. Open http://localhost:8000. The first question downloads the embedding model and builds the search index, so it may take a little longer.

The existing sample PDFs in `data/Directory/` are not used. From the UI, upload your own PDFs and choose **Rebuild search index** to include them. Uploaded files are stored locally in `uploads/`.

## API

- `GET /api/health` — number of PDFs and indexed chunks.
- `POST /api/chat` — JSON: `{"question": "...", "top_k": 4}`.
- `POST /api/documents` — multipart field: `file` (PDF only).
- `POST /api/reindex` — rebuilds the local Chroma collection.
- `GET /docs` — interactive FastAPI documentation.

## Deploy

The included `Dockerfile` runs the complete application and reads the host-provided `PORT`. `render.yaml` lets Render detect it as a Docker web service.

1. Push this repository to GitHub and create a new Render Blueprint from the repository.
2. Enter `GROQ_API_KEY` as the secret environment variable during setup; do not commit `.env`.
3. Deploy and open the service URL. Test `/api/health`, then ask a question in the UI.

The free Render filesystem is ephemeral: uploaded PDFs and the generated Chroma index disappear after a redeploy or restart. For persistent uploads, attach a persistent disk or move PDFs and the vector database to managed storage before using this in production.
