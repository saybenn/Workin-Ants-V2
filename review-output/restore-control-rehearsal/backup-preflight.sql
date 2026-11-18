BEGIN READ ONLY;
SET LOCAL search_path=pg_catalog;
SELECT jsonb_build_object('version_170011',current_setting('server_version_num')='170011','direct_postgres',session_user='postgres' AND current_user='postgres',
'primary',NOT pg_is_in_recovery(),'wal_level_replica',current_setting('wal_level')='replica','two_wal_senders',current_setting('max_wal_senders')::int>=2,
'temporary_slot_available',current_setting('max_replication_slots')::int>=1 AND NOT EXISTS(SELECT 1 FROM pg_replication_slots),'full_page_writes',current_setting('full_page_writes')='on',
'no_senders',NOT EXISTS(SELECT 1 FROM pg_stat_replication),'no_other_clients',NOT EXISTS(SELECT 1 FROM pg_stat_activity WHERE backend_type='client backend' AND pid<>pg_backend_pid()),
'no_external_tablespaces',NOT EXISTS(SELECT 1 FROM pg_tablespace WHERE spcname NOT IN ('pg_default','pg_global')),'only_expected_databases',NOT EXISTS(SELECT 1 FROM pg_database WHERE datname NOT IN ('template0','template1','postgres','wa_p0c_rehearsal')),
'no_recovery_or_archive_transport',current_setting('primary_conninfo')='' AND current_setting('primary_slot_name')='' AND current_setting('restore_command')='' AND current_setting('archive_mode')='off' AND current_setting('archive_command')='' AND current_setting('archive_library')='' AND current_setting('synchronous_standby_names')='',
'no_preload',current_setting('shared_preload_libraries')='' AND current_setting('session_preload_libraries')='' AND current_setting('local_preload_libraries')='','no_subscriptions',NOT EXISTS(SELECT 1 FROM pg_subscription),'no_foreign_servers',NOT EXISTS(SELECT 1 FROM pg_foreign_server),
'safe_logging',current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic' AND current_setting('log_error_verbosity')='terse' AND current_setting('lc_messages')='C',
'system_identifier_sha256',(SELECT encode(sha256(convert_to(system_identifier::text,'UTF8')),'hex') FROM pg_control_system()));
COMMIT;
