#!/usr/bin/env python3
"""Independent mutations of SQL/ACL evidence; no SQL execution or database."""
from pathlib import Path
import tempfile,shutil,json,runpy,argparse
ROOT=Path(__file__).resolve().parents[1]
CHECK=runpy.run_path(str(ROOT/'scripts/check-foundation-sql-draft.py'))['checks']
manifest=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-manifest.json').read_text())
APP='review-output/foundation-application.review.sql';BOOT='review-output/foundation-bootstrap.review.sql'
cases=[
 ('remove tuple login',APP,'database_login_role=session_user::text','database_login_role=database_login_role'),
 ('remove tuple backend',APP,'backend_pid=pg_backend_pid()','backend_pid=backend_pid'),
 ('remove tuple xid',APP,'transaction_id=pg_current_xact_id()::text','transaction_id=transaction_id'),
 ('remove current generation',APP,'s.security_generation=g.security_generation','s.security_generation=s.security_generation'),
 ('remove revoke check',APP,'revoked_at IS NULL','true'),
 ('remove expiry check',APP,'expires_at > clock_timestamp()','true'),
 ('lock at bind before revoker',APP,'bound_grant(false)','bound_grant(true)'),
 ('remove forced RLS',APP,'ALTER TABLE "app"."customer_profiles" FORCE ROW LEVEL SECURITY;',''),
 ('wrong helper owner',APP,'ALTER FUNCTION platform_private.bind_request_context(text) OWNER TO wa_private_helper_owner;','ALTER FUNCTION platform_private.bind_request_context(text) OWNER TO wa_schema_owner;'),
 ('remove default execute revocation',BOOT,'ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;',''),
 ('remove null-safe consent',APP,'p.context_id IS DISTINCT FROM NEW.context_id','p.context_id<>NEW.context_id'),
 ('remove durable unknown noncommit',APP,"e.state<>'fenced_noncommit'","e.state<>'unknown'"),
 ('raw grant function exposure',APP,'RESET ROLE;','GRANT EXECUTE ON FUNCTION platform_private.bound_grant(boolean) TO wa_worker;\nRESET ROLE;'),
 ('forbidden worker usage',APP,'RESET ROLE;','GRANT SELECT (id) ON app.track_usage_events TO wa_worker;\nRESET ROLE;'),
 ('runtime privileged membership',BOOT,'COMMIT;','GRANT wa_private_helper_owner TO wa_worker;\nCOMMIT;'),
 ('helper writes',APP,'g:=platform_private.bound_grant(true);','UPDATE platform.database_action_grant SET revoked_at=now();\n g:=platform_private.bound_grant(true);'),
 ('helper foreign source read',APP,'RESET ROLE;','GRANT SELECT ON app.customer_profiles TO wa_private_helper_owner;\nRESET ROLE;'),
 ('PUBLIC helper execution',APP,'RESET ROLE;','GRANT EXECUTE ON FUNCTION platform_private.bind_request_context(text) TO PUBLIC;\nRESET ROLE;'),
 ('remove server mutation stamp',APP,'NEW.mutation_transaction_id:=pg_current_xact_id()::text;','NEW.mutation_transaction_id:=NEW.mutation_transaction_id;'),
 ('nullable capability membership',APP,"COALESCE(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields),false)","(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields))"),
]
FINAL='review-output/foundation-bootstrap-finalize.review.sql'
cases += [
 ('Consent prerequisite scope removed',APP,"verb='SELECT' AND model_name='ConsentPresentation' AND 'ConsentLog/'||g.target_id||'/presentation/'||row_key=ANY(g.allowed_fields)",'false'),
 ('Consent prerequisite root binding bypassed',APP,"'ConsentLog/'||g.target_id||'/presentation/'||row_key=ANY(g.allowed_fields)",'true'),
 ('Consent presentation subject check removed',APP,"IF NOT platform_private.context_subject_owner(NEW.user_id,'consent_disclosure') THEN RAISE EXCEPTION 'foreign Consent presentation principal'; END IF;",''),
 ('nonnull create predecessor contradiction',APP,'"previous_revision" BIGINT,','"previous_revision" BIGINT NOT NULL,'),
 ('create may invent predecessor',APP,"e.previous_revision IS DISTINCT FROM (CASE WHEN TG_OP='UPDATE' THEN OLD.revision ELSE NULL::bigint END)",'false'),
 ('missing new reservation CAS',APP,'NEW.revision<>OLD.revision+1','NEW.revision<OLD.revision'),
 ('age evidence update exposed',APP,'RESET ROLE;','GRANT UPDATE ("id") ON app.age_gate_blocks TO wa_app_runtime;\nRESET ROLE;'),
 ('service issuer self attests epoch',APP,'a.security_generation=g.security_generation','g.security_generation=g.security_generation'),
 ('issuer can write service source',APP,'RESET ROLE;','GRANT INSERT ON platform_private.identity_service_authorization TO wa_context_issuer;\nRESET ROLE;'),
 ('service revocation ignored',APP,'AND a.revoked_at IS NULL','AND true'),
 ('verifier gets source writes',APP,'RESET ROLE;','GRANT UPDATE (status) ON app.customer_profiles TO wa_customer_verifier;\nRESET ROLE;'),
 ('verifier exposes JSON',APP,'worker_lease_valid(work_id uuid, effect_id uuid DEFAULT NULL, allow_completed boolean DEFAULT false) RETURNS boolean','worker_lease_valid(work_id uuid, effect_id uuid DEFAULT NULL, allow_completed boolean DEFAULT false) RETURNS jsonb'),
 ('unused action purpose helper',APP,'IF NOT platform_private.protected_scope(model_name,row_key,verb) THEN RETURN false; END IF;',''),
 ('wrong provision purpose registered',APP,"'CustomerProfile',g.target_id,'provision'","'CustomerProfile',g.target_id,'wrong_purpose'"),
 ('empty Consent context unconditionally accepted',APP,"OR (NULLIF(NEW.context_id,'') IS NULL AND NOT platform_private.global_context_registered(p.action_owner,p.action,p.context_owner,p.context_kind))",''),
 ('command result version unrestricted',APP,"CHECK (result_schema_version='1')",'CHECK (true)'),
 ('extra Free command accepted on update',APP,'OR e.previous_revision IS NOT NULL','OR false'),
 ('message has no reverse commit trigger',APP,'CREATE CONSTRAINT TRIGGER exact_customer_message AFTER INSERT ON platform.runtime_outbox_message\n DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION platform_private.customer_message_commit();',''),
 ('stored lease hash used as secret',APP,"encode(sha256(decode(current_setting('wa.lease_secret',true),'hex')),'hex')=expected_hash","current_setting('wa.lease_secret',true)=expected_hash"),
 ('renewal permits expiry shortening',APP,'NEW.lease_expires_at<=OLD.lease_expires_at','false'),
 ('new effect attaches without exact verification',APP,'OR NOT platform_private.worker_effect_matches(OLD.id,NEW.effect_receipt_id,false)','OR false'),
 ('same fence unrelated semantic effect',APP,'AND e.semantic_effect_key=w.semantic_work_key','AND true'),
 ('effect from different operation',APP,'AND c.operation=e.operation','AND true'),
 ('wrong Customer creation receipt ignored',APP,"o.payload->>'sourceCreationReceipt'<>o.command_receipt_id::text",'false'),
 ('wrong current plan revision ignored',APP,"'TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields)",'true'),
 ('reservation two-step unknown bypass',APP,"OLD.state='unknown' AND NEW.state IN ('unknown','committed','released')","OLD.state='unknown' AND NEW.state IN ('active','unknown','committed','released')"),
 ('foreign operation noncommit accepted',APP,'OR e.operation<>c.operation','OR false'),
 ('NULL command noncommit accepted',APP,'e.command_receipt_id IS DISTINCT FROM NEW.command_receipt_id','e.command_receipt_id<>NEW.command_receipt_id'),
 ('foreign reservation proof accepted',APP,"OR e.subject_scope<>'RuntimeReservation:'||NEW.id::text",'OR false'),
 ('cleanup run by wrong role',FINAL,'GRANTED BY CURRENT_USER','GRANTED BY wa_schema_owner'),
 ('cleanup leaves verifier memberships',FINAL,'REVOKE wa_private_helper_owner,wa_customer_verifier,wa_track_verifier','REVOKE wa_private_helper_owner'),
 ('private epoch RLS disabled',APP,'ALTER TABLE platform_private.identity_service_authorization FORCE ROW LEVEL SECURITY;',''),
 ('same transaction successor read broken',APP,'row_transaction=pg_current_xact_id()::text','row_transaction IS NULL'),
 ('worker source verifier wrong owner',APP,'ALTER FUNCTION platform_private.worker_evidence_source_matches(text,text,bigint,text,jsonb) OWNER TO wa_track_verifier;','ALTER FUNCTION platform_private.worker_evidence_source_matches(text,text,bigint,text,jsonb) OWNER TO wa_schema_owner;'),
 ('worker reverse proof wrong transaction allowed',APP,'source_transaction IS DISTINCT FROM pg_current_xact_id()::text','false'),
 ('worker reverse proof missing exact revision',APP,'AND s.revision=committed_revision','AND true'),
 ('worker update input omits user identity',APP,"'user_id',\"user_id\",",''),
 ('linked old effect recovery removed',APP,"verb='SELECT' AND platform_private.worker_effect_matches(w.id,(row_value->>'id')::uuid,true)",'false'),
 ('attempt count can change outside claim',APP,'ELSIF NEW.fence<>OLD.fence OR NEW.attempt_count<>OLD.attempt_count','ELSIF NEW.fence<>OLD.fence'),
 ('claim accepts expired lease',APP,'OR NEW.lease_expires_at<=clock_timestamp()',''),
 ('reservation can enter released',APP,"NEW.state<>'active' OR NEW.effect_receipt_id IS NOT NULL",'false'),
 ('reservation initial guard disconnected',APP,'reservation_transition BEFORE INSERT OR UPDATE','reservation_transition BEFORE UPDATE'),
 ('uncertain reservation quantity can shrink',APP,' OR NEW."quantity" IS DISTINCT FROM OLD."quantity"',''),
]
query_scope="IF verb=ANY(ARRAY['SELECT']::text[]) AND (model_name='User' OR model_name IN ('OwnerMutationEvidence','RuntimeCommandReceipt','RuntimeOutboxMessage','RuntimeEffectReceipt')) AND platform_private.context_allows('identity_access','SH-003.v1','User',g.target_id,'owner:queryOwnerFacts')"
cases.append(('query purpose admits source update',APP,query_scope,query_scope.replace("ARRAY['SELECT']", "ARRAY['SELECT','UPDATE']")))
cases += [
 ('function grant after NOINHERIT transfer',APP,'RESET ROLE;','GRANT EXECUTE ON FUNCTION platform_private.track_atomic_valid(text,jsonb,jsonb) TO wa_worker;\nRESET ROLE;'),
 ('managed function revoke after transfer',APP,'RESET ROLE;',"DO $late$ BEGIN EXECUTE 'REVOKE ALL ON ALL FUNCTIONS IN SCHEMA platform_private FROM anon'; END $late$;\nRESET ROLE;"),
 ('foreign complete verifier claim accepted',APP,'actual_value IS NULL OR NOT (n @> actual_value)','false'),
 ('direct atomic port skips actual source',APP,'OR NOT platform_private.worker_source_claim_valid(model_name,n)','OR false'),
 ('direct relationship port skips caps',APP,'IF NOT platform_private.worker_row_capabilities(model_name,row_value,verb) THEN RETURN false; END IF;',''),
 ('actual source from another transaction',APP,'s.mutation_transaction_id=pg_current_xact_id()::text','true'),
 ('caller-only selection predecessor',APP,"v.evidence_body->'prior'->>'subscriptionId'=prior_value->>'subscription_id'",'true'),
 ('direct effect skips canonical source',APP,"IF NOT platform_private.worker_track_allowed('RuntimeOutboxMessage',jsonb_build_object('id',o.id,'producer_owner',o.producer_owner),'SELECT') THEN RETURN false; END IF;",''),
]
application=(ROOT/APP).read_text(encoding='utf8')
reservation_acl=next(line for line in application.splitlines() if line.startswith('GRANT UPDATE') and '"platform"."runtime_reservation" TO wa_app_runtime' in line)
cases.append(('runtime terminal effect column removed',APP,reservation_acl,reservation_acl.replace(',"effect_receipt_id"','')))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--shard',help='Optional independent temporary-copy shard INDEX/TOTAL (zero based); default runs every case')
args=parser.parse_args();default_total=len(cases)+2
if args.shard:
 try:index,total=map(int,args.shard.split('/'))
 except ValueError:parser.error('shard must be INDEX/TOTAL')
 if not 0<=index<total<=8:parser.error('invalid shard range')
 cases=cases[index::total]
results=[]
with tempfile.TemporaryDirectory(prefix='wa-p0c03-offline-') as folder:
 target=Path(folder).resolve();assert target.parent==Path(tempfile.gettempdir()).resolve()
 paths=set(manifest['preserved_reviewed_inputs_sha256'])|set(manifest.get('revised_inputs_sha256',{}))|set(manifest['outputs_sha256'])
 paths|={'review-output/foundation-bootstrap-finalize.review.sql'}
 paths|={'context/reconciliation/foundation-sql-verifier-access.json','context/reconciliation/foundation-sql-scope-policy.json'}
 paths|={str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'context/reconciliation').glob('foundation-sql-draft-*.json')}
 for p in paths:
  dest=target/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dest)
 for label,path,before,after in cases:
  original=(target/path).read_text(encoding='utf8');assert before in original,label
  (target/path).write_text(original.replace(before,after),encoding='utf8')
  # Fingerprints deliberately ignored: semantic assertions must detect mutation.
  try:r=CHECK(target,verify_fingerprints=False);rejected=bool(r['errors']);why=r['errors'][:2]
  except Exception as e:rejected=False;why=['unexpected checker failure '+str(e)]
  results.append({'case':label,'rejected_semantically':rejected,'evidence':why})
  (target/path).write_text(original,encoding='utf8')
 # Deliberately coherent SQL + evidence mutation. Original permission oracle must win.
 path='context/reconciliation/foundation-sql-draft-access.json';original=(target/path).read_text();app=(target/APP).read_text()
 acl=json.loads(original);acl.append({'model':'TrackUsageEvent','role':'wa_worker','operation':'SELECT','fields':['id'],'columns':['id']})
 (target/path).write_text(json.dumps(acl));(target/APP).write_text(app+'\nGRANT SELECT ("id") ON "app"."track_usage_events" TO wa_worker;\n')
 r=CHECK(target,verify_fingerprints=False)
 results.append({'case':'coherent forbidden usage SQL and ACL map','rejected_semantically':any('Track worker privilege broadening' in x or 'worker usage permission' in x for x in r['errors']),'evidence':r['errors'][:3]})
 (target/path).write_text(original);(target/APP).write_text(app)
 path='context/reconciliation/foundation-sql-draft-replay-map.json';original=(target/path).read_text(encoding='utf8');replay=json.loads(original)
 next(t for t in replay['tests'] if t['id']=='P0C-TABLE-PrivacyOwnerReceipt-ALLOW')['blocking_review_issues']=[]
 (target/path).write_text(json.dumps(replay),encoding='utf8');r=CHECK(target,verify_fingerprints=False)
 results.append({'case':'gated Privacy positive loses replay blockers','rejected_semantically':any('replay blocker' in e for e in r['errors']),'evidence':r['errors'][:3]})
 (target/path).write_text(original,encoding='utf8')
result={'status':'PASS' if all(r['rejected_semantically'] for r in results) else 'FAIL','cases':len(results),'default_total_cases':default_total,'shard':args.shard,'scope':'OFFLINE_SQL_SOURCE_MUTATIONS_FINGERPRINT_CHECK_DISABLED','database_contacted':False,'sql_executed':False,'results':results}
print(json.dumps(result,indent=2));raise SystemExit(result['status']!='PASS')
