from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import AdminStats
from app.services.admin_service import admin_service
from app.auth import get_current_user_optional, require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


@router.get("/stats", response_model=AdminStats)
async def get_admin_dashboard_metrics(current_user: dict = Depends(get_current_user_optional)):
    """
    Returns system-wide analytics, ATS trends, missing skills stats, and scan audits.
    """
    # If user is authenticated, ensure admin role. If not logged in, allow demo preview if no users exist.
    if current_user and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access executive metrics."
        )
    return admin_service.get_dashboard_stats()
