"""Pure Read13 source packet preparation; no database/process/network boundary."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
from remaining_app_read13_protocol import (PLAN_SHA,ACK_SHA,PEER_SHA,APPLICATION_SHA,SOURCE_ROOT,PLAN_PATH,
 FINITE,need,sha,digest,canonical,quote,materialize,render,unique_json,value_sql)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review-output/remaining-app-read13-rehearsal'
FIXTURE_RUN_ID='0b7c519e-68be-4c44-ac42-83adcfe0def4'
NEW=('scripts/prepare-remaining-app-read13-rehearsal.py','scripts/remaining_app_read13_protocol.py',
 'scripts/check-remaining-app-read13-rehearsal.py','scripts/check-remaining-app-read13-coordinator.py',
 'scripts/sql-review/run-remaining-app-read13-rehearsal.py','scripts/sql-review/REMAINING-APP-READ13-REHEARSAL.md')
HELPERS=('scripts/sql-review/run-scoped-read-companion-rehearsal.py','scripts/scoped_read_companion_protocol.py',
 'scripts/sql-review/run-context-control-rehearsal.py','scripts/sql-review/run-first-rehearsal.py',
 'scripts/sql-review/run-local-f0-migrate.py','scripts/sql-review/rehearsal-diagnostics.py',
 'scripts/prepare-local-f0-history.py','scripts/sql-review/collect_native_catalog.sql')
STRUCTURAL_INPUTS={'context/reconciliation/foundation-sql-draft-models.json':'d04bf44bd67dceda35199fd1ff1e494eed3016e80d180144018e879f5aee778d',
 'context/reconciliation/foundation-sql-draft-access.json':'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea',
 'context/reconciliation/local-f0-assertions.json':'7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558'}
OFFLINE_ONLY_INPUTS={'scripts/check-app-write-two-control-coordinator.py':'66e5f78cb22bedfeb6eb6c95b5c502291b0c732080d93e91256aee78e09d57eb',
 'scripts/app_write_two_control_protocol.py':'525a84cc6e4acc3a732bdf1c351b2b85e4056857afcef939ab69e9c0b8ff55be',
 'scripts/prepare-app-write-two-control-rehearsal.py':'ce6b5861a22e1e4463ba1a08755336d15a4b6b73bba7ff7c0702cdd919613a62',
 'scripts/sql-review/run-app-write-two-control-rehearsal.py':'c947fe02f067e6cea4c97635f0dc9f96ab1db27bfbc9fe07ea4eeb5ad0e1ceb6',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-before.json':'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8'}
PROVENANCE=(PLAN_PATH,SOURCE_ROOT+'/read13_concrete_v5_Root_bounded_implementation_ACK_20261120.json',
 SOURCE_ROOT+'/read13_concrete_v4_independent_source_plan_review_20261120.json',
 SOURCE_ROOT+'/read13_concrete_v5_independent_key_plan_delta_review_final_20261120.json')

def coherence_sql(plan):
 observations=[]
 for row in plan['fixture_rows']:
  checks=[]
  for column,value in row['values'].items():
   actual='r.'+column
   if type(value) is dict and set(value)=={'source_default_or_guard'}:
    if column=='mutation_transaction_id':checks.append(actual+" ~ '^[0-9]+$'")
    elif column=='created_at':checks.append(actual+' IS NOT NULL AND '+actual+'<=clock_timestamp()')
    else:continue # e.g. actual source DEFAULT display_order is not host-predicted.
   elif type(value) is dict and set(value)=={'server_value'}:checks.append(actual+' IS NOT NULL AND '+actual+'<=clock_timestamp()')
   elif type(value) is dict and set(value)=={'server_expression'}:
    if column in ('period_start','period_end'):continue # Full same-row/window linkage checked below.
    checks.append(actual+' IS NOT NULL AND '+actual+'<=clock_timestamp()')
   elif type(value) is dict and 'PG_jsonb_text_UTF8_SHA256' in value:
    body={'result_digest':'r.result_body','payload_hash':'r.payload','evidence_digest':'r.evidence_body'}.get(column)
    if body:checks.append(actual+" IS NOT DISTINCT FROM encode(sha256(convert_to("+body+"::text,'UTF8')),'hex')")
    else:
     need(column=='result_hash' and row['label']=='CommittedEffect','CLOSED_DIGEST_SOURCE')
     checks.append(actual+' IS NOT DISTINCT FROM (SELECT q.result_digest FROM platform.runtime_command_receipt q WHERE q.id=r.command_receipt_id)')
   elif column=='result_body' and value is not None:
    checks.append("(r.result_body #- '{value,receipt,recordedAt}') IS NOT DISTINCT FROM (("+value_sql(value)+") #- '{value,receipt,recordedAt}')")
    checks.append("(r.result_body#>>'{value,receipt,recordedAt}')::timestamptz BETWEEN r.created_at-interval '300 seconds' AND clock_timestamp()")
   else:checks.append(actual+' IS NOT DISTINCT FROM ('+value_sql(value)+')')
  observations.append('SELECT ('+' AND '.join('('+x+')' for x in checks)+') AS exact FROM '+row['table']+' r WHERE r.id='+quote(row['values']['id']))
 usage=[]
 for side in ('A','B'):
  ids=plan['fixture_namespace']['preview_ids'][side]
  usage.append("EXISTS(SELECT 1 FROM app.track_usage_events e JOIN app.track_usage_counters c ON c.entitlement_grant_id=e.entitlement_grant_id JOIN app.track_entitlement_grants g ON g.id=e.entitlement_grant_id WHERE e.id="+quote(ids['UsageEvent'])+" AND c.id="+quote(ids['Counter'])+" AND e.period_start=date_trunc('month',e.occurred_at AT TIME ZONE 'UTC') AT TIME ZONE 'UTC' AND e.period_end=(date_trunc('month',e.occurred_at AT TIME ZONE 'UTC')+interval '1 month') AT TIME ZONE 'UTC' AND e.occurred_at=e.accepted_at AND e.occurred_at>=e.period_start AND e.occurred_at<e.period_end AND c.period_start=e.period_start AND c.period_end=e.period_end AND c.used_quantity=e.quantity AND c.limit_quantity=g.int_value AND c.limit_quantity=10 AND c.used_quantity=1)")
 return "SELECT jsonb_build_object('rows',count(*),'all_source_values_match',coalesce(bool_and(exact),false),'usage_source_window_sum_limit_match',"+' AND '.join(usage)+') FROM ('+' UNION ALL '.join(observations)+') observed;\n'

def build(root=ROOT,run_id=FIXTURE_RUN_ID):
 root=Path(root);raw=(root/PLAN_PATH).read_bytes();need(sha(raw)==PLAN_SHA,'APPROVED_CONCRETE_PLAN_BYTES')
 source=unique_json(raw)
 paths=sorted(set(NEW+HELPERS+PROVENANCE+tuple(source['source_files_sha256'])+tuple(STRUCTURAL_INPUTS)+tuple(OFFLINE_ONLY_INPUTS)))
 blobs={p:(root/p).read_bytes() for p in paths};pins={p:sha(b) for p,b in blobs.items()}
 for p,h in source['source_files_sha256'].items():need(pins[p]==h,'REVIEWED_SOURCE_INPUT_DRIFT')
 for p,h in STRUCTURAL_INPUTS.items():need(pins[p]==h,'SOURCE_MODEL_ACL_INVENTORY_DRIFT')
 for p,h in OFFLINE_ONLY_INPUTS.items():need(pins[p]==h,'CLOSED_OFFLINE_TEST_SUPPORT_DRIFT')
 need(pins[PROVENANCE[1]]==ACK_SHA and pins[PROVENANCE[3]]==PEER_SHA,'SOURCE_AUTHORITY_BINDING')
 application=blobs['review-output/foundation-application.review.sql'];need(sha(application)==APPLICATION_SHA,'CANONICAL_APPLICATION_SQL')
 for row in source['selected_reads']:
  span=row['policy']['span'];need(sha(application[span['byte_start']:span['byte_start']+span['byte_length']])==span['raw_statement_sha256'],'SELECT_POLICY_SOURCE_SPAN')
 for item in source['trigger_setup_allowlist']:
  for key in ('source_statement','function_source'):
   span=item[key];need(sha(application[span['byte_start']:span['byte_start']+span['byte_length']])==span['raw_statement_sha256'],'EXACT15_SOURCE_SPAN')
 plan=materialize(source,run_id);files,groups,grants,cases=render(plan)
 models={row['model']:row for row in unique_json(blobs['context/reconciliation/foundation-sql-draft-models.json'])}
 access=unique_json(blobs['context/reconciliation/foundation-sql-draft-access.json']);worker=[r for r in access if r['role']=='wa_worker'];need(len(worker)==32,'EXACT32_WORKER_ACL_UNCHANGED')
 tables=sorted({r['object'] for r in models.values()}|{'platform_private.identity_service_authorization','platform_private.identity_service_receipt'});need(len(tables)==42,'COMPLETE42_TABLES')
 def state(table):return "(SELECT jsonb_build_object('count',count(*),'rows_sha256',encode(sha256(convert_to(coalesce(jsonb_agg(to_jsonb(r) ORDER BY to_jsonb(r)::text COLLATE \"C\"),'[]'::jsonb)::text,'UTF8')),'hex')) FROM "+table+' r)'
 files['complete-state-observe.sql']='SELECT jsonb_build_object('+','.join(quote(t)+','+state(t) for t in tables)+');\n'
 files['fixture-coherence-observe.sql']=coherence_sql(plan)
 expected=dict.fromkeys(tables,0)
 for row in plan['fixture_rows']:expected[row['table']]+=1
 inventory=unique_json(blobs['context/reconciliation/local-f0-assertions.json']);claims=[]
 for read in plan['selected_reads']:
  case=next(r for r in inventory['cases'] if r['id']==read['case_id']);assertion=next(r for r in case['assertions'] if r['id']==read['assertion_id'])
  claims.append({'case_id':read['case_id'],'assertion_id':read['assertion_id'],'assertion_sha256':digest(assertion),'status':'NOT_RUN','maximum_status_after_actual_audit':'PASS'})
 limits=['Only13 positive wa_app_runtime SQL SELECT criteria;82 finite recipes, no whole-case/94/451 promotion.',
  '48 synthetic prerequisite rows,78 FK links and exact15 setup-only O-D-O exceptions; all100 user triggers restored before every behavioral read.',
  'No owner API/DTO/result codec, insert/update, worker/enrollment/history, usage adapter/quota, SH003/SH005/SH006/SH056 or legal consent qualification.',
  'Currentness controls explicitly rebind; bare RLS absence is never relabeled a guard exception.',
  'Same fresh source/run/CID native29089/oracle416/ledger22 prerequisite plus separate read-only after proof; no second install.',
  'This packet is NOT_RUN, Posture D. Source approval does not authorize executing fixture bypasses.']
 files['README.md']='Remaining13 app SELECT source packet\n\n'+'\n\n'.join(limits)+'\n'
 packet={'schema':'workinants.remaining-app-read13-fixtures.v1','status':'NOT_RUN','database_posture':'D','database_contacted':False,'sql_executed':False,
  'source_plan_sha256':PLAN_SHA,'Root_ACK_sha256':ACK_SHA,'independent_plan_review_sha256':PEER_SHA,'fixture_run_id':run_id,
  'source_files_sha256':pins,'models':models,'worker_acl_ceiling_rows':worker,'worker_acl_sha256':digest(worker),
  'selected_control_ids':[r['case_id'] for r in claims],'claim_ceilings':claims,'finite_caps':deepcopy(FINITE),
  'fixture_plan':plan,'setup_groups':groups,'grants':grants,'cases':cases,'setup_expected_counts':expected,
  'scope_limits':limits,'prepared_files_sha256':{name:sha(value.encode()) for name,value in sorted(files.items())}}
 packet['source_only_packet_sha256']=digest({k:packet[k] for k in ('source_files_sha256','prepared_files_sha256')})
 files['fixtures.json']=json.dumps(packet,indent=2,ensure_ascii=False,allow_nan=False)+'\n';return files,packet

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');parser.add_argument('--run-id',default=FIXTURE_RUN_ID);args=parser.parse_args(argv)
 files,packet=build(run_id=args.run_id)
 if args.prepare:
  OUT.mkdir(parents=True,exist_ok=False)
  for name,value in files.items():
   with (OUT/name).open('x',encoding='utf8',newline='\n') as stream:stream.write(value)
 print(json.dumps({'status':'PREPARED_NOT_RUN' if args.prepare else 'PLAN_ONLY_NOT_RUN','cases':82,'maximum_links':13,'fixture_rows':48,'files':len(files),'database_contacted':False}));return 0
if __name__=='__main__':raise SystemExit(main())
