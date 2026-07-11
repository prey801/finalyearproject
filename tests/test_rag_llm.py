import unittest
from unittest.mock import patch, MagicMock
import numpy as np

class TestRAGAndLLMModels(unittest.TestCase):
    
    def test_bge_m3_embedding_stub(self):
        # Without FlagEmbedding installed, it should gracefully fall back to stub
        from rag.embeddings.model import BGEM3EmbeddingModel
        
        model = BGEM3EmbeddingModel()
        texts = ["Clinical guideline on malaria treatment.", "Standard protocol for blood smears."]
        
        results = model.encode(texts)
        self.assertIn("dense_vecs", results)
        self.assertIn("sparse_vecs", results)
        self.assertIn("colbert_vecs", results)
        
        self.assertEqual(len(results["dense_vecs"]), 2)
        # Check dense vector dimension
        self.assertEqual(results["dense_vecs"][0].shape[0], 1024)

    def test_qdrant_client_stub(self):
        from rag.vector_store.qdrant_client import QdrantVectorStore
        
        store = QdrantVectorStore()
        
        texts = ["Guideline 1"]
        dense_vecs = [np.random.rand(1024)]
        
        # Test insert stub
        success = store.insert(texts, dense_vecs)
        self.assertTrue(success)
        
        # Test search stub
        results = store.search(np.random.rand(1024))
        self.assertTrue(len(results) > 0)
        self.assertIn("score", results[0])

    @patch('models.llm.model.genai')
    def test_clinical_llm_model(self, mock_genai):
        from models.llm.model import ClinicalLLMModel
        
        # Mock the Gemini generative model
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mock clinical report."
        mock_model_instance.generate_content.return_value = mock_response
        
        mock_genai.GenerativeModel.return_value = mock_model_instance
        
        # Setup environment to bypass the missing API key warning
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'fake-key'}):
            llm = ClinicalLLMModel()
            
            # Test report generation
            report = llm.generate_report("malaria", 98.5)
            self.assertEqual(report, "This is a mock clinical report.")
            
            # Verify the prompt contained the key information
            called_prompt = mock_model_instance.generate_content.call_args[0][0]
            self.assertIn("Malaria", called_prompt)
            self.assertIn("98.5%", called_prompt)

if __name__ == '__main__':
    unittest.main()
