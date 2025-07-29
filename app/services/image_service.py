import cloudinary
import cloudinary.uploader
from typing import Optional, Dict, Any
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        """Inicializa el servicio de imágenes con Cloudinary"""
        try:
            cloudinary.config(
                cloud_name=settings.cloudinary_cloud_name,
                api_key=settings.cloudinary_api_key,
                api_secret=settings.cloudinary_api_secret
            )
            logger.info("✅ Cloudinary configurado correctamente")
        except Exception as e:
            logger.error(f"❌ Error configurando Cloudinary: {e}")
    
    async def upload_image(self, file_path: str, folder: str = "astrade-rewards") -> Optional[Dict[str, Any]]:
        """
        Sube una imagen a Cloudinary
        
        Args:
            file_path: Ruta del archivo local
            folder: Carpeta en Cloudinary (default: astrade-rewards)
            
        Returns:
            Dict con URL y metadata de la imagen, o None si falla
        """
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                resource_type="image",
                transformation=[
                    {"width": 400, "height": 400, "crop": "fill"},
                    {"quality": "auto", "fetch_format": "auto"}
                ]
            )
            
            logger.info(f"✅ Imagen subida: {result['secure_url']}")
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo imagen: {e}")
            return None
    
    async def upload_base64_image(self, base64_data: str, filename: str, folder: str = "astrade-rewards") -> Optional[Dict[str, Any]]:
        """
        Sube una imagen desde base64
        
        Args:
            base64_data: Imagen en formato base64
            filename: Nombre del archivo
            folder: Carpeta en Cloudinary
            
        Returns:
            Dict con URL y metadata de la imagen, o None si falla
        """
        try:
            result = cloudinary.uploader.upload(
                base64_data,
                public_id=filename,
                folder=folder,
                resource_type="image",
                transformation=[
                    {"width": 400, "height": 400, "crop": "fill"},
                    {"quality": "auto", "fetch_format": "auto"}
                ]
            )
            
            logger.info(f"✅ Imagen base64 subida: {result['secure_url']}")
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo imagen base64: {e}")
            return None
    
    async def delete_image(self, public_id: str) -> bool:
        """
        Elimina una imagen de Cloudinary
        
        Args:
            public_id: ID público de la imagen
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            if result.get("result") == "ok":
                logger.info(f"✅ Imagen eliminada: {public_id}")
                return True
            else:
                logger.error(f"❌ Error eliminando imagen: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error eliminando imagen: {e}")
            return False 