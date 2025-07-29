from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator, ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )
    
    # Application
    app_name: str = "AsTrade Backend"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Security
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Supabase Configuration
    supabase_url: str = Field(env="SUPABASE_URL")
    supabase_key: str = Field(env="SUPABASE_KEY")
    
    # Extended Exchange API
    extended_environment: str = Field(default="testnet", env="EXTENDED_ENVIRONMENT")  # testnet or mainnet
    extended_api_key: Optional[str] = Field(default=None, env="EXTENDED_API_KEY")
    extended_secret_key: Optional[str] = Field(default=None, env="EXTENDED_SECRET_KEY")
    extended_stark_private_key: Optional[str] = Field(default=None, env="EXTENDED_STARK_PRIVATE_KEY")
    extended_vault_id: Optional[int] = Field(default=None, env="EXTENDED_VAULT_ID")
    
    # Database
    database_url: str = Field(env="DATABASE_URL", default="postgresql://postgres:postgres@localhost:5432/astrade")
    
    # Redis
    redis_url: str = Field(env="REDIS_URL", default="redis://localhost:6381/0")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")  # seconds
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:8080,http://localhost:8081,http://localhost:19006,http://localhost:19000,exp://localhost:19000,http://localhost",
        env="CORS_ORIGINS"
    )
    
    # Cloudinary Configuration
    cloudinary_cloud_name: Optional[str] = Field(default=None, env="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: Optional[str] = Field(default=None, env="CLOUDINARY_API_KEY")
    cloudinary_api_secret: Optional[str] = Field(default=None, env="CLOUDINARY_API_SECRET")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


# Global settings instance
settings = Settings() 