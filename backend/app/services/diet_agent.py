"""
Diet Agent
Responsible for generating diet/nutrition recommendations
"""

from typing import Dict
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from app.services.agent_tools import search_diet_rag, search_web_diet
from app.services.agent_state import AgentState


class DietAgent:
    """Agent for diet and nutrition recommendations"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [search_diet_rag, search_web_diet]
        self.agent = create_react_agent(llm, self.tools)
    
    def generate_recommendation(self, state: Dict) -> str:
        """
        Generate diet recommendation based on body type and goals
        
        Args:
            state: Current agent state
            
        Returns:
            Diet recommendation string
        """
        body_type = state.get('body_type', 'unknown')
        goals = state.get('goals', 'general fitness')
        iteration = state.get('current_iteration', 0)
        
        # Construct prompt for the agent
        prompt = f"""You are an expert nutritionist and dietitian. 

Generate a comprehensive 4-week diet plan for a {body_type} with the following goals: {goals}

Your plan should include:
1. Meal plan structure for 28 days
2. Daily macronutrient targets (protein, carbs, fats)
3. Meal timing and frequency recommendations
4. Specific food recommendations tailored to {body_type} body type
5. Hydration guidelines
6. Supplement suggestions (if applicable)

Use the search tools available to find relevant information:
- search_diet_rag: Search uploaded diet/nutrition documents
- search_web_diet: Search current web information about diet/nutrition

This is iteration {iteration + 1} of refinement. Provide detailed, actionable recommendations.
Format your response as a comprehensive meal plan that can be followed for 4 weeks.
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
        
        return "Diet recommendation could not be generated."

