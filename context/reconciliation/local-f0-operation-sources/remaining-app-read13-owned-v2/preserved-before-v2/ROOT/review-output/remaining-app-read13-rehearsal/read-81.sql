SELECT jsonb_build_object('read13_marker','shared/revoked_before_action'::text,'position','BEFORE'::text);

SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','shared/revoked_before_action'::text,'position','AFTER'::text);
