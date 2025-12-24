create table public.countries (
  name text not null,
  delegate1 text null,
  delegate2 text null,
  delegate3 text null,
  delegate4 text null,
  role text null default 'member'::text,
  login text null default ''::text,
  speaker_points integer null default 0,
  amendments_submitted integer null default 0,
  country_id serial not null,
  constraint countries_pkey primary key (country_id),
  constraint country_name_key unique (name)
) TABLESPACE pg_default;