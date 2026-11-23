SELECT 'WA_CSP1_BEFORE';
WITH changed AS (UPDATE app.customer_profiles SET display_name='csp1-synthetic-prefix',revision=revision+1 WHERE id='bf01dab5-2588-5135-846f-b546bb6d98a3'::uuid AND revision=1 RETURNING id,revision) SELECT jsonb_build_object('rows',count(*)) FROM changed;
SELECT 'WA_CSP1_AFTER';
ROLLBACK;
SELECT 'WA_CSP1_ROLLBACK';
