# Repository Structure

```text
medscope-ai/

├── frontend/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── schemas/
│   ├── database/
│   └── auth/
│
├── models/
│   ├── quality/
│   ├── yolo/
│   ├── segmentation/
│   ├── classification/
│   ├── explainability/
│   └── uncertainty/
│
├── rag/
│   ├── ingestion/
│   ├── embeddings/
│   └── vector_store/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── annotations/
│   ├── training/
│   ├── validation/
│   └── testing/
│
├── mlops/
│
├── monitoring/
│
├── docker/
│
├── scripts/
│
├── tests/
│
├── notebooks/
│
├── docs/
│
└── deployments/
```

---

# Non-Functional Requirements

## Performance

```text
Single Image Analysis < 10 seconds

YOLO Inference < 1 second

Classification < 2 seconds

Report Generation < 5 seconds
```

---

## Availability

```text
99% uptime
```

---

## Scalability

```text
Support 100+ concurrent analysis requests
```

---

## Reliability

```text
Automatic retries

Model fallback support

Graceful degradation
```

---

# Definition of Done

The project is complete when:

- ✅ YOLOv11 detects infected cells
- ✅ SAM2 generates segmentation masks
- ✅ Swin Transformer classifies malaria
- ✅ Parasitemia is automatically calculated
- ✅ GradCAM explanations are generated
- ✅ Uncertainty scores are generated
- ✅ FastAPI endpoints are functional
- ✅ PostgreSQL stores prediction history
- ✅ Qdrant powers RAG retrieval
- ✅ Qwen generates clinical reports
- ✅ Human review workflow is implemented
- ✅ MLflow tracks experiments
- ✅ Docker deployment succeeds
- ✅ Monitoring dashboards are functional
- ✅ Accuracy and recall targets are met

---

# Final System Output Example

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
    "llm": "qwen2.5_7b_v1"
  }
}
```

---

# Clinical Disclaimer

```text
This platform is a Clinical Decision Support System.

It is intended to assist laboratory professionals
and clinicians.

The platform does not provide autonomous diagnoses.

All outputs must be reviewed and confirmed by
qualified healthcare personnel before clinical use.
```