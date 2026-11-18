SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."age_gate_attempts" WHERE "id"='6756ce05-264c-5520-bf96-b13afa953997'::pg_catalog.uuid));
