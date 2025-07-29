from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from uuid import UUID
from app.services.rewards_service import RewardsService
from app.models.rewards import ClaimRewardRequest
from app.api.v1.users.dependencies import get_current_user, SimpleUser

router = APIRouter(tags=["rewards"])

@router.get("/daily-status")
async def get_daily_rewards_status(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Gets the current status of the user's daily rewards
    - Current and longest streak
    - Week rewards
    - Days exploring the galaxy
    - If can claim today
    """
    try:
        # Initialize profile if necessary
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Get rewards status
        status = await rewards_service.get_daily_rewards_status(current_user.id)
        
        return {
            "success": True,
            "data": status.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting rewards status: {str(e)}"
        )

@router.post("/claim-daily")
async def claim_daily_reward(
    request: ClaimRewardRequest,
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Claims the user's daily reward
    - Increments streak
    - Grants experience
    - Records the reward
    """
    try:
        # Initialize profile if necessary
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Claim reward
        result = await rewards_service.claim_daily_reward(
            current_user.id, 
            request.reward_type
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return {
            "success": True,
            "data": result.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error claiming reward: {str(e)}"
        )

@router.post("/record-activity")
async def record_galaxy_explorer_activity(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Records galaxy exploration activity
    - Called when user uses the app
    - Increments galaxy explorer streak
    - Only once per day
    """
    try:
        # Initialize profile if necessary
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Record activity
        success = await rewards_service.record_galaxy_explorer_activity(current_user.id)
        
        return {
            "success": success,
            "message": "Activity recorded" if success else "You already recorded activity today"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording activity: {str(e)}"
        )

@router.get("/achievements")
async def get_user_achievements(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Gets the user's achievements related to streaks
    - Daily streak achievements
    - Galaxy explorer achievements
    - Current progress
    """
    try:
        # Initialize profile if necessary
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Get achievements
        achievements = await rewards_service.get_user_achievements(current_user.id)
        
        return {
            "success": True,
            "data": achievements
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting achievements: {str(e)}"
        )

@router.get("/streak-info")
async def get_streak_info(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Gets detailed information about the user's streaks
    - Current daily login streak
    - Current galaxy exploration streak
    - Last activity dates
    """
    try:
        # Initialize profile if necessary
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Get rewards status (includes streak info)
        status = await rewards_service.get_daily_rewards_status(current_user.id)
        
        return {
            "success": True,
            "data": {
                "daily_login_streak": status.current_streak,
                "daily_login_longest": status.longest_streak,
                "galaxy_explorer_days": status.galaxy_explorer_days,
                "can_claim_today": status.can_claim,
                "next_reward_in": status.next_reward_in
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting streak information: {str(e)}"
        )

@router.get("/profile")
async def get_user_profile_with_rewards(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Gets the complete user profile with reward information
    - Profile data (level, experience, trades)
    - Current streaks
    - Unlocked achievements
    - Recent rewards
    """
    try:
        # Initialize profile if necessary
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Get complete profile
        profile = await rewards_service.get_user_profile_with_rewards(current_user.id)
        
        return {
            "success": True,
            "data": profile
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user profile: {str(e)}"
        ) 

@router.get("/nfts")
async def get_user_nfts(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends(),
    nft_type: Optional[str] = None,
    rarity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gets the user's NFT collection
    - Optional filters by type and rarity
    - Ordered by acquisition date (most recent first)
    """
    try:
        nfts = await rewards_service.get_user_nfts(current_user.id, nft_type, rarity)
        
        return {
            "success": True,
            "data": nfts,
            "total_count": len(nfts),
            "filters": {
                "nft_type": nft_type,
                "rarity": rarity
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting NFTs: {str(e)}"
        )

@router.get("/nfts/{nft_id}")
async def get_nft_detail(
    nft_id: UUID,
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Gets details of a specific NFT
    """
    try:
        nft = await rewards_service.get_nft_by_id(current_user.id, nft_id)
        
        if not nft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NFT not found"
            )
        
        return {
            "success": True,
            "data": nft
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting NFT: {str(e)}"
        )

@router.get("/nfts/stats")
async def get_nft_stats(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Gets statistics of the NFT collection
    - Total NFTs
    - Distribution by type and rarity
    - Recent NFTs
    """
    try:
        stats = await rewards_service.get_nft_stats(current_user.id)
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting statistics: {str(e)}"
        ) 