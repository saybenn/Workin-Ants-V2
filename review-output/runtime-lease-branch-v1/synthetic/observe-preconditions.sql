BEGIN READ ONLY;
SELECT jsonb_build_object(
'guard_source', (SELECT jsonb_build_object('body_sha256',encode(sha256(convert_to(p.prosrc,'UTF8')),'hex'),'original_grantor_owner',p.proowner='postgres'::regrole,'invoker',NOT p.prosecdef,'volatile',p.provolatile='v','unsafe',p.proparallel='u','not_strict',NOT p.proisstrict,'cost100',p.procost=100,'search_path_exact',p.proconfig=ARRAY['search_path=pg_catalog']::text[]) FROM pg_proc p WHERE p.oid='wa_lease_branch_v1_repro.guard()'::regprocedure),
'lease_fixture', (SELECT jsonb_agg(jsonb_build_object('id',id,'lease_hash_matches_public_dummy',CASE WHEN lease_token_hash IS NULL THEN NULL ELSE lease_token_hash=encode(sha256(decode(repeat('a',64),'hex')),'hex') END,'expired',CASE WHEN lease_expires_at IS NULL THEN NULL ELSE lease_expires_at<=clock_timestamp() END) ORDER BY id) FROM wa_lease_branch_v1_repro.work));
ROLLBACK;
