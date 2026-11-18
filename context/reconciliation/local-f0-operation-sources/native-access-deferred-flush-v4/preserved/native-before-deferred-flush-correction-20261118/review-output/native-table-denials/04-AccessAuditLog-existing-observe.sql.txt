SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."access_audit_logs" WHERE "id"='e4f7eed0-b2e3-5df1-a8e9-8d5d5b86a90f'::pg_catalog.uuid));
