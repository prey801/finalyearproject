from typing import List, Dict, Union, Any
import numpy as np
import os
if os.environ.get("TESTING") == "true":
    BGEM3FlagModel = None
else:
    try:
        from FlagEmbedding import BGEM3FlagModel
    except ImportError:
        BGEM3FlagModel = None

class BGEM3EmbeddingModel:
    """
    Embedding model using BGE-M3 for multi-vector representations.
    Provides dense, sparse, and colbert embeddings for clinical guidelines.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3", use_fp16: bool = True, device: str = "cpu"):
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.device = device
        self.model = None
        self.load_model()
        
    def load_model(self) -> None:
        import os
        if BGEM3FlagModel is None or os.environ.get("TESTING") == "true":
            print("Warning: FlagEmbedding package not found or running in test mode. Using stub embedding.")
            return
            
        try:
            self.model = BGEM3FlagModel(
                self.model_name, 
                use_fp16=self.use_fp16, 
                device=self.device
            )
        except Exception as e:
            print(f"Warning: Failed to load BGE-M3 model ({e}). Using stub.")

    def encode(self, texts: List[str]) -> Dict[str, Union[np.ndarray, List[Any]]]:
        """
        Encode a list of texts into multi-vector formats.
        Returns a dictionary containing 'dense_vecs', 'sparse_vecs', and 'colbert_vecs'.
        """
        if self.model is None:
            # Return stub embeddings
            return {
                "dense_vecs": np.random.rand(len(texts), 1024), # Assuming 1024 dim for BGE-M3
                "sparse_vecs": [{"stub": 1.0} for _ in texts],
                "colbert_vecs": [np.random.rand(10, 1024) for _ in texts]
            }
            
        # Encode using BGE-M3 which automatically produces dict of all three types
        embeddings = self.model.encode(
            texts,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=True
        )
        return embeddings
