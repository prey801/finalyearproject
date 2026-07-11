import pytest
import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag.ingestion.chunker import TextChunker

def test_text_chunker():
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    
    sample_text = "0123456789abcdef" # Length 16
    
    # Expected chunks:
    # 0: "0123456789" (len 10)
    # Next start = 10 - 2 = 8
    # 1: "89abcdef" (len 8)
    
    chunks = chunker.split_text(sample_text)
    
    assert len(chunks) == 2
    assert chunks[0] == "0123456789"
    assert chunks[1] == "89abcdef"

def test_document_chunker():
    chunker = TextChunker(chunk_size=10, chunk_overlap=2)
    
    docs = [
        {"content": "0123456789abcdef", "metadata": {"source": "test.txt"}}
    ]
    
    chunked_docs = chunker.split_documents(docs)
    
    assert len(chunked_docs) == 2
    assert chunked_docs[0]["content"] == "0123456789"
    assert chunked_docs[0]["metadata"]["chunk_index"] == 0
    assert chunked_docs[0]["metadata"]["source"] == "test.txt"
    
    assert chunked_docs[1]["content"] == "89abcdef"
    assert chunked_docs[1]["metadata"]["chunk_index"] == 1
    assert chunked_docs[1]["metadata"]["source"] == "test.txt"
