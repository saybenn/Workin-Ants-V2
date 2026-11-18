SELECT 'WA_OR_BEFORE_CANDIDATE_QUERY_WRONG_ROOT';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.candidate_profiles WHERE id='133d9666-d512-523d-ad6b-8603bff24b44'),'foreign',(SELECT count(*) FROM app.candidate_profiles WHERE id='f27df64a-0a9a-5849-bf9d-39c330f74715'));
SELECT 'WA_OR_AFTER_CANDIDATE_QUERY_WRONG_ROOT';
COMMIT;
