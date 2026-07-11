# MedScope AI - Developer Execution Guide

This document lists the commands required to set up the environment, run the database/infrastructure services, start the backend API server, and run automated tests.

---

## 1. Environment Setup

Set up your virtual environment and install backend and model dependencies:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r models/requirements.txt

# Install development and testing utilities
pip install pytest qdrant-client
```

---

## 2. Infrastructure Services (Docker)

Start the required database and tracking services (PostgreSQL, Redis, Qdrant Vector Database, MLflow) in the background:

```bash
# Start Docker services
docker-compose up -d db redis qdrant mlflow

# Check running services
docker-compose ps
```

---

## 3. Data Preparation & Splitting

To split the raw NIH malaria dataset into training, validation, and testing sets, run the split script:

```bash
# Ensure raw images are in data/raw/nih_malaria/ before running
python3 -m scripts.split_data
```

---

## 4. Run the Backend API Server

Start the FastAPI application locally. Note: In development mode, the default fallback credentials will work.

```bash
# Start API server in reload mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Overrides for Production:
```bash
# Start in production mode (requires custom secrets and passwords)
ENV=production SECRET_KEY="your-custom-secure-key" POSTGRES_PASSWORD="your-secure-db-password" uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## 5. Running Automated Tests

Run unit tests to verify database, ML wrappers, chunking logic, and RAG retrieval pipelines:

```bash
# Run ingestion chunker and RAG LLM tests
TESTING=true pytest tests/test_rag_ingestion.py tests/test_rag_llm.py

# Run primary model wrapper tests (mocks loaded by default)
TESTING=true pytest tests/test_primary_models.py

# Run all test suites
TESTING=true pytest
```
