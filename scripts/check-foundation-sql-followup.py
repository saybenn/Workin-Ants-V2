"""e363ad4 follow-up: offline authority order, claim gates and path reachability.

This follows parsed statements and synthetic scalar facts. It does not implement
Postgres catalogs/RLS, execute SQL, authenticate a role or qualify a DB case.
"""
import json
import re
import runpy
from pathlib import Path
from pglast import ast, parse_sql


def inspect(root, evaluate):
    read=lambda p:(root/p).read_text(encoding='utf8')
    errors=[];cases=[];checks=0
    def need(ok,label):
        nonlocal checks
        checks+=1
        if not ok:errors.append(label)
    def scalar(label,sql,facts,expected):
        node=parse_sql('SELECT '+sql)[0].stmt.targetList[0].val
        try:actual=evaluate(node,facts)
        except (KeyError,TypeError,ValueError) as exc:
            errors.append(label+': unsupported/missing fact '+str(exc));return
        cases.append({'case':label,'expected':expected,'actual':actual,'pass':actual is expected})
        need(actual is expected,label)
    app=read('review-output/foundation-application.review.sql')
    boot=read('review-output/foundation-bootstrap.review.sql')
    current='wa_migrator';owners={};bodies={};grants=[];policies=[];transfers=[]
    # Ownership is tracked at EACH statement. SET TRUE / INHERIT FALSE does
    # not supply the previous owner's grant option after ownership transfer.
    for index,raw in enumerate(parse_sql(app)):
        s=raw.stmt
        if isinstance(s,ast.VariableSetStmt) and s.name=='role':
            if s.args:current=s.args[0].val.sval
            else:current='wa_migrator'
        elif isinstance(s,ast.CreateFunctionStmt):
            name=s.funcname[-1].sval;owners[name]=current
            bodies[name]=next(o.arg[0].sval for o in s.options if o.defname=='as')
        elif isinstance(s,ast.AlterOwnerStmt) and s.objectType.name=='OBJECT_FUNCTION':
            name=s.object.objname[-1].sval
            need(owners.get(name)==current,'function transfer lacks creating owner: '+name)
            owners[name]=s.newowner.rolename;transfers.append(index)
        elif isinstance(s,ast.GrantStmt) and s.objtype.name=='OBJECT_FUNCTION':
            named=[o.objname[-1].sval for o in s.objects or [] if isinstance(o,ast.ObjectWithArgs)]
            targets=named or list(owners)
            for name in targets:need(owners.get(name)==current,'function ACL statement lacks owner authority: '+name)
            if s.is_grant and any(r.rolename=='wa_worker' for r in s.grantees):need(not set(named)&{'worker_source_claim_valid','worker_source_row_valid','worker_row_capabilities'},'internal actual-row helper exposed to worker')
        elif isinstance(s,ast.DoStmt):
            body='\n'.join(o.arg.sval for o in s.args if o.defname=='as')
            if 'REVOKE ALL ON ALL FUNCTIONS' in body:
                need(all(owner==current for owner in owners.values()),'managed-role function revocation after transfer')
        if isinstance(s,ast.GrantStmt) and s.is_grant and s.objtype.name=='OBJECT_TABLE':
            for table in s.objects or []:
                for role in s.grantees:
                    for p in s.privileges or []:grants.append((role.rolename,table.relname,p.priv_name.upper(),{c.sval for c in p.cols or []}))
        if isinstance(s,ast.CreatePolicyStmt):policies.append(s)
    need(bool(transfers),'no function ownership transfer trace')
    need('WITH ADMIN FALSE, INHERIT FALSE, SET TRUE' in boot,'temporary authority options changed')
    need(owners.get('track_atomic_valid')=='wa_track_verifier','Track verifier owner')
    need('GRANTED BY CURRENT_USER' in read('review-output/foundation-bootstrap-finalize.review.sql'),'original grantor cleanup missing')
    # Complete source claims are checked against an actual fixed row, never a
    # caller-provided Boolean or only mutually matching foreign records.
    claim=bodies['worker_source_claim_valid'];atomic=bodies['track_atomic_valid']
    need("n->>'mutation_transaction_id' IS DISTINCT FROM pg_current_xact_id()::text" in claim,'claim current xid gate')
    need('actual_value IS NULL OR NOT (n @> actual_value)' in claim,'claim not compared to actual row')
    need('worker_source_claim_valid(model_name,n)' in atomic,'direct atomic entry bypasses claim gate')
    need('worker_row_capabilities(model_name,row_value,verb)' in bodies['worker_track_allowed'],'direct relationship port bypasses capabilities')
    need("n->>'revision' IS NULL" in bodies['worker_row_capabilities'] and "n->>'fence' IS NULL" in bodies['worker_row_capabilities'],'direct versioned port accepts missing version')
    need(0<=bodies['worker_track_allowed'].find('worker_row_capabilities')<bodies['worker_track_allowed'].find('SELECT j.id'),'capability gate follows privileged relationship lookup')
    need('customer_current_for_track' in bodies['worker_effect_matches'],'direct effect port bypasses source currentness')
    need("worker_track_allowed('RuntimeOutboxMessage',jsonb_build_object('id',o.id,'producer_owner',o.producer_owner),'SELECT')" in bodies['worker_effect_matches'],'direct effect port bypasses canonical job source')
    need('worker_source_claim_valid' in bodies['worker_evidence_source_matches'],'reverse evidence port bypasses exact source caps')
    need("WHEN model_name='TrackSubscriptionEvent' THEN 'INSERT' ELSE 'SELECT'" in claim,'post-write source relationship phase changed')
    need('p.track' in claim and '/version/' in claim and '/contentHash/' in claim,'new source approved plan identity incomplete')
    need('v.evidence_body' in atomic and "->>'subscriptionId'=prior_value->>'subscription_id'" in atomic,'selection predecessor is caller-only')
    need('worker_row_capabilities' in atomic and 'old_s.user_id' in atomic,'prior subscription read lacks job/capability binding')
    registry=json.loads(read('context/reconciliation/foundation-sql-verifier-access.json'))['roles']['wa_track_verifier']['columns']
    models={'TrackSubscription':'track_subscriptions','TrackEntitlementGrant':'track_entitlement_grants','TrackBaseSelection':'track_base_selection','TrackSubscriptionEvent':'track_subscription_events','TrackEnrollmentReceipt':'track_enrollment_receipt'}
    for model,table in models.items():
        part=claim.split("WHEN '"+model+"' THEN",1)[-1].split('WHEN ',1)[0]
        need('FROM "app"."'+table+'" s' in part and 's.id::text=n->>\'id\'' in part and 's.mutation_transaction_id=pg_current_xact_id()::text' in part,'actual source lookup missing '+model)
        need('SELECT *' not in part,'unbounded claim read '+model)
        need(set(re.findall(r's\."([^"]+)"',part))<=set(registry['app.'+table]),'unregistered claim read '+model)
        value={'id':'source-A','user_id':'user-A','track':'customer','customer_profile_id':'customer-A','plan_id':'plan-A','mutation_transaction_id':'tx-A','revision':0}
        for label,delta,actual,expected in [
            ('complete legitimate same-job snapshot',{},value,False),
            ('complete foreign Customer claim',{'user_id':'user-B','customer_profile_id':'customer-B'},value,True),
            ('different source under same job',{'id':'source-B'},value,True),
            ('wrong plan',{'plan_id':'plan-B'},value,True),
            ('wrong transaction',{'mutation_transaction_id':'tx-B'},value,True),
            ('missing actual source',{},None,True)]:
            scalar(model+' '+label,'actual_value IS NULL OR NOT (n @> actual_value)',{'n':value|delta,'actual_value':actual},expected)
    identity=re.search(r"IF (row_value->>'user_id' IS DISTINCT FROM u::text) THEN",bodies['worker_track_allowed'])
    need(identity is not None,'worker source/user binding missing')
    if identity:
        for label,user,expected in [('complete legitimate actual source','user-A',False),('complete correctly formed foreign actual source','user-B',True)]:
            scalar(label,identity[1],{'row_value':{'user_id':user},'u':'user-A'},expected)
    # These are real parsed ACL and policy prerequisites, composed with the
    # existing independent terminal-state/proof predicates in the main suite.
    runtime_update=next((cols for role,t,v,cols in grants if (role,t,v)==('wa_app_runtime','runtime_reservation','UPDATE')),set())
    need('effect_receipt_id' in runtime_update,'runtime terminal receipt column unreachable')
    need('command_receipt_id' not in runtime_update and 'owner_module_id' not in runtime_update,'reservation identity grant broadened')
    for verb in ['select','update']:
        ps=[p for p in policies if p.table.relname=='runtime_reservation' and p.policy_name=='p_app_runtime_'+verb]
        need(len(ps)==1 and ps[0].qual is not None and (verb!='update' or ps[0].with_check is not None),'reservation actual role policy path missing '+verb)
    need('runtime.reservation.v1' in bodies['protected_scope'],'designated reservation operation missing')
    need('one protected outcome link' in app or 'reservation outcome link attaches once' in app,'terminal link guard missing')
    # Dependency labels must be operation-specific and present in the selected
    # replay, rather than claiming that every ACL ceiling is an ALLOW path.
    register=json.loads(read('context/reconciliation/database-candidate-tests.json'))
    replay=json.loads(read('context/reconciliation/foundation-sql-draft-replay-map.json'))
    need(len(register['tests'])==451 and all(t['status']=='NOT_RUN' for t in register['tests']),'451 status/identity boundary')
    need(len(replay['tests'])==94 and all(t['status']=='NOT_RUN' for t in replay['tests']),'94 replay boundary')
    selected={t['id']:t for t in replay['tests']};paths_by_model={}
    for test in register['tests']:
        vector_deps={d for v in test.get('p0c03a_vectors',[]) for d in v.get('execution_dependencies',[])}
        if vector_deps and test['id'] in selected:need(vector_deps<=set(selected[test['id']]['blocking_review_issues']),'missing selected vector dependency '+test['id'])
        if isinstance(test['setup'],dict) and test['setup'].get('operation_dispositions'):
            paths=test['setup']['operation_dispositions'];paths_by_model[test['id']]=paths
            for path in paths:
                need(path['status']=='NOT_RUN' and bool(path['action']) and bool(path['root_kind']),'incomplete operation path '+test['id'])
                need((path['source_admission']=='DEPENDENCY_GATED')==bool(path['dependency_ids']),'unexplained operation gate '+test['id'])
            dependencies={d for p in paths for d in p['dependency_ids']}
            if test['id'] in selected:need(dependencies<=set(selected[test['id']]['blocking_review_issues']),'empty/missing replay blocker '+test['id'])
    for model in ['PrivacyTargetInstruction','PrivacyOwnerReceipt','PrivacyRestoreMarker','TrackUsageReservation']:
        paths=paths_by_model.get('P0C-TABLE-'+model+'-ALLOW',[])
        need(bool(paths) and all(p['dependency_ids'] for p in paths),'gated positive falsely attainable '+model)
    rehearsal=register['first_rehearsal']
    need(rehearsal['status']=='PROPOSED_NOT_RUN_EXECUTION_HELD' and all(s['status']=='NOT_RUN' for s in rehearsal['steps']),'rehearsal falsely executed')
    need('@sha256:' in rehearsal['image']['reference'] and rehearsal['image']['platform']=='linux/amd64','proposed immutable image missing')
    fixture_dir=root/'review-output/first-rehearsal'
    fixture=json.loads((fixture_dir/'fixtures.json').read_text(encoding='utf8'))
    coordinator=runpy.run_path(str(Path(__file__).parent/'sql-review/run-first-rehearsal.py'))
    need(len(fixture['scenarios'])==3 and all(c['status']=='NOT_RUN' for c in fixture['scenarios']),'small fixture status changed')
    for case in fixture['scenarios']:
        statements=parse_sql((fixture_dir/case['transaction_sql']).read_text(encoding='utf8'))
        inserts=[s.stmt for s in statements if isinstance(s.stmt,ast.InsertStmt)]
        need(len(inserts)==(5 if case['name']=='missing-outbox' else 6),'incomplete exact fixture '+case['name'])
        need(not any(isinstance(s.stmt,ast.VariableSetStmt) for s in statements),'fixture uses SET ROLE instead of actual restricted login')
        grant=coordinator['grant_sql'](case,'wa_app_runtime','12345','98765','0'*64)
        need(bool(parse_sql(grant)),'issuer fixture SQL not parseable '+case['name'])
        need(not any('*' in f for f in case['allowed_fields']),'wildcard fixture capability')
        if case['name']=='missing-outbox':need(case['principal_user_id']==case['source_user_id'] and case['source_user_id']!=fixture['scenarios'][0]['source_user_id'],'rollback fixture hits existing Customer uniqueness before missing outbox')
        need(bool(parse_sql((fixture_dir/case['observer_sql']).read_text(encoding='utf8'))),'observer fixture SQL missing')
    need(bool(parse_sql((fixture_dir/'fixtures.sql').read_text(encoding='utf8'))),'privileged seed SQL invalid')
    runner=(Path(__file__).parent/'sql-review/run-first-rehearsal.py').read_text(encoding='utf8')
    need(runner.index('if not a.execute_approved_rehearsal:')<runner.index("endpoint=json.loads"),'dormant coordinator can contact Docker before approval guard')
    need('expected_state' in runner and 'case[\'expected_counts\']' in runner,'coordinator accepts wrong failure/partial state')
    return {'errors':errors,'cases':cases,'predicate_cases':len(cases),'source_graph_checks':checks}
