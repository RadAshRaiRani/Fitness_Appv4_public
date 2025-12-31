"""
Agent API Routes
Endpoints for AI agent-based fitness recommendations
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from langchain_openai import ChatOpenAI
from app.services.supervisor_agent import SupervisorAgent
from app.services.motivational_agent import MotivationalAgent
import os
import asyncio
import json


router = APIRouter(prefix="/agents", tags=["Agents"])

# Initialize supervisor agent
# You'll need to set OPENAI_API_KEY environment variable
supervisor = None
motivational_agent = None


def get_supervisor():
    """Get or create supervisor agent"""
    global supervisor
    if supervisor is None:
        print("🔧 Initializing supervisor agent for the first time...")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        supervisor = SupervisorAgent(llm)
        print("✅ Supervisor agent initialized successfully")
    else:
        print("♻️ Reusing existing supervisor agent instance")
    return supervisor


def get_motivational_agent():
    """Get or create motivational agent"""
    global motivational_agent
    if motivational_agent is None:
        print("🔧 Initializing motivational agent for the first time...")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)  # Slightly higher temp for creativity
        motivational_agent = MotivationalAgent(llm)
        print("✅ Motivational agent initialized successfully")
    else:
        print("♻️ Reusing existing motivational agent instance")
    return motivational_agent


class RecommendationRequest(BaseModel):
    body_type: str  # endomorph, ectomorph, mesomorph
    goals: str
    max_iterations: int = 2


class RecommendationResponse(BaseModel):
    body_type: str
    goals: str
    diet_recommendation: str
    exercise_recommendation: str
    markdown: str
    markdown_file: str
    generated_at: str
    duration: str


@router.post("/recommendations/generate", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate comprehensive fitness recommendations
    
    Args:
        body_type: Body type (endomorph/ectomorph/mesomorph)
        goals: User's fitness goals
        max_iterations: Number of refinement iterations (default: 2)
    
    Returns:
        Complete fitness plan with diet and exercise
    """
    try:
        print(f"🚀 [generate_recommendations] Called with body_type={request.body_type}, goals={request.goals[:50]}...")
        # Validate body type
        valid_body_types = ['endomorph', 'ectomorph', 'mesomorph']
        if request.body_type.lower() not in valid_body_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid body_type. Must be one of: {valid_body_types}"
            )
        
        # Get supervisor
        print("👤 Getting supervisor agent...")
        supervisor_agent = get_supervisor()
        
        # Generate recommendations
        print(f"⚙️ Calling supervisor.generate_recommendations()...")
        result = supervisor_agent.generate_recommendations(
            body_type=request.body_type.lower(),
            goals=request.goals,
            max_iterations=request.max_iterations
        )
        print(f"✅ Supervisor.generate_recommendations() completed successfully")
        
        # Create output directory
        output_dir = Path("data/recommendations")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save markdown file
        timestamp = result['generated_at'].replace(':', '-').replace('.', '-')
        filename = f"plan_{request.body_type}_{timestamp}.md"
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result['markdown'])
        
        # Return response
        return RecommendationResponse(
            body_type=result['body_type'],
            goals=result['goals'],
            diet_recommendation=result['diet_recommendation'],
            exercise_recommendation=result['exercise_recommendation'],
            markdown=result['markdown'],
            markdown_file=str(file_path),
            generated_at=result['generated_at'],
            duration=result['duration']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/recommendations/stream")
async def stream_recommendations(request: RecommendationRequest):
    """
    Stream fitness recommendations in real-time
    
    Args:
        body_type: Body type (endomorph/ectomorph/mesomorph)
        goals: User's fitness goals
        max_iterations: Number of refinement iterations (default: 2)
    
    Yields:
        Server-Sent Events with progress updates
    """
    async def event_generator():
        try:
            # Validate body type
            valid_body_types = ['endomorph', 'ectomorph', 'mesomorph']
            if request.body_type.lower() not in valid_body_types:
                yield f"data: {json.dumps({'error': f'Invalid body_type. Must be one of: {valid_body_types}'})}\n\n"
                return
            
            # Send initial message
            yield f"data: {json.dumps({'event': 'start', 'message': 'Starting plan generation...'})}\n\n"
            
            # Get supervisor
            supervisor_agent = get_supervisor()
            
            # Send status updates
            yield f"data: {json.dumps({'event': 'status', 'message': f'Creating workout plan for {request.body_type} body type...'})}\n\n"
            
            # Generate exercise plan
            exercise_state = {
                'body_type': request.body_type.lower(),
                'goals': request.goals,
                'current_iteration': 0,
                'max_iterations': request.max_iterations
            }
            
            yield f"data: {json.dumps({'event': 'status', 'message': 'Generating exercise recommendations...'})}\n\n"
            
            exercise_rec = supervisor_agent.exercise_agent.generate_recommendation(exercise_state)
            
            yield f"data: {json.dumps({'event': 'workout_complete', 'content': exercise_rec})}\n\n"
            yield f"data: {json.dumps({'event': 'status', 'message': 'Generating diet recommendations...'})}\n\n"
            
            # Generate diet plan
            diet_rec = supervisor_agent.diet_agent.generate_recommendation(exercise_state)
            
            yield f"data: {json.dumps({'event': 'diet_complete', 'content': diet_rec})}\n\n"
            yield f"data: {json.dumps({'event': 'complete', 'message': 'Plan generation complete!'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


class MotivationalRequest(BaseModel):
    tone: str = "Energetic"  # Stoic, Energetic, Scientific, or Empathetic
    day_of_week: Optional[str] = None


class MotivationalResponse(BaseModel):
    sentence: str
    tone: str
    character_count: int


@router.post("/motivational/generate", response_model=MotivationalResponse)
async def generate_motivational(request: MotivationalRequest):
    """
    Generate a single, punchy, and impactful motivational sentence
    
    Args:
        tone: One of "Stoic", "Energetic", "Scientific", or "Empathetic" (default: "Energetic")
        day_of_week: Optional day of the week for context
    
    Returns:
        Motivational sentence (max 100 characters)
    """
    try:
        # Validate tone
        valid_tones = ["Stoic", "Energetic", "Scientific", "Empathetic"]
        if request.tone not in valid_tones:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tone. Must be one of: {valid_tones}"
            )
        
        # Get motivational agent
        agent = get_motivational_agent()
        
        # Generate sentence
        sentence = agent.generate_motivational_sentence(
            tone=request.tone,
            day_of_week=request.day_of_week
        )
        
        return MotivationalResponse(
            sentence=sentence,
            tone=request.tone,
            character_count=len(sentence)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating motivational sentence: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if agent system is ready"""
    try:
        # Check if OpenAI API key is set
        api_key = os.getenv('OPENAI_API_KEY')
        has_key = api_key is not None and len(api_key) > 0
        
        return {
            "status": "ready" if has_key else "missing_api_key",
            "openai_configured": has_key,
            "message": "Ready to generate recommendations" if has_key else "Set OPENAI_API_KEY environment variable"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

