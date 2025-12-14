# Project financial RAG system (FastAPI + Streamlit + Neo4j + Document Pipeline)

This repository contains:
- A FastAPI backend  
- A Streamlit frontend  
- A Neo4j graph database  
- A local document-processing pipeline (Docling → JSON chunks → Neo4j)

All instructions below are minimal and strictly technical.

---

# 0. Environment Configuration

Create two `.env` files with the following variables:

## 0.1 Root `.env` file (for Docker Compose)

Create `.env` in the repository root with:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j
NEO4J_URI=bolt://neo4j_rag:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Optional: Embedding model (default: text-embedding-3-small)
EMBED_MODEL=text-embedding-3-small
```

## 0.2 Document Pipeline `.env` file

Create `doc-pipeline/.env` with:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Optional: Models
EMBED_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
```

**Important:** 
- Use the same `NEO4J_PASSWORD` in both `.env` files
- For `NEO4J_URI` in root `.env`: use `bolt://neo4j_rag:7687` (container name!) for Docker
- For `NEO4J_URI` in pipeline: use `bolt://localhost:7687` (local connection)

---

# 1. Start the Project (Docker Compose)

From the repository root:

```bash
docker compose up --build
```

This starts:
- Neo4j
- FastAPI backend
- Streamlit frontend

## 2. Document Processing Pipeline (Local)

This step loads PDF files into Neo4j.
It runs locally, not inside Docker.

### 2.1 Go to pipeline directory

```bash
cd doc-pipeline
```

### 2.2 Create Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### 2.3 Convert PDFs → JSON

```bash
python3 -m app.cli convert \
    --pdf-dir ../Data \
    --out-dir ../Data/Chunks \
    --overwrite
```

### 2.4 Process JSON chunks → Neo4j

```bash
python3 -m app.cli ingest \
    --json-dir ../Data/Chunks
```

### 2.5 Create vector indexes in Neo4j

```bash
python3 -m app.cli indexes
```

## 3. Testing the System (Streamlit)

After data ingestion finishes, open Streamlit UI:

```
http://localhost:8501
```

You can now run questions, test retrieval and inspect results.



