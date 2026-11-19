SELECT 'WA_SRC_BEFORE_AUDITEVENT_CROSS_MODEL_COMPLETE_CAPS';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.audit_events WHERE id='4565b966-ae72-5f33-80ec-74ff455cf216'),'foreign',(SELECT count(*) FROM app.audit_events WHERE id='fc91a837-2dda-5752-b729-66773c65b9dc'),'User_root',(SELECT count(*) FROM app.users WHERE id='8a9a4b27-ce71-52f9-aa47-c45f09f71952'),'User_foreign',(SELECT count(*) FROM app.users WHERE id='3950fc46-5cfd-5911-a245-ff5e90e915d3'),'UserSecurityProfile_root',(SELECT count(*) FROM app.user_security_profiles WHERE id='24bb1d93-a33d-5de1-aee2-0a6844186ce0'),'UserSecurityProfile_foreign',(SELECT count(*) FROM app.user_security_profiles WHERE id='dbebcfec-f4e8-576a-82f8-122e5bcf3ded'));
SELECT 'WA_SRC_AFTER_AUDITEVENT_CROSS_MODEL_COMPLETE_CAPS';
COMMIT;
