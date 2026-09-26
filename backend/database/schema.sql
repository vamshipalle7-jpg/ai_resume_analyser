-- ==============================================================================
-- AI Resume Analyzer - Supabase PostgreSQL Schema
-- Run this script in your Supabase SQL Editor: Dashboard -> SQL Editor -> New Query
-- ==============================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Create Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create Resumes Table
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- 'pdf' or 'docx'
    file_size_bytes INTEGER,
    raw_text TEXT NOT NULL,
    parsed_sections JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create Analyses Table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES public.resumes(id) ON DELETE SET NULL,
    job_title VARCHAR(255) NOT NULL,
    target_industry VARCHAR(100) DEFAULT 'Technology',
    job_description TEXT NOT NULL,
    ats_score INTEGER NOT NULL CHECK (ats_score >= 0 AND ats_score <= 100),
    score_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb,
    matched_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    bonus_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    experience_analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
    education_analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
    keyword_analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
    ai_recommendations JSONB NOT NULL DEFAULT '{}'::jsonb,
    interview_questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create Audit Logs Table (For Admin Analytics & Security)
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Indexes for High-Performance Queries
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_ats_score ON public.analyses(ats_score);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- 7. Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- 8. Seed Default Admin User
-- Password for admin is: Admin@123456
-- (Bcrypt hash below: $2b$12$e80yq9G0YIq.eW9g8b6kK.yGq7E4rM58xWn5E2cWq.oK/5H0f6sre or standard generated)
INSERT INTO public.users (email, hashed_password, full_name, role)
VALUES (
    'admin@resumely.ai',
    '$2b$12$K8dflG9Qd0v41p9xXfMhceH2QY1d6M3U2w6N8zB0cR.pY7A3k5fFe',
    'System Administrator',
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- Seed Default Test User (User@123456)
INSERT INTO public.users (email, hashed_password, full_name, role)
VALUES (
    'demo@resumely.ai',
    '$2b$12$K8dflG9Qd0v41p9xXfMhceH2QY1d6M3U2w6N8zB0cR.pY7A3k5fFe',
    'Demo Candidate',
    'user'
) ON CONFLICT (email) DO NOTHING;
