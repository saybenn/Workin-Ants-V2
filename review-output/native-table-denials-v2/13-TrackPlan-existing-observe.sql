SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_plans" WHERE "id"='3f3b8aa8-71e7-501c-97d8-ceb0f8bc7d0d'::pg_catalog.uuid));
