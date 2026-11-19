SELECT 'WA_SRC_BEFORE_USERROLE_POSITIVE_ROOT';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.user_roles WHERE user_id::text||':'||role::text='8a9a4b27-ce71-52f9-aa47-c45f09f71952:user'),'foreign',(SELECT count(*) FROM app.user_roles WHERE user_id::text||':'||role::text='3950fc46-5cfd-5911-a245-ff5e90e915d3:user'));
SELECT 'WA_SRC_AFTER_USERROLE_POSITIVE_ROOT';
COMMIT;
