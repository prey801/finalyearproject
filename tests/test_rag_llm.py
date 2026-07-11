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
    assert results["dense_vecs"][0].shape[0] == 1024


def test_qdrant_client_stub():
    """Verify Qdrant vector store stub returns valid shaped results when no server is available."""
    from rag.vector_store.qdrant_client import QdrantVectorStore

    store = QdrantVectorStore()
    texts = ["Guideline 1"]
    dense_vecs = [np.random.rand(1024)]

    # Test insert stub (no live Qdrant server, so client should be None → stub)
    success = store.insert(texts, dense_vecs)
    assert success is True

    # Test search stub
    results = store.search(np.random.rand(1024))
    assert len(results) > 0
    assert "score" in results[0]


@pytest.mark.heavy
def test_clinical_llm_model():
    """Verify ClinicalLLMModel generates a report via a mocked Qwen/OpenAI client."""
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a mock clinical report."
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    with patch("models.llm.model.OpenAI", return_value=mock_client):
        with patch.dict("os.environ", {"DASHSCOPE_API_KEY": "fake-key"}):
            from models.llm.model import ClinicalLLMModel
            llm = ClinicalLLMModel()
            llm.client = mock_client  # force stub bypass

            report = llm.generate_report("malaria", 98.5)
            assert report == "This is a mock clinical report."

            called_prompt = mock_client.chat.completions.create.call_args[1]["messages"][0]["content"]
            assert "Malaria" in called_prompt
            assert "98.5%" in called_prompt
