# Knowledge & Retrieval Models

## Embedding Model

Production:

```text
BGE-M3
```

Alternatives:

```text
E5-Large
Nomic Embed
```

Purpose:

```text
Convert guidelines into vectors
```

---

## Vector Database

Production:

```text
Qdrant
```

Alternatives:

```text
ChromaDB
Weaviate
```

---

# LLM Models

The LLM is NOT responsible for diagnosis.

The LLM explains predictions.

---

## Production LLM

```text
Qwen 2.5 7B Instruct
```

Why:

```text
Strong reasoning

Efficient inference

Good medical report generation
```

---

## Alternative

```text
Llama 3.2 8B
```

---

## Lightweight Deployment

```text
Phi-4 Mini
```

---

## LLM Tasks

### Report Generation

Input:

```json
{
  "prediction":"malaria",
  "confidence":98
}
```

Output:

```text
Clinician-friendly report
```

---

### Guideline Question Answering

Example:

```text
What WHO recommendations apply?
```

---

### Evidence Summarization

Input:

```text
GradCAM

Detection Results

Parasitemia
```

Output:

```text
Human-readable explanation
```

---

