create table public.country_council (
  country_id integer not null,
  council_id integer not null,
  constraint country_council_pkey primary key (country_id, council_id),
  constraint country_council_council_id_fkey foreign KEY (council_id) references councils (council_id) on delete CASCADE,
  constraint country_council_country_id_fkey foreign KEY (country_id) references countries (country_id) on delete CASCADE
) TABLESPACE pg_default;

# must be able to get all countries in a council, get all councils of a country all countries AND council

# should implement indexding on common searched columns like council_id of country e.g FROM countries c
JOIN councils co ON c.council_id = co.council_id; so that when you loop over FROM and try to add councils it will automatically go to the structure containing those rows with matching council_id

must be able to attach main_council to all
when modifying a  country must be able to modify councils list, but will not delete main council from list, unless deleting only from the join table 
