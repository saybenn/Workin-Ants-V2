SELECT jsonb_build_object('read13_marker','TrackSubscriptionEvent/root'::text,'position','BEFORE'::text);
SELECT jsonb_build_object('model','TrackSubscriptionEvent','ids',coalesce(jsonb_agg(observed.id::text ORDER BY observed.id::text COLLATE "C"),'[]'::jsonb)) FROM (SELECT id,subscription_id,plan_id,user_id,name,from_status,to_status,provider,provider_event_id,metadata,created_at,mutation_transaction_id FROM app.track_subscription_events WHERE id IN ('d5648b8c-5fc0-5c20-bf7c-1c1ae7750da7'::uuid,'a9860247-3cd0-5ab7-89e8-7b37d048b1d7'::uuid)) observed;
SET CONSTRAINTS ALL IMMEDIATE;
SELECT jsonb_build_object('read13_marker','TrackSubscriptionEvent/root'::text,'position','AFTER'::text);
