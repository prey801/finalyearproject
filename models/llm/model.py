import os
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from models.base import BaseModel


class ClinicalLLMModel(BaseModel):
    """
    LLM wrapper using Qwen (via OpenAI-compatible API on DashScope) to act as the Clinical Copilot.
    Responsible for generating reports and explaining predictions.
    NOT responsible for diagnosis.

    Required environment variable:
        DASHSCOPE_API_KEY  — Aliyun DashScope API key for Qwen model access.
    """

    DEFAULT_MODEL = "qwen-plus"
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.client = None
        self.load_model()

    def load_model(self) -> None:
        if OpenAI is None:
            print("Warning: openai package not found. Using stub LLM. Install with: pip install openai")
            return

        api_key = os.environ.get("DASHSCOPE_API_KEY")
        if not api_key:
            print("Warning: DASHSCOPE_API_KEY not set. LLM calls will use stub responses.")
            return

        try:
            self.client = OpenAI(api_key=api_key, base_url=self.BASE_URL)
        except Exception as e:
            print(f"Warning: Failed to initialize Qwen client ({e}). Using stub.")

    def preprocess(self, inputs: Any) -> Any:
        return inputs

    def predict(self, prompt: str) -> str:
        """Send a prompt to Qwen and return the text response."""
        if self.client is None:
            return f"[Stub Response] LLM received prompt of length {len(prompt)}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating content: {e}"

    def generate_report(self, prediction: str, confidence: float) -> str:
        """Generate a clinician-friendly report based on CV model predictions."""
        prompt = f"""You are a Clinical Copilot for a microscopy analysis system.
The computer vision system has made the following prediction:
- Diagnosis: {prediction.capitalize()}
- Confidence: {confidence}%

Write a brief, clinician-friendly report summarizing these findings.
You must state that this is an automated analysis and human review is recommended."""
        return self.predict(prompt)

    def answer_guideline_question(self, question: str, context: str) -> str:
        """Answer a clinical question based on retrieved guideline context (RAG)."""
        prompt = f"""You are a Clinical Copilot. Answer the user's question using ONLY the provided clinical guidelines context.
If the context does not contain the answer, state that you do not have sufficient information.

Context:
{context}

Question:
{question}"""
        return self.predict(prompt)

    def summarize_evidence(self, detection_results: str, parasitemia: float) -> str:
        """Summarize raw detection results into a human-readable explanation."""
        prompt = f"""Summarize the following computer vision evidence into a human-readable explanation for a laboratory professional.

Detection Results: {detection_results}
Parasitemia Level: {parasitemia}%

Focus on explaining what the system found and what it means for the sample."""
        return self.predict(prompt)
