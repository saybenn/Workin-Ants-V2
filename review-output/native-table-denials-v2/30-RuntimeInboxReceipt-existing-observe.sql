SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_inbox_receipt" WHERE "id"='3428d74a-c353-5308-8ce7-361e3b00f853'::pg_catalog.uuid));
