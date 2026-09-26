# System Architecture Documentation

## Architectural Overview

Analyzer.ai employs a decoupled, production-grade micro-architecture designed for speed, security, and extensibility:

```
┌─────────────────────────────────────────────────────────────┐
│                 Frontend Client Layer                       │
│  - Vanilla HTML5 / Modern CSS (Tailwind) / Vanilla JS       │
│  - Zero build-step requirement (runs anywhere)              │
│  - Strict security: NO API keys or Supabase secrets stored  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST HTTP (Bearer JWT / CORS)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Application Gateway                 │
│  - CORS Middleware & Centralized Error Handlers             │
│  - JWT Bearer Authentication & Role-Based Access            │
│  - Pydantic v2 Input/Output Contract Validation             │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│    Core Extraction Engine    │ │     Core Analytical Engine  │
│  - PDF Parser (pypdf)        │ │  - 500+ Skill Ontology      │
│  - DOCX Parser (python-docx) │ │  - Action Verb Scorer       │
│  - Semantic Section Slicer   │ │  - Quantifiable KPI Detector│
│  - Contact Info Extractor    │ │  - Keyword Density Scorer   │
└──────────────┬───────────────┘ └─────────────┬───────────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│  Database Persistence Layer  │ │  AI Generative Service      │
│  - Supabase PostgreSQL Client│ │  - Google Gemini 1.5 Flash  │
│  - Dual-mode Local Fallback  │ │  - OpenAI GPT-4o-mini       │
│  - JSONB Analytics Storage   │ │  - Built-in Heuristic STAR  │
│  - Audit Logging Engine      │ │  - Custom Interview Q&A     │
└──────────────────────────────┘ └─────────────────────────────┘
```

---

## 1. Document Extraction Pipeline
1. **Format Validation**: Accepts `.pdf`, `.docx`, `.doc`.
2. **Text Sanitization**:
   - `pypdf`: Streams page characters, cleans zero-width spaces, normalizes carriage returns.
   - `python-docx`: Iterates through paragraphs, headers, and nested table cells.
3. **Section Segmentation**: Regex heuristics identify boundaries for Summary, Experience, Education, Technical Skills, Projects, and Certifications.
4. **Contact Info Extractor**: Captures candidate email, phone numbers, LinkedIn URL, and GitHub handle.

---

## 2. ATS Multi-Factor Scoring Algorithm
ATS Score is a weighted composite index from 0 to 100 calculated as follows:

$$\text{ATS Score} = (S \times 0.35) + (E \times 0.25) + (K \times 0.20) + (D \times 0.10) + (F \times 0.10)$$

Where:
- **$S$ (Skills Match - 35%)**: Ratio of candidate skills matching required job description competencies. Penalizes critical missing skills heavier than optional skills.
- **$E$ (Experience & Impact - 25%)**: Evaluates strong action verbs ("Architected", "Optimized") versus passive verbs ("Assisted", "Helped"), plus quantifiable KPI indicators (percentages, dollar amounts, throughput metrics).
- **$K$ (Keywords - 20%)**: Token frequency of high-relevance recruiter search terms in the target JD.
- **$D$ (Education & Credentials - 10%)**: Degree level match (BS, MS, PhD) and industry certifications (AWS, CKA, PMP).
- **$F$ (Formatting & Parseability - 10%)**: Evaluates clean section structure, bullet density, and ideal length (350–1100 words).

---

## 3. Dual-Mode Database Resilience
- **Supabase Mode**: Uses `supabase-py` to write directly to PostgreSQL tables with Row-Level Security.
- **Local Fallback Mode**: If Supabase credentials are not yet entered, it automatically reads and writes to `backend/data/storage.json`, preserving all data structures and enabling instant testing out of the box.

---

## 4. Security Principles
- **No Secrets in Frontend**: The frontend only holds a short-lived JWT token returned upon authentication.
- **Backend Protected**: Supabase service keys, database passwords, and AI API keys reside exclusively in `backend/.env`.
- **RBAC**: Protected routes enforce `user` vs `admin` roles.
