from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import HistoryItem, AnalysisResult
from app.database import db_service
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=List[HistoryItem])
async def list_analyses(current_user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Get list of past analyses for current user (or public scans if unauthenticated).
    """
    user_id = current_user["id"] if current_user else None
    records = db_service.get_user_analyses(user_id=user_id, limit=50)

    items = []
    for r in records:
        items.append(
            HistoryItem(
                id=r["id"],
                user_id=r.get("user_id"),
                filename=r.get("filename", "resume"),
                job_title=r.get("job_title", "Unknown Role"),
                ats_score=r.get("ats_score", 0),
                match_level=r.get("match_level") or ("Strong" if r.get("ats_score", 0) >= 70 else "Moderate"),
                created_at=r.get("created_at", "")
            )
        )
    return items


@router.get("/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_detail(analysis_id: str, current_user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Retrieve full analysis report by ID.
    """
    record = db_service.get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' was not found."
        )

    # If record has a user_id and current user is someone else (non-admin), check permission
    if record.get("user_id") and current_user:
        if record["user_id"] != current_user["id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this report."
            )

    return AnalysisResult(**record)


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str, current_user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Delete an analysis report.
    """
    user_id = current_user["id"] if (current_user and current_user.get("role") != "admin") else None
    success = db_service.delete_analysis(analysis_id=analysis_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or permission denied."
        )
    return {"message": "Analysis report deleted successfully."}
