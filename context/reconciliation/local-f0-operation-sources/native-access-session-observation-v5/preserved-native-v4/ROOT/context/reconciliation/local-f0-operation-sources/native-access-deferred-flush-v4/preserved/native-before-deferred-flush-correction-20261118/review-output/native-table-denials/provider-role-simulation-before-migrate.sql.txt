-- LOCAL DISPOSABLE PROVIDER-ROLE SIMULATION ONLY. Not hosted Supabase parity.
-- Run AFTER fresh approved bootstrap creates schemas, BEFORE genuine Prisma application install.
-- No passwords/URLs here. Separate reviewed private-tmpfs SCRAM provisioning is required.
BEGIN;
DO $local_provider_presence$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role')) THEN RAISE EXCEPTION 'local provider simulation requires absent role names'; END IF; END $local_provider_presence$;
CREATE ROLE anon LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE authenticated LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE service_role LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION BYPASSRLS;
-- Narrow local schema-USAGE sentinel only: source install's managed-role REVOKE must actually remove it.
GRANT USAGE ON SCHEMA app,platform,platform_private TO anon,authenticated,service_role;
COMMIT;
