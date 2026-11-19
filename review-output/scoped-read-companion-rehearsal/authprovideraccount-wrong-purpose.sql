SELECT 'WA_SRC_BEFORE_AUTHPROVIDERACCOUNT_WRONG_PURPOSE';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.auth_provider_accounts WHERE id='e8181c41-caad-5c3d-bacc-4b07ec218909'),'foreign',(SELECT count(*) FROM app.auth_provider_accounts WHERE id='ccb2ee49-e7e9-51bb-b6da-3499e4b361f6'));
SELECT 'WA_SRC_AFTER_AUTHPROVIDERACCOUNT_WRONG_PURPOSE';
COMMIT;
