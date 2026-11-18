SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_usage_counters" WHERE "id"='fdd63db0-9aae-516a-934b-0df3a240c39a'::pg_catalog.uuid));
