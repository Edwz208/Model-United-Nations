create table public.amendments (
  amendment_id integer generated always as identity not null,
  resolution_id integer not null,
  amendment_number integer not null,
  clause_number smallint not null,
  content text null,
  submitter integer not null,
  status text not null default 'pending review'::text,
  modified_at timestamp without time zone not null default CURRENT_TIMESTAMP,
  constraint amendments_pkey primary key (amendment_id),
  constraint amendments_resolution_amendment_unique unique (resolution_id, amendment_number),
  constraint amendments_resolution_fkey foreign KEY (resolution_id) references resolutions (resolution_id) on delete CASCADE
) TABLESPACE pg_default;

# cannot enforce that country of submitterin council unless add council_id to amendment, maybe unnecessary so check in backend instead