"""
RAG Manager - Centralized lazy loading for RAG systems
This prevents circular import issues
"""

from app.services.diet_rag import DietRAG
from app.services.exercise_rag import ExerciseRAG

# Lazy-loaded RAG instances
_diet_rag = None
_exercise_rag = None


def get_diet_rag():
    """Get or create DietRAG instance (lazy loading)"""
    global _diet_rag
    if _diet_rag is None:
        _diet_rag = DietRAG()
    return _diet_rag


def get_exercise_rag():
    """Get or create ExerciseRAG instance (lazy loading)"""
    global _exercise_rag
    if _exercise_rag is None:
        _exercise_rag = ExerciseRAG()
    return _exercise_rag

