# AI Models Specification

---

# Model Hierarchy

The system uses multiple AI models.

Each model has a clearly defined responsibility.

```text
Microscope Image
        │
        ▼
Image Quality Model
        │
        ▼
YOLOv11 Detection Model
        │
        ▼
SAM2 Segmentation Model
        │
        ▼
Swin Transformer Classification Model
        │
        ▼
Quantification Engine
        │
        ▼
Explainability Engine
        │
        ▼
RAG + Clinical LLM
```

---

# Final Production Stack

```text
Quality Assessment
    ↓
EfficientNet-B0

Detection
    ↓
YOLOv11

Segmentation
    ↓
SAM2

Classification
    ↓
Swin Transformer

Explainability
    ↓
GradCAM + SHAP

Uncertainty
    ↓
MC Dropout

Retrieval
    ↓
BGE-M3 + Qdrant

Clinical Copilot
    ↓
Qwen 2.5 7B

API
    ↓
FastAPI

Frontend
    ↓
Next.js
Backend
    ↓
FastAPI

Database
    ↓
PostgreSQL

Vector Search
    ↓
Qdrant

MLOps
    ↓
MLflow + DVC

Monitoring
    ↓
Prometheus + Grafana

Deployment
    ↓
Docker + Docker Compose

Future Scale
    ↓
Kubernetes
```

---

# Technology Stack

## Frontend

```text
Next.js 15+

React

TypeScript

TailwindCSS

ShadCN UI

Axios

React Query
```

---

## Backend

```text
FastAPI

Pydantic

SQLAlchemy

Alembic

Celery

Redis
```

---

## Computer Vision

```text
PyTorch

OpenCV

Albumentations

Ultralytics YOLO

timm

SAM2
```

---

## Explainability

```text
GradCAM

GradCAM++

SHAP

Integrated Gradients
```

---

## Vector Search

```text
Qdrant
```

Alternatives:

```text
ChromaDB

Weaviate
```

---

## Large Language Models

```text
Qwen 2.5 7B Instruct
```

Alternative:

```text
Llama 3.2 8B

Phi-4 Mini

Mistral 7B
```

---

## MLOps

```text
MLflow

DVC

Weights & Biases

GitHub Actions
```

---

## Monitoring

```text
Prometheus

Grafana

Sentry
```

---

## Infrastructure

```text
Docker

Docker Compose

Nginx

Kubernetes (Future)
```

---

