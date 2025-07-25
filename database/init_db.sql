-- ============================================
-- Setup Script for AI Tutor Postgres DB
-- ============================================

-- 🟡 STEP 1: (Optional) Create the database
-- Uncomment the next two lines if you haven't already created the DB manually
CREATE DATABASE ai_tutor_db;
\c ai_tutor_db

-- 🟡 STEP 2: Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- 🟢 Table: feedback
-- ============================================
CREATE TABLE IF NOT EXISTS public.feedback (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_email TEXT NOT NULL,
  session_id TEXT NULL,
  feedback_type TEXT NOT NULL,
  rating INTEGER NULL,
  title TEXT NOT NULL,
  comments TEXT NOT NULL,
  metadata JSONB NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
  CONSTRAINT feedback_pkey PRIMARY KEY (id),
  CONSTRAINT feedback_feedback_type_check CHECK (
    feedback_type = ANY (ARRAY[
      'general',
      'feature_request',
      'bug_report',
      'ui_feedback',
      'content_feedback'
    ])
  ),
  CONSTRAINT feedback_rating_check CHECK (
    rating IS NULL OR (rating >= 1 AND rating <= 5)
  )
);

CREATE INDEX IF NOT EXISTS idx_feedback_user_email ON public.feedback (user_email);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON public.feedback (created_at DESC);

-- ============================================
-- 🟢 Table: profiles
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid NOT NULL,
  full_name TEXT NULL,
  updated_at TIMESTAMPTZ NULL,
  first_name TEXT NULL,
  last_name TEXT NULL,
  phone_number TEXT NULL,
  preparing_for TEXT NULL DEFAULT 'IELTS',
  previously_attempted_exam BOOLEAN NULL,
  previous_band_score DOUBLE PRECISION NULL,
  exam_date DATE NULL,
  target_band_score DOUBLE PRECISION NULL,
  country TEXT NULL DEFAULT 'India',
  native_language TEXT NULL,
  onboarding_completed BOOLEAN NULL DEFAULT FALSE,
  CONSTRAINT profiles_pkey PRIMARY KEY (id)
  -- Uncomment the next line if you are using Supabase or have an auth.users table
  -- , CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users (id) ON DELETE CASCADE
);

-- ============================================
-- 🟢 Table: students
-- ============================================
CREATE TABLE IF NOT EXISTS public.students (
  email TEXT NOT NULL,
  name TEXT NULL,
  history JSONB NOT NULL DEFAULT '[]'::jsonb,
  CONSTRAINT students_pkey PRIMARY KEY (email)
);
