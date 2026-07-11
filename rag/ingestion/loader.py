import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentLoader:
    """
    Loads text and markdown documents from a directory for RAG ingestion.
    """
    def __init__(self, directory_path: str):
        self.directory_path = Path(directory_path)

    def load_documents(self):
        """
        Reads all .txt and .md files in the configured directory.
        Returns a list of dicts with 'content' and 'metadata'.
        """
        documents = []
        if not self.directory_path.exists() or not self.directory_path.is_dir():
            logging.error(f"Directory not found: {self.directory_path}")
            return documents

        valid_extensions = {".txt", ".md"}
        
        for file_path in self.directory_path.rglob("*"):
            if file_path.suffix.lower() in valid_extensions:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        documents.append({
                            "content": content,
                            "metadata": {
                                "source": str(file_path.name),
                                "path": str(file_path)
                            }
                        })
                except Exception as e:
                    logging.error(f"Failed to read {file_path}: {e}")
                    
        logging.info(f"Loaded {len(documents)} documents from {self.directory_path}")
        return documents
