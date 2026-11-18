SELECT 'WA_OR_BEFORE_PRIVACY_QUERY_STALE_REVISION';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.privacy_requests WHERE id='2ca389cc-26a1-548a-b499-b7e0cb74d984'),'foreign',(SELECT count(*) FROM app.privacy_requests WHERE id='b446004e-ffed-542b-a8ec-a41ffaa29700'));
SELECT 'WA_OR_AFTER_PRIVACY_QUERY_STALE_REVISION';
COMMIT;
