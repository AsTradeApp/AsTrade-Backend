from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.api.v1.users.dependencies import get_current_user, SimpleUser
from app.services.image_service import ImageService
import base64
import io
from PIL import Image

router = APIRouter()

@router.post("/upload-reward-image")
async def upload_reward_image(
    file: UploadFile = File(...),
    current_user: SimpleUser = Depends(get_current_user),
    image_service: ImageService = Depends()
) -> Dict[str, Any]:
    """
    Sube una imagen para recompensa a Cloudinary
    
    Args:
        file: Archivo de imagen (PNG, JPG, etc.)
        current_user: Usuario autenticado
        image_service: Servicio de imágenes
        
    Returns:
        URL de la imagen subida
    """
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos de imagen")
        
        # Leer archivo
        contents = await file.read()
        
        # Validar tamaño (máximo 5MB)
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Archivo demasiado grande (máximo 5MB)")
        
        # Convertir a base64
        base64_data = base64.b64encode(contents).decode('utf-8')
        base64_url = f"data:{file.content_type};base64,{base64_data}"
        
        # Subir a Cloudinary
        filename = f"reward_{current_user.id}_{file.filename}"
        result = await image_service.upload_base64_image(
            base64_url, 
            filename, 
            folder="astrade-rewards"
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Error subiendo imagen")
        
        return {
            "success": True,
            "data": {
                "url": result["url"],
                "public_id": result["public_id"],
                "filename": filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/upload-reward-image-base64")
async def upload_reward_image_base64(
    image_data: Dict[str, str],
    current_user: SimpleUser = Depends(get_current_user),
    image_service: ImageService = Depends()
) -> Dict[str, Any]:
    """
    Sube una imagen desde base64 para recompensa
    
    Args:
        image_data: {"base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...", "filename": "reward.png"}
        current_user: Usuario autenticado
        image_service: Servicio de imágenes
        
    Returns:
        URL de la imagen subida
    """
    try:
        base64_data = image_data.get("base64")
        filename = image_data.get("filename", "reward.png")
        
        if not base64_data:
            raise HTTPException(status_code=400, detail="Base64 data requerido")
        
        # Subir a Cloudinary
        full_filename = f"reward_{current_user.id}_{filename}"
        result = await image_service.upload_base64_image(
            base64_data, 
            full_filename, 
            folder="astrade-rewards"
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Error subiendo imagen")
        
        return {
            "success": True,
            "data": {
                "url": result["url"],
                "public_id": result["public_id"],
                "filename": full_filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") 