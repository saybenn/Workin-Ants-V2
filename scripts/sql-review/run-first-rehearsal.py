"""Dormant small-rehearsal coordinator. NEVER run during source-only approval.

Requires separately approved, installed/finalized, isolated success container and
preprovisioned private PGPASSFILE. Creates/starts/pulls no Docker resources. Does
not implement real authentication/owner adapters or process the Track worker.
"""
import argparse
import hashlib
import json
from pathlib import Path
import queue
import re
import secrets
import subprocess
import threading

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=ROOT/'review-output/first-rehearsal'
CONTAINER='wa-p0c-first-20261110-ok'
def quote(s):return "'"+str(s).replace("'","''")+"'"

def grant_sql(case,login,pid,xid,token_hash):
    if login!='wa_app_runtime' or not re.fullmatch(r'[0-9]+',str(pid)) or not re.fullmatch(r'[0-9]+',str(xid)) or not re.fullmatch(r'[0-9a-f]{64}',token_hash):raise ValueError('invalid captured runtime tuple/hash')
    fields='ARRAY['+','.join(quote(f) for f in case['allowed_fields'])+']::text[]'
    return "BEGIN; INSERT INTO platform.database_action_grant (id,token_hash,issuer_service,principal_user_id,service_principal,database_login_role,owner_module_id,action,purpose,target_kind,target_id,allowed_fields,policy_version,security_generation,source_generation,backend_pid,transaction_id,expires_at) VALUES ("+','.join([quote(case['grant_id']),quote(token_hash),"'wa_context_issuer'",quote(case['principal_user_id']),'NULL',quote(login),"'customer_buyer_profile'","'SH-004.v1'","'provision'","'CustomerProfile'",quote(case['ids']['CustomerProfile']),fields,"'first-rehearsal.v1'",'0','0',str(pid),quote(xid),"clock_timestamp()+interval '5 minutes'"])+"); COMMIT;\n"

def psql(role):
    return ['docker','--context','desktop-linux','exec','-i','-e','PGPASSFILE=/run/wa-secrets/pgpass',CONTAINER,'psql','-X','-qAt','-v','ON_ERROR_STOP=1','-v','VERBOSITY=sqlstate','-h','127.0.0.1','-U',role,'-d','wa_p0c_rehearsal']

def run(role,sql):
    r=subprocess.run(psql(role),input=sql,text=True,capture_output=True,timeout=60)
    if r.returncode:raise RuntimeError('restricted SQL step failed for '+role+'; retain only redacted error/SQLSTATE')
    return r.stdout.strip()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-approved-rehearsal',action='store_true')
    p.add_argument('--evidence-directory',type=Path)
    a=p.parse_args()
    if not a.execute_approved_rehearsal:p.error('EXECUTION HELD: separate Brain approval required; no Docker/DB call performed')
    if a.evidence_directory is None:p.error('an external test-owned evidence directory is required')
    evidence_dir=a.evidence_directory.resolve()
    if evidence_dir==ROOT or ROOT in evidence_dir.parents:p.error('runtime evidence/secrets must remain outside source checkout')
    endpoint=json.loads(subprocess.check_output(['docker','--context','desktop-linux','context','inspect','desktop-linux'],text=True,timeout=30))[0]['Endpoints']['docker']['Host']
    if endpoint!='npipe:////./pipe/dockerDesktopLinuxEngine':raise RuntimeError('unexpected Docker endpoint; stop rather than contact remote daemon')
    resource=json.loads(subprocess.check_output(['docker','--context','desktop-linux','inspect',CONTAINER],text=True,timeout=30))[0]
    plan=json.loads((ROOT/'context/reconciliation/database-candidate-tests.json').read_text(encoding='utf8'))['first_rehearsal']
    if resource['Config']['Image']!=plan['image']['reference']:raise RuntimeError('wrong pinned rehearsal image')
    if resource['Config']['Labels'].get('workinants.rehearsal')!='p0c-first-20261110' or resource['HostConfig']['NetworkMode']!='none' or resource['HostConfig'].get('PortBindings'):raise RuntimeError('wrong rehearsal resource/network')
    final=run('postgres',"SELECT count(*) FROM pg_auth_members m WHERE m.roleid IN ('wa_private_helper_owner'::regrole,'wa_customer_verifier'::regrole,'wa_track_verifier'::regrole) AND m.member='wa_schema_owner'::regrole;")
    if final!='0':raise RuntimeError('temporary authority remains; runtime rehearsal forbidden')
    leaf_create=run('postgres',"SELECT has_schema_privilege('wa_private_helper_owner','platform_private','CREATE') OR has_schema_privilege('wa_customer_verifier','platform_private','CREATE') OR has_schema_privilege('wa_track_verifier','platform_private','CREATE');")
    if leaf_create!='f':raise RuntimeError('temporary function-creation privilege remains')
    if run('postgres',"SELECT current_setting('server_version') LIKE '17.11%';")!='t':raise RuntimeError('wrong PostgreSQL version')
    logging=run('postgres',"SELECT current_setting('log_statement')='none' AND current_setting('log_min_error_statement')='panic';")
    if logging!='t':raise RuntimeError('test logging defaults could retain injected secrets; stop')
    # All roles' test passwords were provisioned separately into private tmpfs.
    # No password or raw context handle appears in process arguments/source/logs.
    run('postgres',(FIXTURES/'fixtures.sql').read_text(encoding='utf8'))
    results=[]
    for case in json.loads((FIXTURES/'fixtures.json').read_text(encoding='utf8'))['scenarios']:
        app=subprocess.Popen(psql('wa_app_runtime'),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        secret=secrets.token_hex(32)
        try:
            lines=queue.Queue()
            def read_tuple():
                for line in app.stdout:
                    lines.put(line.rstrip())
            reader=threading.Thread(target=read_tuple,daemon=True);reader.start()
            app.stdin.write("BEGIN ISOLATION LEVEL READ COMMITTED; SELECT 'WA_TUPLE|'||session_user||'|'||pg_backend_pid()::text||'|'||pg_current_xact_id()::text;\n");app.stdin.flush()
            tuple_line=lines.get(timeout=30)
            if not tuple_line.startswith('WA_TUPLE|'):raise RuntimeError('runtime tuple capture failed')
            _,login,pid,xid=tuple_line.split('|')
            run('wa_context_issuer',grant_sql(case,login,pid,xid,hashlib.sha256(bytes.fromhex(secret)).hexdigest()))
            # Consume the remaining streams via the single reader: stop it at
            # process exit; stderr has no echo/argv secrets and is not retained.
            app.stdin.write('SELECT platform_private.bind_request_context('+quote(secret)+');\n'+(FIXTURES/case['transaction_sql']).read_text(encoding='utf8')+'\n\\q\n');app.stdin.close()
            code=app.wait(timeout=45)
            reader.join(timeout=5)
            if reader.is_alive():raise RuntimeError('runtime output did not finish')
            markers=[]
            while not lines.empty():
                line=lines.get_nowait()
                if line in ['WA_COMMAND_INSERTED','WA_CUSTOMER_INSERTED','WA_READY_TO_COMMIT']:markers.append(line)
            if (code==0)!=case['expected_commit']:raise RuntimeError('unexpected scenario outcome: '+case['name'])
            error=app.stderr.read()
            states=re.findall(r'(?:ERROR|FATAL):\s+([0-9A-Z]{5})\b',error)
            expected_state=None if case['name']=='positive' else '42501' if case['name']=='wrong-person' else 'P0001'
            if (states[-1] if states else None)!=expected_state:raise RuntimeError('wrong failure stage/SQLSTATE: '+case['name'])
            expected_markers=['WA_COMMAND_INSERTED'] if case['name']=='wrong-person' else ['WA_COMMAND_INSERTED','WA_CUSTOMER_INSERTED','WA_READY_TO_COMMIT']
            if markers!=expected_markers:raise RuntimeError('failure occurred before the intended source/COMMIT gate: '+case['name'])
            counts=json.loads(run('postgres',(FIXTURES/case['observer_sql']).read_text(encoding='utf8')))
            if counts!=case['expected_counts']:raise RuntimeError('partial source group: '+case['name'])
            results.append({'case':case['name'],'authenticated_login':login,'exit_code':code,'sqlstate':expected_state,'stage_markers':markers,'counts':counts,'status':'PASS_REHEARSAL_ONLY'})
        finally:
            if app.poll() is None:
                app.terminate()
                try:app.wait(timeout=10)
                except subprocess.TimeoutExpired:app.kill();app.wait(timeout=10)
    evidence_dir.mkdir(parents=True,exist_ok=True)
    (evidence_dir/'first-customer-results.json').write_text(json.dumps({'scope':'THREE_SQL_FIXTURES_ONLY_NOT_94_OR_451_QUALIFICATION','results':results},indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
