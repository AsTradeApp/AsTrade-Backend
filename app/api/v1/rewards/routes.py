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
    Obtiene el estado actual de las recompensas diarias del usuario
    - Streak actual y más largo
    - Recompensas de la semana
    - Días explorando la galaxia
    - Si puede reclamar hoy
    """
    try:
        # Inicializar perfil si es necesario
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Obtener estado de recompensas
        status = await rewards_service.get_daily_rewards_status(current_user.id)
        
        return {
            "success": True,
            "data": status.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado de recompensas: {str(e)}"
        )

@router.post("/claim-daily")
async def claim_daily_reward(
    request: ClaimRewardRequest,
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Reclama la recompensa diaria del usuario
    - Incrementa el streak
    - Otorga experiencia
    - Registra la recompensa
    """
    try:
        # Inicializar perfil si es necesario
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Reclamar recompensa
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
            detail=f"Error reclamando recompensa: {str(e)}"
        )

@router.post("/record-activity")
async def record_galaxy_explorer_activity(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Registra actividad de exploración de galaxia
    - Llamado cuando el usuario usa la app
    - Incrementa el streak de galaxy explorer
    - Solo una vez por día
    """
    try:
        # Inicializar perfil si es necesario
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Registrar actividad
        success = await rewards_service.record_galaxy_explorer_activity(current_user.id)
        
        return {
            "success": success,
            "message": "Actividad registrada" if success else "Ya registraste actividad hoy"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registrando actividad: {str(e)}"
        )

@router.get("/achievements")
async def get_user_achievements(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Obtiene los logros del usuario relacionados con streaks
    - Logros de daily streak
    - Logros de galaxy explorer
    - Progreso actual
    """
    try:
        # Inicializar perfil si es necesario
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Obtener logros
        achievements = await rewards_service.get_user_achievements(current_user.id)
        
        return {
            "success": True,
            "data": achievements
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo logros: {str(e)}"
        )

@router.get("/streak-info")
async def get_streak_info(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Obtiene información detallada de los streaks del usuario
    - Streak actual de login diario
    - Streak actual de exploración de galaxia
    - Fechas de última actividad
    """
    try:
        # Inicializar perfil si es necesario
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Obtener estado de recompensas (incluye info de streaks)
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
            detail=f"Error obteniendo información de streaks: {str(e)}"
        )

@router.get("/profile")
async def get_user_profile_with_rewards(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Obtiene el perfil completo del usuario con información de recompensas
    - Datos del perfil (nivel, experiencia, trades)
    - Streaks actuales
    - Logros desbloqueados
    - Recompensas recientes
    """
    try:
        # Inicializar perfil si es necesario
        await rewards_service.initialize_user_profile(current_user.id)
        
        # Obtener perfil completo
        profile = await rewards_service.get_user_profile_with_rewards(current_user.id)
        
        return {
            "success": True,
            "data": profile
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo perfil del usuario: {str(e)}"
        ) 

@router.get("/nfts")
async def get_user_nfts(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends(),
    nft_type: Optional[str] = None,
    rarity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Obtiene la colección de NFTs del usuario
    - Filtros opcionales por tipo y rareza
    - Ordenados por fecha de adquisición (más recientes primero)
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
            detail=f"Error obteniendo NFTs: {str(e)}"
        )

@router.get("/nfts/{nft_id}")
async def get_nft_detail(
    nft_id: UUID,
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Obtiene detalles de un NFT específico
    """
    try:
        nft = await rewards_service.get_nft_by_id(current_user.id, nft_id)
        
        if not nft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NFT no encontrado"
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
            detail=f"Error obteniendo NFT: {str(e)}"
        )

@router.get("/nfts/stats")
async def get_nft_stats(
    current_user: SimpleUser = Depends(get_current_user),
    rewards_service: RewardsService = Depends()
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de la colección de NFTs
    - Total de NFTs
    - Distribución por tipo y rareza
    - NFTs recientes
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
            detail=f"Error obteniendo estadísticas: {str(e)}"
        ) 