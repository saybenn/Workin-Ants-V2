BEGIN;
ALTER TABLE app.consent_presentation DISABLE TRIGGER owner_commit;
ALTER TABLE app.consent_logs DISABLE TRIGGER owner_commit;
COMMIT;
