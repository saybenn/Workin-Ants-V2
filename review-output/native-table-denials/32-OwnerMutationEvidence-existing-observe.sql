SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "platform"."owner_mutation_evidence" WHERE "id"='0e404704-d801-5dc8-a881-e57d8e273270'::pg_catalog.uuid));
