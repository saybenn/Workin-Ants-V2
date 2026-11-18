SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_command_receipt" WHERE "id"='f8745e8a-71cc-5b07-88ce-23e188f55dba'::pg_catalog.uuid));
