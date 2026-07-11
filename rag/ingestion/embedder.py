import logging
from FlagEmbedding import BGEM3FlagModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BGEM3Embedder:
    """
    Wrapper for the BGE-M3 embedding model.
    """
    def __init__(self, use_fp16=True):
        logging.info("Loading BGE-M3 model...")
        # Load the BGE-M3 model
        self.model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=use_fp16)
        logging.info("BGE-M3 model loaded successfully.")

    def embed_chunks(self, chunks: list):
        """
        Embeds a list of string chunks.
        
        Args:
            chunks (list of str): The text chunks.
            
        Returns:
            np.ndarray: Dense embeddings for each chunk.
        """
        logging.info(f"Embedding {len(chunks)} chunks...")
        # BGE-M3 encode returns a dict containing dense_vecs, sparse_vecs, colbert_vecs
        embeddings = self.model.encode(chunks, return_dense=True, return_sparse=False, return_colbert_vecs=False)
        dense_vecs = embeddings['dense_vecs']
        logging.info("Embedding complete.")
        return dense_vecs
