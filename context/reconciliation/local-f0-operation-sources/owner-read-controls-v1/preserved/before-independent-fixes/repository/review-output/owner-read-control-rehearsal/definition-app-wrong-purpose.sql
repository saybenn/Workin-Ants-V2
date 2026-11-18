SELECT 'WA_OR_BEFORE_DEFINITION_APP_WRONG_PURPOSE';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.track_entitlement_definitions WHERE id='12d534f1-8435-5284-9878-f07a42cd6545'),'foreign',(SELECT count(*) FROM app.track_entitlement_definitions WHERE id='d5be2afb-f16f-594b-adac-587323801677'));
SELECT 'WA_OR_AFTER_DEFINITION_APP_WRONG_PURPOSE';
COMMIT;
