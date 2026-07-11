import os
from typing import Dict, Any
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from models.base import BaseModel

class ClinicalLLMModel(BaseModel):
    """
    LLM wrapper using Gemini API to act as the Clinical Copilot.
    Responsible for generating reports and explaining predictions.
    NOT responsible for diagnosis.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self.model = None
        self.load_model()

    def load_model(self) -> None:
        if genai is None:
            print("Warning: google-generativeai package not found. Using stub LLM.")
            return

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment. LLM calls will fail or use stub.")
        else:
            genai.configure(api_key=api_key)

        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini model ({e}). Using stub.")

    def preprocess(self, inputs: Any) -> Any:
        # Just return the raw prompt
        return inputs

    def predict(self, prompt: str) -> str:
        """Raw prediction endpoint."""
        if self.model is None:
            return f"[Stub Response] LLM received prompt of length {len(prompt)}"
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating content: {e}"

    def generate_report(self, prediction: str, confidence: float) -> str:
        """
        Generate a clinician-friendly report based on CV model predictions.
        """
        prompt = f"""
        You are a Clinical Copilot for a microscopy analysis system.
        The computer vision system has made the following prediction:
        - Diagnosis: {prediction.capitalize()}
        - Confidence: {confidence}%
        
        Write a brief, clinician-friendly report summarizing these findings.
        Remember: You must state that this is an automated analysis and human review is recommended.
        """
        return self.predict(prompt)

    def answer_guideline_question(self, question: str, context: str) -> str:
        """
        Answer a clinical question based on retrieved guideline context (RAG).
        """
        prompt = f"""
        You are a Clinical Copilot. Answer the user's question using ONLY the provided clinical guidelines context.
        If the context does not contain the answer, state that you do not have sufficient information.

        Context:
        {context}

        Question:
        {question}
        """
        return self.predict(prompt)

    def summarize_evidence(self, detection_results: str, parasitemia: float) -> str:
        """
        Summarize the raw evidence from GradCAM and YOLO into a human-readable explanation.
        """
        prompt = f"""
        Summarize the following computer vision evidence into a human-readable explanation for a laboratory professional.
        
        Detection Results: {detection_results}
        Parasitemia Level: {parasitemia}%
        
        Focus on explaining what the system found and what it means for the sample.
        """
        return self.predict(prompt)
