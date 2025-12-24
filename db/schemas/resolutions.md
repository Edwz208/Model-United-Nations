create table public.resolutions (
  resolution_id serial not null,
  number integer not null,
  title text not null,
  clauses integer not null default 0,
  council_id integer not null,
  submitter integer null,
  seconder integer null,
  negator integer null,
  url text null,
  status text not null default 'pending'::text,
  amendment_count integer not null default 0,
  constraint resolutions_pkey primary key (resolution_id),
  constraint unique_resolution_number_per_council unique (council_id, number),
  constraint unique_resolution_title_per_council unique (council_id, title),
  constraint resolutions_seconder_fkey foreign KEY (seconder) references countries (country_id) on delete set null,
  constraint resolutions_council_id_fkey foreign KEY (council_id) references councils (council_id) on delete CASCADE,
  constraint resolutions_submitter_fkey foreign KEY (submitter) references countries (country_id) on delete set null,
  constraint resolutions_submitter_member_fkey foreign KEY (submitter, council_id) references country_council (country_id, council_id) on delete set null,
  constraint resolutions_seconder_member_fkey foreign KEY (seconder, council_id) references country_council (country_id, council_id) on delete set null,
  constraint resolutions_negator_fkey foreign KEY (negator) references countries (country_id) on delete set null,
  constraint resolutions_negator_member_fkey foreign KEY (negator, council_id) references country_council (country_id, council_id) on delete set null
) TABLESPACE pg_default;

# for safety checks for both country and country_council deletions, must manually check that countries are in council in backend, otherwise fk will set null