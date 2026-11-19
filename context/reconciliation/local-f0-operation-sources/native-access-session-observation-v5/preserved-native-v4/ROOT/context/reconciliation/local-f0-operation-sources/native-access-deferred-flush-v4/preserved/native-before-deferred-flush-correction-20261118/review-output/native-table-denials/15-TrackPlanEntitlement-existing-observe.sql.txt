SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_plan_entitlements" WHERE "id"='507cfabe-eefa-5846-a2bc-e4f924628530'::pg_catalog.uuid));
