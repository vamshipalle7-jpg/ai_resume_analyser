from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# ----------------- Auth Schemas -----------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = "Job Seeker"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str = "user"
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

# ----------------- Analysis Sub-Schemas -----------------
class ScoreBreakdown(BaseModel):
    skills: int = Field(..., ge=0, le=100)
    experience: int = Field(..., ge=0, le=100)
    keywords: int = Field(..., ge=0, le=100)
    education: int = Field(..., ge=0, le=100)
    formatting: int = Field(..., ge=0, le=100)

class MissingSkill(BaseModel):
    skill: str
    priority: str  # "Critical", "Recommended", "Bonus"
    category: str  # "Core Technical", "Tool / Framework", "Soft Skill", "Domain"
    tip: str

class ExperienceAnalysis(BaseModel):
    estimated_years: float
    detected_seniority: str
    required_seniority_match: bool
    action_verb_score: int  # 0 to 100
    quantifiable_metrics_count: int
    bullet_points_assessed: int
    summary_verdict: str
    highlights: List[str]

class EducationAnalysis(BaseModel):
    detected_degrees: List[str]
    highest_degree: Optional[str]
    degree_matched: bool
    certifications_found: List[str]
    verdict: str

class KeywordItem(BaseModel):
    keyword: str
    resume_count: int
    jd_count: int
    matched: bool
    importance: str  # "High", "Medium", "Low"

class KeywordAnalysis(BaseModel):
    density_score: int  # 0 to 100
    matched_keywords: List[KeywordItem]
    missing_critical_keywords: List[str]
    recommendation: str

class BulletPointRewrite(BaseModel):
    original: str
    improved: str
    framework: str = "STAR (Situation, Task, Action, Result)"
    rationale: str

class AIRecommendations(BaseModel):
    overall_verdict: str
    fit_assessment: str  # "High Match", "Moderate Match", "Needs Tailoring"
    strengths: List[str]
    weaknesses: List[str]
    bullet_point_rewrites: List[BulletPointRewrite]
    formatting_advice: List[str]
    action_plan: List[str]

class InterviewQuestion(BaseModel):
    question: str
    type: str  # "Technical", "Behavioral", "Situational", "Gap-Probe"
    rationale: str
    answer_strategy: str

# ----------------- Main Analysis Request & Response -----------------
class AnalysisRequest(BaseModel):
    job_title: str = Field(..., min_length=2)
    target_industry: Optional[str] = "Technology"
    job_description: str = Field(..., min_length=20)
    resume_text: Optional[str] = None

class AnalysisResult(BaseModel):
    id: str
    user_id: Optional[str] = None
    filename: str
    file_type: str
    job_title: str
    target_industry: str
    ats_score: int
    match_level: str  # "Exceptional", "Strong", "Moderate", "Needs Improvement"
    score_breakdown: ScoreBreakdown
    matched_skills: List[str]
    missing_skills: List[MissingSkill]
    bonus_skills: List[str]
    experience_analysis: ExperienceAnalysis
    education_analysis: EducationAnalysis
    keyword_analysis: KeywordAnalysis
    ai_recommendations: AIRecommendations
    interview_questions: List[InterviewQuestion]
    created_at: str

class HistoryItem(BaseModel):
    id: str
    user_id: Optional[str]
    filename: str
    job_title: str
    ats_score: int
    match_level: str
    created_at: str

# ----------------- Admin Schemas -----------------
class AdminStats(BaseModel):
    total_scans: int
    total_users: int
    avg_ats_score: float
    pass_rate_percent: float  # Score >= 70
    score_distribution: Dict[str, int]
    top_missing_skills: List[Dict[str, Any]]
    recent_scans: List[Dict[str, Any]]

# ----------------- Health Schema -----------------
class HealthResponse(BaseModel):
    status: str
    version: str
    database_mode: str
    ai_provider: str
    timestamp: str
