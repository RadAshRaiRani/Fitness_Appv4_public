"""
User Data API - Store and retrieve user fitness data
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import (
    create_user,
    save_classification,
    save_plans,
    get_user_latest_plan,
    get_user_classifications,
    user_exists
)

router = APIRouter()


class SaveClassificationRequest(BaseModel):
    clerk_user_id: str
    body_type: str
    gender: str
    workout_plan: str
    meal_plan: str


class SavePlanRequest(BaseModel):
    clerk_user_id: str
    classification_id: int
    workout_plan: str
    meal_plan: str


@router.post("/classify")
async def save_classification_result(request: SaveClassificationRequest):
    """
    Save or update body type classification and fitness plans for a user
    
    This endpoint:
    1. Creates user if doesn't exist
    2. Updates existing classification if user has one, otherwise creates new
    3. Updates existing fitness plans if they exist, otherwise creates new
    
    When an existing user re-uploads images:
    - Their body type and gender will be updated
    - Their workout plan and meal plan will be updated
    - Timestamps will reflect the new upload
    """
    try:
        # Create or get user
        user_id = create_user(
            clerk_user_id=request.clerk_user_id,
            email=None,  # Could get from Clerk if needed
            name=None
        )
        
        # Save classification
        classification_id = save_classification(
            user_id=user_id,
            body_type=request.body_type,
            gender=request.gender
        )
        
        # Save plans
        plan_id = save_plans(
            user_id=user_id,
            classification_id=classification_id,
            workout_plan=request.workout_plan,
            meal_plan=request.meal_plan
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "classification_id": classification_id,
            "plan_id": plan_id,
            "message": "Classification and plans saved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/latest")
async def get_latest_plans(clerk_user_id: str):
    """Get user's latest fitness plan"""
    try:
        result = get_user_latest_plan(clerk_user_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No plans found for this user"
            )
        
        return {
            "success": True,
            "plan": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classifications")
async def get_classification_history(clerk_user_id: str):
    """Get all user's classifications"""
    try:
        classifications = get_user_classifications(clerk_user_id)
        
        return {
            "success": True,
            "classifications": classifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exists")
async def check_user_exists(clerk_user_id: str):
    """Check if user exists in database"""
    try:
        exists = user_exists(clerk_user_id)
        
        return {
            "exists": exists,
            "clerk_user_id": clerk_user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for users API"""
    return {
        "status": "healthy",
        "endpoint": "/api/v1/users",
        "operations": [
            "POST /classify - Save classification and plans",
            "GET /plans/latest - Get latest plan",
            "GET /classifications - Get classification history",
            "GET /exists - Check if user exists"
        ]
    }

