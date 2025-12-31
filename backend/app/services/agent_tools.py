"""
Agent Tools for LangGraph
Tools that agents can use to search the web and RAG systems
"""

from typing import List, Dict
from langchain_core.tools import tool
from app.services.web_search_tool import web_search_tool
from app.services.rag_manager import get_diet_rag, get_exercise_rag

# Use lazy-loaded RAG systems (reduces startup memory)


@tool
def search_diet_rag(query: str, k: int = 3) -> str:
    """
    Search for information from diet/nutrition documents.
    
    Args:
        query: Search query about diet, nutrition, meal plans, etc.
        k: Number of results to return (default: 3)
        
    Returns:
        Formatted string with relevant information from diet documents
    """
    diet_rag = get_diet_rag()
    results = diet_rag.search(query, k)
    
    if not results:
        return "No relevant information found in diet documents."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"Result {i} (Relevance: {result['relevance_score']:.2f}):\n"
            f"{result['content']}\n"
        )
    
    return "\n---\n".join(formatted_results)


@tool
def search_exercise_rag(query: str, k: int = 3) -> str:
    """
    Search for information from exercise/workout documents.
    
    Args:
        query: Search query about exercises, workout routines, training, etc.
        k: Number of results to return (default: 3)
        
    Returns:
        Formatted string with relevant information from exercise documents
    """
    exercise_rag = get_exercise_rag()
    results = exercise_rag.search(query, k)
    
    if not results:
        return "No relevant information found in exercise documents."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"Result {i} (Relevance: {result['relevance_score']:.2f}):\n"
            f"{result['content']}\n"
        )
    
    return "\n---\n".join(formatted_results)


@tool
def search_web_diet(query: str, max_results: int = 3) -> str:
    """
    Search the web for current diet/nutrition information.
    
    Args:
        query: Search query about diet, nutrition, health, etc.
        max_results: Maximum number of results (default: 3)
        
    Returns:
        Formatted string with current web search results about diet/nutrition
    """
    results = web_search_tool.search_diet(query, max_results)
    
    if not results:
        return "No web results found for diet query."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"Source {i}: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Summary: {result['snippet']}\n"
        )
    
    return "\n---\n".join(formatted_results)


@tool
def search_web_exercise(query: str, max_results: int = 3) -> str:
    """
    Search the web for current exercise/workout information.
    
    Args:
        query: Search query about exercises, workouts, fitness, training, etc.
        max_results: Maximum number of results (default: 3)
        
    Returns:
        Formatted string with current web search results about exercise/workouts
    """
    results = web_search_tool.search_exercise(query, max_results)
    
    if not results:
        return "No web results found for exercise query."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"Source {i}: {result['title']}\n"
            f"URL: {result['url']}\n"
            f"Summary: {result['snippet']}\n"
        )
    
    return "\n---\n".join(formatted_results)


# List of all available tools
AGENT_TOOLS = [
    search_diet_rag,
    search_exercise_rag,
    search_web_diet,
    search_web_exercise,
]


def get_all_tools() -> List:
    """Get all available tools for agents"""
    return AGENT_TOOLS

