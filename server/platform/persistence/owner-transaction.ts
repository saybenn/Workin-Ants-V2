import { createHash, randomBytes, randomUUID } from "node:crypto";
import type { Sql, TransactionSql } from "postgres";

const isolationLevel = "isolation level read committed";

type RuntimeLogin = "wa_app_runtime" | "wa_worker";
type Login = RuntimeLogin | "wa_context_issuer";
type Pool = Pick<Sql, "begin" | "end">;
type Scalar = string | number | boolean | null;
type Rows = readonly Record<string, unknown>[];

const activePools = new WeakSet<Pool>();
const closedPools = new WeakSet<Pool>();

export type OwnerQuery = (
  statement: TemplateStringsArray,
  ...parameters: Scalar[]
) => Promise<Rows>;

/** Supplied by the trusted server caller after resolving current action authority. */
export type DatabaseActionContext = Readonly<{
  principal: { userId: string } | { servicePrincipal: string };
  owner: string;
  action: string;
  purpose: string;
  targetKind: string;
  targetId: string;
  allowedFields: readonly string[];
  policyVersion: string;
  securityGeneration: bigint;
  sourceGeneration: bigint;
  expiresAt: Date;
}>;

/** A pair of exclusively owned pools. Use a separate pair for overlapping owner transactions. */
export type OwnerDatabase = Readonly<{
  runtime: Pool;
  issuer: Pool;
  runtimeLogin: RuntimeLogin;
  expectedDatabase: string;
}>;

type FailureCode =
  | "target_mismatch"
  | "context_denied"
  | "transaction_closed"
  | "rolled_back"
  | "database_unavailable"
  | "commit_unconfirmed";

/** Safe for the internal caller. The driver error can contain protected query parameters. */
export class OwnerTransactionFailure extends Error {
  readonly code: FailureCode;

  constructor(code: FailureCode) {
    super(code);
    this.name = "OwnerTransactionFailure";
    this.code = code;
  }
}

type Backend = {
  login: string;
  role: string;
  database: string;
  isolation: string;
  pid: number;
  xid: string;
  backendStart: string;
  serverStart: string;
  serverAddress: string | null;
  serverPort: number | null;
};

async function readBackend(tx: TransactionSql, login: Login, database: string): Promise<Backend> {
  const rows = await tx<Backend[]>`
    SELECT session_user::text AS login, current_user::text AS role,
           pg_catalog.current_database()::text AS database,
           pg_catalog.current_setting('transaction_isolation') AS isolation,
           pg_catalog.pg_backend_pid() AS pid, pg_catalog.pg_current_xact_id()::text AS xid,
           extract(epoch FROM activity.backend_start)::text AS "backendStart",
           extract(epoch FROM pg_catalog.pg_postmaster_start_time())::text AS "serverStart",
           pg_catalog.inet_server_addr()::text AS "serverAddress",
           pg_catalog.inet_server_port() AS "serverPort"
    FROM pg_catalog.pg_stat_activity AS activity
    WHERE activity.pid = pg_catalog.pg_backend_pid()
  `;
  const row = rows[0];
  if (rows.length !== 1 || row === undefined || row.login !== login || row.role !== login
      || row.database !== database || row.isolation !== "read committed"
      || !Number.isInteger(row.pid) || row.pid <= 0 || !/^[1-9]\d*$/.test(row.xid)
      || !row.backendStart || !row.serverStart) {
    throw new OwnerTransactionFailure("target_mismatch");
  }
  return row;
}

function sameServer(left: Backend, right: Backend): boolean {
  return left.database === right.database && left.serverStart === right.serverStart
    && left.serverAddress === right.serverAddress && left.serverPort === right.serverPort;
}

function requireSameTransaction(before: Backend, after: Backend) {
  if (!sameServer(before, after) || before.pid !== after.pid || before.xid !== after.xid
      || before.backendStart !== after.backendStart) {
    throw new OwnerTransactionFailure("target_mismatch");
  }
}

async function localTransaction<Result>(
  pool: Pool,
  login: Login,
  database: string,
  work: (tx: TransactionSql, backend: Backend) => Promise<Result>,
): Promise<Result> {
  let committing = false;
  let confirmedRollback: OwnerTransactionFailure | undefined;
  let callback: Promise<{ value: Result }> | undefined;

  async function run(tx: TransactionSql) {
    try {
      const before = await readBackend(tx, login, database);
      const value = await work(tx, before);
      // An aborted transaction cannot return this current tuple. Owner queries have all settled.
      requireSameTransaction(before, await readBackend(tx, login, database));
      committing = true;
      return { value };
    } catch (error: unknown) {
      confirmedRollback = error instanceof OwnerTransactionFailure ? error : new OwnerTransactionFailure("rolled_back");
      throw confirmedRollback;
    }
  }

  try {
    const result = await pool.begin(isolationLevel, (tx) => {
      callback = run(tx);
      return callback;
    });
    return result.value;
  } catch (error: unknown) {
    const code = committing ? "commit_unconfirmed" : "database_unavailable";
    const cleanRollback = confirmedRollback !== undefined && error === confirmedRollback;
    if (!cleanRollback) {
      // Postgres.js can continue a late transaction callback after reporting connection loss.
      // Quarantine the owned pool before any new operation could borrow its connection.
      closedPools.add(pool);
      await pool.end({ timeout: 0 }).catch(() => undefined);
    }
    await callback?.catch(() => undefined);
    if (cleanRollback) throw confirmedRollback;
    throw new OwnerTransactionFailure(code);
  }
}

async function issueContext(database: OwnerDatabase, runtime: Backend, context: DatabaseActionContext) {
  const secret = randomBytes(32);
  const token = secret.toString("hex");
  const tokenHash = createHash("sha256").update(secret).digest("hex");
  secret.fill(0);
  const id = randomUUID();
  const principalUserId = "userId" in context.principal ? context.principal.userId : null;
  const servicePrincipal = "servicePrincipal" in context.principal ? context.principal.servicePrincipal : null;

  await localTransaction(database.issuer, "wa_context_issuer", database.expectedDatabase, async (issuer, backend) => {
    if (!sameServer(runtime, backend) || runtime.pid === backend.pid || runtime.xid === backend.xid) {
      throw new OwnerTransactionFailure("target_mismatch");
    }
    const rows = await issuer<{ id: string }[]>`
      INSERT INTO platform.database_action_grant (
        id, token_hash, issuer_service, principal_user_id, service_principal,
        database_login_role, owner_module_id, action, purpose, target_kind, target_id,
        allowed_fields, policy_version, security_generation, source_generation,
        backend_pid, transaction_id, expires_at
      ) VALUES (
        ${id}::uuid, ${tokenHash}, session_user::text, ${principalUserId}::uuid, ${servicePrincipal},
        ${runtime.login}, ${context.owner}, ${context.action}, ${context.purpose}, ${context.targetKind},
        ${context.targetId}, ${issuer.array([...context.allowedFields], 25)}::text[], ${context.policyVersion},
        ${context.securityGeneration.toString()}::bigint, ${context.sourceGeneration.toString()}::bigint,
        ${runtime.pid}::integer, ${runtime.xid}, ${context.expiresAt.toISOString()}::timestamptz
      ) RETURNING id::text
    `;
    if (rows.length !== 1 || rows[0]?.id !== id) {
      throw new OwnerTransactionFailure("rolled_back");
    }
  });
  return token;
}

function isContextDenial(error: unknown): boolean {
  return typeof error === "object" && error !== null && "code" in error && error.code === "42501";
}

async function executeOwnerQueries<Result>(runtime: TransactionSql, execute: (query: OwnerQuery) => Promise<Result>) {
  let active = true;
  let failed = false;
  let pending: Promise<Rows> | undefined;
  const query: OwnerQuery = (statement, ...parameters) => {
    if (!active) throw new OwnerTransactionFailure("transaction_closed");
    if (pending || !/^\s*(SELECT|WITH|INSERT|UPDATE|DELETE)\b/i.test(statement[0] ?? "")) {
      failed = true;
      throw new OwnerTransactionFailure("rolled_back");
    }
    const current = (async () => {
      try {
        const rows = await runtime<Record<string, unknown>[]>(statement, ...parameters);
        return [...rows];
      } catch {
        failed = true;
        throw new OwnerTransactionFailure("rolled_back");
      } finally {
        pending = undefined;
      }
    })();
    pending = current;
    // The callback might drop the promise. Keep the failure latched and drain it before rollback.
    void current.catch(() => undefined);
    return current;
  };

  try {
    const value = await execute(query);
    if (pending || failed) throw new OwnerTransactionFailure("rolled_back");
    return value;
  } catch {
    throw new OwnerTransactionFailure("rolled_back");
  } finally {
    active = false;
    await pending?.catch(() => undefined);
  }
}

/** Execute fixed repository statements. Resolve all external authority before calling. */
export async function runOwnerTransaction<Result>(
  database: OwnerDatabase,
  context: DatabaseActionContext,
  execute: (query: OwnerQuery) => Promise<Result>,
): Promise<Result> {
  const owned = { ...database };
  const { runtime, issuer } = owned;
  if (runtime === issuer || activePools.has(runtime) || activePools.has(issuer)
      || closedPools.has(runtime) || closedPools.has(issuer)) {
    throw new OwnerTransactionFailure("database_unavailable");
  }

  // Snapshot mutable inputs before the first await. Authority supplies every grant field.
  const grant = {
    ...context,
    principal: { ...context.principal },
    allowedFields: [...context.allowedFields],
    expiresAt: new Date(context.expiresAt),
  };
  if (grant.allowedFields.length === 0 || grant.allowedFields.length > 1024
      || grant.allowedFields.some((field, index, fields) => !field || field.includes("*")
        || (index > 0 && field <= (fields[index - 1] ?? "")))
      || !Number.isFinite(grant.expiresAt.getTime())) {
    throw new OwnerTransactionFailure("context_denied");
  }

  activePools.add(runtime).add(issuer);
  try {
    return await localTransaction(runtime, owned.runtimeLogin, owned.expectedDatabase, async (tx, before) => {
      let token: string;
      try {
        token = await issueContext(owned, before, grant);
      } catch (error: unknown) {
        if (error instanceof OwnerTransactionFailure && error.code === "commit_unconfirmed") {
          throw new OwnerTransactionFailure("database_unavailable");
        }
        throw error;
      }
      if (closedPools.has(runtime)) throw new OwnerTransactionFailure("database_unavailable");
      requireSameTransaction(before, await readBackend(tx, owned.runtimeLogin, owned.expectedDatabase));
      try {
        await tx`SELECT platform_private.bind_request_context(${token}::text)`;
      } catch (error: unknown) {
        if (isContextDenial(error)) throw new OwnerTransactionFailure("context_denied");
        throw error;
      }
      if (closedPools.has(runtime)) throw new OwnerTransactionFailure("database_unavailable");
      return executeOwnerQueries(tx, execute);
    });
  } finally {
    activePools.delete(runtime);
    activePools.delete(issuer);
  }
}
