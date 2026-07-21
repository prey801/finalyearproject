import os
import logging
from models.llm.model import ClinicalLLMModel
from rag.embeddings.model import BGEM3EmbeddingModel
from rag.vector_store.qdrant_client import QdrantVectorStore

class RAGService:
    def __init__(self, device: str = "cpu"):
        qdrant_host = os.environ.get("QDRANT_HOST", "localhost")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
        self.device = device
        self.embedding_model = BGEM3EmbeddingModel(device=device)
        self.qdrant_store = QdrantVectorStore(host=qdrant_host, port=qdrant_port)
        self.llm = ClinicalLLMModel()

    def generate_clinical_report(self, prediction: str, confidence: float, parasitemia: float, total_cells: int = None) -> str:
        # 1. Retrieve guidelines context using RAG
        query = f"Malaria treatment guidelines for {prediction} case with {parasitemia:.2f}% parasitemia"
        context = ""
        
        try:
            emb_res = self.embedding_model.encode([query])
            if "dense_vecs" in emb_res and len(emb_res["dense_vecs"]) > 0:
                query_vector = emb_res["dense_vecs"][0]
                results = self.qdrant_store.search(query_vector, limit=2)
                
                guideline_texts = []
                for res in results:
                    text = res.get("text", "")
                    if text:
                        guideline_texts.append(text)
                
                if guideline_texts:
                    context = "\n---\n".join(guideline_texts)
        except Exception as e:
            logging.warning(f"RAG retrieval failed: {e}. Falling back to default generation.")
            
        # 2. Use the LLM with the context to generate the report
        detection_note = ""
        if total_cells == 0:
            detection_note = (
                "\n        IMPORTANT: The cell-detection model located ZERO cells in this "
                "image, so parasitemia could NOT actually be measured. Do not describe this "
                "as a clean/negative result — explicitly state that cell detection failed "
                "(likely due to poor image quality, framing, or an unsupported image type) "
                "and that the slide should be re-imaged or reviewed manually rather than "
                "trusting this prediction."
            )

        prompt = f"""
        You are a Clinical Copilot for a microscopy analysis system.
        The computer vision system has made the following prediction:
        - Diagnosis: {prediction.capitalize()}
        - Confidence: {confidence}%
        - Parasitemia: {parasitemia:.2f}%
        {detection_note}

        Using the following clinical guidelines context (if available):
        {context if context else 'No context available.'}

        Write a brief, clinician-friendly report summarizing these findings and recommending next steps based on the guidelines.
        Remember: You must state that this is an automated analysis and human review is recommended.
        """
        
        report = self.llm.predict(prompt)
        
        # Append standard disclaimer and parasitemia
        final_report = f"{report}\n\nEstimated parasitemia is {parasitemia:.1f}%. Human review is recommended."
        return final_report
