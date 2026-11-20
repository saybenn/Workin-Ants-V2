"""Pure immutable INSTALL review transport. Authority remains protocol6c.

No filesystem, process, clock, network, approval issuance or inferred PASS.
"""
import hashlib,json,re,uuid
READY='independent-review-ready.json'
PROOF='rollback-proof-for-review.json'
SNAPSHOT='independent-review-child-snapshot.json'
IDENTITY='independent-review-outer-identity.json'
PLAN='install-coordinator-run-plan.json'
APPROVAL='independent-recovery-approval.json'
TIMEOUT=240
CAPS={READY:65536,PROOF:65536,SNAPSHOT:16*1024*1024,IDENTITY:65536,PLAN:1024*1024,APPROVAL:8192}
READY_SCHEMA='workinants.install-independent-review-ready.v1'
IDENTITY_SCHEMA='workinants.install-independent-review-outer-identity.v1'
PLAN_FIELDS={'schema','scope','run_id','source_commit','source_tree','packet_sha256','reviewed_packet_sha256','source_modules_sha256','targets','histories','credential_bundle'}
SNAPSHOT_FIELDS={'schema','status','current_stage','targets','subsequent_cases_stopped','limits','run_id','source_commit','source_tree','packet_sha256','reviewed_plan_sha256'}
SNAPSHOT_LIMITS={'posture':'D','whole_cases':'NOT_PROMOTED','full_native_acl_and_ledger_comparison':'PENDING_OUTER_OPERATOR','451_register':'NOT_PROMOTED','raw_output_retained':False}
VARIANTS=('canonical','division_failure','late_function_grant')
OPERATORS=('execute_local_f0_install_controls_20261119_review_ready_v3.py','local_f0_install_controls_operation_steps_review_ready_v3.py','prepare_local_f0_install_controls_plan_review_ready_v3.py','check_local_f0_install_controls_operation_review_ready_v3.py','pin_local_f0_install_controls_plan_20261119_review_ready_v3.py')
SQL={'canonical':'5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad','division_failure':'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c','late_function_grant':'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f'}
class Held(ValueError):pass
def need(ok,code):
    if not ok:raise Held(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode('utf8')
def exact(a,b):return canonical(a)==canonical(b)
def decode(raw,canonical_required=False):
    need(type(raw) is bytes,'JSON_BYTES_REQUIRED')
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'DUPLICATE_JSON_FIELD');out[k]=v
        return out
    try:value=json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Held('NONFINITE_JSON')))
    except (UnicodeError,json.JSONDecodeError):raise Held('INVALID_JSON') from None
    if canonical_required:need(raw==canonical(value),'CANONICAL_JSON_REQUIRED')
    return value
def hash_(v):need(type(v) is str and re.fullmatch('[0-9a-f]{64}',v),'HASH_REQUIRED');return v
def checkpoint(v):need(type(v) is str and re.fullmatch('[0-9a-f]{40}',v),'CHECKPOINT_REQUIRED')
def run_(v):
    try:ok=type(v) is str and str(uuid.UUID(v))==v and uuid.UUID(v).version==4
    except (ValueError,AttributeError):ok=False
    need(ok,'RUN_UUID_REQUIRED')
def identity(value):
    need(type(value) is dict and set(value)=={'schema','run_id','source_commit','source_tree','packet_sha256','child_run_plan_sha256','operator_sources_sha256','targets'} and value['schema']==IDENTITY_SCHEMA,'OUTER_IDENTITY_SCHEMA')
    run_(value['run_id']);checkpoint(value['source_commit']);checkpoint(value['source_tree'])
    for k in ('packet_sha256','child_run_plan_sha256'):hash_(value[k])
    pins=value['operator_sources_sha256'];need(type(pins) is dict and set(pins)==set(OPERATORS),'OPERATOR_SOURCE_MAP')
    for h in pins.values():hash_(h)
    targets=value['targets'];need(type(targets) is dict and set(targets)==set(VARIANTS),'THREE_TARGETS')
    for k,v in targets.items():need(type(v) is dict and set(v)=={'container_id','source_sql_sha256'} and v['source_sql_sha256']==SQL[k],'TARGET_IDENTITY');hash_(v['container_id'])
    need(len({v['container_id'] for v in targets.values()})==3,'DISTINCT_CIDS');return value
def ready(value):
    need(type(value) is dict and set(value)=={'schema','run_id','source_commit','source_tree','packet_sha256','container_id','source_sql_sha256','rollback_proof_sha256','closed_child_snapshot_sha256','outer_identity_sha256','child_run_plan_sha256','review_timeout_seconds'} and value['schema']==READY_SCHEMA,'READY_SCHEMA')
    run_(value['run_id']);checkpoint(value['source_commit']);checkpoint(value['source_tree'])
    for k in ('packet_sha256','container_id','source_sql_sha256','rollback_proof_sha256','closed_child_snapshot_sha256','outer_identity_sha256','child_run_plan_sha256'):hash_(value[k])
    need(type(value['review_timeout_seconds']) is int and value['review_timeout_seconds']==TIMEOUT and value['source_sql_sha256']==SQL['division_failure'],'READY_SCOPE');return value
def bindings(raws,expected=None):
    need(type(raws) is dict and set(raws)=={READY,PROOF,SNAPSHOT,IDENTITY,PLAN},'CLOSED_IMMUTABLE_INPUTS')
    for name,raw in raws.items():need(type(raw) is bytes and len(raw)<=CAPS[name],'BOUNDED_IMMUTABLE_INPUT')
    r=ready(decode(raws[READY],True));i=identity(decode(raws[IDENTITY],True));p=decode(raws[PROOF],True);s=decode(raws[SNAPSHOT]);plan=decode(raws[PLAN])
    need(type(p) is dict and set(p)=={'schema','run_id','source_commit','source_tree','packet_sha256','container_id','source_sql_sha256','failure','failed_ledger','application_inventory','original_grantor_finalized','disposition'},'CLOSED_ROLLBACK_PROOF_SCHEMA')
    need(type(s) is dict and set(s)==SNAPSHOT_FIELDS and s['schema']=='workinants.install-controls-results.v1' and s['status']=='RUNNING' and exact(s['limits'],SNAPSHOT_LIMITS),'CLOSED_RUNNING_CHILD_SNAPSHOT')
    need(type(plan) is dict and set(plan)==PLAN_FIELDS and plan['scope']=='FINITE_INSTALL_HISTORY_AND_AUTHORITY_CONTROLS','CLOSED_CHILD_PLAN_SCHEMA')
    for field,name in (('rollback_proof_sha256',PROOF),('closed_child_snapshot_sha256',SNAPSHOT),('outer_identity_sha256',IDENTITY),('child_run_plan_sha256',PLAN)):need(r[field]==sha(raws[name]),'IMMUTABLE_HASH_MISMATCH')
    for k in ('run_id','source_commit','source_tree','packet_sha256'):
        need(r[k]==i[k]==p.get(k)==s.get(k)==plan.get(k),'IMMUTABLE_RUN_IDENTITY')
        if expected is not None:need(type(expected) is dict and expected.get(k)==r[k],'EXPECTED_RUN_IDENTITY')
    need(i['child_run_plan_sha256']==r['child_run_plan_sha256'] and r['container_id']==i['targets']['division_failure']['container_id']==p.get('container_id') and r['source_sql_sha256']==p.get('source_sql_sha256'),'IMMUTABLE_TARGET_IDENTITY')
    need(plan.get('schema')=='workinants.install-controls-run.v1' and type(plan.get('targets')) is dict and set(plan['targets'])==set(VARIANTS),'CHILD_PLAN_SCHEMA')
    for v in VARIANTS:need(plan['targets'][v].get('container_id')==i['targets'][v]['container_id'],'PLAN_CID_IDENTITY')
    need(p.get('schema')=='workinants.install-rollback-observation.v1' and p.get('disposition')=='PENDING_INDEPENDENT_REVIEW' and p.get('original_grantor_finalized') is True,'ACTUAL_ROLLBACK_PROOF_REQUIRED')
    inv=p.get('application_inventory');need(type(inv) is dict and set(inv)=={'relations','functions','types','enums','other_clients'} and all(type(v) is int and v==0 for v in inv.values()),'ACTUAL_ZERO_INVENTORY_REQUIRED')
    need(s.get('current_stage')=='INDEPENDENT_ROLLBACK_REVIEW_REQUIRED' and s.get('reviewed_plan_sha256')==r['child_run_plan_sha256'] and s.get('subsequent_cases_stopped') is False,'CLOSED_HOLD_SNAPSHOT_REQUIRED')
    target=s.get('targets',{}).get('division_failure',{});need(exact(target.get('inventory'),inv) and exact(target.get('failure_verdict'),p.get('failure')) and exact(target.get('ledger',{}).get('rows'),[p.get('failed_ledger')]),'ACTUAL_CHILD_OBSERVATIONS_REQUIRED')
    need(exact(target.get('original_cleanup'),{'original_grantor':'postgres','temporary_memberships':0,'leaf_create':False,'other_clients':0}) and exact(target.get('review_hold'),{'proof_sha256':r['rollback_proof_sha256'],'decision':'PENDING_INDEPENDENT_REVIEW','timeout_seconds':240}),'ORIGINAL_AUTHORITY_HOLD_REQUIRED')
    return {'ready':r,'proof':p,'snapshot':s,'identity':i,'plan':plan}
