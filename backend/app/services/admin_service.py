from typing import Dict, Any, List
from app.database import db_service
from app.models.schemas import AdminStats


class AdminService:
    """
    Analytics and system monitoring service for administrators.
    """

    @staticmethod
    def get_dashboard_stats() -> AdminStats:
        metrics = db_service.get_admin_metrics()
        return AdminStats(
            total_scans=metrics.get("total_scans", 0),
            total_users=metrics.get("total_users", 0),
            avg_ats_score=metrics.get("avg_ats_score", 0.0),
            pass_rate_percent=metrics.get("pass_rate_percent", 0.0),
            score_distribution=metrics.get("score_distribution", {}),
            top_missing_skills=metrics.get("top_missing_skills", []),
            recent_scans=metrics.get("recent_scans", [])
        )


admin_service = AdminService()
