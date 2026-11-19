SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."consent_logs" WHERE "id"='bf0f5fab-7f74-514d-b3c2-edb88a1eca45'::pg_catalog.uuid));
