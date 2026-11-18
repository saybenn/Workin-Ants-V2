SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."user_roles" WHERE "user_id"='fd7f3c21-614d-5a4c-857f-d2e99516c6bf'::pg_catalog.uuid AND "role"='user'::app.platform_role));
