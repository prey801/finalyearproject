# Primary Production Models

These are the models used in production.

## 1. Quality Assessment Model

Purpose:

```text
Reject poor quality microscope images
before analysis.
```

Model:

```text
EfficientNet-B0
```

Input:

```text
RGB Image
224x224
```

Output:

```text
Good
Blurred
Overexposed
Underexposed
Poor Staining
```

Why:

```text
Fast
Lightweight
Excellent transfer learning performance
```

---

## 2. Object Detection Model

Purpose:

```text
Locate cells and parasites
```

Production Model:

```text
YOLOv11
```

Fallback:

```text
YOLOv8
RT-DETR
```

Input:

```text
640x640
```

Output:

```json
{
  "class":"parasite",
  "bbox":[100,120,40,40]
}
```

Classes:

```text
healthy_rbc
infected_rbc
parasite
```

Metrics:

```text
mAP50
mAP50-95
Precision
Recall
```

Target:

```text
mAP50 > 90%
```

---

## 3. Segmentation Model

Purpose:

```text
Extract exact parasite and cell boundaries.
```

Production Model:

```text
SAM2
```

Fallback:

```text
UNet++
```

Output:

```text
Pixel Mask
```

Metrics:

```text
Dice Score
IoU
```

Target:

```text
Dice > 0.85
```

---

## 4. Disease Classification Model

Purpose:

```text
Determine infection status.
```

Production Model:

```text
Swin Transformer Base
```

Input:

```text
224x224 ROI
```

Output:

```text
Healthy
Malaria
```

Metrics:

```text
Accuracy
Recall
Precision
F1
ROC-AUC
```

Target:

```text
Recall > 95%

F1 > 92%
```

Why Swin?

```text
State-of-the-art vision transformer.

Captures local and global image structures.

Performs strongly on medical imaging.
```

---

