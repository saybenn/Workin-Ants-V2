"""Projection-aware process mocks, not Postgres or runtime qualification."""
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime,timedelta,timezone
import importlib.util
import io
import json
from pathlib import Path
import re
import runpy
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch,Mock
from pglast import ast,parse_sql
from pglast.stream import RawStream

ROOT=Path(__file__).resolve().parents[1];TASK=ROOT.parent
sys.path.insert(0,str(ROOT/'scripts'))
import worker_recovery_control_protocol as P
M=runpy.run_path(str(ROOT/'scripts/sql-review/run-worker-recovery-control-rehearsal.py'))
spec=importlib.util.spec_from_file_location('worker_recovery_mock_generator',ROOT/'scripts/prepare-worker-recovery-control-rehearsal.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
CANARY='PRIVATE_PASSWORD_LEASE_HANDLE_STDERR_CANARY';CID='a'*64

class SqlFailure(Exception):
 def __init__(self,state,message,function=None):self.state,self.message,self.function=state,message,function

class Transport:
 """Finite SQL-shape interpreter; never copies case.expected_records.

 Only emitted statements are admitted. This cannot qualify PostgreSQL, its
 JSON storage codec or its deferred guards; it tests coordinator control flow.
 """
 def __init__(self,packet):
  self.packet=packet;self.events=[];self.coordinator=None;self.sequence=0;self.now=0.;self.sessions=[];self.rows={t:{} for t in packet['setup_expected_counts']};self.disabled=set();self.native_mutant=None;self.fail_case=None;self.expire_grant_case=None;self.other_clients=0;self.close_failure=False;self.issued={};self.clock_calls=0;self.recapture_mutant=False;self.reclaim_extra=False;self.clock_reply_delays=[];self.delay_on_expired=0.;self.enforce_clock_timeout=False;self.clock_budgets=[];self.late_before_reclaim=False;self.clock_trip=0;self.holder_reply_delay=0.;self.sleep_calls=[]
  self.acl=packet['worker_acl_rows'];self.by_table={v['object']:k for k,v in packet['models'].items()};self.application=(ROOT/M['APPLICATION']).read_text();self.clock_origin=datetime(2026,11,19,12,tzinfo=timezone.utc)
 def clock(self):
  if self.clock_trip:
   self.clock_trip-=1
   if not self.clock_trip:self.now+=16
  return self.now
 def sleep(self,seconds):self.sleep_calls.append(seconds);self.now+=seconds
 def timestamp(self,delta=0):return (self.clock_origin+timedelta(seconds=self.now+delta)).isoformat()
 def table(self,node):return node.schemaname+'.'+node.relname
 def view(self,session,table):
  rows=deepcopy(self.rows[table])
  if session:rows.update(deepcopy(session.pending.get(table,{})))
  return rows
 def values(self,session):return {k:self.expression(parse_sql('SELECT '+v)[0].stmt.targetList[0].val,session) for k,v in session.bound['values'].items()}
 def work(self,session,key):return self.view(session,'platform.runtime_work_item').get(key)
 def lease_valid(self,session,key):
  if not session or not session.bound:return False
  w=self.work(session,key);v=self.values(session)
  return bool(w and session.role=='wa_worker' and v['target_kind']=='RuntimeWorkItem' and v['target_id']==key and w['state'] in ('leased','completed') and (w['state']!='completed' or w['mutation_transaction_id']==session.backend['xid']) and w['fence']==v['source_generation']==int(session.fence or -1) and w['lease_expires_at']>self.now and w['lease_token_hash']==P.sha(bytes.fromhex(session.lease)) and self.rows['platform_private.identity_service_authorization'])
 def effect_matches(self,session,work,effect,linked):
  w=self.work(session,work);e=self.view(session,'platform.runtime_effect_receipt').get(effect)
  if not self.lease_valid(session,work) or not e:return False
  cmd=self.view(session,'platform.runtime_command_receipt').get(e['command_receipt_id']);out=self.view(session,'platform.runtime_outbox_message').get(w['outbox_message_id']);inbox=[r for r in self.view(session,'platform.runtime_inbox_receipt').values() if r['effect_receipt_id']==effect and r['outbox_message_id']==w['outbox_message_id']]
  return bool(cmd and out and cmd['state']=='committed' and cmd['subject_scope']=='CustomerProfile:'+out['aggregate_id'] and e['fence']<=w['fence'] and len(inbox)==1 and inbox[0]['mutation_transaction_id']==cmd['mutation_transaction_id']==e['mutation_transaction_id'] and (not linked or w['effect_receipt_id']==effect))
 def visible(self,session,table,row):
  if not session or session.role!='wa_worker':return True
  v=self.values(session);w=self.work(session,v['target_id']);model=self.by_table[table];key=row['id'];caps=v['allowed_fields'];acl=next((x for x in self.acl if (x['model'],x['operation'])==(model,'SELECT')),None)
  if not acl or not self.lease_valid(session,v['target_id']) or not all(model+'/'+key+'/SELECT/'+f in caps for f in acl['fields']):return False
  revision={'RuntimeWorkItem':'fence','RuntimeEffectReceipt':'fence','RuntimeAttempt':'fence','TrackSubscription':'revision','TrackEntitlementGrant':'revision','TrackBaseSelection':'revision'}.get(model)
  if revision and model+'/'+key+'/revision/'+str(row.get(revision,0)) not in caps:return False
  if table=='platform.runtime_work_item':return key==v['target_id']
  if table=='platform.runtime_outbox_message':return key==w['outbox_message_id']
  customer=self.view(session,'platform.runtime_outbox_message')[w['outbox_message_id']]['aggregate_id']
  if table=='platform.runtime_attempt':return row['work_item_id']==w['id'] and row['fence']==w['fence']
  if table=='platform.runtime_inbox_receipt':return row['outbox_message_id']==w['outbox_message_id']
  if table=='platform.runtime_effect_receipt':return self.effect_matches(session,w['id'],key,False)
  if table=='platform.runtime_command_receipt':return row['subject_scope']=='CustomerProfile:'+customer
  if table=='platform.owner_mutation_evidence':return row['command_receipt_id'] in {e['command_receipt_id'] for e in self.view(session,'platform.runtime_effect_receipt').values() if e['id']==w['effect_receipt_id']}
  return row.get('customer_profile_id',row.get('profile_id'))==customer
 def expression(self,node,session=None,row=None,ctes=None):
  if node is None:return None
  if isinstance(node,ast.A_Const):return None if node.isnull else node.val.sval if isinstance(node.val,ast.String) else node.val.ival if isinstance(node.val,ast.Integer) else node.val.boolval if isinstance(node.val,ast.Boolean) else float(node.val.fval)
  if isinstance(node,ast.TypeCast):
   value=self.expression(node.arg,session,row,ctes);names=[x.sval for x in node.typeName.names]
   if value is not None and names[-1] in ('jsonb','json'):return json.loads(value)
   if value is not None and names[-1]=='interval':return float(value.split()[0])*(.001 if 'millisecond' in value else 1)
   return value
  if isinstance(node,ast.A_ArrayExpr):return [self.expression(x,session,row,ctes) for x in node.elements]
  if isinstance(node,ast.ColumnRef):return (row or {})[node.fields[-1].sval]
  if isinstance(node,ast.NullTest):return (self.expression(node.arg,session,row,ctes) is None)==(node.nulltesttype.name=='IS_NULL')
  if isinstance(node,ast.BoolExpr):
   vals=[self.expression(x,session,row,ctes) for x in node.args];return not vals[0] if node.boolop.name=='NOT_EXPR' else all(vals) if node.boolop.name=='AND_EXPR' else any(vals)
  if isinstance(node,ast.A_Expr):
   a=self.expression(node.lexpr,session,row,ctes);b=self.expression(node.rexpr,session,row,ctes);op=node.name[0].sval
   if node.kind.name=='AEXPR_NOT_DISTINCT':return a==b
   if op=='=':return a==b
   if op=='+':
    return (datetime.fromisoformat(a)+timedelta(seconds=b)).isoformat() if isinstance(a,str) and isinstance(b,float) else a+b
   if op=='-':return a-b
   if op=='>':return a>b
   if op=='>=':return a>=b
   if op=='<=':return a<=b
   if op=='<':return a<b
   if op=='||':return str(a)+str(b)
   raise AssertionError('UNREGISTERED_EXPRESSION_OPERATOR')
  if isinstance(node,ast.SubLink):return self.select(node.subselect,session,ctes)
  if isinstance(node,ast.FuncCall):
   name=node.funcname[-1].sval
   if name=='count':return len((row or {}).get('_aggregate',[]))
   if name=='bool_and':return all(self.expression(node.args[0],session,r,ctes) for r in (row or {}).get('_aggregate',[])) if (row or {}).get('_aggregate') else None
   args=[self.expression(x,session,row,ctes) for x in (node.args or ())]
   if name=='jsonb_build_object':return dict(zip(args[::2],args[1::2]))
   if name=='current_setting':return session.lease if args[0]=='wa.lease_secret' else session.fence
   if name=='clock_timestamp':return self.now
   if name=='decode':return bytes.fromhex(args[0])
   if name=='sha256':return bytes.fromhex(P.sha(args[0].encode() if isinstance(args[0],str) else args[0]))
   if name=='encode':return args[0].hex()
   if name=='convert_to':return P.canonical(args[0]).encode() if isinstance(args[0],dict) else args[0].encode()
   if name=='worker_lease_valid':return self.lease_valid(session,args[0])
   if name=='worker_effect_matches':return self.effect_matches(session,args[0],args[1],args[2])
   raise AssertionError('UNREGISTERED_FUNCTION_'+name)
  if isinstance(node,ast.CoalesceExpr):return next((x for a in node.args if (x:=self.expression(a,session,row,ctes)) is not None),None)
  raise AssertionError('UNREGISTERED_EXPRESSION_'+type(node).__name__)
 def select(self,node,session,ctes=None):
  ctes=dict(ctes or {})
  if node.withClause:
   for cte in node.withClause.ctes:ctes[cte.ctename]=self.statement(cte.ctequery,session)
  rows=[{}]
  if node.fromClause:
   relation=node.fromClause[0]
   if relation.relname in ctes:rows=ctes[relation.relname]
   else:
    table=self.table(relation);rows=[r for r in self.view(session,table).values() if self.visible(session,table,r)]
   rows=[r for r in rows if node.whereClause is None or self.expression(node.whereClause,session,r,ctes)]
  expr=node.targetList[0].val;aggregate='count(' in RawStream()(expr) or 'bool_and(' in RawStream()(expr)
  if aggregate:return self.expression(expr,session,{'_aggregate':rows},ctes)
  return self.expression(expr,session,rows[0],ctes) if rows else None
 def statement(self,node,session):
  if isinstance(node,ast.InsertStmt):
   table=self.table(node.relation);values={col.name:self.expression(value,session) for col,value in zip(node.cols,node.selectStmt.valuesLists[0])};values['mutation_transaction_id']=session.backend['xid'];key=values.get('id',values.get('service_principal'))
   if table=='app.track_subscriptions' and session.role=='wa_worker' and any(r['user_id']==values['user_id'] and r['status']=='active' for r in self.view(session,table).values()):raise SqlFailure('42501','new row violates row-level security policy for table "track_subscriptions"')
   if key in self.view(session,table):raise SqlFailure('23505','mock duplicate key')
   if table=='platform.runtime_work_item':values.update(lease_token_hash=None,lease_expires_at=None,effect_receipt_id=None)
   if table in ('app.track_subscriptions','app.track_entitlement_grants','app.track_base_selection'):values.setdefault('revision',0)
   if table=='platform.database_action_grant':values['created_at']=self.timestamp(.001);self.issued[key]=values
   session.pending.setdefault(table,{})[key]=values;return {'created_at':values['created_at']} if table=='platform.database_action_grant' else []
  if isinstance(node,ast.UpdateStmt):
   table=self.table(node.relation);changed=[]
   for key,row in self.view(session,table).items():
    if node.whereClause and not self.expression(node.whereClause,session,row):continue
    updates={t.name:self.expression(t.val,session,row) for t in node.targetList}
    if table=='platform.runtime_work_item':
     if 'fence' in updates:
      v=self.values(session);old=row['fence'];allowed=(row['state']=='pending' or row['state']=='leased' and row['lease_expires_at']<=self.now) and v['source_generation']==old and 'RuntimeWorkItem/'+key+'/revision/'+str(old) in v['allowed_fields']
      if not allowed:continue
     elif not self.lease_valid(session,key):continue
     elif row['state']=='completed':raise SqlFailure('P0001','terminal work/regressive attempt','runtime_transition')
     elif 'effect_receipt_id' in updates and (row['effect_receipt_id'] is not None or not self.effect_matches(session,key,updates['effect_receipt_id'],False)):raise SqlFailure('P0001','effect link must be one exact protected attachment','runtime_transition')
     elif updates.get('state')=='completed' and not self.effect_matches(session,key,row['effect_receipt_id'],True):raise SqlFailure('P0001','mock completion without effect')
    if table=='platform.runtime_command_receipt' and session.role=='wa_worker':
     v=self.values(session)
     if not self.lease_valid(session,v['target_id']) or any('RuntimeCommandReceipt/'+key+'/UPDATE/'+re.sub(r'_([a-z])',lambda m:m[1].upper(),field) not in v['allowed_fields'] for field in ('@row',*updates)):continue
    row.update(updates,mutation_transaction_id=session.backend['xid']);session.pending.setdefault(table,{})[key]=row;changed.append({'id':key})
   return changed
  if isinstance(node,ast.SelectStmt):return self.select(node,session)
  raise AssertionError('UNREGISTERED_STATEMENT_'+type(node).__name__)
 def diagnostic(self,error):
  result='ERROR:  '+error.state+': '+error.message+'\n'
  if error.function:
   body=re.search(r'CREATE FUNCTION platform_private\.'+error.function+r'\(\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',self.application,re.S)[2];line=next(i for i,x in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+P.quote(error.message) in x)
   return result+'CONTEXT:  PL/pgSQL function platform_private.'+error.function+'() line '+str(line)+' at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:3911\n'
  return result+'LOCATION:  ExecWithCheckOptions, execMain.c:2231\n'
 def commit(self,session):
  for effect in session.pending.get('platform.runtime_effect_receipt',{}).values():
   work=next((w for w in self.view(session,'platform.runtime_work_item').values() if w['effect_receipt_id']==effect['id']),None)
   if not work or not session.flushed or not self.effect_matches(session,work['id'],effect['id'],True):raise SqlFailure('P0001','mock deferred genuine effect group missing')
   for table,column in [('app.track_enrollment_receipt','effect_receipt_id'),('platform.runtime_attempt','work_item_id')]:
    wanted=effect['id'] if column=='effect_receipt_id' else work['id']
    if not any(r[column]==wanted for r in self.view(session,table).values()):raise SqlFailure('P0001','mock deferred business proof missing')
  for table,rows in session.pending.items():self.rows[table].update(deepcopy(rows))
  session.pending={};session.active=False;self.events.append(('commit',session.role,session.backend['pid'],session.backend['xid']))
 def raw(self,args,**options):
  text=options['input'];self.events.append(('raw',text));c=self.coordinator;active=[s for s in self.sessions if not s.closed];value=None
  if "'other_clients'" in text:value={'other_clients':len(active)+self.other_clients}
  elif "'only_exact_participants'" in text:value={'clients':len(active)+self.other_clients+int(self.reclaim_extra),'only_exact_participants':not self.reclaim_extra and len(active)==2 and all(s.role=='wa_worker' and 'pid='+s.backend['pid'] in text and P.quote(s.backend['started']) in text for s in active)}
  elif "'issuer_owned'" in text:
   ids=re.findall(r" FROM platform.database_action_grant g WHERE g.id='([^']+)'",text);wanted=[r for r in self.rows['platform.database_action_grant'].values() if r['id'] in ids];expired=self.expire_grant_case is not None and self.expire_grant_case==c.evidence.value['current_case'];exact=True
   for identity in ids:
    instance=next((v for v in c.instances.values() if v['id']==identity),None);stored=self.rows['platform.database_action_grant'].get(identity)
    exact=exact and instance is not None and stored is not None and all(text.count('g.'+column+' IS NOT DISTINCT FROM (')==len(ids) for column in self.coordinator.context_columns)
    if instance and stored:
     parsed={k:self.expression(parse_sql('SELECT '+v)[0].stmt.targetList[0].val) for k,v in instance['values'].items()};exact=exact and all(parsed[k]==stored[k] for k in parsed)
   value={'count':len(wanted),'exact':bool(exact),'issuer_owned':all(r['issuer_service']=='wa_context_issuer' for r in wanted),'unrevoked':all(r['revoked_at'] is None for r in wanted),'unexpired':not expired and all(datetime.fromisoformat(r['expires_at'])>self.clock_origin+timedelta(seconds=self.now) for r in wanted)}
  elif text==c.text('complete-state-observe.sql'):
   assert not active,'OBSERVATION_BEFORE_CLOSURE';value={t:{'count':len(rows),'rows_sha256':P.digest(sorted(rows.values(),key=P.canonical))} for t,rows in self.rows.items()}
  elif 'workinants.native-catalog.v1' in text:
   value=deepcopy(c.native)
   for row in value['triggers']:
    if row['table_name'] in self.disabled and row['name']=='owner_commit':row['enabled']='D'
   if self.native_mutant:self.native_mutant(value)
  elif text==c.text('A-clock.sql'):
   self.clock_calls+=1;w=self.rows['platform.runtime_work_item'][self.packet['roots']['A']['ids']['work']];value={'near_expiry':w['lease_expires_at']<=self.now+5,'expired':w['lease_expires_at']<=self.now,'fence1':w['fence']==1,'attempt1':w['attempt_count']==1,'exact_effect':w['effect_receipt_id']==self.packet['roots']['A']['ids']['effect']}
   delay=self.clock_reply_delays.pop(0) if self.clock_reply_delays else self.delay_on_expired if value['expired'] else 0.;self.clock_budgets.append({'started':self.now,'timeout':options['timeout'],'reply_delay':delay});self.now+=delay
   if self.enforce_clock_timeout and delay>options['timeout']:raise subprocess.TimeoutExpired('MOCK_CLOCK',options['timeout'],output=CANARY,stderr=CANARY)
   if value['expired'] and self.late_before_reclaim:self.late_before_reclaim=False;self.clock_trip=2
  elif "'live_exact_holder'" in text:
   key=re.search(r"WHERE id='([^']+)';$",text)[1];w=self.rows['platform.runtime_work_item'].get(key);fence=int(re.search(r'AND fence=([0-9]+)',text)[1]);secret_hash=re.search(r"lease_token_hash='([^']+)'",text)[1];state=re.search(r"bool_and\(state='([^']+)'",text)[1];value={'work':int(w is not None),'live_exact_holder':bool(w and w['state']==state and w['fence']==w['attempt_count']==fence and w['lease_token_hash']==secret_hash and w['lease_expires_at']>self.now),'service_epoch_current':bool(self.rows['platform_private.identity_service_authorization'])}
   self.now+=self.holder_reply_delay;self.holder_reply_delay=0.
  elif text.startswith("SELECT jsonb_build_object('count'"):value=self.select(parse_sql(text)[0].stmt,None)
  elif text.startswith('SELECT EXISTS(SELECT 1 FROM platform.runtime_attempt'):
   row=self.rows['platform.runtime_attempt'].get(self.packet['attempt2']);return types.SimpleNamespace(returncode=0,stdout='t' if row and row['attempt_number']==row['fence']==2 and row['worker_id']==self.packet['service_principal'] else 'f',stderr='')
  elif "jsonb_build_object('customer'" in text:
   key=re.search(r"app.customer_profiles WHERE id='([^']+)'",text)[1];r=self.rows['app.customer_profiles'].get(key);commands=[x for x in self.rows['platform.runtime_command_receipt'].values() if x['subject_scope']=='CustomerProfile:'+key];history=[x for x in self.rows['app.customer_profile_lifecycle_event'].values() if x['customer_profile_id']==key];evidence=[x for x in self.rows['platform.owner_mutation_evidence'].values() if x['aggregate_id']==key];outbox=[x for x in self.rows['platform.runtime_outbox_message'].values() if x['aggregate_id']==key];value={'customer':int(r is not None),'command':len(commands),'history':len(history),'evidence':len(evidence),'outbox':len(outbox),'track_enrollments':sum(x['profile_id']==key for x in self.rows['app.track_enrollment_receipt'].values()),'coherent':bool(r and len(commands)==1 and len(history)==1 and len(evidence)==1 and len(outbox)==2 and all(x['mutation_transaction_id']==r['mutation_transaction_id'] for x in commands+history+evidence+outbox))}
  elif text.startswith('SELECT current_setting(') or text.startswith('SELECT NOT EXISTS('):return types.SimpleNamespace(returncode=0,stdout='t',stderr='')
  else:raise AssertionError('UNREGISTERED_RAW_SQL_BOUNDARY')
  return types.SimpleNamespace(returncode=0,stdout=json.dumps(value),stderr='')
 def session(self,role,c):
  outer=self;self.coordinator=c;self.sequence+=1;sequence=self.sequence
  class Session:
   def __init__(self):self.closed=False;self.role=role;self.active=False;self.bound=None;self.pending={};self.lease='00'*32;self.fence=None;self.flushed=False;self.captures=0;self.process=types.SimpleNamespace(returncode=None,poll=lambda:self.process.returncode)
   def begin(self,isolation):self.active=True;self.isolation=isolation;outer.events.append((role,'begin'))
   def capture(self):
    if not hasattr(self,'backend'):self.backend={'login':role,'current_user':role,'database':'wa_p0c_rehearsal','isolation':self.isolation,'pid':str(4000+sequence),'xid':str(10000+sequence),'started':outer.timestamp(),'clock':outer.timestamp()}
    self.captures+=1;outer.events.append((role,'capture'));value=deepcopy(self.backend)
    if outer.recapture_mutant and self.captures>1:value['xid']=str(int(value['xid'])+100000)
    return value
   def call(self,text):
    outer.events.append((role,'call',text));rows=[]
    if text.startswith('SELECT pg_current_xact_id()'):return ['t'],True,''
    if text.startswith('SELECT platform_private.bind_request_context('):
     secret=re.search(r"\('([^']+)'\)",text)[1];self.bound=next(v for v in c.instances.values() if v['secret']==secret)
     assert not any(s.role=='wa_context_issuer' and not s.closed for s in outer.sessions),'ISSUER_NOT_CLOSED_BEFORE_BIND'
     if '; SET LOCAL' not in text:return [],True,''
     text=text[text.index(' SET LOCAL'):]
    if outer.fail_case is not None and c.evidence.value['current_case']==outer.fail_case and text.startswith("SELECT 'WA_WR_BEFORE_"):self.process.returncode=3;return re.findall(r"SELECT '([^']+)';",text)[:1],False,CANARY
    try:
     for raw in parse_sql(text):
      node=raw.stmt
      if isinstance(node,ast.VariableSetStmt):
       if node.name=='wa.lease_secret':self.lease=outer.expression(node.args[0],self)
       elif node.name=='wa.fence':self.fence=outer.expression(node.args[0],self)
       continue
      if isinstance(node,ast.TransactionStmt):outer.commit(self);continue
      if isinstance(node,ast.ConstraintsSetStmt):self.flushed=True;continue
      if isinstance(node,ast.AlterTableStmt):
       table=outer.table(node.relation)
       if 'DISABLE' in RawStream()(node):outer.disabled.add(table)
       else:outer.disabled.discard(table)
       continue
      result=outer.statement(node,self)
      if isinstance(node,ast.SelectStmt) and result is not None:rows.append(json.dumps(result) if isinstance(result,(dict,list)) else str(result))
      if isinstance(node,ast.InsertStmt) and node.returningList:rows.append(json.dumps(result))
     return rows,True,''
    except SqlFailure as error:self.pending={};self.active=False;self.process.returncode=3;return rows,False,outer.diagnostic(error)
   def close(self):
    outer.events.append((role,'close'))
    if outer.close_failure and role=='wa_worker':raise M['HeldFailure']('MOCK_CLOSURE_UNCONFIRMED')
    self.closed=True;self.pending={};self.active=False
    if self.process.returncode is None:self.process.returncode=0
    return self.process.returncode
  value=Session();self.sessions.append(value);return value

class CoordinatorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.files,cls.packet=G.build();cls.application=(ROOT/M['APPLICATION']).read_text()
 def setUp(self):
  for name in ('run','Popen','call','check_call','check_output'):
   guard=patch.object(subprocess,name,side_effect=AssertionError('NO_UNMOCKED_PROCESS'));guard.start();self.addCleanup(guard.stop)
  guard=patch.object(socket,'create_connection',side_effect=AssertionError('NO_NETWORK'));guard.start();self.addCleanup(guard.stop)
  self.temp=tempfile.TemporaryDirectory(prefix='worker21-offline-',dir=TASK);self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name);self.packetdir=self.base/'packet';self.packetdir.mkdir()
  for name,text in self.files.items():(self.packetdir/name).write_text(text,encoding='utf8',newline='\n')
  guard=patch.dict(M['coordinate'].__globals__,PACKET=self.packetdir);guard.start();self.addCleanup(guard.stop)
  self.context=M['compiled']((ROOT/M['CONTEXT']).read_bytes(),M['CONTEXT']);self.context['load_helpers']({p:(ROOT/p).read_bytes() for p in M['HELPERS']});self.base_module=M['compiled']((ROOT/M['BASE']).read_bytes(),M['BASE'])
  self.native={'format':'workinants.native-catalog.v1','server_version_num':170011,'read_only':True,'collected_as':'postgres','collector_is_superuser':True,'functions':[{'object':'synthetic.function()','body_sha256':'e'*64}],'triggers':[{'table_name':table,'name':'owner_commit','enabled':'O','internal':False,'function_identity':'synthetic.commit_'+str(i)+'()','definition_sha256':'c'*64} for i,table in enumerate(P.FIXTURE_TABLES)]+[{'table_name':'app.users','name':'physical_guard','enabled':'O','internal':False,'function_identity':'synthetic.physical()'}]}
  self.plan={'run_id':'550e8400-e29b-41d4-a716-446655440000','source_commit':'b'*40,'source_tree':'c'*40,'packet_sha256':'d'*64,'reviewed_packet_sha256':P.sha(self.files['fixtures.json'].encode()),'reviewed_content_sha256':self.packet['source_only_packet_sha256'],'immutable_container_id':CID,'packet_files_sha256':{p:P.sha((ROOT/p).read_bytes()) for p in M['HELPERS']+(M['COLLECTOR'],)}}
  self.evidence=M['Evidence'](self.base/'evidence',self.plan,self.packet);self.transport=Transport(self.packet);self.coordinator=M['coordinator_type'](self.context,self.base_module)(self.plan,deepcopy(self.packet),self.native,{},self.evidence,P.__dict__,session_factory=self.transport.session,clock=self.transport.clock,sleep=self.transport.sleep);self.transport.coordinator=self.coordinator;self.coordinator.context_columns=self.context['GRANT_COLUMNS']
  guard=patch.object(subprocess,'run',side_effect=self.transport.raw);guard.start();self.addCleanup(guard.stop)
 def enable_preflight(self):
  self.coordinator.target={'target':{'container_name':'mock','volume_name':'mock-data','image':'pinned'}};host=self.context['HOST'];host['docker_json']=lambda *a:{};host['inspect_live']=lambda *a:{'container_id':CID};host['verify_image']=lambda *a:None;self.context['API']['authentication_preflight']=lambda evidence,container:evidence.value['authentication'].append({'status':'MOCK_PASS'})
 def outer(self,label='outer-evidence'):
  c=self.coordinator
  def factory(*args):c.evidence=args[4];return c
  with patch.dict(M['coordinate'].__globals__,load_inputs=lambda plan:(self.packet,self.native,{},P.__dict__,self.context,self.base_module),coordinator_type=lambda context,base:factory):return M['coordinate'](self.plan,self.base/label)
 def test_full_mock_pipeline21_genuine_checkpoint_before_clock_and_attempt3(self):
  self.enable_preflight();self.coordinator.execute();self.assertEqual(len(self.evidence.value['results']),21);self.assertTrue(self.coordinator.checkpoint_committed);self.assertTrue(self.coordinator.completed_a);self.assertEqual(len(self.transport.rows['platform.runtime_attempt']),3);self.assertEqual(len(self.transport.rows['app.track_subscriptions']),2);self.assertTrue(all(s.closed for s in self.transport.sessions));self.assertTrue(all(len(v['values'])==21 for v in self.coordinator.instances.values()))
  first_clock=next(i for i,e in enumerate(self.transport.events) if e[0]=='raw' and e[1]==self.coordinator.text('A-clock.sql'));effect_commit=next(i for i,e in enumerate(self.transport.events) if e[0]=='commit' and e[3]==self.coordinator.work_xids['B']);self.assertLess(effect_commit,first_clock)
  ordering=next(x for x in self.evidence.value['operations'] if x['stage']=='ACTUAL_RECLAIM_ORDERING');self.assertTrue(ordering['original_tuple_retained']);self.assertTrue(ordering['new_reclaim_commit_before_old_action']);self.assertTrue(ordering['old_current_unrevoked_unexpired_grant'])
 def mutate_sql(self,name,change):
  p=self.packetdir/name;p.write_text(change(p.read_text()),encoding='utf8',newline='\n');self.coordinator.packet['prepared_files_sha256'][name]=P.sha(p.read_bytes())
 def prepare_through(self,index):
  self.enable_preflight();self.coordinator.setup()
  for case in self.coordinator.packet['cases'][:index]:self.coordinator.run_case(case)
 def test_missing_inbox_first_group_stops_before_clock_or_recovery(self):
  self.enable_preflight();self.mutate_sql(self.packet['cases'][0]['sql'],lambda s:re.sub(r'^INSERT INTO platform.runtime_inbox_receipt.*\n','',s,flags=re.M));result=self.outer();self.assertFalse(self.coordinator.checkpoint_committed);self.assertEqual(result['results'],[]);self.assertEqual(self.transport.clock_calls,0);self.assertEqual(len(self.transport.rows['platform.runtime_effect_receipt']),1);self.assertEqual(len(self.transport.rows['app.track_subscriptions']),1);self.assertTrue(result['subsequent_cases_stopped'])
 def test_missing_deferred_flush_cannot_commit_genuine_checkpoint(self):
  self.enable_preflight();self.mutate_sql(self.packet['cases'][0]['sql'],lambda s:s.replace('SET CONSTRAINTS ALL IMMEDIATE;',''));result=self.outer();self.assertFalse(self.coordinator.checkpoint_committed);self.assertEqual(result['results'],[]);self.assertEqual(self.transport.clock_calls,0)
 def test_projection_mutation_is_not_copied_from_expected(self):
  self.prepare_through(1);case=self.packet['cases'][1];a=self.packet['roots']['A']['ids']['subscription'];b=self.packet['roots']['B']['ids']['subscription'];self.mutate_sql(case['sql'],lambda s:s.replace("id='"+b+"'","id='"+a+"'"))
  with self.assertRaises(P.HeldFailure):self.coordinator.run_case(case)
  self.assertEqual(len(self.evidence.value['results']),1)
 def test_current_read_requires_all_named_fields_and_revision(self):
  self.prepare_through(1);case=self.packet['cases'][1];grant=self.coordinator.packet['grants'][case['grant']];key=self.packet['roots']['A']['ids']['subscription']
  for token in ('TrackSubscription/'+key+'/SELECT/status','TrackSubscription/'+key+'/revision/0'):
   with self.subTest(token=token):
    old=list(grant['allowed_fields']);grant['allowed_fields']=[x for x in old if x!=token]
    with self.assertRaises(P.HeldFailure):self.coordinator.operation(case)
    grant['allowed_fields']=old
 def test_copied_hash_zero_has_independent_live_control_and_own_backend_closed(self):
  self.prepare_through(1);case=self.packet['cases'][11];self.coordinator.run_case(case);self.assertTrue(all(s.closed for s in self.transport.sessions));self.assertEqual(self.transport.rows['platform.runtime_work_item'][self.packet['roots']['A']['ids']['work']]['state'],'leased');self.assertTrue(any(x.get('stage')=='ACTUAL_HASH_READ' for x in self.evidence.value['operations']))
 def test_exact_guard_diagnostics_pass_and_generic_codes_or_raw_suffix_reject(self):
  for name in P.DIAGNOSTICS:
   state,message,function=P.DIAGNOSTICS[name];good=self.transport.diagnostic(SqlFailure(state,message,function));self.assertTrue(P.diagnostic(name,good,self.application)['matched'])
   for bad in ('ERROR:  P0001: unrelated\n','ERROR:  42501: unrelated\n',good+CANARY,good.replace('.c:', '.c, ')):
    self.assertFalse(P.diagnostic(name,bad,self.application)['matched'])
 def test_foreign_same_numeric_fence_rows_exist_before_relink_denial(self):
  self.prepare_through(1);a=self.transport.rows['platform.runtime_effect_receipt'][self.packet['roots']['A']['ids']['effect']];b=self.transport.rows['platform.runtime_effect_receipt'][self.packet['roots']['B']['ids']['effect']];self.assertEqual(a['fence'],b['fence']);self.assertNotEqual(a['command_receipt_id'],b['command_receipt_id'])
  for case in self.packet['cases'][12:14]:self.coordinator.run_case(case)
  c=self.transport.rows['platform.runtime_work_item'][self.packet['roots']['C']['ids']['work']];self.assertIsNone(c['effect_receipt_id'])
 def test_unexpected_result_preserves_prefix_stops_later_and_excludes_secrets(self):
  self.enable_preflight();self.transport.fail_case=self.packet['cases'][2]['name'];result=self.outer();self.assertEqual(len(result['results']),2);self.assertTrue(result['subsequent_cases_stopped']);self.assertNotIn(CANARY,json.dumps(result));self.assertEqual(self.transport.clock_calls,0);self.assertTrue(all(s.closed for s in self.transport.sessions))
  for value in list(self.coordinator.leases.values())+[v[k] for v in self.coordinator.instances.values() for k in ('secret','token_hash','id')]:self.assertNotIn(value,json.dumps(result))
 def test_expired_just_used_grant_stops_zero_negative(self):
  self.enable_preflight();self.transport.expire_grant_case=self.packet['cases'][11]['name'];result=self.outer();self.assertEqual(len(result['results']),11);self.assertTrue(result['subsequent_cases_stopped']);self.assertEqual(self.transport.clock_calls,0)
 def test_expired_lease_before_zero_negative_stops(self):
  self.prepare_through(1);w=self.transport.rows['platform.runtime_work_item'][self.packet['roots']['A']['ids']['work']];self.transport.now=w['lease_expires_at']+1
  with self.assertRaises(M['HeldFailure']):self.coordinator.run_case(self.packet['cases'][11])
  self.assertEqual(len(self.evidence.value['results']),1)
 def test_modified_issuer_field_rejects_all21_retention(self):
  self.prepare_through(1);key=next(iter(self.transport.rows['platform.database_action_grant']));self.transport.rows['platform.database_action_grant'][key]['purpose']='unrelated'
  with self.assertRaises(Exception) as error:self.coordinator.retention(list(self.coordinator.instances))
  self.assertEqual(error.exception.code,'IMMUTABLE_21_FIELD_ISSUER_RETENTION')
 def test_wrong_reclaim_predecessor_caps_produce_zero_and_never_promote_fence(self):
  self.prepare_through(1);g=self.coordinator.packet['grants']['A-reclaim'];work=self.packet['roots']['A']['ids']['work'];g['allowed_fields']=[x.replace('RuntimeWorkItem/'+work+'/revision/1','RuntimeWorkItem/'+work+'/revision/2') for x in g['allowed_fields']];g['allowed_fields'].sort()
  with self.assertRaises(P.HeldFailure):self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(self.transport.rows['platform.runtime_work_item'][work]['fence'],1);self.assertTrue(all(s.closed for s in self.transport.sessions))
 def test_terminal_error_rolls_back_then_once_completion_retains_original_effect(self):
  self.prepare_through(20);work=self.packet['roots']['A']['ids']['work'];row=self.transport.rows['platform.runtime_work_item'][work];self.assertEqual(row['state'],'leased');self.assertEqual(row['fence'],2);self.assertEqual(row['effect_receipt_id'],self.packet['roots']['A']['ids']['effect']);self.assertEqual(len(self.transport.rows['platform.runtime_attempt']),3)
  business={t:P.digest(list(self.transport.rows[t].values())) for t in ('app.track_subscriptions','app.track_enrollment_receipt','platform.runtime_effect_receipt','platform.runtime_inbox_receipt')};self.coordinator.run_case(self.packet['cases'][20]);self.assertEqual(self.transport.rows['platform.runtime_work_item'][work]['state'],'completed');self.assertEqual(business,{t:P.digest(list(self.transport.rows[t].values())) for t in business})
 def test_changed_original_transaction_tuple_after_reclaim_stops(self):
  self.prepare_through(1);self.transport.recapture_mutant=True
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'ORIGINAL_HOLDER_TUPLE_RETAINED');self.assertEqual(len(self.evidence.value['results']),1);self.assertTrue(all(s.closed for s in self.transport.sessions));self.assertEqual(self.coordinator.fences['A'],2)
 def test_third_client_in_reclaim_phase_denies_before_reclaim_SQL(self):
  self.prepare_through(1);self.transport.reclaim_extra=True
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'UNDECLARED_CLIENT_DURING_RECLAIM');self.assertEqual(self.coordinator.fences['A'],1);self.assertTrue(all(s.closed for s in self.transport.sessions))
 def near_expiry(self):
  self.prepare_through(1);self.transport.now=self.transport.rows['platform.runtime_work_item'][self.packet['roots']['A']['ids']['work']]['lease_expires_at']-4
 def assert_no_reclaim(self,event_start):
  self.assertFalse(any(len(e)>2 and e[0]=='wa_worker' and 'fence=fence+1' in e[2] for e in self.transport.events[event_start:]));self.assertEqual(self.coordinator.fences['A'],1);self.assertTrue(all(s.closed for s in self.transport.sessions))
 def test_actual_method_late_near_reply_stops_before_holder_setup(self):
  self.near_expiry();self.transport.clock_reply_delays=[151.];start=len(self.transport.events);session_count=len(self.transport.sessions)
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'ACTUAL_EXPIRY_BUDGET_EXHAUSTED');self.assertEqual(len(self.transport.sessions),session_count);self.assert_no_reclaim(start)
 def test_actual_method_late_expired_reply_stops_before_reclaim(self):
  self.near_expiry();self.transport.delay_on_expired=16.;start=len(self.transport.events)
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'ACTUAL_EXPIRY_NOT_OBSERVED');self.assert_no_reclaim(start);self.assertEqual(len(self.evidence.value['results']),1)
 def test_actual_clock_observer_timeout_uses_remaining_positive_budget_and_no_echo(self):
  self.near_expiry();self.transport.clock_reply_delays=[.3];self.transport.enforce_clock_timeout=True;deadline=self.transport.now+.25
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.clock_value(deadline,'ACTUAL_EXPIRY_NOT_OBSERVED')
  self.assertEqual(error.exception.code,'ACTUAL_CLOCK_OBSERVER_TIMEOUT');self.assertEqual(self.transport.clock_budgets[-1]['timeout'],.25);self.assertNotIn(CANARY,str(error.exception));self.assertNotIn(CANARY,json.dumps(self.evidence.value))
  start=self.transport.clock_calls
  with self.assertRaises(M['HeldFailure']):self.coordinator.clock_value(self.transport.now,'ACTUAL_EXPIRY_NOT_OBSERVED')
  self.assertEqual(self.transport.clock_calls,start)
 def test_actual_method_deadline_crossed_just_before_reclaim_stops(self):
  self.near_expiry();self.transport.late_before_reclaim=True;start=len(self.transport.events)
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'ACTUAL_EXPIRY_NOT_OBSERVED');self.assert_no_reclaim(start)
 def test_actual_method_slow_holder_observer_consumes_existing_window(self):
  self.near_expiry();self.transport.holder_reply_delay=16.;start=len(self.transport.events);session_count=len(self.transport.sessions)
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'ACTUAL_EXPIRY_NOT_OBSERVED');self.assertEqual(len(self.transport.sessions),session_count);self.assert_no_reclaim(start)
 def test_actual_method_bounded_sleeps_and_clock_timeouts_legitimate_reclaim(self):
  self.near_expiry();start=self.transport.now;self.coordinator.run_case(self.packet['cases'][14]);self.assertEqual(self.coordinator.fences['A'],2);self.assertLess(self.transport.now-start,15);self.assertTrue(all(0<x<=.1 for x in self.transport.sleep_calls));self.assertTrue(all(0<x['timeout']<=5 for x in self.transport.clock_budgets));self.assertTrue(all(s.closed for s in self.transport.sessions))
 def test_actual_method_sleep_is_clipped_to_last_remaining_inner_budget(self):
  self.near_expiry();self.transport.clock_reply_delays=[0.,14.95];start=len(self.transport.events)
  with self.assertRaises(M['HeldFailure']) as error:self.coordinator.run_case(self.packet['cases'][14])
  self.assertEqual(error.exception.code,'ACTUAL_EXPIRY_NOT_OBSERVED');self.assertTrue(0<self.transport.sleep_calls[-1]<.051);self.assertLessEqual(self.transport.now,131.00000001);self.assert_no_reclaim(start)
 def test_operation_close_failure_prevents_verdict_and_observation(self):
  self.prepare_through(1);self.transport.close_failure=True
  with self.assertRaises(M['HeldFailure']):self.coordinator.run_case(self.packet['cases'][1])
  self.assertEqual(len(self.evidence.value['results']),1);self.assertFalse(next(x for x in reversed(self.evidence.value['operations']) if x['stage']=='RESTRICTED_TRANSACTION')['operation_closed'])
 def test_lost_fixture_ACK_sets_restoration_obligation_before_attempt(self):
  self.enable_preflight();c=self.coordinator;old=c.fixture_commit
  def lost(name,label):
   old(name,label)
   if name=='independent-fixtures.sql':self.transport.disabled=set(P.FIXTURE_TABLES);raise M['HeldFailure']('ACK_LOST')
  c.fixture_commit=lost;result=self.outer();self.assertTrue(result['fixture_owner_bypass_restored']);self.assertEqual(self.transport.disabled,set());self.assertEqual(result['results'],[])
  gate=next(i for i,x in enumerate(result['operations']) if x['stage']=='PRE_RESTORATION_EXACT_FIVE_IDENTITY');restore=next(i for i,x in enumerate(result['operations']) if x['stage']=='FINALLY_EXACT_FIVE_FIXTURE_RESTORE');self.assertLess(gate,restore)
 def test_native_function_foreign_trigger_and_invalid_enable_states_block_restore(self):
  for mutate in (lambda d:d['functions'][0].update(body_sha256='f'*64),lambda d:d['triggers'][-1].update(function_identity='foreign()'),lambda d:d['triggers'][0].update(enabled='A'),lambda d:d['triggers'][0].update(enabled='R')):
   actual=deepcopy(self.native);mutate(actual)
   with self.assertRaises(P.HeldFailure):P.restoration_identity(self.native,actual)
  self.coordinator.bypass_open=True;self.transport.native_mutant=lambda d:d['functions'][0].update(body_sha256='f'*64);self.coordinator.execute=lambda:(_ for _ in ()).throw(M['HeldFailure']('STOP'));result=self.outer();self.assertFalse(result['fixture_owner_bypass_restored']);self.assertFalse(any(len(e)>2 and 'ENABLE TRIGGER owner_commit' in e[2] for e in self.transport.events))
 def test_persistent_evidence_IO_still_global_closes_and_exact_restores(self):
  c=self.coordinator;self.transport.disabled=set(P.FIXTURE_TABLES)
  def fail():c.bypass_open=True;c.evidence.stage('SOURCE_FAILURE')
  c.execute=fail;old=Path.replace;counter={'n':0};save=M['Evidence'].save
  def broken(path,target):
   if path.name=='worker-recovery-results.json.tmp':raise OSError(CANARY)
   return old(path,target)
  def save_wrapper(e):
   counter['n']+=1
   if counter['n']==1:return save(e)
   with patch.object(Path,'replace',broken):return save(e)
  with patch.object(M['Evidence'],'save',save_wrapper):result=self.outer()
  self.assertFalse(result['evidence_complete']);self.assertEqual(result['unexpected'][0]['code'],'SANITIZED_EVIDENCE_WRITE_UNCONFIRMED');self.assertTrue(result['fixture_owner_bypass_restored']);self.assertTrue(result['source_packet_unchanged_after']);self.assertEqual(self.transport.disabled,set());self.assertNotIn(CANARY,json.dumps(result))
 def test_unconfirmed_global_absence_blocks_restore_and_terminal_observers(self):
  self.coordinator.bypass_open=True;self.transport.other_clients=1;self.coordinator.execute=lambda:(_ for _ in ()).throw(M['HeldFailure']('STOP'));result=self.outer();self.assertFalse(result['fixture_owner_bypass_restored']);self.assertFalse(any(len(e)>2 and 'ENABLE TRIGGER owner_commit' in e[2] for e in self.transport.events));self.assertEqual(result['results'],[])
 def test_SQL_same_verified_bytes_and_second_read_drift(self):
  name=self.packet['cases'][0]['sql'];raw=(self.packetdir/name).read_bytes()
  with patch.object(Path,'read_text',side_effect=AssertionError('SECOND_READ')):self.assertEqual(self.coordinator.text(name),raw.decode())
  (self.packetdir/name).write_bytes(CANARY.encode())
  with self.assertRaises(M['HeldFailure']):self.coordinator.text(name)
 def test_driver_cannot_skip_genuine_checkpoint_or_expand_case_order(self):
  fake=types.SimpleNamespace(packet=deepcopy(self.packet),checkpoint_committed=False,run_case=Mock())
  with self.assertRaises(P.HeldFailure):P.finite_driver(fake)
  fake.run_case.assert_called_once();fake.packet['cases']=fake.packet['cases'][1:];fake.run_case.reset_mock()
  with self.assertRaises(P.HeldFailure):P.finite_driver(fake)
  fake.run_case.assert_not_called()
 def test_malformed_count_types_extra_records_and_wrong_markers_reject(self):
  case=self.packet['cases'][1];before=P.marker(case['name'],'BEFORE');after=P.marker(case['name'],'AFTER')
  for rows in ([before,'{"target_count":true,"foreign_count":0}',after],[before,'{"target_count":1,"foreign_count":0,"foreign_count":0}',after],[before,'{"target_count":1,"foreign_count":0}',after,'extra'],['wrong','{"target_count":1,"foreign_count":0}',after]):
   with self.assertRaises(P.HeldFailure):P.verdict(case,0,rows,True,'',self.application)

 def admitted_plan(self):
  plan=deepcopy(self.plan);pins={p:P.sha((ROOT/p).read_bytes()) for p in self.packet['source_files_sha256']}
  for name,text in self.files.items():pins['review-output/worker-recovery-control-rehearsal/'+name]=P.sha(text.encode())
  plan.update(schema='workinants.worker-recovery-run.v1',scope='REVIEWED_SELECTED94_WORKER_RECOVERY_SQL_SUBSET_ONLY',packet_files_sha256=pins,packet_sha256=P.sha(''.join(p+'\0'+pins[p]+'\n' for p in sorted(pins)).encode()),scenario_names=[c['name'] for c in self.packet['cases']])
  # Real pure target validator, with finite metadata only; no source helper mocked.
  history=self.context['HOST']['preparation'];plan['target_manifest']={'schema':'workinants.local-f0-run.v1','run_id':plan['run_id'],'purpose':'LOCAL_F0_MIGRATION_REHEARSAL','target':{'container_name':'wa-p0c-source-only-worker21','volume_name':'wa-p0c-source-only-worker21-data','database':'wa_p0c_rehearsal','image':history['IMAGE'],'network':'none','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':plan['run_id']},'bootstrap_secret_host_path':str(self.base/'bootstrap-password')},'source':{'integrated_sql_sha256':P.APPLICATION_SHA,'foundation_schema_sha256':'f'*64,'runtime_files_sha256':{p:'a'*64 for p in history['RUNTIME_FILES']}},'migration':{'id':'20261117000100_f0_local_initial','history':history['HISTORY']},'tools':{'node_version':'v24.22.1','prisma_version':'7.10.1','engine_commit':'d1b3f377ca835d73fd50954a5e22128b9ebdd6b8','files_sha256':{p:'a'*64 for p in ('node/bin/node','schema-engine','node_modules/prisma/build/index.js','node_modules/prisma/build/cli.js','node_modules/prisma/config.js','node_modules/prisma/package.json')}}}
  comparison={'format':'workinants.catalog-comparison.v1','status':'PASS','source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':P.digest(self.native),'findings':[],'check_counts':{'PASS':29089}}
  for name,value in [('native_snapshot',self.native),('native_comparison',comparison)]:
   p=self.base/(name+'.json');p.write_text(json.dumps(value));plan[name]={'path':str(p),'sha256':P.sha(p.read_bytes())}
  attestation={'schema':'workinants.worker-recovery-native-attestation.v1','run_id':plan['run_id'],'container_id':CID,'source_commit':plan['source_commit'],'source_tree':plan['source_tree'],'packet_sha256':plan['packet_sha256'],'collector_sha256':pins[M['COLLECTOR']],'source_expected_sha256':M['EXPECTED_CATALOG'],'native_snapshot_sha256':P.digest(self.native),'native_comparison_file_sha256':plan['native_comparison']['sha256'],'original_grantor_finalized':True,'operation_backends_absent':True,'comparison_status':'PASS'}
  p=self.base/'attestation.json';p.write_text(json.dumps(attestation));plan['native_attestation']={'path':str(p),'sha256':P.sha(p.read_bytes())};return plan

 def source_redirect(self,relative):return self.packetdir/relative.split('/')[-1] if relative.startswith('review-output/worker-recovery-control-rehearsal/') else ROOT/relative

 def test_whole_actual_load_inputs_real_graph_and_target_validator(self):
  plan=self.admitted_plan()
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect),patch.object(Path,'read_text',side_effect=AssertionError('SECOND_READ')):value=M['load_inputs'](plan)
  self.assertEqual(value[0]['source_only_packet_sha256'],self.packet['source_only_packet_sha256']);self.assertEqual(self.transport.events,[])

 def test_missing_helper_and_historical_folder_reject_before_compile(self):
  for old,new in [(M['HELPERS'][1],None),(M['HELPERS'][1],'historical/run-first-rehearsal.py')]:
   plan=self.admitted_plan();h=plan['packet_files_sha256'].pop(old)
   if new:plan['packet_files_sha256'][new]=h
   plan['packet_sha256']=P.sha(''.join(p+'\0'+plan['packet_files_sha256'][p]+'\n' for p in sorted(plan['packet_files_sha256'])).encode());compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
   with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),self.assertRaises(M['HeldFailure']):M['load_inputs'](plan)
   compiled.assert_not_called()

 def test_second_fixture_read_mutation_rejects_before_compile_without_echo(self):
  plan=self.admitted_plan();p=self.packetdir/'fixtures.json';old=Path.read_bytes;reads={'n':0};compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
  def read(path):
   if path==p:
    reads['n']+=1
    if reads['n']==2:return CANARY.encode()
   return old(path)
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),patch.object(Path,'read_bytes',read),self.assertRaises(M['HeldFailure']) as error:M['load_inputs'](plan)
  compiled.assert_not_called();self.assertNotIn(CANARY,str(error.exception))

 def test_forged_native_CID_rejects_before_compile(self):
  plan=self.admitted_plan();p=Path(plan['native_attestation']['path']);d=json.loads(p.read_bytes());d['container_id']='f'*64;p.write_text(json.dumps(d));plan['native_attestation']['sha256']=P.sha(p.read_bytes());compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),self.assertRaises(M['HeldFailure']):M['load_inputs'](plan)
  compiled.assert_not_called()

 def test_native_comparison_counter_requires_exact_integer_before_compile(self):
  for bad in ({'PASS':29089.0},{'PASS':True},{'PASS':False},{'PASS':-29089},{'PASS':None},{'PASS':'29089'},{'PASS':[]},{'PASS':29089,'OTHER':0},{},None,[]):
   with self.subTest(counter=bad):
    plan=self.admitted_plan();p=Path(plan['native_comparison']['path']);value=json.loads(p.read_bytes());value['check_counts']=bad;p.write_text(json.dumps(value));plan['native_comparison']['sha256']=P.sha(p.read_bytes());a=Path(plan['native_attestation']['path']);attestation=json.loads(a.read_bytes());attestation['native_comparison_file_sha256']=plan['native_comparison']['sha256'];a.write_text(json.dumps(attestation));plan['native_attestation']['sha256']=P.sha(a.read_bytes());compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
    with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),self.assertRaises(M['HeldFailure']) as error:M['load_inputs'](plan)
    self.assertEqual(error.exception.code,'NATIVE_EXACT_INTEGER_COMPARISON_COUNT');compiled.assert_not_called();self.assertEqual(self.transport.events,[])
 def typed_packet_mutant(self,mutate,code):
  plan=self.admitted_plan();p=self.packetdir/'fixtures.json';value=json.loads(self.files['fixtures.json']);mutate(value);p.write_text(json.dumps(value));wanted=P.sha(p.read_bytes());plan['reviewed_packet_sha256']=wanted;plan['packet_files_sha256']['review-output/worker-recovery-control-rehearsal/fixtures.json']=wanted;plan['packet_sha256']=P.sha(''.join(k+'\0'+plan['packet_files_sha256'][k]+'\n' for k in sorted(plan['packet_files_sha256'])).encode());compiled=Mock(side_effect=AssertionError('UNADMITTED_COMPILE'))
  with patch.dict(M['load_inputs'].__globals__,source_path=self.source_redirect,compiled=compiled),self.assertRaises(M['HeldFailure']) as error:M['load_inputs'](plan)
  self.assertEqual(error.exception.code,code);compiled.assert_not_called();self.assertEqual(self.transport.events,[])
 def test_all_declared_finite_caps_reject_float_bool_negative_or_malformed(self):
  for name in ('case_count','jobs','business_groups','audit_attempts','grant_instances_max','clock_wait_seconds_max','simultaneous_worker_sessions_max'):
   expected=self.packet['finite_caps'][name]
   for bad in (float(expected),True,-expected,None,str(expected),[]):
    with self.subTest(field=name,value=bad):self.typed_packet_mutant(lambda p,n=name,v=bad:p['finite_caps'].__setitem__(n,v),'EXACT_TYPED_FINITE_CAPS')
  self.typed_packet_mutant(lambda p:p['finite_caps'].__setitem__('worker_loop',0),'EXACT_TYPED_FINITE_CAPS')
  self.typed_packet_mutant(lambda p:p['finite_caps'].__setitem__('unknown',0),'EXACT_TYPED_FINITE_CAPS')
 def test_complete42_expected_counts_reject_untyped_negative_and_unknown_rows(self):
  for field in ('setup_expected_counts','checkpoint_expected_counts','final_expected_counts'):
   for bad in (0.0,False,-1,None,'0',[]):
    with self.subTest(field=field,value=bad):self.typed_packet_mutant(lambda p,n=field,v=bad:p[n].__setitem__('app.users',v),'EXACT_TYPED_COMPLETE42_COUNTS')
   self.typed_packet_mutant(lambda p,n=field:p[n].__setitem__('unknown.table',0),'EXACT_TYPED_COMPLETE42_COUNTS')
 def test_worker_acl_counter_shape_cannot_be_32_key_dictionary(self):
  self.typed_packet_mutant(lambda p:p.__setitem__('worker_acl_rows',{str(i):r for i,r in enumerate(p['worker_acl_rows'])}),'WORKER_ACL_CEILING')

 def test_import_help_and_missing_authorization_are_dormant(self):
  with redirect_stdout(io.StringIO()),self.assertRaises(SystemExit) as error:M['main'](['--help'])
  self.assertEqual(error.exception.code,0)
  with redirect_stdout(io.StringIO()):self.assertEqual(M['main']([]),1)


if __name__=='__main__':unittest.main(verbosity=2)

