import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine
from app.db.base import Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
logger.info("Database tables created successfully")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Resume & Job Match Hub - Helping job seekers find the perfect match",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info("=== FastAPI Application Started ===")
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("Available endpoints:")
    logger.info("  GET / - Root endpoint")
    logger.info("  GET /health - Health check")
    logger.info("  GET /debug - Debug information")
    logger.info("  GET /docs - Swagger UI documentation")
    logger.info("  GET /redoc - ReDoc documentation")
    logger.info("  GET /openapi.json - OpenAPI schema")
    logger.info("  * /api/v1/* - API endpoints")
    logger.info("=====================================")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI Application shutting down...")


@app.get("/")
async def root():
    """Root endpoint providing service information"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered Resume & Job Match Hub",
        "message": "FastAPI application is running successfully",
        "endpoints": {
            "documentation": "/docs",
            "alternative_docs": "/redoc", 
            "openapi_schema": "/openapi.json",
            "health_check": "/health",
            "debug_info": "/debug",
            "api_base": "/api/v1"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/debug")
async def debug_info(request: Request):
    """Debug endpoint to verify FastAPI is running"""
    import os
    import socket
    
    return {
        "message": "✅ FastAPI application is running correctly",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time(),
        "server_info": {
            "hostname": socket.gethostname(),
            "python_version": os.sys.version.split()[0],
            "platform": os.sys.platform
        },
        "request_info": {
            "client_host": request.client.host if request.client else "unknown",
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers)
        },
        "available_endpoints": [
            "/",
            "/health", 
            "/debug",
            "/docs",
            "/redoc", 
            "/api-docs",
            "/api-redoc",
            "/documentation",
            "/openapi.json",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/resumes/upload",
            "/api/v1/jobs/",
            "/api/v1/matching/analyze"
        ],
        "docs_urls": {
            "primary_swagger": "/docs",
            "alternative_swagger": "/api-docs",
            "primary_redoc": "/redoc", 
            "alternative_redoc": "/api-redoc",
            "openapi_json": "/openapi.json",
            "documentation_links": "/documentation"
        }
    }


# Alternative documentation endpoints to bypass routing issues
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse

@app.get("/api-docs", response_class=HTMLResponse)
async def custom_swagger_ui():
    """Alternative Swagger UI endpoint"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - API Documentation"
    )

@app.get("/api-redoc", response_class=HTMLResponse) 
async def custom_redoc():
    """Alternative ReDoc endpoint"""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{settings.APP_NAME} - API Documentation"
    )

@app.get("/documentation")
async def documentation_links():
    """Documentation links endpoint"""
    return {
        "message": "API Documentation Available",
        "service": settings.APP_NAME,
        "documentation_urls": {
            "primary_swagger": "/docs",
            "alternative_swagger": "/api-docs", 
            "primary_redoc": "/redoc",
            "alternative_redoc": "/api-redoc",
            "openapi_schema": "/openapi.json",
            "debug_info": "/debug"
        },
        "note": "If /docs doesn't work, try /api-docs for Swagger UI documentation"
    }


# Add a catch-all route to log any unhandled requests
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(request: Request, path: str):
    """Catch-all endpoint to log unhandled requests"""
    logger.warning(f"Unhandled request: {request.method} /{path}")
    return {
        "error": "Endpoint not found",
        "path": path,
        "method": request.method,
        "message": "This endpoint does not exist. Check /debug for available endpoints.",
        "available_docs": ["/docs", "/redoc", "/openapi.json"]
    }