import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextChunker:
    """
    Splits text documents into manageable overlapping chunks.
    Fully configurable token/character lengths.
    """
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """
        Args:
            chunk_size (int): Number of characters per chunk.
            chunk_overlap (int): Number of overlapping characters between chunks.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str):
        """
        Splits a single text string into chunks.
        """
        if not text:
            return []
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= text_length:
                break
            # Advance start pointer, subtracting overlap
            start = end - self.chunk_overlap
            
        return chunks

    def split_documents(self, documents: list):
        """
        Splits a list of document dicts into chunk dicts.
        """
        chunked_docs = []
        for doc in documents:
            content = doc["content"]
            metadata = doc["metadata"]
            
            chunks = self.split_text(content)
            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    "content": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i
                    }
                })
                
        logging.info(f"Split {len(documents)} documents into {len(chunked_docs)} chunks.")
        return chunked_docs
