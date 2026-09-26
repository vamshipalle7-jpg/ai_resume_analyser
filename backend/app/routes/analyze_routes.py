import uuid
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from app.models.schemas import AnalysisResult, AnalysisRequest
from app.services.extractor import document_extractor
from app.services.ats_engine import ats_engine
from app.services.ai_service import ai_service
from app.database import db_service
from app.auth import get_current_user_optional

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])


@router.post("/upload", response_model=AnalysisResult)
async def analyze_uploaded_resume(
    file: UploadFile = File(...),
    job_title: str = Form(...),
    target_industry: Optional[str] = Form("Technology"),
    job_description: str = Form(...),
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Upload a resume file (PDF or DOCX), extract text, and run comprehensive ATS & AI analysis against Job Description.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    filename_lower = file.filename.lower()
    if not (filename_lower.endswith(".pdf") or filename_lower.endswith((".docx", ".doc"))):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Only PDF and DOCX documents are supported."
        )

    # Read bytes
    try:
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File size exceeds maximum 10MB limit.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    # 1. Document Extraction
    try:
        extracted = document_extractor.parse_document(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    raw_text = extracted["raw_text"]
    sections = extracted["sections"]
    file_type = extracted["file_type"]

    # 2. ATS Engine Scoring
    ats_results = ats_engine.analyze(
        resume_text=raw_text,
        job_description=job_description,
        job_title=job_title,
        sections=sections
    )

    # 3. AI Recommendations & Interview Questions
    ai_insights = await ai_service.generate_insights(
        resume_text=raw_text,
        job_description=job_description,
        job_title=job_title,
        matched_skills=ats_results["matched_skills"],
        missing_skills=ats_results["missing_skills"],
        ats_score=ats_results["ats_score"]
    )

    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    user_id = current_user["id"] if current_user else None

    # 4. Save to Database
    # Save resume record
    resume_id = db_service.save_resume(
        user_id=user_id,
        filename=file.filename,
        file_type=file_type,
        file_size_bytes=len(file_bytes),
        raw_text=raw_text,
        parsed_sections=sections
    )

    # Assemble complete analysis result
    result_data = {
        "id": analysis_id,
        "user_id": user_id,
        "resume_id": resume_id,
        "filename": file.filename,
        "file_type": file_type,
        "job_title": job_title,
        "target_industry": target_industry or "Technology",
        "job_description": job_description,
        "ats_score": ats_results["ats_score"],
        "match_level": ats_results["match_level"],
        "score_breakdown": ats_results["score_breakdown"],
        "matched_skills": ats_results["matched_skills"],
        "missing_skills": ats_results["missing_skills"],
        "bonus_skills": ats_results["bonus_skills"],
        "experience_analysis": ats_results["experience_analysis"],
        "education_analysis": ats_results["education_analysis"],
        "keyword_analysis": ats_results["keyword_analysis"],
        "ai_recommendations": ai_insights["ai_recommendations"],
        "interview_questions": ai_insights["interview_questions"],
        "created_at": created_at
    }

    db_service.save_analysis(result_data)
    db_service.log_audit(user_id, "RESUME_ANALYZED", {"filename": file.filename, "score": ats_results["ats_score"]})

    return AnalysisResult(**result_data)


@router.post("/text", response_model=AnalysisResult)
async def analyze_text(
    payload: AnalysisRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Analyze raw resume text against Job Description.
    """
    if not payload.resume_text or len(payload.resume_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Resume text is required and must contain at least 50 characters."
        )

    raw_text = payload.resume_text.strip()
    sections = document_extractor.parse_sections(raw_text)

    # 1. ATS Engine
    ats_results = ats_engine.analyze(
        resume_text=raw_text,
        job_description=payload.job_description,
        job_title=payload.job_title,
        sections=sections
    )

    # 2. AI Insights
    ai_insights = await ai_service.generate_insights(
        resume_text=raw_text,
        job_description=payload.job_description,
        job_title=payload.job_title,
        matched_skills=ats_results["matched_skills"],
        missing_skills=ats_results["missing_skills"],
        ats_score=ats_results["ats_score"]
    )

    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    user_id = current_user["id"] if current_user else None

    result_data = {
        "id": analysis_id,
        "user_id": user_id,
        "filename": "Direct Text Input",
        "file_type": "text",
        "job_title": payload.job_title,
        "target_industry": payload.target_industry or "Technology",
        "job_description": payload.job_description,
        "ats_score": ats_results["ats_score"],
        "match_level": ats_results["match_level"],
        "score_breakdown": ats_results["score_breakdown"],
        "matched_skills": ats_results["matched_skills"],
        "missing_skills": ats_results["missing_skills"],
        "bonus_skills": ats_results["bonus_skills"],
        "experience_analysis": ats_results["experience_analysis"],
        "education_analysis": ats_results["education_analysis"],
        "keyword_analysis": ats_results["keyword_analysis"],
        "ai_recommendations": ai_insights["ai_recommendations"],
        "interview_questions": ai_insights["interview_questions"],
        "created_at": created_at
    }

    db_service.save_analysis(result_data)
    return AnalysisResult(**result_data)


@router.get("/samples")
async def get_sample_presets():
    """
    Returns preloaded sample Job Descriptions and Resumes for quick 1-click evaluation.
    """
    return {
        "job_descriptions": [
            {
                "id": "backend_engineer",
                "title": "Senior Python & FastAPI Backend Engineer",
                "industry": "FinTech / SaaS",
                "description": (
                    "About the Role:\n"
                    "We are seeking an experienced Senior Backend Engineer to architect, build, and maintain high-performance microservices.\n\n"
                    "Requirements:\n"
                    "- 4+ years of professional backend engineering experience with Python and modern async frameworks (FastAPI, Django, or Flask).\n"
                    "- Strong expertise in PostgreSQL schema design, complex SQL optimization, and Redis caching.\n"
                    "- Hands-on experience with Docker containerization, Kubernetes, and AWS cloud services (ECS, S3, RDS).\n"
                    "- Proficiency in designing RESTful APIs, gRPC services, and event-driven architectures with Celery or Kafka.\n"
                    "- Solid understanding of CI/CD pipelines, Git, and automated testing with Pytest (aiming for >85% test coverage).\n"
                    "- Excellent system design skills and passion for clean, maintainable code."
                )
            },
            {
                "id": "fullstack_engineer",
                "title": "Full Stack Software Engineer",
                "industry": "Enterprise Software",
                "description": (
                    "Responsibilities:\n"
                    "- Develop end-to-end web applications with modern frontend and backend technologies.\n"
                    "- Build reactive, accessible user interfaces using React.js, TypeScript, and Tailwind CSS.\n"
                    "- Design scalable backend APIs using Node.js, Express, or Python FastAPI with PostgreSQL/MongoDB.\n"
                    "- Collaborate with product managers and UX designers to deliver user-centric features.\n"
                    "- Write robust unit and integration tests using Jest, React Testing Library, and Pytest.\n"
                    "- Experience with Docker, Git version control, and cloud deployments."
                )
            },
            {
                "id": "ai_ml_engineer",
                "title": "AI / Machine Learning Engineer",
                "industry": "Artificial Intelligence",
                "description": (
                    "Key Responsibilities:\n"
                    "- Build and deploy production-grade Large Language Model (LLM) pipelines, Retrieval-Augmented Generation (RAG) systems, and NLP models.\n"
                    "- Strong background in Python, PyTorch, TensorFlow, Pandas, and Scikit-Learn.\n"
                    "- Experience deploying models into cloud environments using Docker, FastAPI, and Vector Databases (Pinecone, ChromaDB, PGVector).\n"
                    "- Solid understanding of MLOps, CI/CD, and prompt engineering best practices."
                )
            },
            {
                "id": "devops_cloud_engineer",
                "title": "DevOps & Cloud Platform Engineer",
                "industry": "Cloud Infrastructure",
                "description": (
                    "Requirements:\n"
                    "- 3+ years experience managing cloud infrastructure on AWS, Azure, or GCP.\n"
                    "- Extensive experience with Docker containerization, Kubernetes (k8s) cluster orchestration, and Helm charts.\n"
                    "- Proficiency with Infrastructure-as-Code (IaC) using Terraform and Ansible.\n"
                    "- Strong experience building automated CI/CD deployment pipelines using GitHub Actions, GitLab CI, or Jenkins.\n"
                    "- Monitoring and observability setup using Prometheus, Grafana, and ELK stack.\n"
                    "- Scripting proficiency in Bash and Python for automation."
                )
            },
            {
                "id": "data_analyst",
                "title": "Data Analyst & Business Intelligence",
                "industry": "Analytics & BI",
                "description": (
                    "Qualifications:\n"
                    "- Proven experience analyzing large datasets, extracting actionable business insights, and KPI reporting.\n"
                    "- Advanced SQL skills (window functions, CTEs, performance tuning, schema design).\n"
                    "- Hands-on data visualization and dashboarding experience using Tableau, Power BI, or Looker.\n"
                    "- Proficiency in Python (Pandas, NumPy, Matplotlib) for data wrangling and statistical analysis.\n"
                    "- Experience with cloud data warehouses like Snowflake, BigQuery, or Amazon Redshift.\n"
                    "- Strong communication and stakeholder presentation skills."
                )
            },
            {
                "id": "frontend_specialist",
                "title": "Senior Frontend React & TypeScript Developer",
                "industry": "SaaS / Web Applications",
                "description": (
                    "Requirements:\n"
                    "- 4+ years building high-traffic, responsive web applications using React.js and TypeScript.\n"
                    "- Deep understanding of Next.js, Server-Side Rendering (SSR), and Static Site Generation (SSG).\n"
                    "- Mastery of modern CSS architectures, Tailwind CSS, styled-components, and responsive UI design.\n"
                    "- Experience with global state management (Redux Toolkit, Zustand, or TanStack Query).\n"
                    "- Automated frontend testing using Jest, React Testing Library, and Cypress.\n"
                    "- Strong focus on Core Web Vitals, performance profiling, and WCAG accessibility standards."
                )
            },
            {
                "id": "product_manager",
                "title": "Technical Product Manager",
                "industry": "Technology Products",
                "description": (
                    "Responsibilities:\n"
                    "- Own product vision, roadmap, and sprint backlog for developer platform and APIs.\n"
                    "- Translate customer needs and business objectives into clear user stories and technical requirements.\n"
                    "- Collaborate daily with software engineers, UX designers, and executive stakeholders in an Agile/Scrum environment.\n"
                    "- Define and monitor core product metrics, conversion funnels, and retention KPIs using Mixpanel or Amplitude.\n"
                    "- Prioritize trade-offs between technical debt, feature velocity, and user experience."
                )
            }
        ]
    }
