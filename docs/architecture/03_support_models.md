# Explainability Models

## GradCAM

Purpose:

```text
Explain image regions used in prediction
```

Output:

```text
Heatmap
```

---

## GradCAM++

Purpose:

```text
More precise localization
```

---

## SHAP

Purpose:

```text
Feature attribution
```

---

# Uncertainty Models

## Monte Carlo Dropout

Purpose:

```text
Estimate confidence reliability
```

Method:

```text
20 stochastic forward passes
```

Output:

```json
{
  "confidence":98,
  "uncertainty":12
}
```

---

## Deep Ensemble

Train:

```text
5 independent Swin models
```

Purpose:

```text
Estimate prediction stability
```

---

