create table public.students (
  email text not null,
  name text null,
  history jsonb not null default '[]'::jsonb,
  constraint students_pkey primary key (email)
) TABLESPACE pg_default;