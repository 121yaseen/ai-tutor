-- Apply email column migration to profiles table
-- Run this script against your PostgreSQL database

-- Add email column to profiles table
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS email TEXT;

-- Make email unique and not null (after ensuring existing data is handled)
-- First, update any existing profiles with a placeholder email if needed
UPDATE public.profiles 
SET email = 'user_' || id || '@placeholder.com' 
WHERE email IS NULL;

-- Now make email unique and not null
ALTER TABLE public.profiles 
ALTER COLUMN email SET NOT NULL;

-- Add unique constraint
ALTER TABLE public.profiles 
ADD CONSTRAINT profiles_email_unique UNIQUE (email);

-- Create index on email for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles (email);

-- Add a comment to document the purpose
COMMENT ON COLUMN public.profiles.email IS 'Unique email identifier linking Supabase auth with PostgreSQL data'; 