SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_subscription_events" WHERE "id"='741e3fc5-63db-53ba-8122-3f24840f3b4d'::pg_catalog.uuid));
