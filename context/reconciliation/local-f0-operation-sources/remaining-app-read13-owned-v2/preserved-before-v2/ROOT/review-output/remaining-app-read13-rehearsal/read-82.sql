SELECT jsonb_build_object('read13_marker','shared/server_expired'::text,'position','BEFORE'::text);

SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','shared/server_expired'::text,'position','AFTER'::text);
