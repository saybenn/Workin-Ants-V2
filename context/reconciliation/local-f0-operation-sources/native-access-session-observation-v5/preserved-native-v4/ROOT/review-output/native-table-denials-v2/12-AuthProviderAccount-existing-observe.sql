SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."auth_provider_accounts" WHERE "id"='bb020b48-ca28-55b2-9bc2-223f7e28250c'::pg_catalog.uuid));
