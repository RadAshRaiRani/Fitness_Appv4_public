"""
RAG API Routes
Endpoints for document upload and retrieval
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
from app.services.rag_manager import get_diet_rag, get_exercise_rag

router = APIRouter(prefix="/rag", tags=["RAG"])

# Use lazy-loaded RAG systems from main.py (reduces startup memory)

# Directory for uploaded files
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/diet/upload")
async def upload_diet_document(file: UploadFile = File(...)):
    """
    Upload a diet/nutrition document
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"diet_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Add to Diet RAG (lazy loads if needed)
        diet_rag = get_diet_rag()
        success = diet_rag.add_document(str(file_path))
        
        if success:
            return JSONResponse(
                content={
                    "message": "Document uploaded successfully",
                    "filename": file.filename,
                    "total_documents": diet_rag.get_document_count()
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to process document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercise/upload")
async def upload_exercise_document(file: UploadFile = File(...)):
    """
    Upload an exercise/workout document
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"exercise_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Add to Exercise RAG (lazy loads if needed)
        exercise_rag = get_exercise_rag()
        success = exercise_rag.add_document(str(file_path))
        
        if success:
            return JSONResponse(
                content={
                    "message": "Document uploaded successfully",
                    "filename": file.filename,
                    "total_documents": exercise_rag.get_document_count()
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to process document")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diet/search")
async def search_diet(query: str, k: int = 3):
    """
    Search in diet/nutrition documents
    
    Args:
        query: Search query
        k: Number of results to return (default: 3)
    """
    try:
        diet_rag = get_diet_rag()
        results = diet_rag.search(query, k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercise/search")
async def search_exercise(query: str, k: int = 3):
    """
    Search in exercise/workout documents
    
    Args:
        query: Search query
        k: Number of results to return (default: 3)
    """
    try:
        exercise_rag = get_exercise_rag()
        results = exercise_rag.search(query, k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diet/stats")
async def diet_stats():
    """Get statistics about diet RAG system"""
    diet_rag = get_diet_rag()
    return {
        "document_count": diet_rag.get_document_count(),
        "type": "diet",
        "status": "active" if diet_rag.get_document_count() > 0 else "empty"
    }


@router.get("/exercise/stats")
async def exercise_stats():
    """Get statistics about exercise RAG system"""
    exercise_rag = get_exercise_rag()
    return {
        "document_count": exercise_rag.get_document_count(),
        "type": "exercise",
        "status": "active" if exercise_rag.get_document_count() > 0 else "empty"
    }


@router.delete("/diet/clear")
async def clear_diet():
    """Clear all diet documents"""
    diet_rag = get_diet_rag()
    diet_rag.clear()
    return {"message": "Diet RAG cleared"}


@router.delete("/exercise/clear")
async def clear_exercise():
    """Clear all exercise documents"""
    exercise_rag = get_exercise_rag()
    exercise_rag.clear()
    return {"message": "Exercise RAG cleared"}


@router.post("/diet/process-folder")
async def process_diet_folder():
    """Process all documents from data/diet_documents/ folder"""
    diet_rag = get_diet_rag()
    folder_path = "data/diet_documents"
    results = diet_rag.process_folder(folder_path)
    return JSONResponse(content=results)


@router.post("/exercise/process-folder")
async def process_exercise_folder():
    """Process all documents from data/exercise_documents/ folder"""
    exercise_rag = get_exercise_rag()
    folder_path = "data/exercise_documents"
    results = exercise_rag.process_folder(folder_path)
    return JSONResponse(content=results)


@router.get("/diet/list-files")
async def list_diet_files():
    """List files in diet documents folder"""
    from app.services.rag_loader import RAGFolderLoader
    loader = RAGFolderLoader("data/diet_documents")
    return loader.list_files()


@router.get("/exercise/list-files")
async def list_exercise_files():
    """List files in exercise documents folder"""
    from app.services.rag_loader import RAGFolderLoader
    loader = RAGFolderLoader("data/exercise_documents")
    return loader.list_files()


@router.get("/web/search")
async def web_search(query: str, max_results: int = 5):
    """Search the web using DuckDuckGo"""
    from app.services.web_search_tool import web_search_tool
    results = web_search_tool.search(query, max_results)
    return {"query": query, "results": results, "count": len(results)}


@router.get("/web/search/diet")
async def web_search_diet(query: str, max_results: int = 5):
    """Search the web for diet/nutrition information"""
    from app.services.web_search_tool import web_search_tool
    results = web_search_tool.search_diet(query, max_results)
    return {"query": query, "results": results, "count": len(results)}


@router.get("/web/search/exercise")
async def web_search_exercise(query: str, max_results: int = 5):
    """Search the web for exercise/workout information"""
    from app.services.web_search_tool import web_search_tool
    results = web_search_tool.search_exercise(query, max_results)
    return {"query": query, "results": results, "count": len(results)}

