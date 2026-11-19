SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."professional_profiles" WHERE "id"='bb86b4ba-9cd7-5008-b30f-a1a0fe65ce86'::pg_catalog.uuid));
