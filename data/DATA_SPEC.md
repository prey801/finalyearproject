# DATA_SPEC.md
# MedScope AI Dataset Specification

Version: 1.0

Purpose:
Define all datasets used by MedScope AI, where they should be downloaded from, where they must be stored locally, and how they move through the ML pipeline.

---

# Dataset Overview

For the MVP (Phase 1), only the following datasets are required:

## Required Datasets

### 1. NIH Malaria Dataset

Purpose:

```text
Cell Classification
```

Used For:

```text
Swin Transformer

ResNet50

EfficientNet

ConvNeXt
```

Classes:

```text
Parasitized

Uninfected
```

Download:

```text
https://www.kaggle.com/datasets/iarunava/cell-images-for-detecting-malaria
```

Alternative Source:

```text
https://lhncbc.nlm.nih.gov/LHC-publications/pubs/MalariaDatasets.html
```

Local Installation:

```text
data/raw/nih_malaria/
```

Expected Structure:

data/raw/nih_malaria/

```text
Parasitized/
│
├── C1.png
├── C2.png
└── ...

Uninfected/
│
├── U1.png
├── U2.png
└── ...
```

---

### 2. Roboflow Malaria Detection Dataset

Purpose:

```text
YOLOv11 Object Detection
```

Used For:

```text
Parasite Detection

RBC Detection

Bounding Boxes
```

Download:

```text
https://universe.roboflow.com
```

Search:

```text
Malaria Blood Smear
```

Required Labels:

```text
healthy_rbc

infected_rbc

parasite
```

Local Installation:

```text
data/raw/roboflow_malaria/
```

Expected Structure:

```text
roboflow_malaria/

├── train/
├── valid/
├── test/
├── data.yaml
└── README.roboflow.txt
```

---

# Directory Structure

The data folder should look like:

```text
data/

├── raw/
├── annotations/
├── processed/
├── training/
├── validation/
├── testing/
└── synthetic/
```

---

# RAW DATA

Location:

```text
data/raw/
```

Purpose:

Store datasets exactly as downloaded.

Rules:

✅ Read only

✅ Preserve original files

✅ Preserve original labels

❌ No preprocessing

❌ No resizing

❌ No augmentation

Example:

```text
data/raw/

├── nih_malaria/
├── roboflow_malaria/
└── external/
```

---

# ANNOTATIONS

Location:

```text
data/annotations/
```

Purpose:

Store human-generated labels.

Generated from:

```text
CVAT

Label Studio

Roboflow
```

Structure:

```text
annotations/

├── yolo/
├── coco/
├── masks/
└── reviews/
```

---

## YOLO Annotations

Location:

```text
annotations/yolo/
```

Example:

```text
cell001.txt
cell002.txt
```

Content:

```text
0 0.52 0.44 0.12 0.10
2 0.63 0.35 0.04 0.05
```

Meaning:

```text
class x_center y_center width height
```

Class Definitions:

```text
0 = Healthy RBC

1 = Infected RBC

2 = Parasite
```

---

## COCO Annotations

Location:

```text
annotations/coco/
```

Files:

```text
instances_train.json

instances_val.json
```

Used For:

```text
SAM2

UNet

Advanced Detection
```

---

## Segmentation Masks

Location:

```text
annotations/masks/
```

Example:

```text
cell_001_mask.png

cell_002_mask.png
```

Pixel Definitions:

```text
0 = Background

1 = Healthy RBC

2 = Infected RBC

3 = Parasite
```

---

## Review Corrections

Location:

```text
annotations/reviews/
```

Purpose:

Store expert corrections.

Example:

```json
{
  "image":"cell001.jpg",
  "old_label":"healthy",
  "new_label":"infected",
  "reviewer":"tech001"
}
```

---

# PROCESSED DATA

Location:

```text
data/processed/
```

Purpose:

Stores transformed datasets ready for training.

Generated automatically by preprocessing scripts.

Structure:

```text
processed/

├── resized/
├── normalized/
├── augmented/
├── balanced/
└── features/
```

---

## RESIZED

Location:

```text
processed/resized/
```

Purpose:

Resize images for models.

Sizes:

```text
224x224

384x384

640x640
```

Used By:

```text
Swin Transformer

YOLOv11
```

---

## NORMALIZED

Location:

```text
processed/normalized/
```

Purpose:

Apply normalization.

Methods:

```text
0-1 Scaling

ImageNet Mean/Std
```

---

## AUGMENTED

Location:

```text
processed/augmented/
```

Purpose:

Generate variations.

Methods:

```text
Flip

Rotate

Crop

Brightness

Contrast

Noise
```

Tool:

```text
Albumentations
```

Example:

```text
cell001_flip.png

cell001_rot90.png
```

---

## BALANCED

Location:

```text
processed/balanced/
```

Purpose:

Balance classes.

Methods:

```text
Oversampling

Undersampling

Synthetic Generation
```

---

## FEATURES

Location:

```text
processed/features/
```

Purpose:

Store extracted features.

Examples:

```text
Cell Area

Parasite Area

Cell Count

Texture Features

Morphology Features
```

Future Use:

```text
Explainability

Statistical Analysis
```

---

# TRAINING DATA

Location:

```text
data/training/
```

Purpose:

Data used to train model weights.

Structure:

```text
training/

├── images/
├── labels/
└── metadata.csv
```

Example:

```text
training/images/

img001.png
img002.png
```

Example Labels:

```text
training/labels/

img001.txt
img002.txt
```

Rules:

✅ Used to update weights

✅ Augmentations allowed

✅ Balancing allowed

---

# VALIDATION DATA

Location:

```text
data/validation/
```

Purpose:

Evaluate model after every epoch.

Structure:

```text
validation/

├── images/
├── labels/
└── metadata.csv
```

Used For:

```text
Hyperparameter Tuning

Early Stopping

Model Selection
```

Rules:

✅ Evaluate model

✅ Compare architectures

❌ Never train on validation data

---

# TESTING DATA

Location:

```text
data/testing/
```

Purpose:

Final unbiased evaluation.

Structure:

```text
testing/

├── images/
├── labels/
└── metadata.csv
```

Rules:

✅ Final metrics only

✅ Used once after training

❌ No tuning

❌ No augmentation

❌ No model selection

---

# SYNTHETIC DATA

Location:

```text
data/synthetic/
```

Purpose:

Future dataset expansion.

Methods:

```text
Diffusion Models

GANs

Image Generation Pipelines
```

Structure:

```text
synthetic/

├── diffusion/
├── gan/
└── metadata/
```

Important:

Synthetic images MUST NEVER be included in the test set.

---

# Dataset Split

Use:

```text
70% Training

15% Validation

15% Testing
```

Example:

```text
27,558 Malaria Images

Training:
19,290

Validation:
4,134

Testing:
4,134
```

---

# Data Flow

```text
Downloaded Dataset
        │
        ▼
data/raw/
        │
        ▼
Annotations
        │
        ▼
data/processed/
        │
        ▼
Training Split
        │
        ▼
Validation Split
        │
        ▼
Model Selection
        │
        ▼
Testing Split
        │
        ▼
Final Metrics
```

---

# Storage Summary

```text
data/raw/
        → Original downloaded datasets

data/annotations/
        → Labels and masks

data/processed/
        → Cleaned and transformed data

data/training/
        → Training dataset

data/validation/
        → Validation dataset

data/testing/
        → Final evaluation dataset

data/synthetic/
        → Artificially generated data
```
