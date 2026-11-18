SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."privacy_owner_receipt" WHERE "id"='4942f3e7-182b-5838-ac1e-8c481a204f6c'::pg_catalog.uuid));
