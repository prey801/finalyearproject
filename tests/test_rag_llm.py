import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock


def test_bge_m3_embedding_stub():
    """Verify the embedding model falls back to stub when TESTING=true or FlagEmbedding is absent."""
    from rag.embeddings.model import BGEM3EmbeddingModel

    model = BGEM3EmbeddingModel()
    texts = ["Clinical guideline on malaria treatment.", "Standard protocol for blood smears."]

    results = model.encode(texts)
    assert "dense_vecs" in results
    assert "sparse_vecs" in results
    assert "colbert_vecs" in results
    assert len(results["dense_vecs"]) == 2
    # Check dense vector dimension
    assert results["dense_vecs"][0].shape[0] == 1024


def test_qdrant_client_stub():
    """Verify Qdrant vector store stub returns valid shaped results."""
    from rag.vector_store.qdrant_client import QdrantVectorStore

    store = QdrantVectorStore()
    texts = ["Guideline 1"]
    dense_vecs = [np.random.rand(1024)]

    # Test insert stub
    success = store.insert(texts, dense_vecs)
    assert success is True

    # Test search stub
    results = store.search(np.random.rand(1024))
    assert len(results) > 0
    assert "score" in results[0]


@pytest.mark.heavy
def test_clinical_llm_model():
    """Verify the ClinicalLLMModel generates a report using a mocked Gemini client."""
    with patch("models.llm.model.genai") as mock_genai:
        from models.llm.model import ClinicalLLMModel

        # Mock the Gemini generative model
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mock clinical report."
        mock_model_instance.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model_instance

        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake-key"}):
            llm = ClinicalLLMModel()
            report = llm.generate_report("malaria", 98.5)
            assert report == "This is a mock clinical report."

            called_prompt = mock_model_instance.generate_content.call_args[0][0]
            assert "Malaria" in called_prompt
            assert "98.5%" in called_prompt
