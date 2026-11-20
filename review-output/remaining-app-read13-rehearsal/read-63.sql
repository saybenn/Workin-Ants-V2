SELECT jsonb_build_object('read13_marker','TrackSubscriptionEvent/unbound'::text,'position','BEFORE'::text);
SELECT jsonb_build_object('model','TrackSubscriptionEvent','ids',coalesce(jsonb_agg(observed.id::text ORDER BY observed.id::text COLLATE "C"),'[]'::jsonb)) FROM (SELECT id,subscription_id,plan_id,user_id,name,from_status,to_status,provider,provider_event_id,metadata,created_at,mutation_transaction_id FROM app.track_subscription_events WHERE id IN ('32edc11f-43d3-552f-a354-5aa0ef5564e0'::uuid,'030e1d8c-c8fa-59b4-959e-7a05dd3c22f9'::uuid)) observed;
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','TrackSubscriptionEvent/unbound'::text,'position','AFTER'::text);
