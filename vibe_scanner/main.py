import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from .config import settings
from .db.database import engine, Base
from .api import routes

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting Vibe Scanner API (Environment: {settings.ENVIRONMENT})")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")
    yield
    
    # Shutdown
    logger.info("Shutting down Vibe Scanner API")
    await engine.dispose()


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Security vulnerability scanner API",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redirect_slashes=False,
    lifespan=lifespan,
)


# CORS middleware - using settings from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)


@app.middleware("http")
async def add_process_time_and_request_id(request: Request, call_next):
    """
    Middleware to add request context tracking and performance monitoring.
    - Adds unique request ID to all requests
    - Tracks request processing time
    - Adds correlation headers to responses
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request details
        logger.info(
            f"Request {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"ID: {request_id}"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request {request.method} {request.url.path} failed - "
            f"Error: {str(e)[:100]} - "
            f"Time: {process_time:.3f}s - "
            f"ID: {request_id}",
            exc_info=True
        )
        raise


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with proper formatting."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"Validation error - ID: {request_id}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "type": "validation_error",
            "request_id": request_id,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors gracefully."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Database error - ID: {request_id}: {str(exc)[:100]}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "type": "database_error",
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception - ID: {request_id}: {str(exc)[:100]}", exc_info=True)
    
    # Don't expose internal error details in production
    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "An internal server error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "type": "server_error",
            "request_id": request_id,
        },
    )


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["health"], include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"{settings.PROJECT_NAME} API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": f"http://localhost:8000{settings.API_V1_STR}/docs",
        "frontend": "http://localhost:3000",
    }


# Include routers
app.include_router(routes.router, prefix=settings.API_V1_STR)

logger.info(f"Application initialized (Debug: {settings.DEBUG})")
