from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import base64
import io
import os
import httpx
from PIL import Image
from app.api.v1.agents import get_supervisor
from pathlib import Path
from openai import OpenAI

router = APIRouter()


class ClassificationRequest(BaseModel):
    front_image: str
    left_image: str
    right_image: str


class ClassificationResponse(BaseModel):
    body_type: str
    gender: str
    confidence: Optional[float] = None
    recommendations: Optional[dict] = None


@router.post("/body-type", response_model=ClassificationResponse)
async def classify_body_type(
    front_image: UploadFile = File(...),
    left_image: UploadFile = File(...),
    right_image: UploadFile = File(...)
):
    """
    Classify user's body type based on front, left, and right images.
    
    This endpoint receives three images and returns the classified body type.
    Currently returns a placeholder response as the actual ML model integration is pending.
    """
    print(f"📸 Classification request received")
    try:
        # Validate that all three images are provided
        if not front_image or not left_image or not right_image:
            print(f"❌ Missing images")
            raise HTTPException(status_code=400, detail="All three images are required")
        
        print(f"✅ All images provided")
        
        # Read and validate images
        print(f"📖 Reading image data...")
        front_data = await front_image.read()
        left_data = await left_image.read()
        right_data = await right_image.read()
        print(f"✅ Images read (sizes: {len(front_data)}, {len(left_data)}, {len(right_data)} bytes)")
        
        # Basic validation - check if files are actually images
        try:
            Image.open(io.BytesIO(front_data))
            Image.open(io.BytesIO(left_data))
            Image.open(io.BytesIO(right_data))
            print(f"✅ Images validated as valid image files")
        except Exception as e:
            print(f"❌ Image validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Detect gender and body type using OpenAI Vision API
        print(f"🤖 Starting AI classification (gender + body type)...")
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print(f"⚠️ OPENAI_API_KEY not set, using defaults")
            body_type = "Endomorph"
            gender = "male"
        else:
            try:
                client = OpenAI(api_key=openai_key)
                
                # Convert images to base64 for OpenAI Vision API
                def image_to_base64(image_data):
                    return base64.b64encode(image_data).decode('utf-8')
                
                # Prepare images for OpenAI Vision
                front_b64 = image_to_base64(front_data)
                left_b64 = image_to_base64(left_data)
                right_b64 = image_to_base64(right_data)
                
                # Call OpenAI Vision API to detect gender and body type
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a fitness expert analyzing body images. You MUST respond with ONLY valid JSON, no other text. The JSON must contain: gender (\"male\" or \"female\"), body_type (\"Ectomorph\", \"Mesomorph\", or \"Endomorph\"), and confidence (a number between 0.0 and 1.0). Example: {\"gender\": \"male\", \"body_type\": \"Mesomorph\", \"confidence\": 0.85}"
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Analyze these three body images (front, left, right views) and determine the gender and body type. You MUST respond with ONLY valid JSON, no markdown, no code blocks, just the raw JSON object. Format: {\"gender\": \"male\" or \"female\", \"body_type\": \"Ectomorph\" or \"Mesomorph\" or \"Endomorph\", \"confidence\": 0.0-1.0}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{front_b64}"
                                    }
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{left_b64}"
                                    }
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{right_b64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                # Parse the response
                import json
                import re
                
                result_text = response.choices[0].message.content.strip()
                print(f"🔍 Raw OpenAI response: {result_text[:200]}...")  # Debug: show first 200 chars
                
                # Remove markdown code blocks if present
                if result_text.startswith("```"):
                    # Extract content from code blocks
                    match = re.search(r'```(?:json)?\s*(.*?)\s*```', result_text, re.DOTALL)
                    if match:
                        result_text = match.group(1).strip()
                    else:
                        # Fallback: try to extract between first and last ```
                        parts = result_text.split("```")
                        if len(parts) >= 3:
                            result_text = parts[1]
                            if result_text.startswith("json"):
                                result_text = result_text[4:]
                            result_text = result_text.strip()
                
                # Try to extract JSON object if there's extra text
                json_match = re.search(r'\{[^{}]*"gender"[^{}]*"body_type"[^{}]*\}', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(0)
                
                result_text = result_text.strip()
                print(f"🔍 Parsed JSON text: {result_text[:200]}...")  # Debug
                
                # Parse JSON response
                try:
                    result = json.loads(result_text)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {str(e)}")
                    print(f"❌ Failed to parse: {result_text}")
                    raise ValueError(f"Invalid JSON response from AI: {str(e)}")
                
                # Handle case where result might be a list (shouldn't happen, but just in case)
                if isinstance(result, list):
                    print(f"⚠️ Warning: Response is a list with {len(result)} elements")
                    if len(result) > 0 and isinstance(result[0], dict):
                        result = result[0]
                        print(f"✅ Using first element from list")
                    else:
                        raise ValueError("Invalid response format: list without dict elements")
                
                # Ensure result is a dictionary
                if not isinstance(result, dict):
                    print(f"❌ Result is not a dict, it's: {type(result)}")
                    print(f"❌ Result value: {result}")
                    raise ValueError(f"Invalid response format: expected dict, got {type(result)}")
                
                # Extract values with validation
                gender = result.get("gender", "male")
                if gender and isinstance(gender, str):
                    gender = gender.lower().strip()
                    if gender not in ["male", "female"]:
                        print(f"⚠️ Invalid gender '{gender}', defaulting to 'male'")
                        gender = "male"
                else:
                    gender = "male"
                
                body_type = result.get("body_type", "Endomorph")
                if body_type and isinstance(body_type, str):
                    body_type = body_type.strip()
                    # Normalize body type names
                    body_type_lower = body_type.lower()
                    if "ectomorph" in body_type_lower:
                        body_type = "Ectomorph"
                    elif "mesomorph" in body_type_lower:
                        body_type = "Mesomorph"
                    elif "endomorph" in body_type_lower:
                        body_type = "Endomorph"
                    else:
                        print(f"⚠️ Invalid body type '{body_type}', defaulting to 'Endomorph'")
                        body_type = "Endomorph"
                else:
                    body_type = "Endomorph"
                
                confidence = result.get("confidence", 0.85)
                if isinstance(confidence, (int, float)):
                    confidence = float(confidence)
                    if confidence < 0 or confidence > 1:
                        confidence = 0.85
                else:
                    confidence = 0.85
                
                print(f"✅ AI Classification complete:")
                print(f"   Gender: {gender}")
                print(f"   Body Type: {body_type}")
                print(f"   Confidence: {confidence}")
                
            except Exception as e:
                print(f"⚠️ AI classification failed: {str(e)}")
                print(f"   Using default values")
                import traceback
                traceback.print_exc()
                # Fallback to defaults
                body_type = "Endomorph"
                gender = "male"
                confidence = 0.5
        
        # Generate fitness recommendations using the agent system
        try:
            print(f"🚀 Starting agent system call for body type: {body_type}")
            print(f"🔑 Checking OPENAI_API_KEY...")
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            print(f"✅ OPENAI_API_KEY is set (length: {len(openai_key)} chars)")
            
            # Call the agent system directly (same process, no HTTP needed)
            print(f"📞 Calling get_supervisor()...")
            supervisor_agent = get_supervisor()
            print(f"✅ Supervisor agent initialized")
            
            goals = f"Create a personalized 4-week fitness plan for a {body_type} body type focusing on balanced training and nutrition"
            print(f"📋 Generating recommendations with goals: {goals[:50]}...")
            
            result = supervisor_agent.generate_recommendations(
                body_type=body_type.lower(),
                goals=goals,
                max_iterations=2
            )
            
            print(f"✅ Agent system returned recommendations")
            print(f"📊 Result keys: {list(result.keys())}")
            print(f"🍎 Diet recommendation length: {len(result.get('diet_recommendation', ''))} chars")
            print(f"💪 Exercise recommendation length: {len(result.get('exercise_recommendation', ''))} chars")
            
            # Save markdown file
            output_dir = Path("data/recommendations")
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = result['generated_at'].replace(':', '-').replace('.', '-')
            filename = f"plan_{body_type.lower()}_{timestamp}.md"
            file_path = output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result['markdown'])
            
            return JSONResponse(
                status_code=200,
                content={
                    "body_type": body_type,
                    "gender": gender,
                    "confidence": confidence,
                    "workout_plan": result.get("exercise_recommendation", ""),
                    "meal_plan": result.get("diet_recommendation", ""),
                    "message": "Classification and plan generation completed successfully!"
                }
            )
        except Exception as e:
            # If agent system is not available, return basic classification
            print(f"❌ Agent system call failed: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=200,
                content={
                    "body_type": body_type,
                    "gender": gender,
                    "confidence": confidence,
                    "workout_plan": "Plan generation temporarily unavailable. Please try again later.",
                    "meal_plan": "Plan generation temporarily unavailable. Please try again later.",
                    "message": "Body type classified successfully. Plan generation service is unavailable."
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error but return a response instead of raising HTTPException
        # This prevents the 502 error and allows the frontend to handle it gracefully
        print(f"❌ Classification endpoint error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Return a proper JSON response instead of raising exception
        return JSONResponse(
            status_code=200,
            content={
                "body_type": "Endomorph",  # Default fallback
                "gender": "male",  # Default fallback
                "confidence": 0.0,
                "workout_plan": f"Classification encountered an error: {str(e)}. Please try again.",
                "meal_plan": f"Classification encountered an error: {str(e)}. Please try again.",
                "message": "Classification failed. Please try again later."
            }
        )


@router.get("/health")
async def classify_health():
    """Health check for classification endpoint"""
    return {
        "status": "healthy",
        "endpoint": "/api/v1/classify/body-type",
        "method": "POST",
        "description": "Classify user body type from front, left, and right images"
    }

