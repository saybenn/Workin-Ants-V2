SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_reservation" WHERE "id"='ef0228f5-ac51-50e0-baf6-e5da6ddbaae0'::pg_catalog.uuid));
