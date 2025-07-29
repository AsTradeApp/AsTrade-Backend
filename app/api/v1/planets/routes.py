"""API routes for planets and quiz system"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional, List
import structlog

from app.models.planets import (
    PlanetsListResponse, PlanetDetailResponse, QuizDetailResponse,
    QuizSubmissionRequest, QuizSubmissionResponse, QuizStartResponse,
    UserProgressOverview, QuizStartRequest
)
from app.models.responses import SuccessResponse, ErrorResponse
from app.services.planets_service import planets_service
from app.services.auth import get_current_user_id, get_optional_user_id

logger = structlog.get_logger()
router = APIRouter()


@router.get("/", response_model=PlanetsListResponse, summary="Get all planets")
async def get_planets(
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get all planets with optional user progress information.
    
    If user is authenticated, returns planets with user progress data.
    If user is not authenticated, returns basic planet information.
    """
    try:
        logger.info("Getting planets list", user_id=user_id)
        result = await planets_service.get_all_planets(user_id)
        return result
    except Exception as e:
        logger.error("Error getting planets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve planets")


@router.get("/{planet_id}", response_model=PlanetDetailResponse, summary="Get planet details")
async def get_planet_detail(
    planet_id: int = Path(..., description="Planet ID"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get detailed information about a specific planet including its quizzes.
    
    If user is authenticated, includes user progress information.
    """
    try:
        logger.info("Getting planet detail", planet_id=planet_id, user_id=user_id)
        result = await planets_service.get_planet_detail(planet_id, user_id)
        return result
    except Exception as e:
        logger.error("Error getting planet detail", planet_id=planet_id, error=str(e))
        if "No rows" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Planet not found")
        raise HTTPException(status_code=500, detail="Failed to retrieve planet details")


@router.get("/quiz/{quiz_id}", response_model=QuizDetailResponse, summary="Get quiz details")
async def get_quiz_detail(
    quiz_id: int = Path(..., description="Quiz ID"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get detailed information about a specific quiz including its questions.
    
    Questions are returned without correct answers for security.
    If user is authenticated, includes user progress information.
    """
    try:
        logger.info("Getting quiz detail", quiz_id=quiz_id, user_id=user_id)
        result = await planets_service.get_quiz_detail(quiz_id, user_id)
        return result
    except Exception as e:
        logger.error("Error getting quiz detail", quiz_id=quiz_id, error=str(e))
        if "No rows" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Quiz not found")
        raise HTTPException(status_code=500, detail="Failed to retrieve quiz details")


@router.post("/quiz/{quiz_id}/start", response_model=QuizStartResponse, summary="Start a quiz")
async def start_quiz(
    quiz_id: int = Path(..., description="Quiz ID"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Start a quiz session for the authenticated user.
    
    Creates or updates user progress tracking and returns quiz questions.
    Questions are returned without correct answers.
    """
    try:
        logger.info("Starting quiz", quiz_id=quiz_id, user_id=user_id)
        result = await planets_service.start_quiz(quiz_id, user_id)
        return result
    except Exception as e:
        logger.error("Error starting quiz", quiz_id=quiz_id, user_id=user_id, error=str(e))
        if "No rows" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Quiz not found")
        raise HTTPException(status_code=500, detail="Failed to start quiz")


@router.post("/quiz/submit", response_model=QuizSubmissionResponse, summary="Submit quiz answers")
async def submit_quiz(
    submission: QuizSubmissionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Submit answers for a quiz and get results.
    
    Calculates score, updates user progress, and returns detailed results
    including correct answers and explanations.
    """
    try:
        logger.info("Submitting quiz", quiz_id=submission.quiz_id, user_id=user_id, 
                   answer_count=len(submission.answers))
        result = await planets_service.submit_quiz(submission, user_id)
        return result
    except Exception as e:
        logger.error("Error submitting quiz", quiz_id=submission.quiz_id, 
                    user_id=user_id, error=str(e))
        if "No rows" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Quiz not found")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")


@router.get("/progress/overview", response_model=UserProgressOverview, summary="Get user progress overview")
async def get_user_progress_overview(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get complete overview of user progress across all planets and quizzes.
    
    Returns summary statistics and progress information.
    """
    try:
        logger.info("Getting user progress overview", user_id=user_id)
        result = await planets_service.get_user_progress_overview(user_id)
        return result
    except Exception as e:
        logger.error("Error getting user progress overview", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve progress overview")


@router.get("/quiz/{quiz_id}/leaderboard", summary="Get quiz leaderboard")
async def get_quiz_leaderboard(
    quiz_id: int = Path(..., description="Quiz ID"),
    limit: int = Query(10, ge=1, le=100, description="Number of top entries to return"),
    user_id: Optional[str] = Depends(get_optional_user_id)
):
    """
    Get leaderboard for a specific quiz.
    
    Returns top performers sorted by best score and completion percentage.
    """
    try:
        logger.info("Getting quiz leaderboard", quiz_id=quiz_id, limit=limit)
        result = await planets_service.get_quiz_leaderboard(quiz_id, limit)
        return SuccessResponse(data=result)
    except Exception as e:
        logger.error("Error getting quiz leaderboard", quiz_id=quiz_id, error=str(e))
        if "No rows" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Quiz not found")
        raise HTTPException(status_code=500, detail="Failed to retrieve leaderboard")


# Health check for planets service
@router.get("/health", summary="Planets service health check")
async def planets_health_check():
    """
    Health check endpoint for planets service.
    
    Verifies that the service can connect to the database.
    """
    try:
        # Try to get planet count as a simple health check
        result = await planets_service.get_all_planets()
        return SuccessResponse(
            data={
                "status": "healthy",
                "planets_count": len(result.planets),
                "service": "planets"
            }
        )
    except Exception as e:
        logger.error("Planets service health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Planets service unhealthy")


# Admin endpoints (these would typically require admin authentication)
@router.post("/admin/seed", summary="Seed planets and quiz data", tags=["admin"])
async def seed_planets_data():
    """
    Admin endpoint to seed the database with initial planets and quiz data.
    
    This would typically require admin authentication in production.
    """
    try:
        # This would call a seeding service
        # For now, we'll return a placeholder response
        return SuccessResponse(
            data={
                "message": "Seeding functionality not yet implemented. Use the separate seeding script.",
                "status": "pending"
            }
        )
    except Exception as e:
        logger.error("Error seeding planets data", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to seed data") 