import sys
from pathlib import Path
from src.logger import logging
from src.exception import CustomException
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader


class Loader:
    
    def __init__(self, directory: str | Path | None = None):
        directory = directory or Path(__file__).resolve().parents[2] / "data" / "Directory"
        self.loader = DirectoryLoader(
            path=str(directory),
            glob="*.pdf",
            loader_cls=PyMuPDFLoader
        )

    def load_document(self):
        try: 
            documents = self.loader.load()
            logging.info(f"Loaded {len(documents)} documents")
            
            return documents
        
        except Exception as e:
            logging.error("Error while loading documents")
            raise CustomException(e, sys)
