SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."candidate_profiles" WHERE "id"='d4592bcc-2742-53db-8bc8-7fdf59588c3e'::pg_catalog.uuid));
