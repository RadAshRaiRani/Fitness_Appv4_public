"""
Exercise RAG System
Retrieval Augmented Generation for Exercise/Workout documents
"""

import os
from typing import List, Optional
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.services.document_processor import DocumentProcessor


class ExerciseRAG:
    """RAG system for exercise and workout documents"""
    
    def __init__(self, persist_directory: str = "data/exercise_vectors"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Lazy load embeddings model to reduce startup memory usage
        # Model loads only when first needed (saves ~150MB at startup)
        self.embedding_model = None  # Will be loaded on first use
        self.dimension = 384
        
        # FAISS index
        self.index = None
        self.documents = []
        self.index_path = self.persist_directory / "index.faiss"
        self.docs_path = self.persist_directory / "documents.txt"
        self.processed_files_path = self.persist_directory / "processed_files.txt"
        self.processed_files = []
        
        # Load processed files list
        self._load_processed_files()
        
        # Load existing index if it exists
        self._load_index()
        
        # Document processor
        self.processor = DocumentProcessor()
    
    def _get_embedding_model(self):
        """Lazy load embedding model only when needed (reduces startup memory)"""
        if self.embedding_model is None:
            print("Loading embedding model (this may take a moment on first use)...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded successfully")
        return self.embedding_model
    
    def _load_index(self):
        """Load existing FAISS index if it exists"""
        try:
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                if self.docs_path.exists():
                    with open(self.docs_path, 'r', encoding='utf-8') as f:
                        self.documents = [line.strip() for line in f.readlines()]
                print(f"Loaded existing Exercise RAG index with {len(self.documents)} documents")
        except Exception as e:
            print(f"Could not load existing index: {e}")
    
    def _save_index(self):
        """Save FAISS index and documents"""
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.docs_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.documents))
    
    def _load_processed_files(self):
        """Load list of processed files"""
        try:
            if self.processed_files_path.exists():
                with open(self.processed_files_path, 'r', encoding='utf-8') as f:
                    self.processed_files = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"Could not load processed files list: {e}")
    
    def _save_processed_files(self):
        """Save list of processed files"""
        with open(self.processed_files_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.processed_files))
    
    def add_document(self, file_path: str) -> bool:
        """Add a document to the exercise RAG system"""
        try:
            # Process document
            chunks = self.processor.process_document(file_path)
            
            # Initialize index if needed
            if self.index is None:
                self.index = faiss.IndexFlatL2(self.dimension)
            
            # Add chunks to vector store
            for chunk in chunks:
                # Create embedding
                embedding = self._get_embedding_model().encode(chunk.page_content)
                embedding = np.array([embedding], dtype=np.float32)
                
                # Add to FAISS index
                self.index.add(embedding)
                
                # Store document text
                self.documents.append(chunk.page_content)
            
            # Track processed file
            file_name = Path(file_path).name
            if file_name not in self.processed_files:
                self.processed_files.append(file_name)
                self._save_processed_files()
            
            # Save index
            self._save_index()
            
            print(f"Added {len(chunks)} chunks from {file_path} to Exercise RAG")
            return True
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def search(self, query: str, k: int = 3) -> List[dict]:
        """Search for relevant documents"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        try:
            # Create query embedding
            query_embedding = self._get_embedding_model().encode(query)
            query_embedding = np.array([query_embedding], dtype=np.float32)
            
            # Search
            distances, indices = self.index.search(query_embedding, k)
            
            # Return results
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx < len(self.documents):
                    results.append({
                        'content': self.documents[idx],
                        'distance': float(distance),
                        'relevance_score': float(1 / (1 + distance))
                    })
            
            return results
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def clear(self):
        """Clear all documents from the RAG system"""
        self.index = None
        self.documents = []
        if self.index_path.exists():
            self.index_path.unlink()
        if self.docs_path.exists():
            self.docs_path.unlink()
        print("Exercise RAG cleared")
    
    def get_document_count(self) -> int:
        """Get number of documents in the system"""
        return len(self.documents) if self.documents else 0
    
    def process_folder(self, folder_path: str) -> dict:
        """Process all documents in a folder"""
        from app.services.rag_loader import RAGFolderLoader
        
        loader = RAGFolderLoader(folder_path)
        files = loader.get_unprocessed_files(self.processed_files)
        
        results = {
            "folder": folder_path,
            "total_files": len(files),
            "processed": 0,
            "failed": 0,
            "files": []
        }
        
        for file_path in files:
            try:
                success = self.add_document(str(file_path))
                if success:
                    results["processed"] += 1
                    results["files"].append({"name": file_path.name, "status": "success"})
                else:
                    results["failed"] += 1
                    results["files"].append({"name": file_path.name, "status": "failed"})
            except Exception as e:
                results["failed"] += 1
                results["files"].append({"name": file_path.name, "status": "error", "error": str(e)})
        
        return results

