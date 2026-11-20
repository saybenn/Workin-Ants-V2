SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_entitlement_grants" WHERE "id"='dff849ab-9955-522c-80ba-a73ad01d713e'::pg_catalog.uuid));
