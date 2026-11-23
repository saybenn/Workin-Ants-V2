BEGIN;
SELECT set_config('wa.lease_secret',repeat('a',64),true) IS NOT NULL;
SELECT wa_lease_branch_v1_repro.lease_secret_matches(encode(sha256(decode(repeat('a',64),'hex')),'hex'));
ROLLBACK;
