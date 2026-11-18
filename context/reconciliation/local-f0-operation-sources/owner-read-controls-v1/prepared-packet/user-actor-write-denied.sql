SELECT 'WA_OR_BEFORE_USER_ACTOR_WRITE_DENIED';
WITH changed AS (UPDATE app.users SET display_name='forbidden read-purpose update',revision=revision+1 WHERE id='078052af-7e37-53e9-a1ae-462cceb06d30' RETURNING id) SELECT jsonb_build_object('modified',count(*)) FROM changed;
SELECT 'WA_OR_AFTER_USER_ACTOR_WRITE_DENIED';
COMMIT;
