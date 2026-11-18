SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_usage_reservation" WHERE "id"='0d6d8274-d15a-5321-ad28-7a82047e38c9'::pg_catalog.uuid));
