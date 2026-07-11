# MedScope AI - Developer Execution Guide

This document lists the commands required to set up the environment, resolve system-level dependencies, run the database/infrastructure services, train models, start the backend API server, and run automated tests.

---

## 1. Environment Setup

### Option A: Using standard Python Virtual Environment (venv)
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install matching versions first to prevent backtracking loops
pip install "aiobotocore==2.13.0" "boto3==1.34.106" "botocore==1.34.106"

# Install dependencies and utilities
pip install -r backend/requirements.txt
pip install -r models/requirements.txt
pip install pytest qdrant-client
```

### Option B: Using Conda
Ensure you have configured a channel (like `conda-forge` or `defaults`) before creating the environment:
```bash
# Add Conda channels
conda config --add channels defaults
conda config --add channels conda-forge

# Create and activate environment
conda create -n medscope_env python=3.10
conda activate medscope_env

# Install matching versions first to prevent backtracking loops
pip install "aiobotocore==2.13.0" "boto3==1.34.106" "botocore==1.34.106"

# Install dependencies and utilities
pip install -r backend/requirements.txt
pip install -r models/requirements.txt
pip install pytest qdrant-client
```

---

## 2. Troubleshooting: `libGL.so.1` Missing
If you see the error `ImportError: libGL.so.1: cannot open shared object file` when running the application (e.g. inside a Codespace or Docker container), apply one of these solutions:

### Solution A: Install system-level graphics packages (Recommended for Codespaces)
Run this command in the terminal to install the missing OpenGL shared libraries:
```bash
sudo apt-get update && sudo apt-get install -y libgl1
```

### Solution B: Ensure Headless OpenCV is used
Make sure your environment is using the headless variant of OpenCV which does not link to GUI libraries:
```bash
pip uninstall -y opencv-python opencv-python-headless
pip install opencv-python-headless
```

---

## 3. Infrastructure Services (Docker)

Start the database and tracking services (PostgreSQL, Redis, Qdrant Vector Database, MLflow) in the background:

```bash
# Start Docker services
docker-compose up -d db redis qdrant mlflow

# Check running services
docker-compose ps
```

---

## 4. Data Preparation & Splitting

To split the raw NIH malaria dataset into training, validation, and testing sets, run the split script:

```bash
# Ensure raw images are in data/raw/nih_malaria/ before running
python3 -m scripts.split_data
```

---

## 5. Model Training

You can train the primary models and log metrics automatically to MLflow:

### Train YOLOv11 Object Detection Model
```bash
# Start YOLO training on CPU or CUDA
python3 -m scripts.train_yolo --data data/raw/roboflow_malaria/data.yaml --epochs 100 --batch 16 --device cpu
```

### Train Swin Transformer Disease Classification Model
```bash
# Start Swin Transformer training
python3 -m scripts.train_classification --data_dir data/ --epochs 20 --batch 32 --device cpu
```

---

## 6. Run the Backend API Server

Start the FastAPI application. 

### Running with Custom Trained Weights (Production/Diagnostic Mode)
Point the model configuration to your newly trained weights:
```bash
# Set environment variables for weights paths
export YOLO_WEIGHTS_PATH="runs/detect/yolo11n_malaria/weights/best.pt"

# Start the API server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
*Note: If no custom weights are found at `YOLO_WEIGHTS_PATH` (or default `models/yolo/best.pt`), the model will run in a safe stub mode to prevent COCO classes (like pedestrians and cars) from being mapped to malaria diagnoses.*

### Running with Default Fallbacks (Development Mode)
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running with Production Security Constraints
```bash
ENV=production SECRET_KEY="your-custom-secure-key" POSTGRES_PASSWORD="your-secure-db-password" uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

---

## 7. Running Automated Tests

Run unit tests to verify database, ML wrappers, chunking logic, and RAG retrieval pipelines:

```bash
# Run ingestion chunker and RAG LLM tests
TESTING=true pytest tests/test_rag_ingestion.py tests/test_rag_llm.py

# Run primary model wrapper tests (mocks loaded by default)
TESTING=true pytest tests/test_primary_models.py

# Run all test suites
TESTING=true pytest
```
