BEGIN;
ALTER TABLE app.track_base_selection ENABLE TRIGGER owner_commit;
ALTER TABLE app.track_subscriptions ENABLE TRIGGER owner_commit;
COMMIT;
