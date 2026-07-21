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
    
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "clinical_guidelines", vector_size: int = 1024):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
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
        """Create the collection if it doesn't exist."""
        if self.client and not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )

    @staticmethod
    def _point_id(id_str: str) -> str:
        """Qdrant point IDs must be unsigned ints or UUIDs — derive a stable
        UUID from an arbitrary caller-supplied id (e.g. a sample_id) so the
        same logical entity always maps to the same point and can be
        retrieved later by that id."""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, id_str))

    def insert(self, texts: List[str], dense_embeddings: List[Any], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> bool:
        if self.client is None:
            print("Stub: Inserted vectors.")
            return True

        if metadatas is None:
            metadatas = [{} for _ in texts]

        points = []
        for i, (text, emb, meta) in enumerate(zip(texts, dense_embeddings, metadatas)):
            # Combine payload with original text
            payload = {**meta, "text": text}
            point_id = self._point_id(ids[i]) if ids else str(uuid.uuid4())
            points.append(
                PointStruct(
                    id=point_id,
                    vector=emb.tolist() if hasattr(emb, "tolist") else emb,
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return True

    def retrieve_vector(self, id_str: str) -> Optional[Any]:
        """Fetch a previously-inserted point's vector by the id passed to
        insert()'s `ids` argument. Returns None if not found or Qdrant is
        unavailable (stub mode)."""
        if self.client is None:
            return None
        results = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[self._point_id(id_str)],
            with_vectors=True,
        )
        if not results:
            return None
        return results[0].vector
        
    def search(self, query_vector: Any, limit: int = 5) -> List[Dict[str, Any]]:
        if self.client is None:
            print("Stub: Searching vectors.")
            return [{"text": "Stub guideline result", "score": 0.99}]

        # qdrant-client >= 1.7 uses query_points() — .search() was removed.
        vec = query_vector.tolist() if hasattr(query_vector, "tolist") else query_vector
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=vec,
            limit=limit,
        )

        results = []
        for hit in response.points:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "text": hit.payload.get("text", "") if hit.payload else "",
            })

        return results
