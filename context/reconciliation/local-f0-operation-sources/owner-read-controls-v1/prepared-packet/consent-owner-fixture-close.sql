BEGIN;
ALTER TABLE app.consent_logs ENABLE TRIGGER owner_commit;
ALTER TABLE app.consent_presentation ENABLE TRIGGER owner_commit;
COMMIT;
