SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."consent_presentation" WHERE "id"='b907e3d7-3dda-5bb0-a9c9-27fcffad4ad7'::pg_catalog.uuid));
