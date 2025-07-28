"""Database connection and configuration based on AtticusZeller template"""
import os
from functools import lru_cache
from supabase import create_client, Client
from typing import Optional


class SupabaseConfig:
    """Supabase configuration"""
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        # Try to get from parameters first, then from settings, then from env
        if supabase_url and supabase_key:
            self.supabase_url = supabase_url
            self.supabase_key = supabase_key
        else:
            try:
                from app.config.settings import settings
                self.supabase_url = settings.supabase_url
                self.supabase_key = settings.supabase_key
            except ImportError:
                # Fallback to environment variables for edge cases
                self.supabase_url = os.getenv("SUPABASE_URL")
                self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.supabase_key:
            raise ValueError("SUPABASE_KEY environment variable is required")


@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    """Get cached Supabase configuration"""
    return SupabaseConfig()


@lru_cache()
def get_supabase_client() -> Client:
    """Get cached Supabase client instance"""
    config = get_supabase_config()
    return create_client(config.supabase_url, config.supabase_key)


def refresh_supabase_config():
    """Clear cached configuration and reload from environment"""
    get_supabase_config.cache_clear()
    get_supabase_client.cache_clear()


def get_supabase() -> Client:
    """Get Supabase client for dependency injection"""
    return get_supabase_client()


async def check_supabase_connection() -> tuple[bool, str]:
    """Check if Supabase connection is working"""
    try:
        client = get_supabase_client()
        
        # Try to query a simple table or make a basic request
        response = client.table('astrade_user_profiles').select("count").limit(1).execute()
        
        return True, "Supabase connection successful"
    except Exception as e:
        return False, f"Supabase connection failed: {str(e)}"


# For backwards compatibility - these functions might be used elsewhere
def get_db():
    """Legacy function for SQLAlchemy compatibility - returns Supabase client"""
    return get_supabase_client()


def create_tables():
    """Legacy function - tables are managed by Supabase migrations"""
    print("Tables are managed by Supabase migrations and RLS policies")
    pass 