create table public.secretariat (
  secretariat_id serial not null,
  name text not null default ''::text,
  position text not null default ''::text,
  constraint secretariat_pkey primary key (secretariat_id),
  constraint unique_exec unique (name)
) TABLESPACE pg_default;