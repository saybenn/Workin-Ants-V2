SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."privacy_target_instruction" WHERE "id"='dc0750b3-468b-558f-85b4-721cf93fce09'::pg_catalog.uuid));
