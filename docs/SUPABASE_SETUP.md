# Supabase PostgreSQL Integration Guide

This guide walks you through connecting **Analyzer.ai** to your Supabase PostgreSQL instance.

---

## 1. Create a Supabase Project

1. Log in to [Supabase](https://supabase.com/).
2. Click **New Project**, select an organization, name your project (e.g. `ai-resume-analyzer`), set a secure database password, and choose your preferred cloud region.

---

## 2. Execute the Database Migration Schema

1. In the Supabase Dashboard left sidebar, navigate to **SQL Editor** (the terminal icon).
2. Click **New query**.
3. Copy the entire contents of [`backend/database/schema.sql`](../backend/database/schema.sql) and paste it into the query editor.
4. Click **Run** (or press `Ctrl+Enter`).

### What this schema provisions:
- **`users`**: Candidate and administrator accounts with bcrypt password hashes and roles (`user`, `admin`).
- **`resumes`**: Raw extracted text and parsed sections for candidate resumes.
- **`analyses`**: Full ATS analysis records with JSONB columns for `score_breakdown`, `matched_skills`, `missing_skills`, `experience_analysis`, `ai_recommendations`, and `interview_questions`.
- **`audit_logs`**: System activity audit tracking for security and admin analytics.
- **Indexes**: High-performance indexes on `user_id`, `created_at`, and `ats_score`.
- **Row Level Security (RLS)**: Protects user records so candidates can only access their own analyses.
- **Default Seed Accounts**:
  - Admin: `admin@resumely.ai` (Password: `Admin@123456`)
  - Demo User: `demo@resumely.ai` (Password: `Admin@123456`)

---

## 3. Retrieve Supabase API Credentials

1. Navigate to **Project Settings** (gear icon) -> **API**.
2. Copy:
   - **Project URL** (e.g. `https://xyzcompany.supabase.co`)
   - **`anon` public key**
   - **`service_role` secret key** (needed for backend administrative queries and RLS bypass for system metrics)

---

## 4. Configure Backend Environment Variables

Open `backend/.env` and update the Supabase parameters:

```env
# Supabase PostgreSQL Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

---

## 5. Verify Connectivity

Start or restart your FastAPI server:

```powershell
cd backend
& .venv\Scripts\python.exe run.py
```

The server console will output:
```
[INFO] Successfully initialized Supabase PostgreSQL client.
```
And the frontend header pill will display:
```
Supabase Connected (Online)
```
