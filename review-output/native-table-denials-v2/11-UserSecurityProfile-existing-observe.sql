SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."user_security_profiles" WHERE "id"='1cbf4490-3012-5925-82c2-242c6b6c1927'::pg_catalog.uuid));
