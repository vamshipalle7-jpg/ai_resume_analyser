# 🚀 Analyzer.ai — Production-Style AI Resume Analyzer

A production-ready AI Resume Analyzer built with a clean separated architecture: modern **HTML, CSS, JavaScript** on the frontend, **Python FastAPI** on the backend, **Supabase PostgreSQL** for the database, and **AI Models** (Gemini / OpenAI / Heuristic) for deep resume optimization and interview coaching.

---

## 🌟 Key Features

- 📄 **Multi-Format Resume Support**: Native extraction for both **PDF** (`pypdf`) and **DOCX** (`python-docx`).
- 🎯 **Multi-Factor ATS Scoring Engine**: 0–100% weighted composite scoring evaluating:
  - **Skill Matching (35%)**: 500+ tech competencies categorized into languages, frameworks, cloud, databases, and AI.
  - **Experience & Impact (25%)**: Strong action verbs vs passive voice, years of experience, and quantifiable KPIs.
  - **Keyword Density & Relevance (20%)**: Token frequency of high-impact recruiter search terms.
  - **Education & Credentials (10%)**: Degree level and industry certifications (AWS, CKA, PMP).
  - **Formatting & Parseability (10%)**: Clean section headers and optimal word density.
- 💡 **AI Recommendations & STAR Rewrites**: Contextual before-and-after bullet rewrites using the STAR (Situation, Task, Action, Result) methodology.
- 🎙️ **Role-Specific Interview Questions**: Tailored technical, situational, and gap-probing interview questions with recommended answering strategies.
- 🗄️ **Dual-Mode Database**:
  - **Supabase PostgreSQL Mode**: Production tables, JSONB storage, indexes, and Row Level Security (RLS).
  - **Zero-Config Local Storage Mode**: Runs seamlessly out of the box before Supabase credentials are configured!
- 🔐 **User Authentication & RBAC**: JWT Bearer token authentication with bcrypt password hashing and roles (`user`, `admin`).
- 📊 **Executive Admin Dashboard**: Real-time metrics on scans run, user growth, average ATS scores, score distribution, and top missing skills across all applicants.
- 🖨️ **Print & Export**: Print formatted resume audit reports or export raw JSON analysis.

---

## 🏗️ Architecture

```
Frontend (HTML5 / Tailwind CSS / Vanilla JS)
                    │
                    ▼ REST API (JWT Bearer Token / CORS)
FastAPI Backend (Python 3.12)
   ├── Extraction Service (PDF & DOCX text parsing)
   ├── ATS Scoring Engine (Skill taxonomy & metrics)
   ├── AI Recommendations Engine (STAR rewrites & Q&A)
   └── Admin & Audit Service
        │                         │
        ▼                         ▼
Supabase PostgreSQL       AI Model Provider
(Tables, RLS, Indexes)    (Gemini / OpenAI / Heuristic)
```

> **Security Note**: No secret keys, database credentials, or AI tokens are ever exposed in frontend code. All requests flow through the FastAPI backend gateway.

---

## 📁 Folder Structure

```
ai-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── models/            # Pydantic schemas and data contracts
│   │   ├── routes/            # FastAPI API routers (Auth, Analyze, History, Admin, Health)
│   │   ├── services/          # Document Extractor, ATS Engine, AI Service, Admin Service
│   │   ├── auth.py            # JWT token encoding & bcrypt password hashing
│   │   ├── config.py          # Settings management with pydantic-settings
│   │   ├── database.py        # Supabase client & local persistent fallback
│   │   └── main.py            # FastAPI app initialization & CORS middleware
│   ├── database/
│   │   └── schema.sql         # Supabase PostgreSQL schema with RLS and seed data
│   ├── scripts/
│   │   └── generate_samples.py # Script to create realistic PDF and DOCX test resumes
│   ├── tests/                 # Automated test suite (Extractor, ATS Engine, API endpoints)
│   ├── .env.example           # Environment variables template
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Backend launcher
├── frontend/
│   ├── index.html             # Responsive Single Page Application interface
│   ├── css/
│   │   └── styles.css         # Custom typography, animations, and print styles
│   ├── js/
│   │   ├── config.js          # API base URL configuration (No secrets!)
│   │   ├── api.js             # HTTP client with JWT injection
│   │   ├── auth.js            # User session management
│   │   ├── analyzer.js        # File upload, dropzone, and results rendering
│   │   ├── history.js         # Scan history management
│   │   ├── admin.js           # Admin metrics and distribution charts
│   │   └── app.js             # Application coordinator and toasts
│   └── assets/
│       └── sample_resumes/    # Sample PDF and DOCX files for 1-click testing
├── docs/
│   ├── SUPABASE_SETUP.md      # Supabase setup and migration guide
│   └── ARCHITECTURE.md        # Technical architecture and scoring algorithm
├── start.bat                  # One-click Windows startup script
├── start.ps1                  # PowerShell startup script
└── README.md                  # Project documentation
```

---

## ⚡ Quickstart Guide

### Step 1: Set up the Python Backend

```powershell
cd backend

# Option A: Using uv (Recommended - ultra fast)
uv venv --python 3.12 .venv
uv pip install -r requirements.txt --python .venv\Scripts\python.exe

# Option B: Using standard Python 3.12
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

A ready-to-use `.env` file is included in `backend/` configured for **zero-config local evaluation mode**.

To connect Supabase PostgreSQL or Google Gemini / OpenAI:
1. Open `backend/.env`.
2. Follow the instructions in [docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md) to set `SUPABASE_URL` and `SUPABASE_KEY`.
3. Add your `AI_API_KEY` if you wish to use Google Gemini or OpenAI (the built-in heuristic AI engine works without any API keys).

### Step 3: Run the Backend

```powershell
cd backend
.\.venv\Scripts\python.exe run.py
```
- Server URL: **http://127.0.0.1:8000**
- Interactive Swagger API Docs: **http://127.0.0.1:8000/docs**

### Step 4: Open the Frontend

Simply open `frontend/index.html` in any web browser, or serve it using any static server:
```powershell
# In a new terminal window:
cd frontend
python -m http.server 3000
```
Open **http://localhost:3000** (or double click `frontend/index.html`).

---

## 🧪 Running Automated Tests

Run the full automated test suite covering document extraction, ATS scoring, and API endpoints:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Expected output:
```
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_auth_registration_and_login PASSED
tests/test_api.py::test_analyze_text_endpoint PASSED
tests/test_api.py::test_analyze_file_upload_pdf PASSED
tests/test_api.py::test_admin_stats_endpoint PASSED
tests/test_ats_engine.py::test_ats_skills_matching PASSED
tests/test_ats_engine.py::test_experience_and_action_verbs PASSED
tests/test_extractor.py::test_pdf_extraction PASSED
tests/test_extractor.py::test_docx_extraction PASSED
tests/test_extractor.py::test_contact_info_parser PASSED
10 passed in 0.88s
```

---

## 👤 Default Demo Accounts

The application includes two pre-seeded accounts:

| Role | Email | Password | Privileges |
|------|-------|----------|------------|
| **Admin** | `admin@analyzer.ai` | `Admin@123456` | Full Admin Dashboard, Global Scan Analytics |
| **Candidate** | `demo@analyzer.ai` | `Admin@123456` | Resume Analysis, Personal History |

You can also create a new account directly in the UI.

---

## 📄 License
MIT License. Built for production recruitment and applicant tracking intelligence.
