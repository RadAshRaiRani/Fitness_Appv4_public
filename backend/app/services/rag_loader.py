"""
RAG Folder Loader
Automatically processes documents from folder uploads
"""

from pathlib import Path
from typing import List
import os


class RAGFolderLoader:
    """Load and process documents from folders"""
    
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.folder_path.mkdir(parents=True, exist_ok=True)
        self.supported_extensions = {'.pdf', '.docx', '.txt', '.md'}
    
    def get_files(self) -> List[Path]:
        """Get all supported files in the folder"""
        files = []
        if not self.folder_path.exists():
            return files
        
        for file_path in self.folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                files.append(file_path)
        
        return files
    
    def get_unprocessed_files(self, processed_files: List[str]) -> List[Path]:
        """Get files that haven't been processed yet"""
        all_files = self.get_files()
        processed_set = set(processed_files)
        
        return [f for f in all_files if f.name not in processed_set]
    
    def list_files(self) -> dict:
        """List all files in the folder"""
        files = self.get_files()
        return {
            "folder_path": str(self.folder_path),
            "file_count": len(files),
            "files": [
                {
                    "name": f.name,
                    "size": f.stat().st_size,
                    "extension": f.suffix,
                    "path": str(f)
                }
                for f in files
            ]
        }

