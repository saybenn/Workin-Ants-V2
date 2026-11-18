SELECT 'WA_OR_BEFORE_PROFESSIONAL_QUERY_MISSING_FIELD';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.professional_profiles WHERE id='950775a7-51fb-5b92-bf05-293a3cd573f7'),'foreign',(SELECT count(*) FROM app.professional_profiles WHERE id='4c9baa8e-38e2-5672-b96c-7a6ec7d1e471'));
SELECT 'WA_OR_AFTER_PROFESSIONAL_QUERY_MISSING_FIELD';
COMMIT;
