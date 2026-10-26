BEGIN TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '15s';
SELECT migration_name, checksum, started_at, finished_at, rolled_back_at, applied_steps_count
FROM public._prisma_migrations
ORDER BY started_at, migration_name;
ROLLBACK;
