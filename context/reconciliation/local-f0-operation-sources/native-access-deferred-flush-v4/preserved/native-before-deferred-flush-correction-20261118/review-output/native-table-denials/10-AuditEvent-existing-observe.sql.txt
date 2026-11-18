SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."audit_events" WHERE "id"='2b9f0d67-d675-5f87-8dbc-86b77f4c8125'::pg_catalog.uuid));
