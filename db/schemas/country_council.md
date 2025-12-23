create table public.country_council (
  country_id integer not null,
  council_id integer not null,
  constraint country_council_pkey primary key (country_id, council_id),
  constraint country_council_council_id_fkey foreign KEY (council_id) references councils (council_id) on delete CASCADE,
  constraint country_council_country_id_fkey foreign KEY (country_id) references countries (country_id) on delete CASCADE
) TABLESPACE pg_default;