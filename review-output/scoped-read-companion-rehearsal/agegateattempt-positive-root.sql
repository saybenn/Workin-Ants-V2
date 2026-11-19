SELECT 'WA_SRC_BEFORE_AGEGATEATTEMPT_POSITIVE_ROOT';
SELECT jsonb_build_object('root',(SELECT count(*) FROM app.age_gate_attempts WHERE id='cf53d0d3-9da1-5c9c-bc37-3ce396ee72ba'),'foreign',(SELECT count(*) FROM app.age_gate_attempts WHERE id='84967295-3b84-5266-877c-1fa229c14a53'));
SELECT 'WA_SRC_AFTER_AGEGATEATTEMPT_POSITIVE_ROOT';
COMMIT;
