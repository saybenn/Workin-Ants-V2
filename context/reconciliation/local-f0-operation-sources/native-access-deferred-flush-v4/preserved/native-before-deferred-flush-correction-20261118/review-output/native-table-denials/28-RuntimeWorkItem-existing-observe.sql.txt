SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."runtime_work_item" WHERE "id"='cf2cca20-b1c4-524e-bb9e-38fbd9dba7a2'::pg_catalog.uuid));
