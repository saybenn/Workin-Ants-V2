"""Pure, versioned source preparation; never executes SQL or changes old history."""
from pathlib import Path
import hashlib
import json
import math
import re

BASE = 'review-output/foundation-application.review.sql'
BASE_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
OLD_BODY_SHA = '10f9fbdd4b20513d2fa74af2136bb2a60e07eaf567b3425c365bc68290e54038'
CAUSE = 'context/reconciliation/local-f0-operation-sources/runtime-lease-branch-v1/cause-plan.json'
CAUSE_SHA = '650697274a35632841a9fbfd16e323e401480c232816f892f56c8dc1bef5d568'
OUT = 'review-output/runtime-lease-branch-v1'
HISTORY = OUT+'/history-source-artifact'
INITIAL = '20261117000100_f0_local_initial'
SECOND = '20261120000100_f0_runtime_lease_branch_v1'
INPUTS = {
 BASE: BASE_SHA,
 'prisma/foundation/migrations/'+INITIAL+'/migration.sql': BASE_SHA,
 'prisma/migrations/20260602021702_phase_2_database_truth_layer/migration.sql': '5b4f44a1b1f989743df227c487a6ecb3dd793e9915d9a635d8e32b99304b2055',
 'scripts/sql-review/foundation-invariants.sql': '8fc28f505bf100db89c8d441a507f3a8d58532dfb5ef960c8790d729a73f9904',
 'prisma/foundation/history-manifest.json': '7b7d385b978f43d06ad519be34c00144ae6b3101f92ce6032dc32202353f971e',
 'review-output/app-write-two-guard-observation-v2/pending-work-next-attempt-update.sql': '09301370c3ec2bf45d9385442b8da1b3bbba5e6d955673d15e89e52f12389e4b',
 'review-output/app-write-two-guard-observation-v2/fixtures.json': '9a0b874d96fb621e20adfa5dcca5b1cc472f025507b171af056b58c9ff23c962',
 'scripts/prepare-local-f0-history.py': '33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8',
 'scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/foundation-sql-draft-access.json': 'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea',
 'prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 CAUSE: CAUSE_SHA,
}
OUTER = "OLD.state='leased' AND NEW.state<>'leased'"
INNER = "OLD.lease_expires_at<=clock_timestamp()\n    OR NOT platform_private.lease_secret_matches(OLD.lease_token_hash::text)\n    OR current_setting('wa.fence',true) IS DISTINCT FROM OLD.fence::text"
RAISE = "THEN RAISE EXCEPTION 'expired or foreign worker'; END IF;"
OLD = '   IF '+OUTER+' AND ('+INNER+')\n   '+RAISE
NEW = '   IF '+OUTER+' THEN\n    IF '+INNER+'\n    '+RAISE+'\n   END IF;'
SYNTH = 'wa_lease_branch_v1_repro'
ROLES = ('wa_lease_v1_app','wa_lease_v1_worker','wa_lease_v1_verifier')

class SourceFailure(Exception):
    pass

def need(ok, code):
    if not ok:
        raise SourceFailure(code)

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n').encode()

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def decode(blob):
    def pairs(items):
        out={}
        for key,value in items:
            need(key not in out,'DUPLICATE_JSON_KEY');out[key]=value
        return out
    value=json.loads(blob,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE_JSON'))
    def finite(item,depth=0):
        need(depth<=64,'JSON_DEPTH')
        if type(item)is dict:
            for value in item.values():finite(value,depth+1)
        elif type(item)is list:
            for value in item:finite(value,depth+1)
        else:need(item is None or type(item)in(str,int,bool)or type(item)is float and math.isfinite(item),'JSON_TYPE')
    finite(value);return value

def extract(text,name):
    matches=list(re.finditer(r'^CREATE FUNCTION '+re.escape(name)+r'\(',text,re.M))
    need(len(matches)==1,'ONE_SOURCE_FUNCTION')
    tail=text[matches[0].start():]
    marker=re.search(r'\bAS\s+(\$[a-z_0-9]*\$)',tail)
    need(marker is not None,'SOURCE_FUNCTION_DELIMITER')
    end=tail.find(marker[1],marker.end())
    need(end>=0 and tail[end+len(marker[1]):].startswith(';'),'SOURCE_FUNCTION_TERMINAL')
    return tail[:end+len(marker[1])+1],tail[marker.end():end]

def patch_body(body):
    need(type(body)is str and sha(body.encode())==OLD_BODY_SHA,'ORIGINAL_BODY_HASH')
    need(body.count(OLD)==1 and NEW not in body,'ONE_FINAL_LEASE_EXIT')
    result=body.replace(OLD,NEW,1)
    need(result.replace(NEW,OLD,1)==body,'BODY_REVERSIBLE_DELTA')
    need(result.count('platform_private.lease_secret_matches(')==body.count('platform_private.lease_secret_matches(')==3,'PRIVATE_HELPER_CALLS_UNCHANGED')
    return result

def effective_definition(body):
    return ('CREATE OR REPLACE FUNCTION platform_private.runtime_transition() RETURNS trigger\n'
            'LANGUAGE plpgsql VOLATILE CALLED ON NULL INPUT SECURITY INVOKER\n'
            'PARALLEL UNSAFE COST 100 SET search_path=pg_catalog AS $wa$'+body+'$wa$;\n')

def synthetic_function(fragment):
    body='\nBEGIN\n'+fragment.replace('platform_private.lease_secret_matches',SYNTH+'.lease_secret_matches')+'\n RETURN NEW;\nEND '
    return ('CREATE OR REPLACE FUNCTION '+SYNTH+'.guard() RETURNS trigger\n'
            'LANGUAGE plpgsql VOLATILE CALLED ON NULL INPUT SECURITY INVOKER\n'
            'PARALLEL UNSAFE COST 100 SET search_path=pg_catalog AS $wa$'+body+'$wa$;\n')

def reproduction(helper):
    app,worker,verifier=ROLES
    old=synthetic_function(OLD);new=synthetic_function(NEW)
    values="(1,'pending',0,0,NULL,NULL,NULL,'2026-01-01T00:00:00Z')"
    for row in range(2,6):
        interval="-interval '1 hour'"if row==3 else"+interval '1 hour'"
        values+=",("+str(row)+",'leased',7,1,encode(sha256(decode(repeat('a',64),'hex')),'hex'),clock_timestamp()"+interval+",NULL,'2026-01-01T00:00:00Z')"
    setup=('BEGIN;\nCREATE SCHEMA '+SYNTH+';\n'+''.join('CREATE ROLE '+r+' LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;\n'for r in ROLES)+
        'GRANT USAGE ON SCHEMA '+SYNTH+' TO '+','.join(ROLES)+';\n'+
        helper.replace('platform_private.lease_secret_matches',SYNTH+'.lease_secret_matches')+'\n'+old+
        'REVOKE ALL ON ALL FUNCTIONS IN SCHEMA '+SYNTH+' FROM PUBLIC;\n'+
        'GRANT EXECUTE ON FUNCTION '+SYNTH+'.lease_secret_matches(text) TO '+worker+','+verifier+';\n'+
        'CREATE TABLE '+SYNTH+'.work(id integer PRIMARY KEY,state text NOT NULL,fence bigint NOT NULL,attempt_count integer NOT NULL,lease_token_hash text,lease_expires_at timestamptz,effect_receipt_id uuid,next_attempt_at timestamptz NOT NULL);\n'+
        'INSERT INTO '+SYNTH+'.work VALUES'+values+';\n'+
        'CREATE TRIGGER exact_guard BEFORE UPDATE ON '+SYNTH+'.work FOR EACH ROW EXECUTE FUNCTION '+SYNTH+'.guard();\n'+
        'GRANT SELECT ON '+SYNTH+'.work TO '+','.join(ROLES)+';\n'+
        'GRANT UPDATE(next_attempt_at) ON '+SYNTH+'.work TO '+app+';\n'+
        'GRANT UPDATE(state,lease_token_hash,lease_expires_at) ON '+SYNTH+'.work TO '+worker+';\nCOMMIT;\n')
    pending=('BEGIN ISOLATION LEVEL READ COMMITTED;\nSELECT \'LEASE_V1_BEFORE\';\nUPDATE '+SYNTH+".work SET next_attempt_at='2026-01-02T00:00:00Z' WHERE id=1 RETURNING jsonb_build_object('id',id,'state',state,'fence',fence,'attempt_count',attempt_count,'lease_fields_null',lease_token_hash IS NULL AND lease_expires_at IS NULL,'effect_absent',effect_receipt_id IS NULL,'next_attempt_at',next_attempt_at);\nSELECT 'LEASE_V1_AFTER';\nCOMMIT;\n")
    direct="BEGIN;\nSELECT set_config('wa.lease_secret',repeat('a',64),true) IS NOT NULL;\nSELECT "+SYNTH+".lease_secret_matches(encode(sha256(decode(repeat('a',64),'hex')),'hex'));\nROLLBACK;\n"
    cases=[{'id':'old-pending','variant':'OLD','role':app,'file':'pending-update.sql','expected':'42501_EXACT_PRIVATE_HELPER_ACL_AND_SYNTHETIC_GUARD_FRAME_NO_COMMIT'},
           {'id':'nested-pending','variant':'NESTED','role':app,'file':'pending-update.sql','expected':'ONE_EXACT_ROW_CLEAN_ACK_COMMIT_ONLY_TIMESTAMP_CHANGE'},
           {'id':'restored-old-pending','variant':'RESTORED_OLD','role':app,'planned_baseline_reset_under_nested':'reset-pending-baseline.sql','file':'pending-update.sql','expected':'42501_AGAIN_OLD_EXPRESSION_TRIPWIRE'},
           {'id':'app-helper-before','variant':'OLD','role':app,'file':'direct-helper.sql','expected':'42501_NATIVE_FUNCTION_ACL'},
           {'id':'app-helper-after','variant':'NESTED','role':app,'file':'direct-helper.sql','expected':'42501_NATIVE_FUNCTION_ACL'},
           {'id':'worker-helper','variant':'NESTED','role':worker,'file':'direct-helper.sql','expected':'TRUE'},
           {'id':'verifier-helper','variant':'NESTED','role':verifier,'file':'direct-helper.sql','expected':'TRUE'}]
    files={'setup-original.sql':setup.encode(),'install-nested.sql':('BEGIN;\n'+new+'COMMIT;\n').encode(),
           'restore-old.sql':('BEGIN;\n'+old+'COMMIT;\n').encode(),'pending-update.sql':pending.encode(),'direct-helper.sql':direct.encode(),
           'reset-pending-baseline.sql':('BEGIN;\nUPDATE '+SYNTH+".work SET next_attempt_at='2026-01-01T00:00:00Z' WHERE id=1 RETURNING id,next_attempt_at;\nCOMMIT;\n").encode()}
    for row,(label,secret,fence)in enumerate([('current',"repeat('a',64)",'7'),('expired',"repeat('a',64)",'7'),('wrong-secret',"repeat('b',64)",'7'),('wrong-fence',"repeat('a',64)",'8')],2):
        # Public dummy bytes are not login credentials or a real worker handle.
        action=("BEGIN ISOLATION LEVEL READ COMMITTED;\nSELECT set_config('wa.lease_secret',"+secret+",true) IS NOT NULL;\nSELECT set_config('wa.fence','"+fence+"',true)='"+fence+"';\nSELECT 'LEASE_V1_BEFORE';\nUPDATE "+SYNTH+".work SET state='pending',lease_token_hash=NULL,lease_expires_at=NULL WHERE id="+str(row)+" RETURNING id,state,fence,attempt_count;\nSELECT 'LEASE_V1_AFTER';\nCOMMIT;\n")
        files['worker-'+label+'.sql']=action.encode()
        cases.append({'id':'worker-'+label,'variant':'NESTED','role':worker,'target_row':row,'file':'worker-'+label+'.sql','expected':'ONE_ROW_COMMIT'if label=='current'else'P0001_EXACT_EXPIRED_OR_FOREIGN_WORKER_RAISE_ROLLBACK'})
    files['observe.sql']=('BEGIN READ ONLY;\nSELECT jsonb_build_object(\n\'rows\',(SELECT jsonb_agg(jsonb_build_object(\'id\',id,\'state\',state,\'fence\',fence,\'attempt_count\',attempt_count,\'lease_fields_null\',lease_token_hash IS NULL AND lease_expires_at IS NULL,\'effect_absent\',effect_receipt_id IS NULL,\'next_attempt_at\',next_attempt_at) ORDER BY id) FROM '+SYNTH+'.work),\n\'app_helper_execute\',has_function_privilege(\''+app+'\',\''+SYNTH+'.lease_secret_matches(text)\',\'EXECUTE\'),\n\'worker_helper_execute\',has_function_privilege(\''+worker+'\',\''+SYNTH+'.lease_secret_matches(text)\',\'EXECUTE\'),\n\'verifier_helper_execute\',has_function_privilege(\''+verifier+'\',\''+SYNTH+'.lease_secret_matches(text)\',\'EXECUTE\'),\n\'trigger_enabled\',(SELECT tgenabled=\'O\' FROM pg_trigger WHERE tgrelid=\''+SYNTH+'.work\'::regclass AND tgname=\'exact_guard\'));\nROLLBACK;\n').encode()
    files['observe-preconditions.sql']=('BEGIN READ ONLY;\nSELECT jsonb_build_object(\n'
        "'guard_source', (SELECT jsonb_build_object('body_sha256',encode(sha256(convert_to(p.prosrc,'UTF8')),'hex'),'original_grantor_owner',p.proowner='postgres'::regrole,'invoker',NOT p.prosecdef,'volatile',p.provolatile='v','unsafe',p.proparallel='u','not_strict',NOT p.proisstrict,'cost100',p.procost=100,'search_path_exact',p.proconfig=ARRAY['search_path=pg_catalog']::text[]) FROM pg_proc p WHERE p.oid='"+SYNTH+".guard()'::regprocedure),\n"
        "'lease_fixture', (SELECT jsonb_agg(jsonb_build_object('id',id,'lease_hash_matches_public_dummy',CASE WHEN lease_token_hash IS NULL THEN NULL ELSE lease_token_hash=encode(sha256(decode(repeat('a',64),'hex')),'hex') END,'expired',CASE WHEN lease_expires_at IS NULL THEN NULL ELSE lease_expires_at<=clock_timestamp() END) ORDER BY id) FROM "+SYNTH+'.work));\nROLLBACK;\n').encode()
    guards={}
    for label,definition in(('OLD',old),('NESTED',new)):
        body=definition.split('AS $wa$',1)[1].rsplit('$wa$;',1)[0]
        guards[label]={'body_sha256':sha(body.encode()),'condition_body_line':3 if label=='OLD'else 4,
            'raise_body_line':next(i for i,line in enumerate(body.split('\n'),1)if "RAISE EXCEPTION 'expired or foreign worker'"in line)}
    contract={'schema':'workinants.runtime-lease-branch-v1-synthetic-reproduction.v1','status':'NOT_RUN','source_review':'PENDING','scope':'PG17_11_DIAGNOSTIC_MECHANISM_ONLY_NO_BUSINESS_PROMOTION','schema_name':SYNTH,'roles':list(ROLES),'cases':cases,'guard_source_profiles':guards,
        'source_inputs':{'runtime_transition_body_sha256':OLD_BODY_SHA,'helper_body_sha256':sha(extract(helper,'platform_private.lease_secret_matches')[1].encode())},
        'privileges':'Real independent SCRAM logins; app never granted helper EXECUTE; worker AND verifier allowed. No SET ROLE masquerade for behavioral actor.',
        'mandatory_external_protocol':['NEW separately reviewed oneC1V/noports/networknone exact PG17.11 manifest and original-grantor bootstrap/cleanup; all source/literal gates required before real execution. No operator/credentials are prepared here.',
         'Provision independent owner-only credentials outside these SQL files; loopbackSCRAM correct/wrong/HBA/method verification, disabled statement/error-statement logging. No password placeholders in SQL.',
         'Original grantor creates fresh synthetic schema/roles. Before every actor ensure exactly one target row, source body/owner/ACL identity, exact intended column grants and enabled trigger. Never infer target visibility from zero updates.',
         'Bind observe-preconditions.sql guard body to exact OLD/NESTED source profile. Before worker cases require exact fixed row2/3/4/5 fence7/attempt1/public dummy hash, row3 expired and other leased rows live; observers retain booleans and hashes, not raw helper values.',
         'The initial setup inserts five synthetic rows before creating its synthetic trigger. Each worker case has a different fixed row2/3/4/5. No trigger is disabled or reset between cases; independently verify exact enabled trigger before every actor. No canonical guard or object is touched.',
         'Before the planned restore-old contrast, reset only the pending scheduling timestamp through the actual app login while nested source is installed; require one clean committed row and independently exact original baseline. Then original grantor installs ONLY the old guard definition. This planned baseline step is forbidden after any unexpected result.',
         'Run each actor from a fresh real login/process. On error close it and prove backend absence before rollback observations. Stop later cases on any unlisted result; original/nested/old-restoration are separately planned contrasts, never repairs during an unexpected failure.',
         'Retain typed result/exit/ACK/marker/SQLSTATE/source-frame/hash comparisons only. Public repeat(a,64) is dummy source data, not a retained login password or real worker secret.',
         'Require source-sensitive native42501 helper attribution (schema/function identity/location plus synthetic guard line), not SQLSTATE alone. P0001 must name exact synthetic expired-or-foreign-worker RAISE line and bodyhash.',
         'Clean only exact run-owned sandbox resources/test files after identity labels. Retain image; independently confirm absence. Synthetic proof does not promote old App8f2a/0a, worker or94/451 assertions.'],
        'Posture':'D'}
    files['plan.json']=encoded(contract)
    return {OUT+'/synthetic/'+name:blob for name,blob in files.items()}

def build(root):
    root=Path(root).resolve(strict=True);blobs={}
    for rel,wanted in INPUTS.items():
        path=root/rel
        need(not path.is_symlink()and path.resolve(strict=True).is_relative_to(root),'SOURCE_PATH')
        blob=path.read_bytes();need(len(blob)<=8*1024*1024 and sha(blob)==wanted,'SOURCE_HASH');blobs[rel]=blob
    cause=decode(blobs[CAUSE]);need(cause['minimal_repair_PLAN_ONLY']['target_old_body_sha256']==OLD_BODY_SHA,'CAUSE_BODY_BINDING')
    base=blobs[BASE].decode();original,body=extract(base,'platform_private.runtime_transition')
    need(original.startswith('CREATE FUNCTION platform_private.runtime_transition() RETURNS trigger\nLANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $wa$'),'EXACT_ORIGINAL_HEADER')
    need(extract(blobs['scripts/sql-review/foundation-invariants.sql'].decode(),'platform_private.runtime_transition')[1]==body,'OLD_FRAGMENT_EXACT_BODY')
    new=patch_body(body);definition=effective_definition(new)
    patch=('BEGIN;\nSET LOCAL ROLE wa_schema_owner;\n'+definition+'RESET ROLE;\nCOMMIT;\n').encode()
    helper,_=extract(base,'platform_private.lease_secret_matches')
    acl=decode(blobs['context/reconciliation/foundation-sql-draft-access.json']);worker=[r for r in acl if r['role']=='wa_worker'];need(len(worker)==32,'EXACT32_WORKER_ACL')
    files={HISTORY+'/migrations/'+INITIAL+'/migration.sql':blobs[BASE],HISTORY+'/migrations/'+SECOND+'/migration.sql':patch,
           HISTORY+'/migrations/migration_lock.toml':blobs['prisma/foundation/migrations/migration_lock.toml'],
           OUT+'/effective-runtime-transition.sql':definition.encode(),OUT+'/worker-acl32.json':encoded(worker)}
    overlay={'schema':'workinants.runtime-lease-branch-v1-targeted-source-overlay.v1','status':'NOT_RUN','review_status':'PENDING',
        'kind':'TARGETED_FUNCTION_OVERLAY_NOT_COMPLETE_CATALOG','base_application_sha256':BASE_SHA,'patch_sha256':sha(patch),
        'ordered_history':[{'migration':INITIAL,'sha256':BASE_SHA},{'migration':SECOND,'sha256':sha(patch)}],
        'function':{'identity':'platform_private.runtime_transition()','old_body_sha256':OLD_BODY_SHA,'new_body_sha256':sha(new.encode()),
        'language':'plpgsql','security_definer':False,'volatility':'v','strict':False,'parallel':'u','cost':100,'settings':['search_path=pg_catalog'],'return_type':'pg_catalog.trigger','owner':'wa_schema_owner','ownership_permissions':'PRESERVED_BY_REPLACE_NO_GRANTS_OR_OWNER_STATEMENTS'},
        'helper':{'source_definition_sha256':sha(helper.encode()),'app_execute':'REMAINS_DENIED','allowed_explicit_grantees':['wa_track_verifier','wa_worker']},
        'worker_acl32_sha256':sha(canonical(worker)),'source_files_sha256':INPUTS,
        'history_limits':'Versioned review/source artifact only, outside every active Prisma migration directory. Original7-file/one-ledger evidence unchanged. Existing one-migration guard/config does not admit this history. A future reviewed2-migration operator may materialize an exact fresh snapshot. No generated full native/oracle/ledger registration; cannot execute using old operators.',
        'additional_affected_checks_required':['Versioned exact two-migration history/preparer/guard/config/runner and explicit replace-aware catalog compiler/expected/oracle/ledger source closure.','Fresh two-row deploy/noop immutable-checksum/registration/catalog/ownerACL/trigger-link proof with new correct counts; never reuse old29089/22 as new authority.','New App diagnostic body/frame admission and unchanged real R01/R02 recipes after fresh source qualification.','Actual synthetic PG17.11 old/nested/restored-old/helper/worker contrasts; then actual new-source leased-exit current/expired/secret/fence checks before business assertions.'],
        'Posture':'D'}
    overlay['effective_ordered_source_sha256']=sha(canonical({'base_application_sha256':BASE_SHA,'ordered_history':overlay['ordered_history'],'target_function':overlay['function']}))
    files[OUT+'/overlay.json']=encoded(overlay);files.update(reproduction(helper))
    proposal={'schema':'workinants.runtime-lease-branch-v1-source-proposal.v1','status':'NOT_RUN','review_status':'PENDING','runtime_authority':False,'scope':'SOURCE_ONLY_APPEND_ONLY_CANDIDATE_AND_SYNTHETIC_DIAGNOSTIC_PACKET','inputs_sha256':INPUTS,
        'generated_files_sha256':{p:sha(b)for p,b in sorted(files.items())},'base_application_sha256':BASE_SHA,'new_body_sha256':sha(new.encode()),'effective_ordered_source_sha256':overlay['effective_ordered_source_sha256'],
        'observed_cause_limit':'0a42501/old10f9/bodyline33 observed; denied callee source-supported inference.8f2a complete cause remains UNOBSERVED. Offline mocks are not actual PG proof.','Posture':'D'}
    files[OUT+'/proposal.json']=encoded(proposal)
    return files,proposal
