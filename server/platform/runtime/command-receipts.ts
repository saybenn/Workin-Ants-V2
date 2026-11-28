import type { OwnerQuery } from "../persistence/owner-transaction";

export type CommandIdentity = Readonly<{
  receiptId: string;
  owner: string;
  operation: string;
  subjectScope: string;
  semanticKey: string;
  fingerprint: string;
}>;

export type CommandResultSchema = Readonly<{ id: string; version: string }>;

export type CommandReceiptRead =
  | { status: "unobserved" | "conflict" | "unavailable" }
  | { status: "committed"; body: unknown };

/** The caller supplies an already authorized, stable receipt ID inside its owner transaction. */
export async function readCommandReceipt(
  query: OwnerQuery,
  command: CommandIdentity,
  schema: CommandResultSchema,
  revision: string,
): Promise<CommandReceiptRead> {
  const rows = await query`
    SELECT owner_module_id, operation, subject_scope, semantic_key, fingerprint,
           state, source_revision::text, result_schema_id, result_schema_version, result_body,
           pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(result_body::text, 'UTF8')), 'hex')
             = result_digest AS digest_matches
    FROM platform.runtime_command_receipt
    WHERE id = ${command.receiptId}::uuid
  `;
  const row = rows[0];
  if (!row) return { status: "unobserved" };
  if (rows.length !== 1 || row.owner_module_id !== command.owner || row.operation !== command.operation
      || row.subject_scope !== command.subjectScope || row.semantic_key !== command.semanticKey) {
    return { status: "unavailable" };
  }
  if (row.state !== "committed" || row.source_revision !== revision || row.digest_matches !== true || row.result_schema_id !== schema.id
      || row.result_schema_version !== schema.version) {
    return { status: "unavailable" };
  }
  if (row.fingerprint !== command.fingerprint) return { status: "conflict" };
  return { status: "committed", body: row.result_body };
}

/** Call before owner writes. Commit the result and the corresponding owner effect together. */
export async function insertCommandResult(
  query: OwnerQuery,
  command: CommandIdentity,
  schema: CommandResultSchema,
  revision: string,
  body: object,
): Promise<boolean> {
  const rows = await query`
    WITH result AS (SELECT ${JSON.stringify(body)}::jsonb AS body)
    INSERT INTO platform.runtime_command_receipt (
      id, owner_module_id, operation, subject_scope, semantic_key, fingerprint, state,
      source_revision, result_schema_id, result_schema_version, result_digest, result_body
    ) SELECT ${command.receiptId}::uuid, ${command.owner}, ${command.operation}, ${command.subjectScope},
             ${command.semanticKey}, ${command.fingerprint}, 'committed', ${revision}::bigint,
             ${schema.id}, ${schema.version},
             pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(result.body::text, 'UTF8')), 'hex'), result.body
      FROM result
    ON CONFLICT DO NOTHING
    RETURNING id::text
  `;
  if (rows.length === 0) return false;
  if (rows.length !== 1 || rows[0]?.id !== command.receiptId) throw new Error("command_receipt_write_unconfirmed");
  return true;
}
