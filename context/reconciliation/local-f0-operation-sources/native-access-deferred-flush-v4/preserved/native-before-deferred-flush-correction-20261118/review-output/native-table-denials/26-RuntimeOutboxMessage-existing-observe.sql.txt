SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_outbox_message" WHERE "id"='3811671b-7554-55ae-8c0a-777a297cbae0'::pg_catalog.uuid));
