create table public.profiles (
  id uuid not null,
  full_name text null,
  updated_at timestamp with time zone null,
  first_name text null,
  last_name text null,
  phone_number text null,
  preparing_for text null default 'IELTS'::text,
  previously_attempted_exam boolean null,
  previous_band_score double precision null,
  exam_date date null,
  target_band_score double precision null,
  country text null default 'India'::text,
  native_language text null,
  onboarding_completed boolean null default false,
  constraint profiles_pkey primary key (id),
  constraint profiles_id_fkey foreign KEY (id) references auth.users (id) on delete CASCADE
) TABLESPACE pg_default;