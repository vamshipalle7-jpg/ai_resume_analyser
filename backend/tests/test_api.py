import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert "database_mode" in data


def test_auth_registration_and_login():
    test_email = f"test_{os.urandom(4).hex()}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "Password123!",
        "full_name": "Test Tester"
    })
    assert reg_resp.status_code == 200
    token_data = reg_resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Test /me endpoint
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == test_email


def test_analyze_text_endpoint():
    payload = {
        "job_title": "FastAPI Developer",
        "target_industry": "Technology",
        "job_description": "We need a Python FastAPI backend developer with Docker, PostgreSQL, and Redis expertise.",
        "resume_text": "Experienced Python and FastAPI engineer. Designed PostgreSQL schemas, used Docker and Redis for caching."
    }
    response = client.post("/api/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ats_score"] > 50
    assert "Python" in data["matched_skills"]
    assert len(data["interview_questions"]) > 0
    assert "ai_recommendations" in data


def test_analyze_file_upload_pdf():
    pdf_path = "tests/assets/sample_backend_developer.pdf"
    assert os.path.exists(pdf_path)

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/analyze/upload",
            data={
                "job_title": "Senior Python Backend Engineer",
                "target_industry": "FinTech",
                "job_description": "Looking for Python, FastAPI, Docker, and Kubernetes skills."
            },
            files={"file": ("sample_backend_developer.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample_backend_developer.pdf"
    assert data["file_type"] == "pdf"
    assert data["ats_score"] > 60
    assert "FastAPI" in data["matched_skills"]


def test_admin_stats_endpoint():
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "avg_ats_score" in data
    assert "top_missing_skills" in data
