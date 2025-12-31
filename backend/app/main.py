"""
FastAPI Application - Fitness App Backend
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.services.rag_manager import get_diet_rag, get_exercise_rag
from app.api.v1 import rag as rag_router
from app.api.v1 import agents as agents_router
from app.api.v1 import classify as classify_router
from app.api.v1 import users as users_router
from app.api.v1 import admin as admin_router
from app.api.v1 import admin_auth as admin_auth_router
from app.database import init_database

# Load environment variables from .env file
load_dotenv()

# Initialize database
init_database()

app = FastAPI(
    title="Fitness App API",
    description="Backend API for Fitness App with RAG systems",
    version="1.0.0"
)

# CORS middleware - configure for production
# Get allowed origins from environment variable, default to all for development
cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001"
)

# Split by comma and clean whitespace
allowed_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Log CORS configuration (without exposing full URLs)
print(f"🌐 CORS configured for {len(allowed_origins)} origin(s)")
if allowed_origins:
    print(f"   Origins: {', '.join([f'{origin[:20]}...' if len(origin) > 20 else origin for origin in allowed_origins])}")

# In production, add your Vercel URL to CORS_ORIGINS env var in Render
# Example: CORS_ORIGINS=https://fitness-app-six-self.vercel.app,https://fitness-app-rajubholanis-projects.vercel.app,http://localhost:3000

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-loaded RAG systems are managed by rag_manager module
# This prevents circular import issues and reduces startup memory

# Create document folders
from pathlib import Path
Path("data/diet_documents").mkdir(parents=True, exist_ok=True)
Path("data/exercise_documents").mkdir(parents=True, exist_ok=True)

# Include routers
app.include_router(rag_router.router)
app.include_router(agents_router.router)
app.include_router(classify_router.router, prefix="/api/v1/classify", tags=["classification"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["users"])
app.include_router(admin_router.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(admin_auth_router.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fitness App API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    diet = get_diet_rag()
    exercise = get_exercise_rag()
    return {
        "status": "healthy",
        "diet_rag_documents": diet.get_document_count(),
        "exercise_rag_documents": exercise.get_document_count()
    }

