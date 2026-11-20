SELECT jsonb_build_object('read13_marker','shared/identity_generation_mismatch'::text,'position','BEFORE'::text);

SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','shared/identity_generation_mismatch'::text,'position','AFTER'::text);
