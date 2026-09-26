import pytest
from app.services.ats_engine import ats_engine


def test_ats_skills_matching():
    resume = """
    Experienced Backend Developer with deep knowledge of Python, FastAPI, PostgreSQL, Redis, and Docker.
    Built automated CI/CD pipelines using GitHub Actions.
    """
    job_description = """
    Requirements:
    - Proficient in Python, FastAPI, and PostgreSQL.
    - Experience with Docker, Kubernetes, and AWS (Amazon Web Services).
    - Nice to have: Redis and GraphQL.
    """

    analysis = ats_engine.analyze(resume, job_description, job_title="Backend Engineer")
    
    # Check matched skills
    matched = analysis["matched_skills"]
    assert "Python" in matched
    assert "FastAPI" in matched
    assert "PostgreSQL" in matched
    assert "Docker" in matched
    assert "Redis" in matched

    # Check missing skills
    missing_names = [m.skill for m in analysis["missing_skills"]]
    assert "Kubernetes" in missing_names
    assert "Amazon Web Services (AWS)" in missing_names

    # Check score range
    assert 50 <= analysis["ats_score"] <= 100
    assert analysis["score_breakdown"].skills > 0
    assert analysis["score_breakdown"].experience > 0


def test_experience_and_action_verbs():
    resume = """
    Work Experience:
    Senior Software Engineer | Apex (2020 - 2024)
    - Architected and deployed 8 microservices in Python, handling 5M daily requests.
    - Spearheaded database query optimization reducing latency by 45%.
    - Engineered continuous integration pipelines with 90% unit test coverage.
    """
    job_description = "Looking for a Senior Backend Developer with 4+ years of experience."

    analysis = ats_engine.analyze(resume, job_description, job_title="Senior Backend Developer")
    exp = analysis["experience_analysis"]
    
    assert exp.action_verb_score >= 60
    assert exp.quantifiable_metrics_count >= 2
    assert exp.detected_seniority in ["Senior", "Mid-Level", "Lead / Architect"]
