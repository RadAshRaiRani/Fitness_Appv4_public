"""
Exercise Agent
Responsible for generating workout/exercise recommendations
"""

from typing import Dict
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.services.agent_tools import search_exercise_rag, search_web_exercise
from app.services.agent_state import AgentState


class ExerciseAgent:
    """Agent for exercise and workout recommendations"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [search_exercise_rag, search_web_exercise]
        self.agent = create_react_agent(llm, self.tools)
    
    def generate_recommendation(self, state: Dict) -> str:
        """
        Generate exercise recommendation based on body type and goals
        
        Args:
            state: Current agent state
            
        Returns:
            Exercise recommendation string
        """
        body_type = state.get('body_type', 'unknown')
        goals = state.get('goals', 'general fitness')
        iteration = state.get('current_iteration', 0)
        
        # Construct prompt for the agent
        prompt = f"""You are an expert fitness trainer and exercise physiologist.

Generate a comprehensive 4-week workout plan for a {body_type} with the following goals: {goals}

Your plan should include:
1. Weekly workout structure (4 weeks, 28 days)
2. Exercise selection tailored to {body_type} body type
3. Sets, reps, and rest periods for each exercise
4. Progressive overload plan
5. Weekly frequency and split
6. Cardio recommendations
7. Form and safety considerations
8. Recovery and rest day recommendations

Use the search tools available to find relevant information:
- search_exercise_rag: Search uploaded exercise/workout documents
- search_web_exercise: Search current web information about exercises/workouts

This is iteration {iteration + 1} of refinement. Provide detailed, actionable workout recommendations.
Format your response as a comprehensive training program that can be followed for 4 weeks.
"""
        
        # Call the agent
        response = self.agent.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        
        # Extract content from the last message
        if response.get('messages'):
            last_message = response['messages'][-1]
            if hasattr(last_message, 'content'):
                return last_message.content
            elif isinstance(last_message, dict) and 'content' in last_message:
                return last_message['content']
        
        return "Exercise recommendation could not be generated."

