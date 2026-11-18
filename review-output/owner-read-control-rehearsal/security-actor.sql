SELECT 'WA_OR_BEFORE_SECURITY_ACTOR';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.user_security_profiles WHERE id='0ad89161-cd46-5bc5-b5d8-769ddb12c8a6'),'foreign',(SELECT count(*) FROM app.user_security_profiles WHERE id='25bd7411-37d4-5dee-9f67-b961aeffbd48'));
SELECT 'WA_OR_AFTER_SECURITY_ACTOR';
COMMIT;
