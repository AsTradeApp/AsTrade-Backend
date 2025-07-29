from datetime import date, datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID


class DailyReward(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    reward_date: date
    reward_type: str = Field(..., description="'daily_streak' or 'galaxy_explorer'")
    reward_data: Dict[str, Any] = Field(..., description="Reward details like amount, currency, item")
    claimed_at: Optional[datetime] = None
    streak_count: int = Field(default=1, description="Current streak count")
    created_at: Optional[datetime] = None


class RewardConfig(BaseModel):
    id: Optional[UUID] = None
    reward_type: str = Field(..., description="'daily_streak' or 'galaxy_explorer'")
    day_number: Optional[int] = Field(None, description="1-7 for streak, null for galaxy explorer")
    reward_data: Dict[str, Any] = Field(..., description="Reward configuration")
    is_active: bool = True
    created_at: Optional[datetime] = None


class UserStreak(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    streak_type: str = Field(..., description="'daily_login' or 'galaxy_explorer'")
    current_streak: int = Field(default=0, description="Current streak count")
    longest_streak: int = Field(default=0, description="Longest streak achieved")
    last_activity_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DailyRewardResponse(BaseModel):
    can_claim: bool
    current_streak: int
    longest_streak: int
    next_reward_in: Optional[str] = None  # "19h 37m" format
    today_reward: Optional[Dict[str, Any]] = None
    week_rewards: list[Dict[str, Any]] = Field(default_factory=list)
    galaxy_explorer_days: int = Field(default=0, description="Days exploring the galaxy")


class ClaimRewardRequest(BaseModel):
    reward_type: str = Field(..., description="'daily_streak' or 'galaxy_explorer'")


class ClaimRewardResponse(BaseModel):
    success: bool
    reward_data: Dict[str, Any]
    new_streak: int
    message: str 


class UserNFT(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    nft_type: str = Field(..., description="'daily_reward', 'achievement', 'special'")
    nft_name: str
    nft_description: Optional[str] = None
    image_url: str
    rarity: str = Field(default="common", description="'common', 'rare', 'epic', 'legendary'")
    acquired_date: date
    acquired_from: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NFTCollectionResponse(BaseModel):
    success: bool
    data: List[UserNFT]
    total_count: int
    filters: Optional[Dict[str, Any]] = None

class NFTDetailResponse(BaseModel):
    success: bool
    data: UserNFT 