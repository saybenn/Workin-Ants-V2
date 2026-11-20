SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_subscriptions" WHERE "id"='fbd0a523-22f3-55c0-b2c9-9c05b155ad28'::pg_catalog.uuid));
