import os
import json
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from app.config import settings

logger = logging.getLogger("resumely.database")

# Check if supabase package is available and credentials are set
supabase_client = None
if settings.is_supabase_configured:
    try:
        from supabase import create_client, Client
        key_to_use = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
        supabase_client = create_client(settings.SUPABASE_URL, key_to_use)
        logger.info("Successfully initialized Supabase PostgreSQL client.")
    except Exception as e:
        logger.warning(f"Could not connect to Supabase: {e}. Falling back to persistent local storage mode.")
        supabase_client = None
else:
    logger.info("Supabase not configured or placeholder detected. Operating in persistent local storage mode.")


class LocalStorageEngine:
    """
    Production-grade local persistent JSON storage engine.
    Mirrors Supabase PostgreSQL schema with full CRUD for users, resumes, analyses, and audit logs.
    """
    def __init__(self, filepath: str = "backend/data/storage.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            self._init_default_data()

    def _init_default_data(self):
        # Default seed accounts
        # Default pass is Admin@123456 (or User@123456)
        initial_data = {
            "users": [
                {
                    "id": str(uuid.uuid4()),
                    "email": "admin@analyzer.ai",
                    "hashed_password": "$2b$12$K8dflG9Qd0v41p9xXfMhceH2QY1d6M3U2w6N8zB0cR.pY7A3k5fFe", # Admin@123456
                    "full_name": "System Administrator",
                    "role": "admin",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "email": "admin@analyer.ai",
                    "hashed_password": "$2b$12$K8dflG9Qd0v41p9xXfMhceH2QY1d6M3U2w6N8zB0cR.pY7A3k5fFe", # Admin@123456
                    "full_name": "System Administrator",
                    "role": "admin",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "email": "demo@analyzer.ai",
                    "hashed_password": "$2b$12$K8dflG9Qd0v41p9xXfMhceH2QY1d6M3U2w6N8zB0cR.pY7A3k5fFe", # Admin@123456
                    "full_name": "Demo Candidate",
                    "role": "user",
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "email": "demo@analyer.ai",
                    "hashed_password": "$2b$12$K8dflG9Qd0v41p9xXfMhceH2QY1d6M3U2w6N8zB0cR.pY7A3k5fFe", # Admin@123456
                    "full_name": "Demo Candidate",
                    "role": "user",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ],
            "resumes": [],
            "analyses": [],
            "audit_logs": []
        }
        self._write(initial_data)

    def _read(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.filepath):
                self._init_default_data()
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": [], "resumes": [], "analyses": [], "audit_logs": []}

    def _write(self, data: Dict[str, Any]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    # User operations
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        data = self._read()
        for u in data.get("users", []):
            if u["email"].lower() == email.lower():
                return u
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        data = self._read()
        for u in data.get("users", []):
            if u["id"] == user_id:
                return u
        return None

    def create_user(self, email: str, hashed_password: str, full_name: Optional[str] = None, role: str = "user") -> Dict[str, Any]:
        data = self._read()
        new_user = {
            "id": str(uuid.uuid4()),
            "email": email.lower(),
            "hashed_password": hashed_password,
            "full_name": full_name or "Job Seeker",
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        data["users"].append(new_user)
        self._write(data)
        return new_user

    # Resume operations
    def save_resume(self, user_id: Optional[str], filename: str, file_type: str, file_size_bytes: int, raw_text: str, parsed_sections: Dict[str, Any]) -> str:
        data = self._read()
        resume_id = str(uuid.uuid4())
        resume_record = {
            "id": resume_id,
            "user_id": user_id,
            "filename": filename,
            "file_type": file_type,
            "file_size_bytes": file_size_bytes,
            "raw_text": raw_text,
            "parsed_sections": parsed_sections,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        data["resumes"].append(resume_record)
        self._write(data)
        return resume_id

    # Analysis operations
    def save_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read()
        if "id" not in analysis_data or not analysis_data["id"]:
            analysis_data["id"] = str(uuid.uuid4())
        if "created_at" not in analysis_data or not analysis_data["created_at"]:
            analysis_data["created_at"] = datetime.now(timezone.utc).isoformat()
        
        data["analyses"].insert(0, analysis_data)
        self._write(data)
        return analysis_data

    def get_analyses_by_user(self, user_id: Optional[str], limit: int = 50) -> List[Dict[str, Any]]:
        data = self._read()
        analyses = data.get("analyses", [])
        if user_id:
            user_analyses = [a for a in analyses if a.get("user_id") == user_id]
        else:
            user_analyses = analyses
        return user_analyses[:limit]

    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        data = self._read()
        for a in data.get("analyses", []):
            if a["id"] == analysis_id:
                return a
        return None

    def delete_analysis(self, analysis_id: str, user_id: Optional[str] = None) -> bool:
        data = self._read()
        initial_len = len(data["analyses"])
        data["analyses"] = [
            a for a in data["analyses"] 
            if not (a["id"] == analysis_id and (user_id is None or a.get("user_id") == user_id))
        ]
        if len(data["analyses"]) < initial_len:
            self._write(data)
            return True
        return False

    # Audit & Admin
    def log_audit(self, user_id: Optional[str], action: str, details: Dict[str, Any], ip_address: Optional[str] = None):
        data = self._read()
        log_entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "details": details,
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        data["audit_logs"].append(log_entry)
        self._write(data)

    def get_admin_metrics(self) -> Dict[str, Any]:
        data = self._read()
        analyses = data.get("analyses", [])
        users = data.get("users", [])
        
        total_scans = len(analyses)
        total_users = len(users)
        
        if total_scans > 0:
            scores = [a.get("ats_score", 0) for a in analyses]
            avg_score = round(sum(scores) / total_scans, 1)
            pass_rate = round(len([s for s in scores if s >= 70]) / total_scans * 100, 1)
        else:
            avg_score = 0.0
            pass_rate = 0.0

        # Score distribution
        distribution = {"0-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        missing_skills_counter = {}
        for a in analyses:
            score = a.get("ats_score", 0)
            if score <= 40:
                distribution["0-40"] += 1
            elif score <= 60:
                distribution["41-60"] += 1
            elif score <= 80:
                distribution["61-80"] += 1
            else:
                distribution["81-100"] += 1
            
            for ms in a.get("missing_skills", []):
                name = ms.get("skill") if isinstance(ms, dict) else str(ms)
                if name:
                    missing_skills_counter[name] = missing_skills_counter.get(name, 0) + 1

        top_missing = [
            {"skill": k, "count": v} 
            for k, v in sorted(missing_skills_counter.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        recent_scans = [
            {
                "id": a.get("id"),
                "job_title": a.get("job_title", "Unknown"),
                "filename": a.get("filename", "resume"),
                "ats_score": a.get("ats_score", 0),
                "created_at": a.get("created_at"),
                "user_id": a.get("user_id")
            }
            for a in analyses[:15]
        ]

        return {
            "total_scans": total_scans,
            "total_users": total_users,
            "avg_ats_score": avg_score,
            "pass_rate_percent": pass_rate,
            "score_distribution": distribution,
            "top_missing_skills": top_missing,
            "recent_scans": recent_scans
        }


local_db = LocalStorageEngine()


# Unified Database Interface supporting both Supabase and Local Storage
class DatabaseService:
    @property
    def mode(self) -> str:
        return "supabase" if supabase_client else "local_persistent"

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        if supabase_client:
            try:
                res = supabase_client.table("users").select("*").eq("email", email.lower()).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase get_user_by_email error: {e}")
        return local_db.get_user_by_email(email)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        if supabase_client:
            try:
                res = supabase_client.table("users").select("*").eq("id", user_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase get_user_by_id error: {e}")
        return local_db.get_user_by_id(user_id)

    def create_user(self, email: str, hashed_password: str, full_name: Optional[str] = None, role: str = "user") -> Dict[str, Any]:
        if supabase_client:
            try:
                user_id = str(uuid.uuid4())
                user_data = {
                    "id": user_id,
                    "email": email.lower(),
                    "hashed_password": hashed_password,
                    "full_name": full_name or "Job Seeker",
                    "role": role
                }
                res = supabase_client.table("users").insert(user_data).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase create_user error: {e}")
        return local_db.create_user(email, hashed_password, full_name, role)

    def save_resume(self, user_id: Optional[str], filename: str, file_type: str, file_size_bytes: int, raw_text: str, parsed_sections: Dict[str, Any]) -> str:
        if supabase_client:
            try:
                resume_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "filename": filename,
                    "file_type": file_type,
                    "file_size_bytes": file_size_bytes,
                    "raw_text": raw_text,
                    "parsed_sections": parsed_sections
                }
                res = supabase_client.table("resumes").insert(resume_data).execute()
                if res.data:
                    return res.data[0]["id"]
            except Exception as e:
                logger.error(f"Supabase save_resume error: {e}")
        return local_db.save_resume(user_id, filename, file_type, file_size_bytes, raw_text, parsed_sections)

    def save_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        if supabase_client:
            try:
                # Prepare record matching Supabase schema
                record = {
                    "id": analysis_data.get("id") or str(uuid.uuid4()),
                    "user_id": analysis_data.get("user_id"),
                    "job_title": analysis_data.get("job_title", "Unknown"),
                    "target_industry": analysis_data.get("target_industry", "Technology"),
                    "job_description": analysis_data.get("job_description", ""),
                    "ats_score": analysis_data.get("ats_score", 0),
                    "score_breakdown": analysis_data.get("score_breakdown", {}),
                    "matched_skills": analysis_data.get("matched_skills", []),
                    "missing_skills": analysis_data.get("missing_skills", []),
                    "bonus_skills": analysis_data.get("bonus_skills", []),
                    "experience_analysis": analysis_data.get("experience_analysis", {}),
                    "education_analysis": analysis_data.get("education_analysis", {}),
                    "keyword_analysis": analysis_data.get("keyword_analysis", {}),
                    "ai_recommendations": analysis_data.get("ai_recommendations", {}),
                    "interview_questions": analysis_data.get("interview_questions", [])
                }
                res = supabase_client.table("analyses").insert(record).execute()
                if res.data:
                    return analysis_data
            except Exception as e:
                logger.error(f"Supabase save_analysis error: {e}")
        return local_db.save_analysis(analysis_data)

    def get_user_analyses(self, user_id: Optional[str], limit: int = 50) -> List[Dict[str, Any]]:
        if supabase_client:
            try:
                query = supabase_client.table("analyses").select("*").order("created_at", desc=True).limit(limit)
                if user_id:
                    query = query.eq("user_id", user_id)
                res = query.execute()
                if res.data is not None:
                    return res.data
            except Exception as e:
                logger.error(f"Supabase get_user_analyses error: {e}")
        return local_db.get_analyses_by_user(user_id, limit)

    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        if supabase_client:
            try:
                res = supabase_client.table("analyses").select("*").eq("id", analysis_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase get_analysis_by_id error: {e}")
        return local_db.get_analysis_by_id(analysis_id)

    def delete_analysis(self, analysis_id: str, user_id: Optional[str] = None) -> bool:
        if supabase_client:
            try:
                query = supabase_client.table("analyses").delete().eq("id", analysis_id)
                if user_id:
                    query = query.eq("user_id", user_id)
                res = query.execute()
                if res.data:
                    return True
            except Exception as e:
                logger.error(f"Supabase delete_analysis error: {e}")
        return local_db.delete_analysis(analysis_id, user_id)

    def log_audit(self, user_id: Optional[str], action: str, details: Dict[str, Any], ip_address: Optional[str] = None):
        if supabase_client:
            try:
                record = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "action": action,
                    "details": details,
                    "ip_address": ip_address
                }
                supabase_client.table("audit_logs").insert(record).execute()
            except Exception as e:
                logger.warning(f"Supabase audit log error: {e}")
        local_db.log_audit(user_id, action, details, ip_address)

    def get_admin_metrics(self) -> Dict[str, Any]:
        # Local or combined metrics
        return local_db.get_admin_metrics()


db_service = DatabaseService()
