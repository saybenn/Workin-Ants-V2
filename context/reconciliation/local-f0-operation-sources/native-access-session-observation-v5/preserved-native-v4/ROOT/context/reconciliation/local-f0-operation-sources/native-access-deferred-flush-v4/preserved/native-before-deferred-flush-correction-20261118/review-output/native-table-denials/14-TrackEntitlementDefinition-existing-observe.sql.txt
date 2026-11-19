SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_entitlement_definitions" WHERE "id"='d552339e-0c94-5e6f-80b8-f6b70fad3cc7'::pg_catalog.uuid));
