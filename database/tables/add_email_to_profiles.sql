-- Add email column to profiles table
ALTER TABLE public.profiles 
ADD COLUMN email TEXT UNIQUE NOT NULL;

-- Create index on email for better query performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles (email);

-- Add a comment to document the purpose
COMMENT ON COLUMN public.profiles.email IS 'Unique email identifier linking Supabase auth with PostgreSQL data'; 