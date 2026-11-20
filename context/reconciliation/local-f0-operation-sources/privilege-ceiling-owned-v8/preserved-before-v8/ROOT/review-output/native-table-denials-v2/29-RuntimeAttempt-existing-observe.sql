SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_attempt" WHERE "id"='61e78ddd-cb3e-5ee2-a9b9-c64150bb14e0'::pg_catalog.uuid));
