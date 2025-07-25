-- Complete profiles table migration
-- Add all missing columns to match Prisma schema

-- Add email column if not exists
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS email TEXT;

-- Add onboarding_presented column if not exists
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS onboarding_presented BOOLEAN DEFAULT FALSE;

-- Add created_at column if not exists
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();

-- Update existing records with placeholder email if needed
UPDATE public.profiles 
SET email = 'user_' || id || '@placeholder.com' 
WHERE email IS NULL;

-- Make email unique and not null
ALTER TABLE public.profiles 
ALTER COLUMN email SET NOT NULL;

-- Add unique constraint on email (handle if already exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'profiles_email_unique') THEN
        ALTER TABLE public.profiles ADD CONSTRAINT profiles_email_unique UNIQUE (email);
    END IF;
END $$;

-- Create index on email for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles (email);

-- Add comments for documentation
COMMENT ON COLUMN public.profiles.email IS 'Unique email identifier linking Supabase auth with PostgreSQL data';
COMMENT ON COLUMN public.profiles.onboarding_presented IS 'Flag indicating if onboarding has been presented to user';
COMMENT ON COLUMN public.profiles.created_at IS 'Timestamp when profile was created'; 