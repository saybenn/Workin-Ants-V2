SELECT 'WA_CSP1_BEFORE';
\set ON_ERROR_STOP off
UPDATE app.customer_profiles SET display_name='csp1-synthetic-prefix',revision=revision+2 WHERE id='bf01dab5-2588-5135-846f-b546bb6d98a3'::uuid AND revision=0 RETURNING id,revision;
\if :ERROR
\echo WA_CSP1_FAILED_STATEMENT
\echo WA_CSP1_SQLSTATE :SQLSTATE
\else
\echo WA_CSP1_UNEXPECTED_SUCCESS
\endif
\set ON_ERROR_STOP on
ROLLBACK;
SELECT 'WA_CSP1_ROLLBACK';
