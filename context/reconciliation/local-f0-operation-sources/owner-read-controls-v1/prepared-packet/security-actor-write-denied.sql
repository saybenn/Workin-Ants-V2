SELECT 'WA_OR_BEFORE_SECURITY_ACTOR_WRITE_DENIED';
WITH changed AS (UPDATE app.user_security_profiles SET lock_reason='forbidden read-purpose update',revision=revision+1 WHERE id='0ad89161-cd46-5bc5-b5d8-769ddb12c8a6' RETURNING id) SELECT jsonb_build_object('modified',count(*)) FROM changed;
SELECT 'WA_OR_AFTER_SECURITY_ACTOR_WRITE_DENIED';
COMMIT;
