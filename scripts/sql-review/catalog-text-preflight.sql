-- Fixed read-only control of the ACL UNION's identifier-preservation contract.
-- Only Boolean outcomes leave this query; no application data is selected.
BEGIN READ ONLY;
SET LOCAL search_path = pg_catalog;
WITH signature(value) AS (
 SELECT 'platform_private.track_atomic_valid(pg_catalog.text,pg_catalog.jsonb,pg_catalog.jsonb)'::text
), old_projection(object) AS (
 SELECT 'schema'::name UNION ALL SELECT value FROM signature
), corrected_projection(object) AS (
 SELECT 'schema'::text UNION ALL SELECT value FROM signature
)
SELECT jsonb_build_object(
 'format','workinants.catalog-text-preflight.v1',
 'server_version_num',current_setting('server_version_num')::integer,
 'read_only',current_setting('transaction_read_only')='on',
 'collected_as',current_user,
 'collector_is_superuser',(SELECT rolsuper FROM pg_roles WHERE rolname=current_user),
 'identifier_limit_is_63',current_setting('max_identifier_length')::integer=63,
 'old_projection_type_is_name',pg_typeof((SELECT object FROM old_projection LIMIT 1))='pg_catalog.name'::regtype,
 'old_projection_truncates_long_value',(SELECT length(object::text)=63 AND object::text=left((SELECT value FROM signature),63) FROM old_projection WHERE object::text<>'schema'),
 'corrected_projection_type_is_text',pg_typeof((SELECT object FROM corrected_projection LIMIT 1))='pg_catalog.text'::regtype,
 'corrected_projection_preserves_long_value',(SELECT length(object)>63 AND object=(SELECT value FROM signature) FROM corrected_projection WHERE object<>'schema'));
ROLLBACK;
