from typing import List, Dict, Any, Optional
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import VectorParams, Distance, PointStruct
except ImportError:
    QdrantClient = None
import uuid

class QdrantVectorStore:
    """
    Interface for the Qdrant Vector Database.
    Handles storing and retrieving embeddings (dense/sparse) for RAG.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "clinical_guidelines"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = None
        self._connect()
        
    def _connect(self) -> None:
        if QdrantClient is None:
            print("Warning: qdrant_client package not found. Using stub vector store.")
            return
            
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            self._ensure_collection()
        except Exception as e:
            print(f"Warning: Failed to connect to Qdrant ({e}). Ensure Docker container is running.")
            self.client = None
            
    def _ensure_collection(self) -> None:
        """Create the collection if it doesn't exist. BGE-M3 dense uses 1024 dim."""
        if self.client and not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )
            
    def insert(self, texts: List[str], dense_embeddings: List[Any], metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        if self.client is None:
            print("Stub: Inserted vectors.")
            return True
            
        if metadatas is None:
            metadatas = [{} for _ in texts]
            
        points = []
        for i, (text, emb, meta) in enumerate(zip(texts, dense_embeddings, metadatas)):
            # Combine payload with original text
            payload = {**meta, "text": text}
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=emb.tolist() if hasattr(emb, "tolist") else emb,
                    payload=payload
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return True
        
    def search(self, query_vector: Any, limit: int = 5) -> List[Dict[str, Any]]:
        if self.client is None:
            print("Stub: Searching vectors.")
            return [{"text": "Stub guideline result", "score": 0.99}]
            
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist() if hasattr(query_vector, "tolist") else query_vector,
            limit=limit
        )
        
        results = []
        for hit in search_result:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "text": hit.payload.get("text", "") if hit.payload else ""
            })
            
        return results
