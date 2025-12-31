"""
Document Processing Service
Handles loading and processing of documents for RAG systems
"""

import os
from typing import List, Optional
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)

class DocumentProcessor:
    """Processes documents for RAG ingestion"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    def load_document(self, file_path: str) -> List:
        """Load a document based on its extension"""
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        try:
            if extension == '.pdf':
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif extension == '.txt' or extension == '.md':
                loader = TextLoader(file_path)
                documents = loader.load()
            elif extension == '.docx':
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            else:
                raise ValueError(f"Unsupported file type: {extension}")
            
            return documents
        except Exception as e:
            raise Exception(f"Error loading document: {str(e)}")
    
    def split_documents(self, documents: List) -> List:
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
    
    def process_document(self, file_path: str) -> List:
        """Process a document: load and split"""
        documents = self.load_document(file_path)
        chunks = self.split_documents(documents)
        return chunks

