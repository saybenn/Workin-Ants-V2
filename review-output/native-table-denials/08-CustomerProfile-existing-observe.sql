SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."customer_profiles" WHERE "id"='7885fb01-896e-529c-b0f4-ecaca7f48ea6'::pg_catalog.uuid));
