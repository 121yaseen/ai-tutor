-- Create students table
CREATE TABLE public.students (
    email text PRIMARY KEY,
    name text,
    history jsonb DEFAULT '[]'::jsonb NOT NULL
);

ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for authenticated users based on email"
  ON public.students FOR SELECT
  TO authenticated
  USING (auth.email() = email);

CREATE POLICY "Enable insert for authenticated users"
  ON public.students FOR INSERT
  TO authenticated
  WITH CHECK (auth.email() = email);

CREATE POLICY "Enable update for authenticated users"
  ON public.students FOR UPDATE
  TO authenticated
  USING (auth.email() = email);
