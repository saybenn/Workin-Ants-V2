SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."age_gate_blocks" WHERE "id"='49723ae0-0cdd-5417-91c2-fa9d77e433d8'::pg_catalog.uuid));
