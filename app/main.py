import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import structlog

from app.config.settings import settings
from app.models.responses import SuccessResponse, ErrorResponse, ErrorDetail, HealthResponse
from app.services.extended_client import extended_client
from app.services.database import create_tables
from app.api.v1 import markets, accounts, orders, users

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Store application start time for uptime calculation
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AsTrade Backend", version=settings.app_version, environment=settings.extended_environment)
    
    # Initialize database tables
    create_tables()
    logger.info("Database tables initialized")
    
    # Initialize Extended Exchange client
    await extended_client.connect()
    logger.info("Connected to Extended Exchange API", base_url=extended_client.base_url)
    
    yield
    
    # Shutdown
    logger.info("Shutting down AsTrade Backend")
    await extended_client.disconnect()


# Create FastAPI application
app = FastAPI(
    title="AsTrade Backend",
    description="Backend API for AsTrade - A professional trading platform integrating Extended Exchange",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.astrade.com"]
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        client_ip=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=f"{process_time:.4f}s"
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method
    )
    
    error_detail = ErrorDetail(
        code=exc.status_code,
        message=str(exc.detail) if isinstance(exc.detail, str) else "An error occurred",
        details=exc.detail if isinstance(exc.detail, dict) else None
    )
    
    error_response = ErrorResponse(error=error_detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(error_response)
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method
    )
    
    error_detail = ErrorDetail(
        code=500,
        message="Internal server error",
        details={"error_type": type(exc).__name__, "error": str(exc)} if settings.debug else None
    )
    
    error_response = ErrorResponse(error=error_detail)
    
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response)
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - app_start_time
    
    # Check services
    services = {
        "extended_exchange": "healthy" if extended_client.session else "disconnected",
        "api": "healthy"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.extended_environment,
        uptime=uptime,
        services=services
    )


# Root endpoint
@app.get("/", response_model=SuccessResponse, tags=["Root"])
async def root():
    """Root endpoint with API information"""
    data = {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.extended_environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_v1": "/api/v1"
    }
    
    return SuccessResponse(data=data)


# Include API routers
app.include_router(
    markets.router,
    prefix="/api/v1",
    tags=["Markets"]
)

app.include_router(
    accounts.router,
    prefix="/api/v1",
    tags=["Accounts"]
)

app.include_router(
    orders.router,
    prefix="/api/v1",
    tags=["Orders"]
)

app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["Users"]
)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "Starting server",
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        environment=settings.extended_environment
    )
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower(),
        access_log=True
    ) 