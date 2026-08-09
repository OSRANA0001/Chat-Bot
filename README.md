JAY MATAJI

Chat-bot ( Sahayak ) is a locally-running RAG (Retrieval-Augmented Generation) chatbot that answers questions about C.U. Shah University using only the content of official university documents — no cloud APIs, no internet dependency once set up, and no answers invented outside what the documents actually say.

## What is this?

Sahayak is a full-stack chatbot assistant. Feed it one or more PDF documents (student handbook, admissions brochure, fee circular, etc.), and it answers natural-language questions about them — entirely on your own machine, using a locally-run open-source language model instead of a paid API like OpenAI or Gemini.

## How it works

This project uses **Retrieval-Augmented Generation (RAG)**, a technique that grounds an LLM's answers in real documents instead of letting it answer purely from memory:

1. **Ingest** — PDF(s) placed in `backend/documents/` are loaded and split into small, overlapping text chunks.
2. **Embed** — each chunk is converted into a vector (a list of numbers representing its meaning) using Ollama's `nomic-embed-text` model.
3. **Store** — those vectors are saved locally in a ChromaDB vector database.
4. **Retrieve** — when a question comes in, it's embedded the same way, and ChromaDB returns the most semantically relevant chunks from the documents.
5. **Generate** — those chunks, plus the original question, are handed to a local `gemma3:4b` language model (via Ollama), which is instructed to answer using only that retrieved context.
6. **Serve** — a Flask REST API wraps this whole pipeline, and a React frontend sends user questions to it and displays the answers in a chat interface.

Because the model only ever sees the actual retrieved text from your documents, it can't invent facts, policies, or numbers — and if the documents don't cover a question, it says so instead of guessing.

## Tech stack

**Backend:** Python, Flask, Flask-CORS, LangChain (`langchain-core`, `langchain-community`, `langchain-text-splitters`, `langchain-ollama`, `langchain-chroma`), pypdf

**AI / ML:** Ollama (local LLM runtime), Gemma 3 (4B) for generation, Nomic Embed Text for embeddings, ChromaDB as the vector store

**Frontend:** React 18, Vite 5, plain CSS (no framework)

## Features

- Chat-style interface for asking questions
- Answers grounded strictly in the provided PDF(s)
- Fully offline after setup — no API keys, no per-query cost
- Works with one PDF or several dropped into the same folder

## Project structure

```
RAG/
├── backend/
│   ├── main.py            # original CLI version (kept for reference)
│   ├── vector.py          # loads PDFs, chunks + embeds them into ChromaDB
│   ├── server.py          # Flask API + the chatbot's persona/prompt
│   ├── requirements.txt
│   └── documents/         # put your PDF(s) here
└── frontend/
    ├── src/
    │   ├── App.jsx         # chat UI + logic
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Setup

**1. Add your document** — place your PDF(s) in `backend/documents/`.

**2. Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
ollama pull gemma3:4b
ollama pull nomic-embed-text
python server.py
```

**3. Frontend** (in a separate terminal)
```
cd frontend
npm install
npm run dev
```

Open the local URL Vite prints (usually `http://localhost:5173`) and start asking questions.

## Notes

- [Ollama](https://ollama.com) must be installed and running in the background.
- The first run takes a little longer while the PDF(s) get embedded into `backend/chrome_langchain_db/`. Delete that folder if you swap in a new or updated PDF, so it re-embeds from scratch.
- Requires Windows 10/11, macOS, or Linux (not Windows 7), with at least 8GB RAM recommended.

## About

Built as a semester project for C.U. Shah College of Engineering and Technology.
