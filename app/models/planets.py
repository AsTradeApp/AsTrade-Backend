"""Pydantic models for planets and quiz system"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AnswerOption(str, Enum):
    """Valid answer options for quiz questions"""
    A = "A"
    B = "B" 
    C = "C"
    D = "D"


# Base Planet Models
class PlanetBase(BaseModel):
    """Base planet model"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")  # hex color validation
    order_index: int = Field(..., ge=1)
    is_active: bool = True


class Planet(BaseModel):
    """Planet model with database fields"""
    id: int
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    order_index: int = Field(..., ge=1)
    total_quizzes: Optional[int] = 0
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlanetWithProgress(Planet):
    """Planet model with user progress information"""
    user_progress: Optional["UserPlanetProgress"] = None
    quizzes: List["QuizWithProgress"] = []


# Base Quiz Models
class QuizBase(BaseModel):
    """Base quiz model"""
    planet_id: int
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    quiz_code: str = Field(..., max_length=10)  # e.g., "1A", "1B"
    order_index: int = Field(..., ge=1)
    is_active: bool = True


class Quiz(BaseModel):
    """Quiz model with database fields"""
    id: int
    planet_id: int
    name: str = Field(..., max_length=255)
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    description: Optional[str] = None
    quiz_code: str = Field(..., max_length=10)
    order_index: int = Field(..., ge=1)
    xp_reward: int = 50
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizWithProgress(Quiz):
    """Quiz model with user progress information"""
    total_questions: int = 0  # Calculated dynamically
    user_progress: Optional["UserQuizProgress"] = None
    questions: List["Question"] = []


# Base Question Models
class QuestionBase(BaseModel):
    """Base question model"""
    quiz_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: AnswerOption
    explanation: Optional[str] = None
    order_index: int = Field(..., ge=1)


class Question(QuestionBase):
    """Question model with database fields"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionForQuiz(BaseModel):
    """Question model for quiz display (without correct answer)"""
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    order_index: int


# Progress Models
class UserPlanetProgress(BaseModel):
    """User planet progress model"""
    id: int
    user_id: str
    planet_id: int
    is_unlocked: bool = False
    is_completed: bool = False
    quizzes_completed: int = 0
    total_quizzes: int = 2
    experience_earned: int = 0
    unlocked_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserQuizProgress(BaseModel):
    """User quiz progress model"""
    id: int
    user_id: str
    quiz_id: int
    is_completed: bool = False
    best_score: int = 0
    total_attempts: int = 0
    first_completed_at: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    completion_percentage: float = 0.0
    attempts: int = 0
    first_attempt_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserQuestionAttempt(BaseModel):
    """User question attempt model"""
    id: int
    user_id: str
    question_id: int
    quiz_attempt_id: Optional[int] = None
    selected_answer: AnswerOption
    is_correct: bool
    answered_at: datetime
    response_time_seconds: Optional[int] = None

    class Config:
        from_attributes = True


# Request Models
class QuizAnswerRequest(BaseModel):
    """Request model for submitting a quiz answer"""
    question_id: int
    selected_answer: AnswerOption
    response_time_seconds: Optional[int] = None


class QuizSubmissionRequest(BaseModel):
    """Request model for submitting a complete quiz"""
    quiz_id: int
    answers: List[QuizAnswerRequest]


class QuizStartRequest(BaseModel):
    """Request model for starting a quiz"""
    quiz_id: int


# Response Models
class QuizAnswerResult(BaseModel):
    """Response model for a single question result"""
    question_id: int
    selected_answer: AnswerOption
    correct_answer: AnswerOption
    is_correct: bool
    explanation: Optional[str] = None


class QuizSubmissionResponse(BaseModel):
    """Response model for quiz submission"""
    quiz_id: int
    score: int
    total_questions: int
    completion_percentage: float
    is_completed: bool
    answers: List[QuizAnswerResult]
    previous_best_score: int
    is_new_best: bool


class PlanetProgressSummary(BaseModel):
    """Summary of user progress on a planet"""
    planet_id: int
    planet_name: str
    planet_color: str
    completed_quizzes: int
    total_quizzes: int
    total_score: int
    is_completed: bool
    completion_percentage: float
    last_activity_at: Optional[datetime] = None


class QuizProgressSummary(BaseModel):
    """Summary of user progress on a quiz"""
    quiz_id: int
    quiz_title: str
    quiz_code: str
    score: int
    total_questions: int
    completion_percentage: float
    is_completed: bool
    attempts: int
    best_score: int
    last_attempt_at: Optional[datetime] = None


class UserProgressOverview(BaseModel):
    """Complete overview of user progress"""
    planets: List[PlanetProgressSummary]
    total_planets_completed: int
    total_quizzes_completed: int
    overall_score: int
    overall_completion_percentage: float


# Detailed Response Models
class PlanetDetailResponse(BaseModel):
    """Detailed planet information with quizzes and progress"""
    planet: Planet
    user_progress: Optional[UserPlanetProgress] = None
    quizzes: List[QuizWithProgress]


class QuizDetailResponse(BaseModel):
    """Detailed quiz information with questions and progress"""
    quiz: Quiz
    planet: Planet
    user_progress: Optional[UserQuizProgress] = None
    questions: List[QuestionForQuiz]  # Without correct answers
    can_start: bool
    can_retake: bool


class QuizStartResponse(BaseModel):
    """Response when starting a quiz"""
    quiz_attempt_id: int
    quiz: Quiz
    questions: List[QuestionForQuiz]
    started_at: datetime


# List Response Models
class PlanetsListResponse(BaseModel):
    """Response model for planets list"""
    planets: List[PlanetWithProgress]
    user_overview: Optional[UserProgressOverview] = None


class QuizzesListResponse(BaseModel):
    """Response model for quizzes list"""
    quizzes: List[QuizWithProgress]
    planet: Planet


# Admin Models (for seeding data)
class QuestionCreate(BaseModel):
    """Model for creating questions (admin use)"""
    question_text: str
    option_a: str
    option_b: str  
    option_c: str
    option_d: str
    correct_answer: AnswerOption
    explanation: Optional[str] = None
    order_index: int


class QuizCreate(BaseModel):
    """Model for creating quizzes (admin use)"""
    title: str
    description: Optional[str] = None
    quiz_code: str
    order_index: int
    questions: List[QuestionCreate]


class PlanetCreate(BaseModel):
    """Model for creating planets (admin use)"""
    name: str
    description: Optional[str] = None
    color: str
    order_index: int
    quizzes: List[QuizCreate]


# Update forward references
PlanetWithProgress.model_rebuild()
QuizWithProgress.model_rebuild() 