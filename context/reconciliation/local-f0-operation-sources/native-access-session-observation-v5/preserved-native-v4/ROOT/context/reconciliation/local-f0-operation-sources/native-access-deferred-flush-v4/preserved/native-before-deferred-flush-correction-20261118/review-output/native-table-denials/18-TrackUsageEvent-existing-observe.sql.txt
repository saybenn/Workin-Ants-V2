SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_usage_events" WHERE "id"='5b4e2ffc-98bd-5890-9e31-e0bd9498efb8'::pg_catalog.uuid));
