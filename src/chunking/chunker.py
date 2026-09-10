import sys
from src.logger import logging
from src.exception import CustomException
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Chunking:
    
    def create_chunks(self, documents):
            
            try: 
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, 
                    chunk_overlap=200
                )
                chunks = splitter.split_documents(documents)
                logging.info(f"Created {len(chunks)} chunks")
                
                return chunks
                
            except Exception as e:
                
                logging.error("Error while creating chunks")
                
                raise CustomException(e, sys)