SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."consent_content_revision" WHERE "id"='4b85a58c-01f3-5888-a1d2-ac4691357597'::pg_catalog.uuid));
