SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."track_base_selection" WHERE "id"='512cddc0-8c3a-5924-9e8c-31ebeda15349'::pg_catalog.uuid));
