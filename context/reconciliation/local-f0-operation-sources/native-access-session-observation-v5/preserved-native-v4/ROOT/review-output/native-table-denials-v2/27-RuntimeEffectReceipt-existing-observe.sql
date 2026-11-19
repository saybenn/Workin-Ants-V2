SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_effect_receipt" WHERE "id"='3d1780cf-5495-555d-a3f0-9204d9160128'::pg_catalog.uuid));
