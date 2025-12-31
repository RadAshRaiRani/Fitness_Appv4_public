"""
Agent State Management
Manages the state for the multi-agent recommendation system
"""

from typing import List, Dict, Optional, TypedDict
from langgraph.graph.message import AnyMessage, add_messages


class AgentState(TypedDict):
    """State for the multi-agent system"""
    
    # Input
    body_type: str  # endomorph, ectomorph, mesomorph
    goals: str  # user's fitness goals
    current_iteration: int  # current refinement iteration
    max_iterations: int  # total iterations to perform
    
    # Agent outputs
    diet_recommendation: str  # diet agent's recommendation
    exercise_recommendation: str  # exercise agent's recommendation
    
    # Web search results
    diet_web_results: str
    exercise_web_results: str
    
    # RAG search results
    diet_rag_results: str
    exercise_rag_results: str
    
    # Final output
    final_recommendation: Optional[str]
    markdown_output: Optional[str]
    
    # Messages for LangGraph
    messages: List[AnyMessage]


def create_initial_state(body_type: str, goals: str, max_iterations: int = 2) -> AgentState:
    """Create initial state for agent system"""
    return AgentState(
        body_type=body_type,
        goals=goals,
        current_iteration=0,
        max_iterations=max_iterations,
        diet_recommendation="",
        exercise_recommendation="",
        diet_web_results="",
        exercise_web_results="",
        diet_rag_results="",
        exercise_rag_results="",
        final_recommendation=None,
        markdown_output=None,
        messages=[]
    )

