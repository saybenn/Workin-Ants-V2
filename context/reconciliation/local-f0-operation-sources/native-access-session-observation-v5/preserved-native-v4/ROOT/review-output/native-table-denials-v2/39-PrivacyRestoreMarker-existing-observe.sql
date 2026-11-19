SELECT jsonb_build_object('row_count',(SELECT count(*) FROM "app"."privacy_restore_marker" WHERE "id"='4d182d2b-dbeb-502e-be43-c764ff78293d'::pg_catalog.uuid));
