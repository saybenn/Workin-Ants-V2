-- Run ONLY after guarded source collector confirms native ledger type/columns/ACL.
BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL search_path=pg_catalog;
SET LOCAL TimeZone='UTC';
SET LOCAL DateStyle='ISO, YMD';
SET LOCAL extra_float_digits=3;
SET LOCAL bytea_output='hex';
SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to(COALESCE(jsonb_agg(to_jsonb(x) ORDER BY to_jsonb(x)::text COLLATE "C"),'[]'::jsonb)::text,'UTF8')),'hex'),
'exact_applied',count(*)=1 AND COALESCE(bool_and(migration_name='20261117000100_f0_local_initial' AND checksum='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad' AND finished_at IS NOT NULL AND rolled_back_at IS NULL AND logs IS NULL AND applied_steps_count=1),false)) FROM public._prisma_migrations x;
COMMIT;
