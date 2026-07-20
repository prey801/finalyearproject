## this project is not finished its under development thank you 
# MedScope AI — Clinical Decision Support Platform for Malaria Diagnosis

MedScope AI is a state-of-the-art clinical decision support system designed to assist laboratory professionals and clinicians by automating microscopy analysis for malaria diagnosis. It integrates advanced computer vision detection and classification models, explainability engines, uncertainty quantification, and a Retrieval-Augmented Generation (RAG) clinical copilot to generate verified diagnostic reports.

---

## 🔬 Model Pipeline Hierarchy

The system processes microscope images sequentially through a series of specialized models to ensure high accuracy, accountability, and clinical utility:

```
Microscope Image
       │
       ▼
[ Image Quality Model ] (EfficientNet-B0) -> Validates image quality
       │
       ▼
[ Detection Model ]     (YOLOv11)        -> Identifies cells and potential infected areas
       │
       ▼
[ Segmentation Model ]  (SAM2)           -> Extracts cell boundaries/masks
       │
       ▼
[ Classification Model ](Swin Transformer)-> Classifies malaria species/stages
       │
       ▼
[ Quantification Eng. ]                  -> Automatically calculates Parasitemia rate
       │
       ▼
[ Explainability Eng. ] (GradCAM / SHAP)  -> Visualizes model focus and features
       │
       ▼
[ Clinical Copilot ]    (GPT-4o)         -> Evaluates via RAG and writes draft report
```

---

## 🛠️ Technology Stack & Architecture

### 📊 Production Stack
* **Quality Assessment:** EfficientNet-B0
* **Cell Detection:** Ultralytics YOLOv11
* **Cell Segmentation:** SAM2 (Segment Anything Model 2)
* **Malaria Classification:** Swin Transformer (`timm`)
* **Explainability:** GradCAM, GradCAM++, SHAP, Integrated Gradients
* **Uncertainty Quantification:** Monte Carlo (MC) Dropout
* **Knowledge Retrieval:** BGE-M3 Embeddings + Qdrant Vector DB
* **Clinical Assistant:** GPT-4o (via GitHub Models API)
* **Backend API:** FastAPI (Python)
* **Web Frontend:** Next.js (React, TypeScript, TailwindCSS, ShadCN UI)
* **Databases:** PostgreSQL (Relational metadata/history), Qdrant (Vector storage)
* **MLOps & Tracking:** MLflow, DVC (Data Version Control)
* **Infrastructure:** Docker & Docker Compose, Celery, Redis (Asynchronous Task Queue)
* **Monitoring:** Prometheus & Grafana

---

## 📁 Repository Structure

```text
medscope-ai/
├── frontend/             # Next.js 15+ Web application
├── backend/              # FastAPI Application (API, Services, Database schemas, Auth)
├── models/               # ML models (Quality, YOLO, SAM2, Swin, SHAP/GradCAM, Uncertainty)
│   ├── experimental/     # Unintegrated stubs for future research (GraphSAGE, Federated Learning)
│   ├── foundation/       # Unintegrated stubs for future research (BiomedCLIP, DINOv2)
│   └── baselines/        # Unintegrated stubs for future research (ResNet, EfficientNet)
├── rag/                  # RAG pipeline (Ingestion, BGE-M3 embeddings, Qdrant vector store)
├── data/                 # Raw/Processed datasets & split folders (NIH Malaria, Roboflow)
├── mlops/                # MLOps configuration, MLflow and DVC tracking
├── monitoring/           # Prometheus and Grafana dashboards/provisions
├── docker/               # Docker configuration files
├── scripts/              # Data splitting, YOLO & classification training scripts
├── tests/                # Automated pytest suite
├── notebooks/            # Diagnostic and exploratory Jupyter notebooks
├── docs/                 # Architectural specifications
└── deployments/          # Deployment-related scripts and manifests
```

---

## 🚀 Getting Started

### 1. Environment Setup

You can set up the project dependencies using a standard Python Virtual Environment (`venv`) or `Conda`.

#### Option A: Using Standard Python Virtual Environment (`venv`)
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install matching versions first to prevent backtracking loops
pip install "aiobotocore==2.13.0" "boto3==1.34.106" "botocore==1.34.106"

# Install backend and models requirements
pip install -r backend/requirements.txt
pip install -r models/requirements.txt
pip install pytest qdrant-client
```

#### Option B: Using Conda
```bash
# Configure Conda channels
conda config --add channels defaults
conda config --add channels conda-forge

# Create and activate environment
conda create -n medscope_env python=3.10
conda activate medscope_env

# Install matching versions first to prevent backtracking loops
pip install "aiobotocore==2.13.0" "boto3==1.34.106" "botocore==1.34.106"

# Install requirements
pip install -r backend/requirements.txt
pip install -r models/requirements.txt
pip install pytest qdrant-client
```

### 2. Troubleshooting `libGL.so.1` (OpenGL dependency)
If you encounter `ImportError: libGL.so.1: cannot open shared object file` in Codespaces or Docker containers, apply one of these solutions:

* **Solution A (Ubuntu/Debian):**
  ```bash
  sudo apt-get update && sudo apt-get install -y libgl1
  ```
* **Solution B (Python level fallback):**
  ```bash
  pip uninstall -y opencv-python opencv-python-headless
  pip install opencv-python-headless
  ```

### 3. Running Infrastructure Services
Use Docker Compose to launch PostgreSQL, Redis, Qdrant Vector Database, Celery Worker, and MLflow in the background:
```bash
# Start Docker services
docker-compose up -d db redis qdrant mlflow

# Check running services
docker-compose ps
```

### 4. Data Preparation & Model Training

```bash
# 1. Split raw NIH malaria dataset (place raw images in data/raw/nih_malaria/ first)
python3 -m scripts.split_data

# 2. Train YOLOv11 Object Detection Model
python3 -m scripts.train_yolo --data data/raw/roboflow_malaria/data.yaml --epochs 100 --batch 16 --device cpu

# 3. Train Swin Transformer Disease Classification Model
python3 -m scripts.train_classification --data_dir data/ --epochs 20 --batch 32 --device cpu
```

### 5. Running the Backend API Server & Celery Worker

Start the FastAPI application in the environment of your choice:

* **Diagnostic Mode (Custom Weights):**
  ```bash
  export YOLO_WEIGHTS_PATH="runs/detect/yolo11n_malaria/weights/best.pt"
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
  ```
* **Development Mode (Stub / Fallbacks):**
  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
  ```
* **Production Mode (with Security constraints):**
  ```bash
  ENV=production SECRET_KEY="your-custom-secure-key" POSTGRES_PASSWORD="your-secure-db-password" uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```

### 6. Running Automated Tests
Execute the test suites to verify ingestion, ML pipelines, and API integrations:
```bash
# Run ingestion chunker and RAG LLM tests
TESTING=true python3 -m pytest tests/test_rag_ingestion.py tests/test_rag_llm.py

# Run primary model wrapper tests (mocks loaded by default)
TESTING=true python3 -m pytest tests/test_primary_models.py

# Run all test suites
TESTING=true python3 -m pytest
```

---

## 📋 System Output Format

FastAPI endpoints return analysis payloads matching the following schema:

```json
{
  "sample_id": "MAL-001",
  "quality": "good",
  "prediction": "malaria",
  "confidence": 98.2,
  "uncertainty": 10.4,
  "infected_cells": 36,
  "total_cells": 1200,
  "parasitemia": 3.0,
  "heatmap_path": "/heatmaps/MAL-001.png",
  "report": "Automated microscopy analysis detected findings consistent with malaria infection. Estimated parasitemia is 3.0%. Human review is recommended.",
  "review_required": true,
  "model_versions": {
    "quality": "efficientnet_b0_v1",
    "detection": "yolov11_v1",
    "segmentation": "sam2_v1",
    "classification": "swin_base_v1",
    "llm": "gpt-4o"
  }
}
```

---

## ⚠️ Clinical Disclaimer

> [!WARNING]
> **Clinical Decision Support Only**  
> This platform is a Clinical Decision Support System (CDSS) intended to assist laboratory professionals and clinicians. It does not provide autonomous medical diagnoses. All model outputs, heatmaps, and LLM-generated reports must be reviewed and confirmed by qualified healthcare personnel before any clinical use.
