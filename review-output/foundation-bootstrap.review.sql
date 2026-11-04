-- P0-C-03 REVIEW DRAFT ONLY. NOT EXECUTION-APPROVED. PostgreSQL 17.
-- Separate environment authority must run any future bootstrap; no credentials here.
-- Deliberately not idempotent: existing roles/namespaces require inspection, not takeover.
BEGIN;
CREATE ROLE wa_schema_owner NOLOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_migrator LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_context_issuer LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_app_runtime LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_worker LOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
CREATE ROLE wa_private_helper_owner NOLOGIN NOINHERIT NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
-- Privacy executor remains unprovisioned; support_operation is an action, not a role.
GRANT wa_schema_owner TO wa_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;
-- Ownership transfers require temporary membership; app/worker receive none.
GRANT wa_private_helper_owner TO wa_schema_owner WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;
CREATE SCHEMA app AUTHORIZATION wa_schema_owner;
CREATE SCHEMA platform AUTHORIZATION wa_schema_owner;
CREATE SCHEMA platform_private AUTHORIZATION wa_schema_owner;
REVOKE ALL ON SCHEMA app,platform,platform_private FROM PUBLIC;
GRANT USAGE ON SCHEMA app,platform,platform_private TO wa_app_runtime,wa_worker;
GRANT USAGE ON SCHEMA app,platform,platform_private TO wa_context_issuer,wa_private_helper_owner;
-- Prisma ledger exception: only migrator may create its private metadata in public.
-- No ledger is created and no migrate execution configuration is activated here.
GRANT USAGE,CREATE ON SCHEMA public TO wa_migrator;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_migrator REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_private_helper_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE USAGE ON TYPES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner IN SCHEMA app,platform,platform_private REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner IN SCHEMA app,platform,platform_private REVOKE ALL ON SEQUENCES FROM PUBLIC;
COMMIT;
