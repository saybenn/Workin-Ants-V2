#!/usr/bin/env python3
"""Independent P0-C-03A source/predicate checks. NO SQL execution or database.

Parses actual draft expressions, then evaluates a deliberately small SQL Boolean
AST subset against synthetic scalar facts. Unsupported nodes fail. This is not a
database emulator: catalog resolution, RLS/privilege application, concurrency and
all 451 database/runtime cases remain NOT_RUN.
"""
import hashlib
import json
import re
from pathlib import Path
from pglast import parse_sql, ast

ROOT=Path(__file__).resolve().parents[1]
JSON_NULL=object()
READ_ONLY_SOURCE_ACTIONS={
    'SH-001.v1','SH-003.v1','SH-005.v1','SH-008.v1','SH-009.v1','SH-010.v1',
    'SH-015.v1','SH-016.v1','SH-024.v1','SH-026.v1','SH-031.v1','SH-043.v1',
    'SH-050.v1','SH-061.v1','SH-094.v1','SH-096.v1','SH-097.v1','SH-102.v1',
    'SH-115.v1','SH-123.v1','SH-125.v1'}


def sql_truth(kind, values):
    if kind=='NOT_EXPR':return None if values[0] is None else not values[0]
    if kind=='AND_EXPR':return False if False in values else None if None in values else True
    if kind=='OR_EXPR':return True if True in values else None if None in values else False
    raise ValueError(kind)


def evaluate(n, facts):
    """Bounded evaluation of actual parser AST, not execution of SQL statements."""
    if n is None:return None
    if isinstance(n,ast.A_Const):
        if n.isnull:return None
        for name in ['sval','ival','boolval','fval']:
            if hasattr(n.val,name):return getattr(n.val,name)
    if isinstance(n,ast.ColumnRef):return facts['.'.join(s.sval for s in n.fields)]
    if isinstance(n,ast.A_ArrayExpr):return [evaluate(a,facts) for a in n.elements]
    if isinstance(n,ast.BoolExpr):return sql_truth(n.boolop.name,[evaluate(a,facts) for a in n.args])
    if isinstance(n,ast.NullTest):return (evaluate(n.arg,facts) is None)==(n.nulltesttype.name=='IS_NULL')
    if isinstance(n,ast.CoalesceExpr):return next((v for a in n.args if (v:=evaluate(a,facts)) is not None),None)
    if isinstance(n,ast.TypeCast):
        v=evaluate(n.arg,facts); t=n.typeName.names[-1].sval
        if v is None:return None
        if n.typeName.arrayBounds:return v
        if t=='jsonb':return JSON_NULL if v=='null' else json.loads(v)
        if t in ['int8','int4','bigint','integer']:return int(v)
        if t in ['text','uuid']:return str(v)
        raise ValueError('unsupported cast '+t)
    if isinstance(n,ast.CaseExpr):
        for a in n.args:
            if evaluate(a.expr,facts) is True:return evaluate(a.result,facts)
        return evaluate(n.defresult,facts)
    if isinstance(n,ast.SubLink):return facts['scalar_subquery'] if 'scalar_subquery' in facts else facts['existing_exact_inbox_or_history']
    if isinstance(n,ast.FuncCall):
        name='.'.join(s.sval for s in n.funcname);args=[evaluate(a,facts) for a in n.args or ()]
        if name=='jsonb_typeof':return 'null' if args[0] is JSON_NULL else 'object' if isinstance(args[0],dict) else None
        if name=='length':return len(args[0]) if args[0] is not None else None
        if name=='to_jsonb':return args[0]
        if name=='jsonb_build_object':return dict(zip(args[::2],args[1::2]))
        if name=='platform_private.worker_track_allowed':return facts['worker_source_allowed']
        if name=='platform_private.worker_effect_matches':return facts['exact_linked_committed_effect']
        if name=='nullif':return None if args[0]==args[1] else args[0]
        if name=='current_setting':return facts.get('settings',{}).get(args[0])
        if name=='pg_current_xact_id':return facts['xid']
        if name=='clock_timestamp':return facts['now']
        if name=='decode':return bytes.fromhex(args[0])
        if name=='sha256':return hashlib.sha256(args[0]).digest()
        if name=='encode':return args[0].hex()
        if name=='platform_private.context_allows':
            g=facts['grant'];return all(g[k]==a for k,a in zip(['owner','action','kind','id','purpose'],args))
        if name=='platform_private.lease_secret_matches':
            value=facts.get('settings',{}).get('wa.lease_secret','')
            return bool(re.fullmatch('[0-9a-f]{64}',value)) and hashlib.sha256(bytes.fromhex(value)).hexdigest()==args[0]
        if name=='platform_private.global_context_registered':return tuple(args) in facts.get('global_contexts',[])
        raise ValueError('unsupported scalar function '+name)
    if isinstance(n,ast.A_Expr):
        left=evaluate(n.lexpr,facts);op=n.name[0].sval
        if n.kind.name=='AEXPR_IN':
            values=[evaluate(a,facts) for a in n.rexpr]
            value=None if left is None or (left not in values and None in values) else left in values
            return None if value is None else (value if op=='=' else not value)
        right=evaluate(n.rexpr,facts)
        if n.kind.name=='AEXPR_NULLIF':return None if left==right else left
        if n.kind.name=='AEXPR_DISTINCT':return left!=right
        if n.kind.name=='AEXPR_NOT_DISTINCT':return left==right
        if n.kind.name=='AEXPR_OP_ANY':return False if right is None else left in right
        if op in ['->','->>']:
            if left is None:return None
            if right not in left:return None
            value=left[right]
            return (None if value is None else str(value)) if op=='->>' else JSON_NULL if value is None else value
        if left is None or right is None:return None
        if op=='=':return left==right
        if op in ['<>','!=']:return left!=right
        if op=='+':return left+right
        if op=='-':return left-right
        if op=='||':return str(left)+str(right)
        if op=='>':return left>right
        if op=='>=':return left>=right
        if op=='<':return left<right
        if op=='<=':return left<=right
        if op=='~':return bool(re.search(right,left))
        raise ValueError('unsupported operator '+op)
    raise ValueError('unsupported AST '+type(n).__name__)


def expression(text):return parse_sql('SELECT '+text)[0].stmt.targetList[0].val


def inspect(root=ROOT):
    read=lambda p:(root/p).read_text(encoding='utf8')
    errors=[];cases=[]
    def need(value,label):
        if not value:errors.append(label)
    def case(label,node,facts,expected):
        try:actual=evaluate(node,facts)
        except (KeyError,ValueError,TypeError) as e:
            errors.append(label+': predicate evaluator rejected unsupported/missing fact '+str(e));return
        ok=actual is expected
        cases.append({'case':label,'expected':expected,'actual':actual,'pass':ok})
        need(ok,'predicate mismatch: '+label)
    app=read('review-output/foundation-application.review.sql');boot=read('review-output/foundation-bootstrap.review.sql');cleanup=read('review-output/foundation-bootstrap-finalize.review.sql')
    functions={};tables={};constraints={};grants=[];owners={};policies=[]
    for raw in parse_sql(app):
        s=raw.stmt
        if isinstance(s,ast.CreateFunctionStmt):functions[s.funcname[-1].sval]=(s,{o.defname:o.arg for o in s.options}['as'][0].sval)
        if isinstance(s,ast.CreateStmt):tables[(s.relation.schemaname,s.relation.relname)]={c.colname:c for c in s.tableElts if isinstance(c,ast.ColumnDef)}
        if isinstance(s,ast.AlterTableStmt):
            for c in s.cmds:
                if isinstance(c.def_,ast.Constraint):constraints[c.def_.conname]=c.def_
        if isinstance(s,ast.GrantStmt) and s.is_grant and s.objtype.name=='OBJECT_TABLE':
            for ob in s.objects or []:
                for role in s.grantees:
                    for privilege in s.privileges or []:grants.append((role.rolename,ob.schemaname+'.'+ob.relname,privilege.priv_name.upper(),sorted(c.sval for c in privilege.cols or [])))
        if isinstance(s,ast.AlterOwnerStmt) and s.objectType.name=='OBJECT_FUNCTION':owners[s.object.objname[-1].sval]=s.newowner.rolename
        if isinstance(s,ast.CreatePolicyStmt):policies.append(s)
    body=lambda name:functions[name][1]
    # The original contradiction is checked against the actual native column,
    # actual CHECK expression and actual per-source predecessor predicate.
    previous=tables[('platform','owner_mutation_evidence')]['previous_revision']
    need(not any(c.contype.name=='CONSTR_NOTNULL' for c in previous.constraints or []),'first-write predecessor is still NOT NULL')
    rule=constraints['evidence_identity'].raw_expr.args[-1]
    for name,old,new,prior,expected in [
        ('create revision zero',None,0,None,True),('create nonzero denied',None,1,None,False),
        ('create fabricated prior denied',None,0,{},False),('update zero to one',0,1,{'revision':'0'},True),
        ('update missing prior denied',0,1,None,False),('skipped revision denied',0,2,{'revision':'0'},False),
        ('negative predecessor denied',-1,0,{},False)]:
        case(name,rule,{'previous_revision':old,'committed_revision':new,'evidence_body':{'prior':prior}},expected)
    pred=re.search(r'e.previous_revision IS DISTINCT FROM \((CASE.*?END)\)',body('commit_customerprofile'),re.S)
    need(pred is not None,'exact source predecessor check missing')
    if pred:
        for name,op,old,e,expected in [('source create valid','INSERT',None,None,False),('source update valid','UPDATE',0,0,False),('wrong predecessor denied','UPDATE',0,7,True),('create invented predecessor denied','INSERT',None,0,True)]:
            case(name,expression(pred[0]),{'tg_op':op,'old.revision':old,'e.previous_revision':e},expected)
    case('omitted update prior denied',rule,{'previous_revision':0,'committed_revision':1,'evidence_body':{}},False)
    # New mutable revisions and immutable age evidence must agree in both schema cuts.
    for p in ['prisma/review/foundation-candidate.prisma','prisma/review/physical-candidate.prisma']:
        schema=read(p)
        for model in ['TrackUsageReservation','PrivacyRestoreMarker']:
            fragment=re.search(r'model '+model+r' \{(.*?)^\}',schema,re.S|re.M)[1]
            need(bool(re.search(r'\brevision BigInt @default\(0\)',fragment)),p+': missing '+model+' revision')
    evidence=json.loads(read('contracts/database-review/owner-mutation-evidence.v1.schema.json'))['$defs']
    for model in ['TrackUsageReservation','PrivacyRestoreMarker']:
        for arm in ['prior','committed']:need('revision' in evidence[model]['properties'][arm]['required'],'evidence revision missing '+model+':'+arm)
        need('NEW.revision<>OLD.revision+1' in body('guard_'+model.lower()),'CAS guard missing '+model)
        condition=re.search(r'IF (NEW.revision<>OLD.revision\+1)',body('guard_'+model.lower()))
        if condition:
            for before,after,denied in [(0,1,False),(3,4,False),(3,3,True),(3,5,True),(3,2,True)]:
                case(model+' CAS '+str(before)+' -> '+str(after),expression(condition[1]),{'old.revision':before,'new.revision':after},denied)
    for model,table in [('AgeGateAttempt','app.age_gate_attempts'),('AgeGateBlock','app.age_gate_blocks')]:
        need('immutable evidence or receipt' in body('guard_'+model.lower()),'age evidence not append-only '+model)
        need(not any(g[1]==table and g[2] in ['UPDATE','DELETE'] and g[0] in ['wa_app_runtime','wa_worker'] for g in grants),'age update privilege '+model)
    need('previous_revision IS DISTINCT FROM' in body('commit_privacyrestoremarker'),'restore marker predecessor not exact')
    # Independent Identity state, not an issuer-created assertion.
    bind=body('bound_grant')
    for fragment in ['platform_private.identity_service_authorization a','a.security_generation=g.security_generation','a.revoked_at IS NULL',"'service:'||g.service_principal"]:need(fragment in bind,'service authority check missing: '+fragment)
    service_match=re.search(r'WHERE (a.service_principal=.*?a.revoked_at IS NULL)',bind,re.S)
    need(service_match is not None,'current service filter missing')
    if service_match:
        service=expression(service_match[1])
        f={'a.service_principal':'service-A','g.service_principal':'service-A','a.security_generation':3,'g.security_generation':3,'a.revoked_at':None}
        case('current independent service epoch valid',service,f,True)
        for name,delta in [('revoked service',{'a.revoked_at':5}),('old service generation',{'g.security_generation':2}),('foreign service',{'g.service_principal':'service-B'})]:case(name,service,f|delta,False)
    need(not any(g[0] in ['wa_context_issuer','wa_app_runtime','wa_worker'] and g[1].startswith('platform_private.identity_service_') for g in grants),'issuer/runtime can write or read Identity authority')
    need('NEW.security_generation<>OLD.security_generation+1' in body('identity_service_guard'),'Identity epoch not monotonic')
    need('old_authority.revoked_at IS NOT NULL AND NEW.transition' in body('identity_service_guard'),'revocation recovery not guarded')
    # Exact scope helper has a real policy -> row -> scope -> action call chain.
    need('platform_private.protected_scope(model_name,row_key,verb)' in body('row_allowed'),'registered scope has no protected caller')
    need('context_allows' in body('protected_scope') and "'default_free_enrollment'" in body('protected_scope'),'action/purpose not enforced')
    need("platform_private.context_allows('customer_buyer_profile','SH-004.v1','CustomerProfile',g.target_id,'provision')" in body('protected_scope'),'Customer provision purpose not registered exactly')
    need('row_transaction=pg_current_xact_id()::text' in body('row_allowed') and 'authorized_revision' in body('row_allowed'),'same-transaction successor read cannot prove update')
    # Evaluate the generated scope conditions, including otherwise matching
    # grants and row capabilities: a query purpose never admits source writes.
    scope_conditions=re.findall(r'IF (verb=ANY\(.*?) THEN RETURN true; END IF;',body('protected_scope'))
    scope_register=json.loads(read('context/reconciliation/foundation-sql-scope-policy.json'))['domain_scopes']
    for row in scope_register:
        if row['action'] not in READ_ONLY_SOURCE_ACTIONS:continue
        need(row['verbs']==['SELECT'],'nonmutating source purpose permits writes '+row['action'])
        matches=[s for s in scope_conditions if all("'"+row[k]+"'" in s for k in ['owner','action','purpose','root_kind'])]
        need(len(matches)==1,'query source scope missing/ambiguous '+row['action']+':'+row['root_kind'])
        if len(matches)==1:
            facts={'model_name':row['root_kind'],'g.target_id':'source-A',
                   'g.allowed_fields':[], 'row_key':'source-A',
                   'grant':{'owner':row['owner'],'action':row['action'],'purpose':row['purpose'],'kind':row['root_kind'],'id':'source-A'}}
            for verb in ['SELECT','INSERT','UPDATE']:
                case(row['action']+' '+row['root_kind']+' '+verb,expression(matches[0]),facts|{'verb':verb},verb=='SELECT')
    # Exercise the actual compiled Consent scope graph. Exact ordinary row/field
    # caps are deliberately present in denial fixtures: relationship admission
    # must also match this proof/presentation/disposition root and purpose.
    root_check="model_name=g.target_kind AND row_key<>g.target_id"
    need('IF '+root_check+' THEN RETURN false;' in body('protected_scope'),'exact scope root ID check missing')
    def consent_scope_case(label,facts,expected):
        try:
            actual=evaluate(expression(root_check),facts) is not True and any(
                evaluate(expression(condition),facts) is True for condition in scope_conditions)
            cases.append({'case':label,'expected':expected,'actual':actual,'pass':actual is expected})
            need(actual is expected,'Consent scope graph mismatch: '+label)
        except (KeyError,ValueError,TypeError) as e:need(False,label+': scope graph evaluator '+str(e))
    def consent_facts(action,purpose,root,model,row_key,verb='SELECT',tokens=()):
        return {'g.target_kind':root,'g.target_id':'root-A','model_name':model,'row_key':row_key,'verb':verb,
                'g.allowed_fields':list(tokens)+[model+'/'+row_key+'/SELECT/id'],
                'grant':{'owner':'consent_disclosure','action':action,'purpose':purpose,'kind':root,'id':'root-A'}}
    for model,relationship in [('ConsentPresentation','presentation'),('ConsentContentRevision','contentRevision')]:
        token='ConsentLog/root-A/'+relationship+'/child-A'
        f=consent_facts('SH-007.v1','owner:recordConsentProof','ConsentLog',model,'child-A',tokens=[token])
        consent_scope_case('Consent proof exact '+model+' prerequisite read',f,True)
        consent_scope_case('Consent proof foreign '+model+' despite row caps',f|{'row_key':'child-B'},False)
        consent_scope_case('Consent proof missing '+model+' relationship',f|{'g.allowed_fields':[model+'/child-A/SELECT/id']},False)
        consent_scope_case('Consent proof cannot insert '+model,f|{'verb':'INSERT'},False)
        consent_scope_case('Consent prerequisite wrong purpose '+model,f|{'grant':f['grant']|{'purpose':'wrong'}},False)
        consent_scope_case('Consent prerequisite wrong root '+model,f|{'grant':f['grant']|{'kind':'CustomerProfile'}},False)
        consent_scope_case('Consent prerequisite foreign root ID '+model,f|{'g.target_id':'root-B','grant':f['grant']|{'id':'root-B'}},False)
    for action,purpose,scope_root,related in [
        ('publishConsentVersion.v1','consent.publish_version','ConsentContentRevision',{}),
        ('recordConsentPresentation.v1','consent.record_presentation','ConsentPresentation',{'ConsentContentRevision':'contentRevision'}),
        ('recordConsentDisposition.v1','consent.record_disposition','ConsentDisposition',{'ConsentPresentation':'presentation','ConsentLog':'proof'})]:
        for verb in ['SELECT','INSERT','UPDATE']:
            f=consent_facts(action,purpose,scope_root,scope_root,'root-A',verb)
            consent_scope_case(action+' exact root '+verb,f,verb!='UPDATE')
            consent_scope_case(action+' foreign root '+verb,f|{'row_key':'root-B'},False)
        for model,relationship in related.items():
            f=consent_facts(action,purpose,scope_root,model,'child-A',tokens=[scope_root+'/root-A/'+relationship+'/child-A'])
            consent_scope_case(action+' exact prerequisite '+model,f,True)
            consent_scope_case(action+' foreign prerequisite '+model,f|{'row_key':'child-B'},False)
            consent_scope_case(action+' prerequisite append denied '+model,f|{'verb':'INSERT'},False)
    for action,purpose,scope_root in [('SH-009.v1','owner:resolveActiveConsentVersion','ConsentContentRevision'),('SH-010.v1','owner:presentStandaloneConsent','ConsentPresentation')]:
        for verb in ['SELECT','INSERT','UPDATE']:
            consent_scope_case(action+' exact auxiliary root '+verb,consent_facts(action,purpose,scope_root,scope_root,'root-A',verb),verb=='SELECT')
    need("context_subject_owner(NEW.user_id,'consent_disclosure')" in body('guard_consentpresentation'),'foreign presentation principal not checked')
    actual_context=re.search(r'RETURN COALESCE\((.*),false\);',body('context_allows'),re.S)
    if actual_context:
        f={'g.id':'grant','g.owner_module_id':'customer_buyer_profile','g.action':'SH-004.v1','g.target_kind':'CustomerProfile','g.target_id':'customer-A','g.purpose':'provision','owner_id':'customer_buyer_profile','action_name':'SH-004.v1','target_kind':'CustomerProfile','target_id':'customer-A','purpose_name':'provision'}
        node=expression('COALESCE('+actual_context[1]+',false)')
        case('matching action purpose root',node,f,True)
        for field,value in [('g.purpose','wrong'),('g.target_id','customer-B'),('g.action','SH-008.v1')]:case('scope denies '+field,node,f|{field:value},False)
    need('NULLIF(NEW.context_id' in body('consent_guard') and 'global_context_registered' in body('consent_guard'),'empty Consent context not registered')
    context=expression("NULLIF(new.context_id,'') IS NULL AND NOT platform_private.global_context_registered(p.action_owner,p.action,p.context_owner,p.context_kind)")
    base={'p.action_owner':'consent','p.action':'accept','p.context_owner':'consent','p.context_kind':'contract','global_contexts':[]}
    case('non-global exact context valid',context,base|{'new.context_id':'contract-A'},False)
    case('unregistered NULL context denied',context,base|{'new.context_id':None},True)
    case('unregistered empty context denied',context,base|{'new.context_id':''},True)
    need(body('global_context_registered').strip()=='SELECT false;','unreviewed global context activated')
    # Read maxima are checked independently of role-visible worker privileges.
    access=json.loads(read('context/reconciliation/foundation-sql-verifier-access.json'))['roles']
    for role,profile in access.items():
        actual={(g[1],g[2],tuple(g[3])) for g in grants if g[0]==role}
        expected={(t,'SELECT',tuple(sorted(cols))) for t,cols in profile['columns'].items()}
        need(actual==expected,'verifier read surface differs: '+role)
        need('NOLOGIN NOINHERIT NOBYPASSRLS' in boot.split('CREATE ROLE '+role+' ',1)[-1].split(';',1)[0],'verifier can login/inherit/bypass: '+role)
        need(not re.search(r'GRANT[^;]*\b'+role+r'\b[^;]*TO wa_(app_runtime|worker)\b',boot),'worker can assume verifier '+role)
    for name,owner in [('customer_current_for_track','wa_customer_verifier'),('worker_track_allowed','wa_track_verifier'),('worker_lease_valid','wa_track_verifier'),('worker_effect_matches','wa_track_verifier'),('track_atomic_valid','wa_track_verifier'),('worker_evidence_source_matches','wa_track_verifier')]:
        need(owners.get(name)==owner,'verifier owner wrong '+name)
        need(functions[name][0].returnType.names[-1].sval in ['bool','boolean'],'verifier exposes body '+name)
        need(not re.search(r'(^|[;\n])\s*(INSERT|UPDATE|DELETE|EXECUTE)\b',re.sub('--[^\n]*','',body(name)),re.I),'verifier writes/dynamic SQL '+name)
    need('platform_private.track_atomic_valid(' in body('track_enrollment_commit'),'Track atomic port not wired')
    need('platform_private.worker_track_allowed(' in body('track_binding'),'Track binding still requires foreign direct read')
    need('platform_private.customer_current_for_track(' in body('worker_track_allowed'),'Customer/worker source linkage missing')
    reverse=body('worker_evidence_source_matches')
    need('source_transaction IS DISTINCT FROM pg_current_xact_id()::text' in reverse,'worker reverse proof lacks current transaction')
    need('platform_private.worker_evidence_source_matches(' in body('evidence_source_commit'),'worker reverse proof still uses invoker source read')
    need('to_jsonb(s)' not in reverse and not re.search(r'SELECT\s+\*',reverse,re.I),'worker reverse proof needs ungranted whole row')
    for model in ['TrackSubscription','TrackEntitlementGrant','TrackBaseSelection']:
        fragment=reverse.split("WHEN '"+model+"' THEN",1)[-1].split(';',1)[0]
        predicate=re.search(r'WHERE (.*)\)\s*$',fragment,re.S)
        need(predicate is not None,'fixed worker source branch missing '+model)
        if predicate:
            columns=set(a or b for a,b in re.findall(r's\."([^\"]+)"|s\.(\w+)',fragment))
            table={'TrackSubscription':'app.track_subscriptions','TrackEntitlementGrant':'app.track_entitlement_grants','TrackBaseSelection':'app.track_base_selection'}[model]
            need(columns<=set(access['wa_track_verifier']['columns'][table]),'worker source verifier lacks needed read columns '+model)
            scalar={'s.id':'source-A','aggregate_id':'source-A','s.mutation_transaction_id':'tx-A','source_transaction':'tx-A','s.revision':1,'committed_revision':1,
                    's.user_id':'user-A','s.track':'customer','s.customer_profile_id':'customer-A','s.candidate_profile_id':None,'s.professional_profile_id':None,
                    's.status':'active','s.provider':'none','s.value_type':'boolean','s.source_generation':2,'worker_source_allowed':True}
            snapshot=evidence[model]['properties']['committed']['properties']
            mapping={'id':'s.id','userId':'s.user_id','track':'s.track','status':'s.status','provider':'s.provider','revision':'s.revision','valueType':'s.value_type','sourceGeneration':'s.source_generation'}
            scalar['committed_value']={k:str(scalar[mapping[k]]) if k in ['revision','sourceGeneration'] else scalar[mapping[k]] for k in snapshot}
            node=expression(predicate[1]);case(model+' exact worker reverse proof',node,scalar,True)
            for label,delta in [('foreign aggregate',{'aggregate_id':'other'}),('foreign transaction',{'source_transaction':'other'}),('wrong revision',{'committed_revision':2}),('wrong snapshot',{'committed_value':{}}),('wrong worker source',{'worker_source_allowed':False})]:
                case(model+' reverse proof '+label,node,scalar|delta,False)
    # Policy input includes fixed read identity even when UPDATE grants are tiny.
    for policy in policies:
        if policy.table.relname=='track_base_selection' and policy.policy_name=='p_worker_update':
            text=str(policy)
            for column in ['id','user_id','track','customer_profile_id','subscription_id','revision','source_generation']:
                need(column in text,'worker UPDATE verifier input missing '+column)
    for token in ['w.outbox_message_id','o.command_receipt_id','o.aggregate_id','sourceCreationReceipt','TrackPlan/','/revision/','/version/','/contentHash/']:need(token in body('worker_track_allowed'),'worker fixed binding missing '+token)
    plan=expression("'TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields)")
    need("'TrackPlan/'||p.id::text||'/revision/'||p.revision::text=ANY(g.allowed_fields)" in body('worker_track_allowed'),'plan revision not enforced')
    f={'p.id':'plan-A','p.revision':4,'g.allowed_fields':['TrackPlan/plan-A/revision/4']}
    case('approved plan revision valid',plan,f,True)
    case('wrong plan revision denied',plan,f|{'p.revision':5},False)
    case('wrong plan identity denied',plan,f|{'p.id':'plan-B'},False)
    # Actual secret hashing expression: knowing the stored digest is not ownership.
    secret='11'*32;digest=hashlib.sha256(bytes.fromhex(secret)).hexdigest()
    node=parse_sql(body('lease_secret_matches'))[0].stmt.targetList[0].val
    case('lease holder has preimage',node,{'expected_hash':digest,'settings':{'wa.lease_secret':secret}},True)
    case('copied stored hash is not secret',node,{'expected_hash':digest,'settings':{'wa.lease_secret':digest}},False)
    case('wrong lease secret denied',node,{'expected_hash':digest,'settings':{'wa.lease_secret':'22'*32}},False)
    case('missing lease secret denied',node,{'expected_hash':digest,'settings':{}},False)
    lease=re.search(r'RETURN COALESCE\((.*),false\);',body('worker_lease_valid'),re.S)
    need(lease is not None,'lease predicate missing')
    if lease:
        facts={'w.id':'job-A','w.handler_name':'assignDefaultFreeTrack.v1','w.state':'leased','allow_completed':False,'w.mutation_transaction_id':'tx-A','xid':'tx-A','w.fence':2,'g.source_generation':2,'w.lease_expires_at':20,'now':10,'w.lease_token_hash':digest,'effect_id':'effect-A','w.effect_receipt_id':'effect-A','settings':{'wa.lease_secret':secret,'wa.fence':'2'}}
        node=expression('COALESCE('+lease[1]+',false)')
        case('live current lease valid',node,facts,True)
        for label,delta in [('expired lease',{'now':21}),('stale fence',{'w.fence':3}),('unrelated effect same fence',{'effect_id':'effect-B'}),('renewed live lease',{'w.lease_expires_at':30}),('same transaction completion',{'w.state':'completed','allow_completed':True})]:
            case(label,node,facts|delta,label in ['renewed live lease','same transaction completion'])
    transition=body('runtime_transition')
    need('OLD.effect_receipt_id IS NOT NULL' in transition and 'worker_effect_matches(OLD.id,NEW.effect_receipt_id,false)' in transition,'one protected effect link missing')
    need('NEW.lease_expires_at<=OLD.lease_expires_at' in transition and 'runtime.renew_work.v1' in transition,'renewal not constrained')
    recovery=body('worker_track_allowed').split("ELSIF model_name='RuntimeEffectReceipt' THEN",1)[-1].split("ELSIF model_name='RuntimeInboxReceipt'",1)[0]
    recovery_condition=re.search(r'RETURN COALESCE\((.*),false\);',recovery,re.S)
    need(recovery_condition is not None and "verb='SELECT'" in recovery and 'worker_effect_matches' in recovery,'old exact committed effect cannot be read after reclaim')
    if recovery_condition:
        facts={'row_value':{'id':'effect-A','command_receipt_id':'command-A','owner_module_id':'track_subscription_entitlement','operation':'assignDefaultFreeTrack.v1','subject_scope':'CustomerProfile:customer-A','semantic_effect_key':'semantic-A','fingerprint':'hash-A','fence':2},'w.id':'job-A','g.allowed_fields':['RuntimeWorkItem/job-A/effect/effect-A','RuntimeWorkItem/job-A/command/command-A'],'scope':'CustomerProfile:customer-A','expected_effect':'semantic-A','o.payload_hash':'hash-A','w.fence':2,'verb':'INSERT','exact_linked_committed_effect':False}
        node=expression('COALESCE('+recovery_condition[1]+',false)')
        case('new current-fence effect insert valid',node,facts,True)
        case('old linked committed effect read after reclaim',node,facts|{'w.fence':3,'verb':'SELECT','exact_linked_committed_effect':True},True)
        case('old effect cannot be inserted after reclaim',node,facts|{'w.fence':3,'exact_linked_committed_effect':True},False)
        case('foreign old effect cannot be read after reclaim',node,facts|{'w.fence':3,'verb':'SELECT'},False)
    need('NEW.fence<>OLD.fence+1' in transition and 'OLD.lease_expires_at>clock_timestamp()' in transition,'reclaim cannot fence old worker')
    need('ELSIF NEW.fence<>OLD.fence OR NEW.attempt_count<>OLD.attempt_count' in transition,'attempt changes outside claim')
    need('NEW.lease_expires_at<=clock_timestamp()' in transition,'claim accepts expired lease')
    need("NEW.state<>'active' OR NEW.effect_receipt_id IS NOT NULL" in transition,'reservation can start terminal')
    need('reservation_transition BEFORE INSERT OR UPDATE' in app,'reservation insert entry guard not wired')
    need('NEW."quantity" IS DISTINCT FROM OLD."quantity"' in body('guard_runtimereservation'),'unknown reservation quantity can shrink')
    entry=re.search(r"IF (NEW.state<>'active' OR NEW.effect_receipt_id IS NOT NULL)",transition)
    if entry:
        for state,effect,denied in [('active',None,False),('unknown',None,True),('released',None,True),('committed','effect-A',True),('active','effect-A',True)]:
            case('reservation initial '+state+' '+str(effect),expression(entry[1]),{'new.state':state,'new.effect_receipt_id':effect},denied)
    quantity=expression('NEW."quantity" IS DISTINCT FROM OLD."quantity"')
    case('uncertain reservation quantity preserved',quantity,{'new.quantity':10,'old.quantity':10},False)
    case('uncertain reservation quantity reduction denied',quantity,{'new.quantity':1,'old.quantity':10},True)
    need('OLD.state=\'unknown\' AND NEW.state IN (\'unknown\',\'committed\',\'released\')' in transition,'unknown -> active release bypass')
    allowed=expression("(old.state='active' AND new.state IN ('active','unknown','committed','released')) OR (old.state='unknown' AND new.state IN ('unknown','committed','released'))")
    # The independently enumerated transition matrix must equal the literal SQL guard.
    need("IF NOT ((OLD.state='active' AND NEW.state IN ('active','unknown','committed','released'))" in transition,'transition matrix differs from reviewed fixture')
    for a,b,ok in [('active','unknown',True),('unknown','released',True),('unknown','active',False),('released','active',False),('committed','released',False)]:case('reservation '+a+' -> '+b,allowed,{'old.state':a,'new.state':b},ok)
    for token in ['e.command_receipt_id IS DISTINCT FROM NEW.command_receipt_id','e.owner_module_id<>NEW.owner_module_id','e.operation<>c.operation','e.fingerprint<>c.fingerprint',"e.subject_scope<>'RuntimeReservation:'||NEW.id::text",'e.semantic_effect_key<>NEW.semantic_key',"c.state<>'fenced_noncommit'"]:
        need(token in transition,'reservation proof binding missing '+token)
    release=re.search(r'IF (e.command_receipt_id IS DISTINCT FROM NEW.command_receipt_id.*?)\n\s*THEN RAISE EXCEPTION \'reservation outcome',transition,re.S)
    if release:
        f={'e.command_receipt_id':'command-A','new.command_receipt_id':'command-A','e.owner_module_id':'owner-A','c.owner_module_id':'owner-A','new.owner_module_id':'owner-A','e.operation':'operation-A','c.operation':'operation-A','e.fingerprint':'hash-A','c.fingerprint':'hash-A','e.fence':3,'new.fence':3,'e.subject_scope':'RuntimeReservation:reservation-A','c.subject_scope':'RuntimeReservation:reservation-A','new.id':'reservation-A','e.semantic_effect_key':'reserve-A','c.semantic_key':'reserve-A','new.semantic_key':'reserve-A','new.state':'released','e.state':'fenced_noncommit','c.state':'fenced_noncommit','e.mutation_transaction_id':'tx-A','c.mutation_transaction_id':'tx-A','xid':'tx-A'}
        node=expression(release[1]);case('exact durable noncommit release valid',node,f,False)
        for name,delta in [('different operation release denied',{'e.operation':'operation-B'}),('different command release denied',{'e.command_receipt_id':'command-B'}),('NULL command release denied',{'e.command_receipt_id':None}),('foreign reservation receipt denied',{'new.id':'reservation-B'}),('foreign semantic identity denied',{'e.semantic_effect_key':'reserve-B'}),('unresolved command release denied',{'c.state':'unknown'}),('wrong reservation fence denied',{'e.fence':4}),('foreign command subject denied',{'c.subject_scope':'RuntimeReservation:reservation-B'}),('foreign command semantic key denied',{'c.semantic_key':'reserve-B'}),('foreign command owner denied',{'c.owner_module_id':'owner-B'})]:case(name,node,f|delta,True)
    else:need(False,'exact release proof predicate not found')
    need('platform_private.worker_effect_matches' in body('effect_fence_guard'),'effect fence compares only number')
    for token in ['e.semantic_effect_key=w.semantic_work_key','e.operation=w.handler_name','c.operation=e.operation','e.fingerprint=o.payload_hash','i.outbox_message_id=o.id']:need(token in body('worker_effect_matches'),'unrelated effect can complete: '+token)
    match=re.search(r'RETURN COALESCE\((.*),false\);',body('worker_effect_matches'),re.S)
    if match:
        f={'require_link':True,'w.effect_receipt_id':'effect-A','e.id':'effect-A','w.id':'job-A','c.id':'command-A','g.allowed_fields':['RuntimeWorkItem/job-A/effect/effect-A','RuntimeWorkItem/job-A/command/command-A'],'e.owner_module_id':'track_subscription_entitlement','c.owner_module_id':'track_subscription_entitlement','e.operation':'assignDefaultFreeTrack.v1','w.handler_name':'assignDefaultFreeTrack.v1','c.operation':'assignDefaultFreeTrack.v1','e.state':'committed','c.state':'committed','e.subject_scope':'CustomerProfile:customer-A','o.aggregate_id':'customer-A','c.subject_scope':'CustomerProfile:customer-A','e.semantic_effect_key':'source-A','w.semantic_work_key':'source-A','c.semantic_key':'source-A','e.fingerprint':'hash-A','o.payload_hash':'hash-A','c.fingerprint':'hash-A','e.fence':2,'w.fence':2,'e.mutation_transaction_id':'tx-A','c.mutation_transaction_id':'tx-A','existing_exact_inbox_or_history':True}
        node=expression('COALESCE('+match[1]+',false)')
        case('matching committed work effect valid',node,f,True)
        for name,delta in [('same fence foreign effect key',{'e.semantic_effect_key':'source-B','c.semantic_key':'source-B'}),('foreign operation receipt',{'c.operation':'other_operation'}),('wrong customer message',{'o.aggregate_id':'customer-B'}),('wrong job receipt capability',{'w.id':'job-B'}),('missing exact inbox',{'existing_exact_inbox_or_history':False}),('reclaimed worker recognizes original committed effect',{'w.fence':3})]:
            case(name,node,f|delta,name.startswith('reclaimed'))
    # Both directions: required messages exist AND every message traces exact source.
    for token in ['e.previous_revision IS NOT NULL','h.from_status IS NOT NULL','NEW.ordinal<>1','NEW.payload->>\'userId\'<>c.user_id::text','count(*)']:
        need(token in body('customer_message_commit'),'extra message escapes source check '+token)
    need('extra or missing Customer messages' in body('customer_atomic'),'allowed source message count missing')
    need('CREATE CONSTRAINT TRIGGER exact_customer_message AFTER INSERT ON platform.runtime_outbox_message' in app,'message reverse guard not wired')
    need("CHECK (result_schema_version='1')" in app,'command result version not enforced')
    version=constraints['result_version_registered'].raw_expr
    case('registered command result version valid',version,{'result_schema_version':'1'},True)
    case('wrong command result version denied',version,{'result_schema_version':'2'},False)
    message=re.search(r'IF (c.revision<>NEW.source_revision.*?)\n\s*THEN RAISE EXCEPTION',body('customer_message_commit'),re.S)
    need(message is not None,'exact reverse message predicate missing')
    if message:
        f={'c.revision':0,'new.source_revision':0,'c.privacy_generation':0,'new.source_generation':0,'c.mutation_transaction_id':'tx-A','new.mutation_transaction_id':'tx-A','xid':'tx-A','h.name':'customer.lifecycle_changed.v1','h.to_status':'active','c.status':'active','h.actor_user_id':'user-A','c.user_id':'user-A','new.payload':{'userId':'user-A','safeState':'active'},'new.kind':'event','new.name':'customer.lifecycle_changed.v1','new.ordinal':0,'e.previous_revision':None,'h.from_status':None,'scalar_subquery':2}
        node=expression(message[1]);case('create lifecycle message valid',node,f,False)
        command=f|{'new.kind':'command','new.name':'assignDefaultFreeTrack.v1','new.ordinal':1,'new.payload':{'userId':'user-A','customerProfileId':'customer-A','sourceCreationRevision':'0','sourceCreationReceipt':'command-A','semanticKey':'customer_buyer_profile/customer-A/default-free-enrollment/v1'}}
        case('create Free enrollment message valid',node,command,False)
        update=f|{'c.revision':1,'new.source_revision':1,'e.previous_revision':0,'h.from_status':'active','scalar_subquery':1}
        case('update lifecycle message valid',node,update,False)
        case('extra Free command beside valid update denied',node,update|{'new.kind':'command','new.name':'assignDefaultFreeTrack.v1','new.ordinal':1,'scalar_subquery':2},True)
        for label,delta in [('wrong user',{'new.payload':{'userId':'user-B','safeState':'active'}}),('wrong revision',{'new.source_revision':2}),('wrong generation',{'new.source_generation':1}),('wrong transaction',{'new.mutation_transaction_id':'tx-B'}),('extra emitted message',{'scalar_subquery':3}),('wrong event ordinal',{'new.ordinal':1})]:
            case('Customer message '+label,node,f|delta,True)
    need('GRANTED BY CURRENT_USER' in cleanup and 'm.grantor<>principal' in cleanup,'cleanup lacks authorized grantor')
    need('REVOKE wa_private_helper_owner FROM wa_schema_owner;' not in app,'ADMIN FALSE owner attempts cleanup')
    need('temporary installation membership remains' in cleanup,'cleanup not verified on success/failure')
    need('REVOKE wa_private_helper_owner,wa_customer_verifier,wa_track_verifier FROM wa_schema_owner GRANTED BY CURRENT_USER;' in cleanup,'not all temporary memberships cleaned')
    for (_,table),columns in tables.items():
        if table.startswith('identity_service_'):
            need('ALTER TABLE platform_private.'+table+' FORCE ROW LEVEL SECURITY;' in app,'private Identity RLS missing '+table)
    need(not re.search(r'OLD\.lease_token_hash::text\s*\)',body('runtime_transition')) or 'lease_secret_matches' in transition,'lease hash used as bearer proof')
    return {'status':'FAIL' if errors else 'PASS','scope':'OFFLINE_AST_SCALAR_PREDICATES_AND_SOURCE_GRAPH_ONLY','predicate_cases':len(cases),'cases':cases,'errors':errors,'database_contacted':False,'sql_executed':False,'database_runtime_cases':'451_NOT_RUN'}


if __name__=='__main__':
    result=inspect();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
