SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_enrollment_receipt" WHERE "id"='733d03b3-0279-520f-8fb7-48c77debee7d'::pg_catalog.uuid));
