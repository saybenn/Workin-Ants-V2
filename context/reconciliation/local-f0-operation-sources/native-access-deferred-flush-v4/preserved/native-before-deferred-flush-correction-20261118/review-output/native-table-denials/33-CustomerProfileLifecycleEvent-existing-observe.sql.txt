SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."customer_profile_lifecycle_event" WHERE "id"='d72bb123-5c63-53cb-87f6-85e0a38b6620'::pg_catalog.uuid));
