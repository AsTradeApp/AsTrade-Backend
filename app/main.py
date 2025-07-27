"""FastAPI application with Supabase integration"""
import structlog
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.users.routes import router as users_router
from app.api.v1.markets.routes import router as markets_router
from app.api.v1.orders.routes import router as orders_router
from app.api.v1.accounts.routes import router as accounts_router
from app.services.database import check_supabase_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="AsTrade API",
    description="Backend API for AsTrade platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(markets_router, prefix="/api/v1/markets", tags=["markets"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(accounts_router, prefix="/api/v1/account", tags=["accounts"])

@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    logger.info("Starting AsTrade API")
    
    # Check database connection
    success, message = await check_supabase_connection()
    if success:
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed", error=message)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check database connection
    success, message = await check_supabase_connection()
    
    return {
        "status": "healthy" if success else "unhealthy",
        "database": {
            "connected": success,
            "message": message
        }
    } 