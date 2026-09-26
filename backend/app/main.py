import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes.auth_routes import router as auth_router
from app.routes.analyze_routes import router as analyze_router
from app.routes.history_routes import router as history_router
from app.routes.admin_routes import router as admin_router
from app.routes.health_routes import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resumely")

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Production-grade API for ATS scoring, resume extraction, skill matching, and AI recommendations.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Supporting separated frontend (Live Server, Vite, static file or localhost ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please check server logs."}
    )

# Include Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(admin_router)

@app.get("/")
async def root():
    return {
        "name": "AI Resume Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
