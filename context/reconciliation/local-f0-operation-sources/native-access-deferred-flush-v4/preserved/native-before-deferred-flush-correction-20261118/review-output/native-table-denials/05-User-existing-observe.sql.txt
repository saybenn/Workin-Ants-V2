SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."users" WHERE "id"='fd7f3c21-614d-5a4c-857f-d2e99516c6bf'::pg_catalog.uuid));
