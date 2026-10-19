"""Executable architectural reference models, deliberately NOT production adapters.
Atomic methods below model the required transaction; no database/RLS/provider proof follows.
"""
import hashlib
import hmac
import itertools
import re
from dataclasses import dataclass, field

class Conflict(Exception): pass
class Blocked(Exception): pass

@dataclass
class CommandHistory:
    records: dict = field(default_factory=dict)
    def apply(self, key, fingerprint, effect):
        if key in self.records:
            old,result=self.records[key]
            if old!=fingerprint:raise Conflict('changed semantic fingerprint')
            return result
        result=effect();self.records[key]=(fingerprint,result);return result

@dataclass
class Capacity:
    limit: int
    reservations: dict = field(default_factory=dict)
    def reserve(self,intent,quantity=1):
        if intent in self.reservations:return self.reservations[intent]
        used=sum(r['quantity'] for r in self.reservations.values() if r['state']!='released')
        if used+quantity>self.limit:raise Blocked('capacity exhausted')
        r={'quantity':quantity,'state':'reserved','can_late_commit':True};self.reservations[intent]=r;return r
    def commit(self,intent):
        r=self.reservations[intent]
        if r['state']=='released' or not r['can_late_commit']:raise Conflict('fenced noncommit')
        r['state']='committed'
    def release(self,intent,outcome):
        r=self.reservations[intent]
        if outcome!='fenced_noncommit' or r['state']=='committed':raise Blocked('unknown/committed cannot release')
        r['can_late_commit']=False;r['state']='released'

@dataclass
class RevisionProjection:
    revision:int=-1
    tombstoned:bool=False
    value:object=None
    def apply(self,revision,value,remove=False):
        if revision<=self.revision:return False
        self.revision=revision;self.tombstoned=remove;self.value=None if remove else value;return True

def privacy_summary(receipts):
    accepted={'completed','lawfully_retained'}
    return 'completed' if receipts and all(s in accepted for s in receipts) else 'pending'

def hold_release(source_ready,other_holds):
    # One cause may clear while another independent Hold remains. No financial dispatch occurs.
    return {'released':source_ready is True,'business_allowed':source_ready is True and not other_holds,'money_dispatched':False}

def join_allowed(current_member,current_parent,generation,current_generation,now,start,end):
    return bool(current_member and current_parent and generation==current_generation and start<=now<end)

def submission_period_valid(authorized_period,commit_period):return authorized_period==commit_period

def audience(registered,current):return sorted(set(registered)&set(current))

def cycle_exists(edges):
    graph={}
    for a,b in edges:graph.setdefault(a,[]).append(b);graph.setdefault(b,[])
    visiting=set();done=set()
    def visit(n):
        if n in visiting:return True
        if n in done:return False
        visiting.add(n)
        if any(visit(v) for v in graph[n]):return True
        visiting.remove(n);done.add(n);return False
    return any(visit(n) for n in graph)

def event_effects(events):
    # Economic/rule effect identity remains stable even if transport event IDs differ.
    effects={}
    for event_id,effect_id,fingerprint in events:
        if effect_id in effects and effects[effect_id]!=fingerprint:raise Conflict('economic identity mismatch')
        effects[effect_id]=fingerprint
    return effects

def validate_workflow(definition):
    ids={s['id'] for s in definition}
    if len(ids)!=len(definition):raise Conflict('duplicate step')
    for s in definition:
        if set(s['dependsOn'])-ids:raise Conflict('missing step')
    if cycle_exists([(s['id'],d) for s in definition for d in s['dependsOn']]):raise Conflict('workflow cycle')
    return True

@dataclass
class WorkClaims:
    row: dict = field(default_factory=lambda:{'holder':None,'fence':0,'leaseUntil':0,'revision':0,'completed':False})
    def claim(self,holder,now,until):
        if self.row['holder'] is not None and now<self.row['leaseUntil'] and not self.row['completed']:raise Conflict('active holder')
        self.row.update(holder=holder,fence=self.row['fence']+1,leaseUntil=until,completed=False)
        return self.row['fence'],self.row['revision']
    def complete(self,holder,fence,expected_revision,now):
        if holder!=self.row['holder'] or fence!=self.row['fence'] or expected_revision!=self.row['revision'] or now>=self.row['leaseUntil']:raise Conflict('stale claim/lease/revision')
        self.row['completed']=True;self.row['revision']+=1

def conserved_ledger(entries):
    totals={}
    for currency,amount in entries:totals[currency]=totals.get(currency,0)+amount
    return all(v==0 for v in totals.values())

def tests():
    out=[]
    def case(name,ops,fn):
        fn();out.append({'case':name,'contracts':ops.split(),'result':'PASS'})
    def assert_true(v):
        if not v:raise AssertionError('invariant failed')
    def rejects(fn,kind=(Conflict,Blocked)):
        try:fn()
        except kind:return
        raise AssertionError('prohibited effect accepted')
    def idempotency():
        h=CommandHistory();seen=[]
        for _ in range(5):h.apply('owner:command:subject','a',lambda:seen.append('effect') or 'receipt')
        assert_true(len(seen)==1);rejects(lambda:h.apply('owner:command:subject','b',lambda:'changed'))
    case('same command replay once; changed fingerprint conflicts','SH-044 SH-060 SH-107 SH-108',idempotency)
    def capacity():
        c=Capacity(4)
        for i in range(4):c.reserve(str(i))
        rejects(lambda:c.reserve('fifth'));assert_true(len(c.reservations)==4)
        rejects(lambda:c.release('0','timeout'));rejects(lambda:c.release('0','not_found'))
        c.release('0','fenced_noncommit');rejects(lambda:c.commit('0'));c.reserve('new')
    case('bounded sessions; unknown release denied; late commit fenced','SH-056 SH-058 SH-006',capacity)
    def permutations():
        for order in itertools.permutations([(1,'old',False),(3,None,True),(2,'middle',False)]):
            p=RevisionProjection()
            for rev,value,remove in order:p.apply(rev,value,remove)
            assert_true(p.revision==3 and p.tombstoned and p.value is None)
    case('all event orderings preserve newest tombstone','SH-045 SH-046 SH-091 SH-092 SH-093 SH-094',permutations)
    def effects():
        assert_true(len(event_effects([('evt1','money1','f'),('evt2','money1','f')]))==1)
        rejects(lambda:event_effects([('evt1','money1','f'),('evt2','money1','different')]))
    case('economic identity independent of event duplicate identity','SH-045 SH-060 SH-108 SH-117 SH-118',effects)
    case('Privacy accepted/unsupported/unknown never completes','SH-095 SH-096 SH-099 SH-100 SH-070',lambda:[assert_true(privacy_summary(['completed',s])=='pending') for s in ['accepted','unsupported','unknown','partial','failed']])
    case('lawfully accounted retention distinct from failed/erased','SH-097 SH-098 SH-099',lambda:assert_true(privacy_summary(['completed','lawfully_retained'])=='completed'))
    case('empty Privacy inventory is not complete coverage','SH-096 SH-099',lambda:assert_true(privacy_summary([])=='pending'))
    case('one Hold release cannot waive another or dispatch money','SH-011 SH-013 SH-019',lambda:assert_true(hold_release(True,['other'])=={'released':True,'business_allowed':False,'money_dispatched':False}))
    case('unknown source does not release Hold','SH-012 SH-013',lambda:assert_true(not hold_release(None,[])['released']))
    case('current participant and generation before join credential','SH-026 SH-068 SH-088 SH-127',lambda:[assert_true(not join_allowed(member,parent,g,2,15,10,20)) for member,parent,g in [(False,True,2),(True,False,2),(True,True,1)]])
    case('server interval checked despite delayed expiry worker','SH-055 SH-068 SH-088',lambda:assert_true(not join_allowed(True,True,2,2,20,10,20)))
    case('month boundary requires reauthorized reservation','SH-005 SH-006 SH-057',lambda:assert_true(not submission_period_valid('2026-09','2026-10')))
    case('revoked audience excluded at actual emission','SH-043 SH-071 SH-113',lambda:assert_true(audience(['old','current'],['current'])==['current']))
    case('liveness separate from dependent business readiness','SH-039 SH-047 SH-038',lambda:assert_true(not cycle_exists([('config','runtime'),('runtime','owners'),('owners','diagnostics')])) )
    case('diagnostic startup backedge detected','SH-038 SH-039 SH-047',lambda:assert_true(cycle_exists([('runtime','diagnostics'),('diagnostics','runtime')])))
    def workflow():
        assert_true(validate_workflow([{'id':'a','dependsOn':[]},{'id':'b','dependsOn':['a']}]))
        rejects(lambda:validate_workflow([{'id':'a','dependsOn':['b']},{'id':'b','dependsOn':['a']}]))
        rejects(lambda:validate_workflow([{'id':'a','dependsOn':['missing']}]))
    case('workflow acyclic and required dependencies registered','SH-049 SH-050',workflow)
    def claim():
        c=WorkClaims();first,rev=c.claim('first',0,10)
        rejects(lambda:c.claim('second',5,20))
        second,rev2=c.claim('second',11,30)
        rejects(lambda:c.complete('first',first,rev,12))
        c.complete('second',second,rev2,12)
        rejects(lambda:c.complete('second',second,rev2,13))
        assert_true(c.row['completed'] and c.row['revision']==1)
    case('stale reviewer fence cannot acknowledge new holder','SH-051 SH-052 SH-053 SH-054',claim)
    case('exact SHA-256 known vectors, no semantic-similarity claim','SH-072 SH-086 SH-112',lambda:[assert_true(hashlib.sha256(x).hexdigest()==expected) for x,expected in [(b'', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),(b'abc','ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')]])
    case('purpose-bound identifier HMAC differs across purposes','SH-072 SH-076',lambda:assert_true(hmac.new(b'fixture-key',b'purposeA:123',hashlib.sha256).digest()!=hmac.new(b'fixture-key',b'purposeB:123',hashlib.sha256).digest()))
    case('Unicode scanner offsets are code points not bytes/UTF16','SH-077 SH-081',lambda:assert_true([(m.start(),m.end()) for m in re.finditer('😀','a😀b')]==[(1,2)]))
    case('financial conservation is per currency, not cross-currency cancellation','SH-019 SH-108 SH-117 SH-118',lambda:[assert_true(conserved_ledger([('USD',100),('USD',-100)])),assert_true(not conserved_ledger([('USD',100),('EUR',-100)]))])
    return {'status':'PASS','cases':out,'count':len(out),'scope':'Executable architectural reference models and known vectors only. In-memory atomic methods do NOT prove Postgres locking, crash durability, server/RLS, real adapters, CSPRNG/KMS or provider behavior.'}
if __name__=='__main__':
    import json
    print(json.dumps(tests(),indent=2))
