SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."consent_disposition" WHERE "id"='6a58aae8-4e3d-5181-8c11-327a76313125'::pg_catalog.uuid));
