"""Native ACL fixture facts only; no business-owner or execution proof.

Source schema/enum/FK/CHECK/JSON projection. No DB/process/network imports.
Unsupported value/default/check shapes raise PreparationBlocked, never fake PASS.
Native controls must still prove actual PG type/CHECK/FK acceptance before probes.
"""
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

import catalog_manifest as source
import compare_native_catalog as compare
from pglast.stream import RawStream

sys.path.insert(0, str(source.ROOT / "scripts"))
from contract_schema import Registry

NAMESPACE = uuid.UUID("49b5ff64-4716-45ec-9d23-c8a5f5624b7d")
START = "2026-11-17T00:00:00Z"
END = "2026-11-18T00:00:00Z"
OWNER = "customer_buyer_profile"


class PreparationBlocked(ValueError): pass


@dataclass(frozen=True)
class StorageDigest:
    value: object
    codec: str = "jsonb"


@dataclass(frozen=True)
class JsonText:
    value: object


JSON_NULL = object()


class FixtureRegistry(Registry):
    def errors(self, value, schema, current=None, path="$"):
        if isinstance(schema.get("type"), list):
            return [] if any(not self.errors(value, {**schema, "type": kind}, current or schema, path) for kind in schema["type"]) else [path + ": union rejected"]
        return super().errors(value, schema, current, path)


def ident(value): return '"' + value.replace('"', '""') + '"'
def table_sql(value): return ".".join(ident(part) for part in value.split("."))
def quote(value): return "'" + str(value).replace("'", "''") + "'"
def uuid_value(variant, table): return str(uuid.uuid5(NAMESPACE, variant + "/" + table))
def fingerprint(value): return hashlib.sha256(value.encode("utf8")).hexdigest()


def sql_value(value, info):
    native = compare._typename(info)
    if value is None: return "NULL::" + native
    if isinstance(value, StorageDigest):
        if value.codec not in ("text", "jsonb"): raise PreparationBlocked("unknown storage digest codec")
        if value.codec == "text": return "encode(sha256(convert_to(" + quote(value.value) + ",'UTF8')),'hex')"
        return "encode(sha256(convert_to(" + quote(json.dumps(value.value, separators=(",", ":"))) + "::jsonb::text,'UTF8')),'hex')"
    if info["array_dimensions"]:
        return "ARRAY[" + ",".join(quote(v) for v in value) + "]::" + native
    if info["name"] in ("pg_catalog.json", "pg_catalog.jsonb"):
        return quote(json.dumps(value, separators=(",", ":"))) + "::" + native
    if type(value) is bool: return "true" if value else "false"
    return quote(value) + "::" + native


def default_literal(ast):
    if "A_Const" in ast:
        item = ast["A_Const"]
        if item.get("isnull"): return None
        for key, field, fallback in (("sval", "sval", ""), ("ival", "ival", 0), ("fval", "fval", "0"), ("boolval", "boolval", False)):
            if key in item: return item[key].get(field, fallback)
    if "TypeCast" in ast: return default_literal(ast["TypeCast"]["arg"])
    if "SQLValueFunction" in ast and ast["SQLValueFunction"]["op"] == "SVFOP_CURRENT_TIMESTAMP": return START
    if "A_ArrayExpr" in ast: return [default_literal(v) for v in ast["A_ArrayExpr"].get("elements", [])]
    if "FuncCall" in ast and source.names(ast["FuncCall"]["funcname"]) in (["pg_current_xact_id"], ["pg_catalog", "pg_current_xact_id"]): return "native-acl-setup-transaction"
    raise PreparationBlocked("unsupported native fixture default")


def registry(root):
    result = FixtureRegistry(root)
    for relative in ("contracts/database-review/owner-mutation-evidence.v1.schema.json", "contracts/database-review/foundation-payloads.v1.schema.json"):
        doc = json.loads((Path(root) / relative).read_text(encoding="utf8")); result.documents[doc["$id"]] = doc
    return result


def evaluate(ast, row, schemas):
    """Small source-CHECK interpreter, with SQL NULL and symbolic storage codec.

    This checks concrete fixture derivation only, not PostgreSQL execution or
    planner equivalence. Unsupported syntax/function names fail preparation.
    """
    if isinstance(ast, list): return [evaluate(value, row, schemas) for value in ast]
    if not isinstance(ast, dict) or len(ast) != 1: raise PreparationBlocked("unsupported CHECK node")
    tag, item = next(iter(ast.items()))
    if tag == "A_Const": return default_literal(ast)
    if tag == "ColumnRef":
        names = source.names(item["fields"])
        if len(names) != 1 or names[0] not in row: raise PreparationBlocked("foreign CHECK reference")
        return row[names[0]]
    if tag == "List": return [evaluate(value, row, schemas) for value in item.get("items", [])]
    if tag == "TypeCast":
        value = evaluate(item["arg"], row, schemas); typ = source.typename(item["typeName"])["name"]
        if value is None: return None
        if typ == "pg_catalog.jsonb":
            parsed = json.loads(value) if isinstance(value, str) else value
            return JSON_NULL if parsed is None else parsed
        if typ in ("pg_catalog.text", "pg_catalog.varchar"):
            return JsonText(value) if isinstance(value, (dict, list)) or value is JSON_NULL else str(value)
        if typ in ("pg_catalog.float4", "pg_catalog.float8", "pg_catalog.numeric"): return float(value)
        if typ in ("pg_catalog.int2", "pg_catalog.int4", "pg_catalog.int8"): return int(value)
        if typ == "pg_catalog.bool": return bool(value)
        raise PreparationBlocked("unsupported CHECK cast")
    if tag == "NullTest":
        value = evaluate(item["arg"], row, schemas)
        if item["nulltesttype"] not in ("IS_NULL", "IS_NOT_NULL"): raise PreparationBlocked("unsupported NULL test")
        return value is None if item["nulltesttype"] == "IS_NULL" else value is not None
    if tag == "BoolExpr":
        values = [evaluate(value, row, schemas) for value in item["args"]]
        if item["boolop"] == "AND_EXPR": return False if False in values else None if None in values else True
        if item["boolop"] == "OR_EXPR": return True if True in values else None if None in values else False
        if item["boolop"] == "NOT_EXPR": return None if values[0] is None else not values[0]
    if tag == "CoalesceExpr":
        for value in item["args"]:
            value = evaluate(value, row, schemas)
            if value is not None: return value
        return None
    if tag == "CaseExpr":
        subject = evaluate(item["arg"], row, schemas) if item.get("arg") else None
        for branch in item["args"]:
            branch = source.node(branch, "CaseWhen")
            condition = evaluate(branch["expr"], row, schemas)
            if (subject == condition if item.get("arg") else condition is True): return evaluate(branch["result"], row, schemas)
        return evaluate(item["defresult"], row, schemas) if item.get("defresult") else None
    if tag == "A_Expr":
        left = evaluate(item["lexpr"], row, schemas); right = evaluate(item["rexpr"], row, schemas)
        operator = source.names(item["name"])[-1]; kind = item["kind"]
        if kind == "AEXPR_NULLIF": return None if left == right else left
        if kind == "AEXPR_IN":
            if left is None: return None
            result = left in right
            if not result and None in right: return None
            return not result if operator == "<>" else result
        if kind == "AEXPR_BETWEEN": return None if left is None else right[0] <= left <= right[1]
        if operator in ("->", "->>"):
            if left is None or not isinstance(left, dict) or right not in left: return None
            value = left[right]
            if operator == "->": return JSON_NULL if value is None else value
            return None if value is None else str(value)
        if left is None or right is None: return None
        if operator == "=": return left == right
        if operator == "<>": return left != right
        if operator == ">": return left > right
        if operator == "<": return left < right
        if operator == ">=": return left >= right
        if operator == "<=": return left <= right
        if operator == "+": return left + right
        if operator == "||": return left + right
        if operator == "~":
            if isinstance(left, StorageDigest):
                if right != "^[0-9a-f]{64}$" or left.codec not in ("text", "jsonb"): raise PreparationBlocked("unproved symbolic digest format")
                return True
            return bool(re.search(right, left))
    if tag == "FuncCall":
        name = ".".join(source.names(item["funcname"])); short = name.removeprefix("pg_catalog.")
        args = [evaluate(value, row, schemas) for value in item.get("args", [])]
        if short == "length": return None if args[0] is None else len(args[0])
        if short == "convert_to" and args[1] == "UTF8": return ("UTF8", args[0])
        if short == "sha256": return ("SHA256", args[0])
        if short == "encode" and args[1] == "hex" and args[0][0] == "SHA256" and args[0][1][0] == "UTF8":
            value = args[0][1][1]
            return StorageDigest(value.value, "jsonb") if isinstance(value, JsonText) else StorageDigest(value, "text")
        if short == "jsonb_typeof":
            value = args[0]
            return None if value is None else "null" if value is JSON_NULL else "object" if isinstance(value, dict) else "array" if isinstance(value, list) else "boolean" if type(value) is bool else "number" if type(value) in (int, float) else "string"
        if name == "platform_private.json_evidence_customerprofile":
            doc = schemas.documents["urn:workinants:database-review:owner-evidence:v1"]
            return not schemas.errors(args[0], doc["$defs"]["CustomerProfile"], doc)
        if name == "platform_private.json_sh004_result": return not schemas.check("SH-004", "response", args[0])
        # CASE/OR branches for unselected registered results may be evaluated;
        # validate their actual schema rather than approximate JSON truthiness.
        if name == "platform_private.json_sh114_result": return not schemas.check("SH-114", "response", args[0])
        if name == "platform_private.json_track_result":
            doc = schemas.documents["urn:workinants:database-review:foundation-payloads:v1"]
            return not schemas.errors(args[0], doc["$defs"]["assignDefaultFreeTrackCustomerResult"], doc)
    raise PreparationBlocked("unsupported CHECK expression/function form")


def validate_checks(expected, rows, schemas):
    result = []
    for table, desc in expected["tables"].items():
        for ordinal, constraint in enumerate(desc["constraints"]):
            if constraint["kind"] != "CHECK": continue
            outcome = evaluate(constraint["expression"]["ast"], rows[table], schemas)
            if outcome is False: raise PreparationBlocked("source CHECK rejects derived native fact: " + table + "/" + str(constraint["name"]))
            if outcome is not True and outcome is not None: raise PreparationBlocked("CHECK did not produce SQL Boolean/NULL")
            result.append({"table": table, "constraint": constraint["name"] or "<source-ordinal-" + str(ordinal) + ">", "source_ast_sha256": constraint["expression"]["ast_sha256"], "derivation": "TRUE" if outcome is True else "SQL_NULL_ACCEPTED", "native_execution": "NOT_RUN"})
    return result


def primitive(table, column, info, expected, variant):
    if info["default"] is not None: return default_literal(info["default"]["ast"])
    if info["nullable"]: return None
    typ = info["type"]
    if typ["array_dimensions"]: return []
    name = typ["name"]
    if name in expected["enums"]: return expected["enums"][name]["labels"][0]
    if name == "pg_catalog.uuid": return uuid_value(variant, table + "/" + column)
    if name in ("pg_catalog.int2", "pg_catalog.int4", "pg_catalog.int8", "pg_catalog.numeric", "pg_catalog.float4", "pg_catalog.float8"): return 0
    if name == "pg_catalog.bool": return False
    if name in ("pg_catalog.timestamptz", "pg_catalog.timestamp", "pg_catalog.date"): return START
    if name in ("pg_catalog.text", "pg_catalog.varchar", "pg_catalog.name"):
        return "native-acl-" + fingerprint(variant + "/" + table + "/" + column)[:24]
    if name == "pg_catalog.bpchar": return fingerprint(variant + "/" + table + "/" + column)
    if name == "pg_catalog.jsonb" and (table, column) in (("platform.owner_mutation_evidence", "evidence_body"), ("platform.runtime_outbox_message", "payload")):
        return {}  # Filled only by the registered closed-shape constructors below.
    raise PreparationBlocked("required native type needs an explicit reviewed shape")


def make_rows(expected, variant, schemas):
    rows = {table: {column: primitive(table, column, info, expected, variant) for column, info in desc["columns"].items()}
            for table, desc in expected["tables"].items()}
    for table, row in rows.items():
        if "id" in row: row["id"] = uuid_value(variant, table)
        for column in ("quantity", "attempt_number"): 
            if column in row: row[column] = 1
        if "period_start" in row: row["period_start"] = START
        if "period_end" in row: row["period_end"] = END
        if "accepted_at" in row and not expected["tables"][table]["columns"]["accepted_at"]["nullable"]: row["accepted_at"] = START
        if "started_at" in row: row["started_at"] = START
        if "finished_at" in row and not expected["tables"][table]["columns"]["finished_at"]["nullable"]: row["finished_at"] = END
        if "value_type" in row: row["value_type"] = "boolean"
        if "boolean_value" in row: row["boolean_value"] = True
    rows["platform.runtime_attempt"]["fence"] = 1
    for table in ("app.consent_content_revision", "app.consent_presentation"):
        row = rows[table]
        field = "content_text" if table.endswith("content_revision") else "rendered_text"
        row[field] = "synthetic local ACL fact; not legal approval or rendered acceptance"
        row["content_hash" if field == "content_text" else "rendered_hash"] = StorageDigest(row[field], "text")
    receipt = rows["platform_private.identity_service_receipt"]
    receipt.update(service_principal="local-acl-fixture-not-an-authorized-adapter", security_generation=0, transition="bootstrap", previous_generation=None, previous_receipt_id=None, revoked_at=None)
    grant = rows["platform.database_action_grant"]
    grant.update(issuer_service="wa_context_issuer", database_login_role="wa_app_runtime", owner_module_id=OWNER,
                 action="SH-004.v1", purpose="provision", target_kind="CustomerProfile", policy_version="native-acl-fixture.v1",
                 backend_pid=0, transaction_id="inert-native-acl-fixture", expires_at=START, revoked_at=START)
    # Assign every required/composite FK from the actual source key values.
    # Optional FK tuples remain all NULL, except composites with required parts.
    for _ in range(len(rows) + 1):
        changed = False
        for table, desc in expected["tables"].items():
            for fk in desc["constraints"]:
                if fk["kind"] != "FOREIGN": continue
                if all(rows[table][column] is None for column in fk["columns"]): continue
                for column, parent_column in zip(fk["columns"], fk["referenced_columns"]):
                    value = rows[fk["references"]][parent_column]
                    if rows[table][column] != value: rows[table][column] = deepcopy(value); changed = True
        if not changed: break
    else: raise PreparationBlocked("native FK tuple assignment did not converge")
    user = rows["app.users"]["id"]; customer = rows["app.customer_profiles"]["id"]
    command = rows["platform.runtime_command_receipt"]
    semantic = "native-acl-" + fingerprint(variant)[:24]
    response = {"contract": "SH-004.v1", "requestId": semantic, "status": "ok", "value": {"customerProfileId": customer, "userId": user, "lifecycle": "active", "sourceToken": "0",
                "receipt": {"owner": OWNER, "id": command["id"], "semanticKey": semantic, "fingerprint": command["fingerprint"], "sourceToken": "0", "recordedAt": START}}}
    command.update(owner_module_id=OWNER, operation="SH-004.v1", subject_scope="CustomerProfile:" + customer, semantic_key=semantic, state="committed", source_revision=0,
                   result_schema_id="SH-004.v1#/$defs/response", result_schema_version="1", result_body=response, result_digest=StorageDigest(response))
    evidence = {"schema": "database-owner-evidence.v1", "owner": OWNER, "model": "CustomerProfile", "primaryKey": {"id": customer}, "prior": None,
                "committed": {"id": customer, "userId": user, "status": "active", "revision": "0", "privacyGeneration": "0"}, "decisionRef": "native-acl-fact-not-owner-proof"}
    rows["platform.owner_mutation_evidence"].update(owner_module_id=OWNER, aggregate_kind="CustomerProfile", aggregate_id=customer, previous_revision=None, committed_revision=0, action="SH-004.v1", decision_ref=evidence["decisionRef"], evidence_schema_id="urn:workinants:database-review:owner-evidence:v1#/$defs/CustomerProfile", evidence_schema_version="1", evidence_body=evidence, evidence_digest=StorageDigest(evidence))
    event = {"eventName": "customer.lifecycle_changed.v1", "customerProfileId": customer, "userId": user, "lifecycleRevision": "0", "safeState": "active"}
    rows["platform.runtime_outbox_message"].update(kind="event", producer_owner=OWNER, aggregate_kind="CustomerProfile", aggregate_id=customer, source_revision=0, source_generation=0, ordinal=0, name="customer.lifecycle_changed.v1", schema_version="1", payload_schema_id="urn:workin-ants:types:v1#/$defs/EventPayload_customer_lifecycle_changed_v1", payload=event, payload_hash=StorageDigest(event), causation_id=command["id"])
    rows["app.customer_profile_lifecycle_event"].update(name="customer.lifecycle_changed.v1", source_revision=0, to_status="active", from_status=None)
    rows["app.privacy_owner_receipt"]["result_schema_version"] = "1"
    rows["platform.runtime_effect_receipt"].update(owner_module_id=OWNER, operation="SH-004.v1", subject_scope="CustomerProfile:" + customer, result_schema_id="SH-004.v1#/$defs/response")
    if rows["app.privacy_owner_receipt"]["disposition"] == "retained": rows["app.privacy_owner_receipt"]["legal_basis_ref"] = "synthetic-not-a-legal-retention-decision"
    grant.update(principal_user_id=user, service_principal=None, target_id=customer)
    rows["platform_private.identity_service_authorization"]["revoked_at"] = START
    for table, row in rows.items():
        for column, info in expected["tables"][table]["columns"].items():
            if not info["nullable"] and row[column] is None: raise PreparationBlocked("required native column remains NULL")
            if row[column] is not None and info["type"]["name"] in expected["enums"] and row[column] not in expected["enums"][info["type"]["name"]]["labels"]:
                raise PreparationBlocked("enum fact outside source vocabulary")
    if schemas.check("SH-004", "response", response): raise PreparationBlocked("SH004 fact shape rejected")
    doc = schemas.documents["urn:workinants:database-review:owner-evidence:v1"]
    if schemas.errors(evidence, doc["$defs"]["CustomerProfile"], doc): raise PreparationBlocked("closed Customer evidence fact rejected")
    types = schemas.documents["urn:workin-ants:types:v1"]
    if schemas.errors(event, types["$defs"]["EventPayload_customer_lifecycle_changed_v1"], types): raise PreparationBlocked("closed event fact rejected")
    return rows


def dependencies(expected, rows):
    result = {table: set() for table in rows}
    for table, desc in expected["tables"].items():
        for fk in desc["constraints"]:
            if fk["kind"] != "FOREIGN" or any(rows[table][column] is None for column in fk["columns"]): continue
            if fk["match"] != "s": raise PreparationBlocked("non-simple FK match requires separate fixture derivation")
            if any(rows[table][c] != rows[fk["references"]][p] for c, p in zip(fk["columns"], fk["referenced_columns"])):
                raise PreparationBlocked("native FK fact mismatch")
            result[table].add(fk["references"])
    return result


def ordered(graph, selected=None):
    selected = set(graph) if selected is None else set(selected)
    result, pending = [], set(selected)
    while pending:
        ready = sorted(table for table in pending if not (graph[table] & pending))
        if not ready: raise PreparationBlocked("required native parent cycle needs separate reviewed shape")
        result.extend(ready); pending.difference_update(ready)
    return result


def parent_closure(graph, table):
    result, pending = set(), list(graph[table])
    while pending:
        current = pending.pop()
        if current == table: raise PreparationBlocked("self-parent requires separate source-supported INSERT fixture")
        if current not in result: result.add(current); pending.extend(graph[current])
    return result


def predicate(table, row, expected):
    keys = next((c["columns"] for c in expected["tables"][table]["constraints"] if c["kind"] == "PRIMARY"), None)
    if not keys: raise PreparationBlocked("source primary key required for exact existing row")
    return " AND ".join(ident(key) + "=" + sql_value(row[key], expected["tables"][table]["columns"][key]["type"]) for key in keys)


def insert_sql(table, row, expected):
    columns = expected["tables"][table]["columns"]
    return "INSERT INTO " + table_sql(table) + "(" + ",".join(ident(column) for column in columns) + ") VALUES (" + ",".join(sql_value(row[column], info["type"]) for column, info in columns.items()) + ")"


def validate_unique(expected, facts):
    definitions = {}
    for table, desc in expected["tables"].items():
        for ordinal, constraint in enumerate(desc["constraints"]):
            if constraint["kind"] in ("PRIMARY", "UNIQUE"):
                definitions[(table, "constraint-" + str(ordinal))] = (constraint["columns"], constraint.get("nulls_not_distinct", False))
    for identity, index in expected["explicit_indexes"].items():
        if not index["unique"]: continue
        keys = [source.node(key, "IndexElem") for key in index["keys_ast"]]
        if index["predicate"] is not None or any(not key.get("name") or key.get("expr") or key.get("collation") or key.get("opclass") for key in keys):
            raise PreparationBlocked("native unique expression/predicate/opclass needs separate fixture control")
        definitions[(index["table"], "index-" + identity)] = ([key["name"] for key in keys], index["nulls_not_distinct"])
    seen = {identity: set() for identity in definitions}
    for table, row in facts:
        for identity, (columns, nulls_equal) in definitions.items():
            if identity[0] != table: continue
            values = [row[column] for column in columns]
            if not nulls_equal and any(value is None for value in values): continue
            key = source.canonical(serializable(values))
            if key in seen[identity]: raise PreparationBlocked("duplicate native synthetic key: " + table)
            seen[identity].add(key)
    return {"projected_setup_rows": len(facts), "source_key_definitions": len(definitions), "derivation": "NO_DUPLICATE_CONCRETE_SOURCE_KEYS", "native_execution": "NOT_RUN"}


def trigger_sets(expected, application_sql):
    bodies = {}
    for match in re.finditer(r"CREATE FUNCTION (platform_private\.[a-z_0-9]+)\([^;]*?\nAS \$wa\$(.*?)\$wa\$;", application_sql, re.S):
        bodies[match[1]] = match[2]
    bypass, retained = [], []
    for identity, trigger in expected["triggers"].items():
        row = {"identity": identity, "table": trigger["table"], "name": trigger["name"], "function": trigger["function"],
               "original_enabled": trigger["enabled"], "body_sha256": expected["functions"][trigger["function"] + "()"]["body_sha256"]}
        if trigger["enabled"] != "O": raise PreparationBlocked("nonordinary trigger state needs explicit restoration review")
        if trigger["name"] == "physical_guard" and trigger["function"] in bodies and "context_" not in bodies[trigger["function"]] and "bound_grant" not in bodies[trigger["function"]]:
            row["reason"] = "Retain INSERT-time native scalar/revision stamping; source owner/group proof is not claimed."
            retained.append(row)
        elif trigger["function"] == "platform_private.message_json_guard":
            row["reason"] = "Retain the registered closed event/payload boundary: every native outbox fact uses exact Customer event JSON and its source revision/schema identity."
            retained.append(row)
        elif trigger["function"] == "platform_private.infrastructure_atomic" and trigger["table"] in ("platform.owner_mutation_evidence", "platform.runtime_outbox_message"):
            row["reason"] = "Retain the mandatory native-parent committed command/owner/action/transaction match. Factory FK parent is the same committed SH004 command and generic physical guards stamp all three rows in the same setup transaction."
            retained.append(row)
        else:
            row["reason"] = "Privileged native-fact setup cannot assert owner authority/atomic groups/worker/privacy behavior; disable exact USER trigger only for setup, then restore before ACL probe."
            bypass.append(row)
    return bypass, retained


def serializable(value):
    if isinstance(value, StorageDigest): return {"source_sql_storage_digest_of": serializable(value.value), "codec": "PostgreSQL17 jsonb::text UTF8 SHA256" if value.codec == "jsonb" else "UTF8 literal text SHA256"}
    if isinstance(value, dict): return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, list): return [serializable(item) for item in value]
    return value
