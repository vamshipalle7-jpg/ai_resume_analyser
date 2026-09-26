from datetime import datetime, timezone
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import settings
from app.database import db_service

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="operational",
        version="1.0.0",
        database_mode=db_service.mode,
        ai_provider=settings.AI_PROVIDER,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

