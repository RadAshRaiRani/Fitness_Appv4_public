"""
Motivational Agent
Generates a single, punchy, and impactful motivational sentence
that bridges training intensity and nutritional discipline.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


class MotivationalAgent:
    """Agent for generating motivational sentences"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def generate_motivational_sentence(
        self, 
        tone: str = "Energetic",
        day_of_week: Optional[str] = None
    ) -> str:
        """
        Generate a motivational sentence
        
        Args:
            tone: One of "Stoic", "Energetic", "Scientific", or "Empathetic"
            day_of_week: Optional day of the week for context
            
        Returns:
            Single sentence string (max 100 characters)
        """
        # Validate tone
        valid_tones = ["Stoic", "Energetic", "Scientific", "Empathetic"]
        if tone not in valid_tones:
            tone = "Energetic"  # Default
        
        # Build context for day of week if provided
        day_context = ""
        if day_of_week:
            day_context = f"Today is {day_of_week}. "
        
        # Construct prompt
        prompt = f"""Generate a single, punchy, and impactful motivational sentence for fitness.

REQUIREMENTS:
- Maximum 100 characters (strict limit)
- Must mention or imply both physical movement (workout/training) AND fueling (eating/nutrition)
- Tone: {tone}
- Bridge training intensity and nutritional discipline
- No quotes, no intro text - just the sentence itself

EXAMPLES:
- "Train like an athlete, eat like a scientist."
- "Your body is built in the gym but fueled in the kitchen."
- "Honor your effort today with a workout and a meal that counts."

{day_context}Generate a {tone.lower()} sentence that captures both training and nutrition in a powerful, concise way.

IMPORTANT: Return ONLY the sentence string - no quotes, no explanation, no additional text."""

        # Call the LLM
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Extract content
        sentence = ""
        if hasattr(response, 'content'):
            sentence = response.content.strip()
        elif isinstance(response, dict) and 'content' in response:
            sentence = response['content'].strip()
        
        # Remove quotes if present
        sentence = sentence.strip('"\'')
        
        # Ensure it's within character limit
        if len(sentence) > 100:
            # Truncate if needed, but try to get a shorter one
            sentence = sentence[:97] + "..."
        
        return sentence

