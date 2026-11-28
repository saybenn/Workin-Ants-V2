"""Render the accepted bounded pipe and finite coordinator method bodies."""

import ast
from copy import deepcopy
import datetime
import hashlib
import json
import re
import secrets
import sys
import uuid

import business_proof as proof


CONTEXT = 'scripts/sql-review/run-context-control-rehearsal.py'
RENDERER = 'scripts/sql-review/cloud-app-source8-v1/app_child.py'
PIPE = 'scripts/sql-review/cloud-app-source8-v1/host_session.py'
WORKER = 'scripts/sql-review/run-worker-recovery-control-rehearsal.py'
SCOPED = 'scripts/sql-review/run-scoped-read-companion-rehearsal.py'
PROTO = 'scripts/worker_recovery_control_protocol.py'
ROLES = ('postgres', 'wa_context_issuer', 'wa_app_runtime', 'wa_worker', 'wa_identity_service_authority')


def compile_nodes(nodes, path, namespace):
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, path, 'exec', dont_inherit=True), namespace)
    return namespace


def function_nodes(raw, names, path):
    nodes = [node for node in ast.parse(raw, filename=path).body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    proof.need(len(nodes) == len(names) and {node.name for node in nodes} == names, 'TRACK_SHARED_FUNCTION_ORIGIN')
    return nodes


def coordinator_method(raw, name, path):
    constructor, = function_nodes(raw, {'coordinator_type'}, path)
    cls, = (node for node in constructor.body if isinstance(node, ast.ClassDef) and node.name == 'Coordinator')
    method, = (node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    return method


def safe_code(error):
    code = getattr(error, 'code', None)
    if code is None and len(error.args) == 1:
        code = error.args[0]
    return code if type(code) is str and re.fullmatch('[A-Z0-9_]{1,100}', code) else 'TRACK_BOUNDED_CHILD_FAILURE'


def persist_before_dispatch(raw, context):
    """Retain the exact context operations with protected evidence/close ordering."""
    classes = [node for node in ast.parse(raw, filename=CONTEXT).body if isinstance(node, ast.ClassDef) and node.name == 'Coordinator']
    proof.need(len(classes) == 1, 'TRACK_SHARED_COORDINATOR_ORIGIN')
    selected = []
    for name, session in (('commit', 'session'), ('issue', 'issuer')):
        method, = (node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == name)
        launch, = (node for node in method.body if isinstance(node, ast.Assign) and len(node.targets) == 1
                   and isinstance(node.targets[0], ast.Name) and node.targets[0].id == session
                   and isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == 'self.session')
        attempt, = (node for node in method.body if isinstance(node, ast.Try) and node.finalbody and not node.handlers)
        records = [node for node in method.body if isinstance(node, ast.Expr) and ast.unparse(node.value) == 'self.record(record)']
        proof.need(len(records) == 1 and method.body.index(launch) < method.body.index(records[0]) < method.body.index(attempt),
                   'TRACK_EVIDENCE_BEFORE_SESSION_ORIGIN')
        method.body.remove(launch)
        method.body.insert(method.body.index(attempt), ast.parse(f'{session} = None').body[0])
        attempt.body.insert(0, launch)
        attempt.handlers = ast.parse('try:\n pass\nexcept BaseException as error:\n self.evidence.stop(safe_code(error))\n raise').body[0].handlers
        finish = ast.parse(f'''if {session} is not None:
    preserve_primary = sys.exc_info()[0] is not None
    previous_finalizing = self.evidence.finalizing
    self.evidence.finalizing = True
    try:
        pass
    except BaseException as secondary:
        self.evidence.stop(safe_code(secondary))
        if not preserve_primary:
            raise
    finally:
        self.evidence.finalizing = previous_finalizing
''').body[0]
        finish.body[-1].body = attempt.finalbody
        attempt.finalbody = [finish]
        method.body.insert(method.body.index(attempt) + 1, ast.parse('self.evidence.save()').body[0])
        if name == 'issue':
            point, = (index for index, node in enumerate(method.body) if ast.unparse(node) == 'token_hash = sha(bytes.fromhex(secret))')
            method.body.insert(point + 1, ast.parse('_register_secret(secret, token_hash)').body[0])
        selected.append(method)
    return compile_nodes(selected, CONTEXT, {**context, 'safe_code': safe_code, 'sys': sys})


def load(material, register_secret):
    _, _, sources, _ = material
    for path in (RENDERER, PIPE, WORKER, SCOPED, PROTO):
        proof.need(proof.sha(sources[path]) == proof.PROFILE_SOURCES[path], 'TRACK_PINNED_SHARED_FRAGMENT')
    scope = {'ast': ast, 'CONTEXT': CONTEXT, 'require': proof.need, 'deepcopy': deepcopy, 'datetime': datetime,
             'hashlib': hashlib, 'json': json, 're': re, 'uuid': uuid, 'secrets': secrets}
    render = compile_nodes(function_nodes(sources[RENDERER], {'render_context', 'exact_nodes', 'execute_ast'}, RENDERER),
                           RENDERER, scope)['render_context']
    context = render(sources, safe_code, register_secret)
    old_roles = b'APP_ROLES = ("postgres", "wa_context_issuer", "wa_app_runtime")'
    old_ack = b'"WA_CLOUD_APP_ACK|"'
    pipe = sources[PIPE]
    proof.need(pipe.count(old_roles) == pipe.count(old_ack) == 1, 'TRACK_EXACT_PIPE_DELTA')
    pipe = pipe.replace(old_roles, b'APP_ROLES = ' + repr(ROLES).encode()).replace(old_ack, b'"WA_CLOUD_TRACK_ACK|"')
    bounded = {}
    exec(compile(pipe, PIPE, 'exec', dont_inherit=True), bounded)

    class Session(bounded['BoundedSession'], context['Session']):
        pass

    proto = {}
    exec(compile(sources[PROTO], PROTO, 'exec', dont_inherit=True), proto)
    shared = {'need': proof.need, 'context': {**context, 're': re}, 'unique_json': proof.unique_json,
              'safe_code': safe_code, 'quote': context['quote'], 'HeldFailure': proof.Held}
    transaction = compile_nodes([coordinator_method(sources[WORKER], 'transaction', WORKER)], WORKER, dict(shared))['transaction']
    retention = compile_nodes([coordinator_method(sources[SCOPED], 'retention', SCOPED)], SCOPED, dict(shared))['retention']
    guarded = persist_before_dispatch(sources[CONTEXT], context)

    class Core(context['Coordinator']):
        commit = guarded['commit']
        issue = guarded['issue']

        def grant_values(self, template, backend, issuer, identity, token_hash):
            proof.need(backend['login'] == template['database_login_role'], 'TRACK_EXACT_GRANT_HOLDER_LOGIN')
            return super().grant_values(template, backend, issuer, identity, token_hash)

        def retention(self, instances, unexpired=False):
            return retention(self, instances, unexpired)

        def finite_transaction(self, name, grant, leaf, expected, lease, fence):
            return transaction(self, name, grant, leaf, expected, lease, fence, global_after=True)

    return Core, Session, proto
