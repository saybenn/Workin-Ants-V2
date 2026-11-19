SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."privacy_requests" WHERE "id"='e6888d0f-d15d-5d82-927f-4c7915315879'::pg_catalog.uuid));
