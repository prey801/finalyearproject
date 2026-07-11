import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from rag.ingestion.loader import DocumentLoader
from rag.ingestion.chunker import TextChunker
from rag.ingestion.embedder import BGEM3Embedder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_ingestion_pipeline(docs_dir: str, collection_name="clinical_guidelines", qdrant_url="http://localhost:6333"):
    """
    End-to-End RAG Ingestion Pipeline.
    Loads docs, chunks them, embeds them, and upserts to Qdrant.
    """
    logging.info(f"Starting RAG Ingestion Pipeline from {docs_dir}")
    
    # 1. Load Documents
    loader = DocumentLoader(docs_dir)
    documents = loader.load_documents()
    
    if not documents:
        logging.warning("No documents found to ingest.")
        return

    # 2. Chunk Documents
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    chunked_docs = chunker.split_documents(documents)
    
    # 3. Embed Chunks
    embedder = BGEM3Embedder()
    chunk_texts = [doc["content"] for doc in chunked_docs]
    embeddings = embedder.embed_chunks(chunk_texts)
    
    # 4. Upsert to Qdrant
    logging.info(f"Connecting to Qdrant at {qdrant_url}...")
    client = QdrantClient(url=qdrant_url)
    
    # Ensure collection exists. BGE-M3 dense vectors are 1024 dimensions.
    if not client.collection_exists(collection_name):
        logging.info(f"Creating Qdrant collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
        
    points = []
    for i, (doc, vector) in enumerate(zip(chunked_docs, embeddings)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector.tolist(),
                payload={
                    "content": doc["content"],
                    **doc["metadata"]
                }
            )
        )
        
    logging.info(f"Upserting {len(points)} points to Qdrant...")
    # Upsert in batches of 100 to avoid payload size issues
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )
        
    logging.info("RAG Ingestion Pipeline complete!")

if __name__ == "__main__":
    # Configurable data directory, defaults to a local folder for guidelines
    # Change as needed or pass via arguments
    target_docs_dir = str(Path(__file__).resolve().parent.parent.parent / "data" / "guidelines")
    
    # Ensure dir exists so it doesn't fail immediately if not created yet
    Path(target_docs_dir).mkdir(parents=True, exist_ok=True)
    
    run_ingestion_pipeline(docs_dir=target_docs_dir)
