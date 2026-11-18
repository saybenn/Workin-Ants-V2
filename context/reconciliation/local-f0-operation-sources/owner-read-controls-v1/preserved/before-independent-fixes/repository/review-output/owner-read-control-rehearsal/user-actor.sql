SELECT 'WA_OR_BEFORE_USER_ACTOR';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.users WHERE id='078052af-7e37-53e9-a1ae-462cceb06d30'),'foreign',(SELECT count(*) FROM app.users WHERE id='f4f00e95-1f1c-5920-955c-2b8d37ea3187'));
SELECT 'WA_OR_AFTER_USER_ACTOR';
COMMIT;
