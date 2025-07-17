create table public.feedback (
  id uuid not null default gen_random_uuid (),
  user_email text not null,
  session_id text null,
  feedback_type text not null,
  rating integer null,
  title text not null,
  comments text not null,
  metadata jsonb null default '{}'::jsonb,
  created_at timestamp with time zone not null default timezone ('utc'::text, now()),
  updated_at timestamp with time zone not null default timezone ('utc'::text, now()),
  constraint feedback_pkey primary key (id),
  constraint feedback_feedback_type_check check (
    (
      feedback_type = any (
        array[
          'general'::text,
          'feature_request'::text,
          'bug_report'::text,
          'ui_feedback'::text,
          'content_feedback'::text
        ]
      )
    )
  ),
  constraint feedback_rating_check check (
    (
      (rating >= 1)
      and (rating <= 5)
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_feedback_user_email on public.feedback using btree (user_email) TABLESPACE pg_default;

create index IF not exists idx_feedback_created_at on public.feedback using btree (created_at desc) TABLESPACE pg_default;