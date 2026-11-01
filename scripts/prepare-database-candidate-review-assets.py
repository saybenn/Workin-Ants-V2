#!/usr/bin/env python3
"""Pure offline review-asset generation; no database, SQL generation or shell calls."""
import json,pathlib,re,hashlib,runpy
root=pathlib.Path(__file__).resolve().parents[1];rec=root/'context/reconciliation'; inv=json.loads((rec/'greenfield-model-security-inventory.json').read_text());rv=inv['physical_candidate_review']; rows=rv['rows']; byname={x['model']:x for x in rows}
parse=runpy.run_path(str(root/'scripts/prepare-database-candidate.py'))['parse']; blocks=parse((root/'prisma/review/physical-candidate.prisma').read_text()); enums={n:[x.strip() for x in b['body'].splitlines() if re.match(r'^\s*\w+\s*$',x)] for n,b in blocks.items() if b['kind']=='enum'}
def field_schema(f):
 t=f['type']; base=t.rstrip('?[]'); a=f['attributes']
 if base in enums:d={'type':'string','enum':enums[base]}
 elif base=='Boolean':d={'type':'boolean'}
 elif base=='Int':d={'type':'integer'}
 elif base=='Float':d={'type':'number'}
 else:d={'type':'string'}
 if '@db.Uuid' in a:d={'type':'string','format':'uuid'}
 if base=='DateTime':d={'type':'string','format':'date-time'}
 if base=='BigInt':d={'type':'string','pattern':'^-?[0-9]+$','description':'Internal integer token encoding only; public owner tokens remain opaque'}
 if t.endswith('[]'):d={'type':'array','items':d}
 if t.endswith('?'):d={'anyOf':[d,{'type':'null'}]}
 return d
def pk(row):
 single=[f['name'] for f in row['candidate_fields'] if '@id' in f['attributes']]
 if single:return single
 for s in row['identifiers_and_indexes']:
  m=re.match(r'@@id\(\[([^\]]+)\]',s)
  if m:return [x.strip() for x in m[1].split(',')]
 raise Exception(row['model'])
defs={}
for row in rows:
 pks=pk(row);selected={}
 for f in row['candidate_fields']:
  t=f['type'].rstrip('?[]');n=f['name']
  if t not in blocks or blocks[t]['kind']=='enum':
   if n in pks or t in enums or re.search(r'(Revision|Generation|Cents|Quantity|Count|Hash|Digest)$',n) or n in ['revision','generation','fence','userId','currency','sourceOwner','sourceId','sourceFactId','sourceFactRevision','periodStart','periodEnd','acceptedAt','semanticEffectKey']:
    selected[n]=field_schema(f)
 # Explicitly no raw body/notes/resume/email/phone/endpoint/credentials or arbitrary JSON.
 key_fields={f['name']:field_schema(f) for f in row['candidate_fields'] if f['name'] in pks}
 defs[row['model']]={'type':'object','additionalProperties':False,'required':['schema','owner','model','primaryKey','committed','decisionRef'],'properties':{'schema':{'const':'database-owner-evidence.v1'},'owner':{'const':row['source_owner']},'model':{'const':row['model']},'primaryKey':{'type':'object','additionalProperties':False,'required':pks,'properties':key_fields},'prior':{'type':['object','null'],'additionalProperties':False,'required':list(selected),'properties':selected},'committed':{'type':'object','additionalProperties':False,'required':list(selected),'properties':selected},'decisionRef':{'type':'string','minLength':1}}}
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:workinants:database-review:owner-evidence:v1','description':'Review-only closed minimized source-evidence shapes. Not a replacement SH wire schema. SQL checks bind actual PK/revision/transaction and selected source values; owner protected snapshots remain separate. Runtime serializer/DB checks are NOT RUN.','oneOf':[{'$ref':'#/$defs/'+r['model']} for r in rows],'$defs':defs}
path=root/'contracts/database-review';path.mkdir(parents=True,exist_ok=True);(path/'owner-mutation-evidence.v1.schema.json').write_text(json.dumps(schema,indent=2)+'\n', encoding='utf-8', newline='\n')
# R078's existing owner command gets a review-only storage shape, not a new SH.
def closed(properties):
 return {'type':'object','additionalProperties':False,'required':list(properties),'properties':properties}
identifier={'$ref':'urn:workin-ants:types:v1#/$defs/Id'}
opaque={'$ref':'urn:workin-ants:types:v1#/$defs/Token'}
free_input=closed({'sourceOwner':{'const':'customer_buyer_profile'},'userId':identifier,'track':{'const':'customer'},'customerProfileId':identifier,'sourceCreationRevision':opaque,'sourceCreationReceipt':identifier,'semanticKey':{'type':'string','minLength':1}})
free_result=closed({'outcome':{'enum':['enrolled','already_enrolled','conflict','denied','unavailable']},'selectionRevision':{'anyOf':[opaque,{'type':'null'}]},'receipt':identifier})
wire={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:workinants:database-review:foundation-payloads:v1','description':'Review-only Customer branch of existing R078; service identity is trusted side-channel, never asserted by payload. No canonical SH changed. Outcome invariants and receipt coherence also require SQL-07/08/12.','\u0024defs':{'assignDefaultFreeTrackCustomerCommand':free_input,'assignDefaultFreeTrackCustomerResult':free_result},'external_schema_registry':['contracts/shared/types.v1.schema.json','contracts/shared/SH-004.v1.schema.json','contracts/shared/SH-114.v1.schema.json']}
(path/'foundation-payloads.v1.schema.json').write_text(json.dumps(wire,indent=2)+'\n', encoding='utf-8', newline='\n')
json_boundaries=[]
for row in rows:
 for f in row['candidate_fields']:
  if f['type'].rstrip('?')!='Json':continue
  item={'model':row['model'],'field':f['name'],'owner':row['source_owner'],'stage':row['stage'],'nullable':f['type'].endswith('?'),'admission':'DENY_NON_NULL_UNTIL_EXACT_CLOSED_SCHEMA_AND_OWNER_STAGE_REVIEW','schemas':[],'truth':'No ownership, lifecycle, idempotency, currentness, money or reservation invariant may exist only in this value'}
  if row['stage']=='F0_FOUNDATION':
   item['admission']='NULL_ONLY_IN_INITIAL_CUSTOMER_SLICE'
  if row['model']=='OwnerMutationEvidence':
   item.update(admission='EXACT_MODEL_EVIDENCE_SCHEMA_AND_SOURCE_COLUMN_COMPARISON',schemas=['contracts/database-review/owner-mutation-evidence.v1.schema.json'])
  if row['model']=='RuntimeCommandReceipt':
   item.update(admission='EXACT_REGISTERED_OWNER_RESPONSE_VARIANT_ONLY',schemas=['contracts/shared/SH-004.v1.schema.json#/$defs/response','contracts/shared/SH-114.v1.schema.json#/$defs/response','contracts/database-review/foundation-payloads.v1.schema.json#/$defs/assignDefaultFreeTrackCustomerResult'])
  if row['model']=='RuntimeOutboxMessage':
   item.update(admission='MESSAGE_KIND_NAME_AND_SCHEMA_BINDING_REQUIRED',schemas=['contracts/shared/types.v1.schema.json#/$defs/EventPayload_customer_lifecycle_changed_v1','contracts/database-review/foundation-payloads.v1.schema.json#/$defs/assignDefaultFreeTrackCustomerCommand'])
  item['activation_gate']='Nonnullable deferred JSON blocks that table migration/activation until exact closed schema is recorded; nullable deferred fields remain null. Future schemas need owner review, never an arbitrary-json fallback.'
  json_boundaries.append(item)
(rec/'database-candidate-json-boundaries.json').write_text(json.dumps({'status':'REVIEW_ONLY_NOT_ENFORCED','boundaries':json_boundaries,'f0_rule':'Only the three explicitly registered evidence/result/outbox paths accept JSON in the first Customer slice; other F0 JSON stays null, including JSON-valued Track entitlements. Native typed benefits are sufficient for default-Free fixtures.','runtime_validation':'NOT_RUN'},indent=2)+'\n', encoding='utf-8', newline='\n')
fixtures={'status':'SYNTHETIC_FIXTURE_SPEC_NOT_LOADED','users':{'A':{'id':'11111111-1111-4111-8111-111111111111','email':'actor-a@workinants.invalid'},'B':{'id':'22222222-2222-4222-8222-222222222222','email':'actor-b@workinants.invalid'}},'customers':{'A':'33333333-3333-4333-8333-333333333333','B':'44444444-4444-4444-8444-444444444444'},'organizations':{'A':'55555555-5555-4555-8555-555555555555','B':'66666666-6666-4666-8666-666666666666'},'clock':'2026-10-27T12:00:00Z','security_generation':'7','profile_creation_revision':'0','scope':'NONPRODUCTION_DRAFT_POLICY_ONLY','free_plan':{'track':'customer','key':'free-fixture','version':'test-v1','billingModel':'free','status':'active','provider':'none'},'active_paid_plan':'Fixture only: subscription_plus_commission plan with future paid-through instant and provider identity; no vendor call or actual paid subscription','authority_grants':'Created by wa_context_issuer test attestor for named source/user/action/target/field set; synthetic secret generated at execution, never committed','retention':'No production period or legal approval inferred; no automatic deletion of managed/old data'}
(root/'tests/database').mkdir(parents=True,exist_ok=True);(root/'tests/database/candidate-fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n', encoding='utf-8', newline='\n')
corrections=runpy.run_path(str(root/'scripts/database-candidate-correction-rules.py'))
tests=[]
def test(id,phase,requirement,setup,action,expect,stage='F0_FOUNDATION'):
 tests.append({'id':id,'phase':phase,'stage':stage,'requirement':requirement,'setup':setup,'action':action,'expected':expect,'status':'NOT_RUN'})
for r in rows:
 table=r['candidate_table'];stage=r['stage'];purpose=r['source_owner']+'.registered_owner_action'
 setup,action,expected,negative=corrections['table_cases'](r,pk(r))
 test('P0C-TABLE-'+r['model']+'-ALLOW','P0-C',r['sql_companion'],setup,action,expected,stage)
 test('P0C-TABLE-'+r['model']+'-DENY','P0-C',r['sql_companion'],negative,'Run each explicit direct_denials_by_role attempt with that actual login; also deny foreign/missing/stale context, unregistered worker actions, field reassignment and immutable tuple changes. No helper-owner LOGIN/SET ROLE is used.','42501 or specified nonenumerating filtered SELECT; no denied row/effect or private grant disclosure',stage)
for id,req,setup,action,expect in [
('P0C-INSTALL-01',['DBP-06','DBP-10'],'Approved immutable SQL history and captured disposable identity; empty application state, provider-managed stand-ins explicitly listed','Apply only selected F0 history with dedicated migrator, then apply again','First deploy completes; second deploy has zero pending work and unchanged applied checksums'),
('P0C-INSTALL-02',['DBP-10'],'Disposable clone only; injected failure before initial transactional migration COMMIT','Run approved failed migration, inspect app catalog/ledger and perform reviewed rollback/forward-repair procedure','Failure is nonzero and not accepted; app transaction rolled back; ledger failure preserved until actual verified repair'),
('P0C-CATALOG-01',['DBP-06','DBP-07','DBP-08'],'Post-install schema-only catalog under read-only collector','Compare every selected table/column/type/enum/default/nullability/PK/FK/check/index/view/function/trigger/owner/grant/policy/extension/default ACL against approved physical+SQL manifest','No unexpected application object or privilege, missing invariant or fingerprint drift; managed differences explicitly excluded and independently reviewed'),
('P0C-CTX-01',['SQL-02','SQL-06'],'Separate issuer login plus two runtime/worker READ COMMITTED connections; issue nonnullable immutable tuple before each bind','Exercise full ROLLBACK after bind; SAVEPOINT then bind then ROLLBACK TO SAVEPOINT then full rollback; a failed bind; commit then same-pool reuse; different backend, same backend/new xid, and wrong isolation. Try every old token in a later transaction, then obtain a freshly authorized tuple grant for the same semantic command key','Old tuple survives bind rollback in issuer-owned committed row and never authorizes a later xid; no runtime/helper grant writes; fresh grant succeeds. Same-live-transaction rebind is idempotent'),
('P0C-CTX-02',['SQL-02','SQL-06'],'Valid grant issued before source transaction','Change security/source generation or revoke grant before the sensitive effect','Current recheck denies stale grant; no source mutation or protected disclosure'),
('P0C-PRIV-01',['SQL-01','SQL-06'],'Actual issuer/runtime/worker logins and NOLOGIN helper owner; browser role simulation separately labeled','Issuer exercises authorized INSERT/own SELECT/one-way revoke only; deny issuer scope/tuple rewrite and source writes. Runtime/worker try direct grant SELECT/INSERT/UPDATE/DELETE, TRUNCATE, CREATE and SET ROLE issuer/helper/owner. Deny helper grant writes and browser helper EXECUTE; then run both named helper paths','All forbidden operations denied; exact issuer and SELECT-only helper operations succeed; runtime/worker receive only helper results, never raw grants'),
('P0C-BOOT-01',['SQL-06','SQL-08'],'Empty approved infrastructure plus synthetic Identity actor','Issuer issues context; runtime appends own proof and pending work; optional Ops sink unavailable','No recursive proof/outbox/bootstrap dependency; denied protected read remains possible without Ops startup'),
('P0C-ATOMIC-01',['SQL-08'],'Synthetic existing actor and new Customer','Try source write without receipt/history/intents, then coherent single-transaction write','Missing piece rejects COMMIT; positive transaction commits one source, one history and each required intent'),
('P0C-UNIQUE-01',['SQL-07'],'One scoped command/effect receipt and a different owner/scope','Insert same scoped key twice, changed fingerprint, then identical text key under other permitted scope','Duplicate source/economic effect blocked; conflicting meaning rejected; distinct legitimate scope permitted'),
('P0C-CAS-01',['SQL-03'],'Two connections with same expected Customer revision','Compete on owner mutation with current-context evidence','Exactly one wins; loser conflicts; one retained next revision'),
('P0C-IMMUTABLE-01',['SQL-04','SQL-05'],'Stored exact per-user/action/context test Consent and retained F0 source/runtime-effect proof','Accept coherent presentation; reject cross-user/content/action/context/rendered-hash and NULL-context wildcard substitutions; verify same-key identical replay and changed-fingerprint conflict. Reject rewrite/delete; append valid same-user withdrawal. Agreement-signature and financial-ledger branches wait for later commerce schema','Composite FK and SQL-05 reject mismatches and tampering; minimized exact proof and append-only withdrawal retained; absent later feature is not an F0 failure'),
('P0C-TRACK-01',['SQL-12'],'Explicit Free selection and another active paid-through fixture','Try wrong profile/user/track, second current selection and delayed Free replacing paid','Mismatch/duplicate/downgrade denied; same original enrollment receipt remains valid'),
('P0C-EVIDENCE-01',['SQL-08','SQL-16'],'Closed per-model evidence shapes and known source values','Insert extra JSON keys/private body, wrong enum/PK/revision or a false transaction ID','Rejected; approved minimal evidence accepted without copying personal content'),
('P0C-RESTORE-01',['DBP-03','DBP-11','SQL-14'],'Separate authorized synthetic disposable restore target and tested artifact checksum','Restore approved backup, reapply privacy/restriction generations before any service read','Exact restoration accounted for; tombstoned generation never served; missing backup/restore fact remains blocked'),
('P0C-AUTORLS-01',['DBP-07','DBP-08'],'Disposable copy of captured public event-trigger setup only; provider objects labeled emulated','After separate environment-control approval, test current DDL-role CREATE TABLE/AS under public, then exact-function EXECUTE revocation proposal and repeat; do not expose Data API','Legitimate auto-RLS still works; ordinary direct unauthorized invocation denied; differences from hosted behavior remain unqualified')]:test(id,'P0-C',req,setup,action,expect)
for id,setup,action,expect in [
('P0D-REPLAY-01','Customer resolve/provision owner command SH-004 plus shared SH-044/114','Repeat same key/body and changed-body reuse','Original receipt replayed; changed fingerprint conflicts; one Customer and one default-Free intent'),
('P0D-CRASH-01','Committed source/outbox; worker claims current fence','Crash before/after consumer commit, lose acknowledgment and reclaim','No lost durable work; replay uses same semantic effect; one actual Track enrollment'),
('P0D-FENCE-01','Worker A lease expires; worker B reclaims with higher fence','A attempts late source/consumer effect and B processes current work','A cannot commit late; B commits at most once; no expiration-only reservation release'),
('P0D-DOWNSTREAM-01','Track unavailable or original result unknown','Retry/reconcile same assignDefaultFreeTrack.v1 identity; inspect source Customer','Customer remains created; pending intent retained; no inferred Free, paid downgrade or duplicated effect'),
('P0D-ROLLBACK-01','New Customer command about to write proof/outbox','Inject failure within owner transaction','Source/history/command result/outbox roll back together; safe original-key retry later succeeds'),
('P0D-SOURCE-REVOKED-01','Pending original enrollment intent','Archive/revoke source before retry; change current security/consent/Hold facts where relevant','Fresh owner fact check fails closed; no new enrollment inferred; terminal explained disposition or pending reconciliation retained')]:test(id,'P0-D',['SH-004','SH-044','SH-046','SH-047','SH-114','WA-R078'],setup,action,expect)
for id,req,action,expect in [
('P0E-ACTOR-01',['SH-001','SH-002','SH-008'],'Exercise actual credential/provider/current member/source authorization and server-versus-RLS parity','Untrusted actor/role/source claims and stale scopes denied; valid user owner action works'),
('P0F-EXECUTOR-01',['DBP-11','SQL-14'],'Run actual field/serializer/provider/export/erasure/backup executors on synthetic data','Complete owner accounting and exact bytes; unsupported/unknown provider disposition never reported complete')]:test(id,'P0-E' if id.startswith('P0E') else 'P0-F',req,'Actual qualified ports and account/provider scope after their separate entry conditions',action,expect,'LATER_PHASE')
plan={'status':'SPECIFIED_NOT_RUN','scope':'Executable environment/actions/fixtures/expectations plan only; no database harness executed under this directive','disposable_environment':{'provider':'LOCAL_DISPOSABLE_POSTGRES_PROPOSED','postgres_version':'17.11','immutable_image_digest':'NOT_RESOLVED_NOT_PROVISIONED','synthetic_only':True,'old_project_forbidden':'sdceenkakajslwpctbgl','hosted_fresh_project_read_only_until_separate_execution_approval':'lyalfdmfheevpahywuhv','limitations':['Historical Work tool absence is not current Windows inventory; Docker was observed locally on 2026-10-30, but no disposable identity/image/DDL/execution is authorized','Local provider-managed Auth/Storage/Realtime/default-role/extension/event-trigger emulation is not hosted Supabase parity','Image digest, backup/restore method and exact disposable identity must be approved/resolved before execution']},'tests':tests,'all_tests_not_run':True,'first_p0d_owner':'customer_buyer_profile','first_p0d_consumer':'track_subscription_entitlement','normal_network_delivery':'AT_LEAST_ONCE','business_effect_goal':'NO_REPEATED_COMMITTED_EFFECT','provider_sandbox_or_real_account_actions_authorized':False}
(rec/'database-candidate-tests.json').write_text(json.dumps(plan,indent=2)+'\n', encoding='utf-8', newline='\n')
# A human route into every model, preserving exact detailed fields in the canonical JSON.
lines=['# Physical model disposition ledger — review only','',f'All 177 original models accounted for; {len(rows)} staged candidate models, {rv["foundation_model_count"]} in the F0 parent-FK closure. Exact field/FK/index/change/evidence/access rows are in greenfield-model-security-inventory.json → physical_candidate_review. No SQL is generated or executed.','']
for owner in sorted({r['source_owner'] for r in rows}):
 lines+=['## '+owner,'']
 for r in [x for x in rows if x['source_owner']==owner]:
  lines += ['### '+r['model'],'',r['purpose']+'.','',f'- Object: `{r["candidate_table"]}`. Class: {r["classification"]}. Stage: {r["stage"]}.',f'- Stable key: {", ".join(pk(r))}. Foreign keys: '+(', '.join(f['name']+' → '+f['type'] for f in r['foreign_relationships']) or 'none; typed registered descriptor scope is explicit in the SQL companion')+'.', '- Physical changes: '+'; '.join(dict.fromkeys(r['changes']))+'.','- Required SQL/access checks: '+', '.join(r['sql_companion'])+'. Owner Privacy executor: '+r['privacy_executor']+'.','']
(rec/'database-candidate-model-ledger.md').write_text('\n'.join(lines).rstrip()+'\n', encoding='utf-8', newline='\n')
# Actual source files read by the review: include hash and selected model/ruling context,
# not a fabricated claim that every historical architecture document was re-adjudicated.
cat=json.loads((root/'context/shared/contracts/contract-catalog.json').read_text())['contracts'];paths={'prisma/schema.prisma','context/architecture.md','context/build-plan.md','context/reconciliation/platform-architecture-rulings.md','context/shared/contracts/contract-catalog.json','context/reconciliation/launch-scope-baseline.md'}
for r in rows:paths.update(r['authority'])
source_index=[]
for name in sorted(paths):
 p=root/name
 if not p.exists():raise ValueError(name)
 text=p.read_text();source_index.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'review_mode':'Source structure/owner contract and applied-ruling review; historical unresolved headings do not supersede rulings','model_mentions':[r['model'] for r in rows if re.search(r'\b'+re.escape(r['model'])+r'\b',text)]})
(rec/'database-candidate-source-review.json').write_text(json.dumps({'status':'REVIEW_INPUTS_PINNED','source_checkpoint':'a067dd52d14f6313e4f350a33750c3486426d91f','inputs':source_index},indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({'tests_specified':len(tests),'tests_executed':0,'closed_model_evidence_shapes':len(defs),'source_files':len(source_index)}))
