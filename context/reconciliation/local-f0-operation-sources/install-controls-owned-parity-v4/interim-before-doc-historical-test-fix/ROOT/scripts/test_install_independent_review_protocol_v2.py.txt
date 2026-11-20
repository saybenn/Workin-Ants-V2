"""Pure immutable transport schema/hash mutation checks; no runtime."""
from copy import deepcopy
import json,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=runpy.run_path(str(ROOT/'scripts/install_independent_review_protocol_v2.py'))
def fixture():
    run='12345678-1234-4234-8234-123456789abc';base={'run_id':run,'source_commit':'a'*40,'source_tree':'b'*40,'packet_sha256':'c'*64}
    target={v:{'container_id':str(n+1)*64,'source_sql_sha256':P['SQL'][v]} for n,v in enumerate(P['VARIANTS'])}
    plan={'schema':'workinants.install-controls-run.v1','scope':'FINITE_INSTALL_HISTORY_AND_AUTHORITY_CONTROLS',**base,'targets':{v:{'container_id':t['container_id']} for v,t in target.items()},'reviewed_packet_sha256':'0'*64,'source_modules_sha256':{},'histories':{},'credential_bundle':'SYNTHETIC_PRIVATE_BUNDLE_PATH_NO_CREDENTIALS'}
    planraw=P['canonical'](plan)
    identity={'schema':P['IDENTITY_SCHEMA'],**base,'child_run_plan_sha256':P['sha'](planraw),'operator_sources_sha256':{n:'d'*64 for n in P['OPERATORS']},'targets':target}
    inventory=dict.fromkeys(('relations','functions','types','enums','other_clients'),0)
    failed={'name_sha256':'e'*64,'checksum_sha256':'f'*64,'finished':False,'rolled_back':False,'steps':0,'logs_state':'NULL','immutable_sha256':'1'*64}
    verdict={'primary_sqlstate':'22012','secondary_sqlstate':'25P02','failed_row_logs':'NULL','recovery_approved':False}
    proof={'schema':'workinants.install-rollback-observation.v1',**base,**target['division_failure'],'failure':verdict,'failed_ledger':failed,'application_inventory':inventory,'original_grantor_finalized':True,'disposition':'PENDING_INDEPENDENT_REVIEW'}
    proofraw=P['canonical'](proof)
    snapshot={'schema':'workinants.install-controls-results.v1',**base,'status':'RUNNING','limits':dict(P['SNAPSHOT_LIMITS']),'current_stage':'INDEPENDENT_ROLLBACK_REVIEW_REQUIRED','subsequent_cases_stopped':False,'reviewed_plan_sha256':P['sha'](planraw),'targets':{'division_failure':{'inventory':inventory,'ledger':{'rows':[failed]},'failure_verdict':verdict,'original_cleanup':{'original_grantor':'postgres','temporary_memberships':0,'leaf_create':False,'other_clients':0},'review_hold':{'proof_sha256':P['sha'](proofraw),'decision':'PENDING_INDEPENDENT_REVIEW','timeout_seconds':240}}}}
    raws={P['PLAN']:planraw,P['IDENTITY']:P['canonical'](identity),P['PROOF']:proofraw,P['SNAPSHOT']:P['canonical'](snapshot)}
    marker={'schema':P['READY_SCHEMA'],**base,**target['division_failure'],'rollback_proof_sha256':P['sha'](raws[P['PROOF']]),'closed_child_snapshot_sha256':P['sha'](raws[P['SNAPSHOT']]),'outer_identity_sha256':P['sha'](raws[P['IDENTITY']]),'child_run_plan_sha256':P['sha'](raws[P['PLAN']]),'review_timeout_seconds':240}
    raws[P['READY']]=P['canonical'](marker);return raws,base
def rebound(raws,name,value):
    raws=dict(raws);raws[name]=P['canonical'](value)
    if name!=P['READY']:
        marker=P['decode'](raws[P['READY']]);key={P['PROOF']:'rollback_proof_sha256',P['SNAPSHOT']:'closed_child_snapshot_sha256',P['IDENTITY']:'outer_identity_sha256',P['PLAN']:'child_run_plan_sha256'}[name];marker[key]=P['sha'](raws[name]);raws[P['READY']]=P['canonical'](marker)
    return raws
class Tests(unittest.TestCase):
    def test_exact_closed_handoff(self):
        raw,expected=fixture();v=P['bindings'](raw,expected);self.assertEqual(v['ready']['review_timeout_seconds'],240);self.assertEqual(raw[P['READY']][-1:],b'\n')
    def test_every_missing_extra_schema_and_type_field(self):
        raw,_=fixture()
        for func,name in ((P['ready'],P['READY']),(P['identity'],P['IDENTITY'])):
            value=P['decode'](raw[name])
            for key in value:
                mutant=dict(value);mutant.pop(key)
                with self.subTest(name=name,key=key),self.assertRaises(P['Held']):func(mutant)
            with self.assertRaises(P['Held']):func(dict(value,unknown=True))
    def test_boolean_timeout_hash_and_uuid_do_not_coerce(self):
        raw,_=fixture();r=P['decode'](raw[P['READY']])
        for k,v in (('review_timeout_seconds',True),('review_timeout_seconds',241),('container_id','x'*64),('run_id','123'),('source_tree','f'*64),('source_sql_sha256',P['SQL']['canonical'])):
            with self.subTest(k=k),self.assertRaises(P['Held']):P['ready'](dict(r,**{k:v}))
    def test_duplicate_nonfinite_nonutf8_and_noncanonical(self):
        for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'\xff',b'{ "a":1}\n'):
            with self.subTest(raw=raw),self.assertRaises((P['Held'],ValueError)):P['decode'](raw,True)
    def test_each_immutable_hash_is_required(self):
        raws,expected=fixture()
        for name in raws:
            mutant=dict(raws);mutant[name]+=b' '
            with self.subTest(name=name),self.assertRaises(P['Held']):P['bindings'](mutant,expected)
    def test_rehashed_wrong_run_cid_source_and_original_authority(self):
        raw,expected=fixture()
        for name,key,value in ((P['PROOF'],'run_id','22345678-1234-4234-8234-123456789abc'),(P['PROOF'],'container_id','9'*64),(P['PROOF'],'source_sql_sha256',P['SQL']['canonical']),(P['PROOF'],'original_grantor_finalized',False),(P['SNAPSHOT'],'current_stage','RECOVERY'),(P['SNAPSHOT'],'subsequent_cases_stopped',True)):
            mutant=P['decode'](raw[name]);mutant[key]=value
            with self.subTest(name=name,key=key),self.assertRaises(P['Held']):P['bindings'](rebound(raw,name,mutant),expected)
    def test_rehashed_snapshot_cannot_fake_zero_or_discard_failed_row(self):
        raw,expected=fixture()
        for kind in ('inventory','ledger','cleanup','review_hold'):
            s=P['decode'](raw[P['SNAPSHOT']]);t=s['targets']['division_failure']
            if kind=='inventory':t[kind]['relations']=1
            elif kind=='ledger':t[kind]['rows']=[]
            elif kind=='cleanup':t['original_cleanup']['original_grantor']='wa_migrator'
            else:t[kind]['timeout_seconds']=True
            with self.subTest(kind=kind),self.assertRaises(P['Held']):P['bindings'](rebound(raw,P['SNAPSHOT'],s),expected)
    def test_expected_checkpoint_and_all_three_cids(self):
        raw,expected=fixture()
        with self.assertRaises(P['Held']):P['bindings'](raw,dict(expected,packet_sha256='0'*64))
        i=P['decode'](raw[P['IDENTITY']]);i['targets']['canonical']['container_id']=i['targets']['division_failure']['container_id']
        with self.assertRaises(P['Held']):P['bindings'](rebound(raw,P['IDENTITY'],i),expected)
    def test_closed_file_map_caps_and_bytes_only(self):
        raw,_=fixture()
        for mutant in ({**raw,'run-evidence.json':b'{}'},dict(raw,**{P['SNAPSHOT']:b' '* (P['CAPS'][P['SNAPSHOT']]+1)}),dict(raw,**{P['PROOF']:'not bytes'})):
            with self.assertRaises(P['Held']):P['bindings'](mutant)
    def test_rehashed_extra_proof_plan_or_snapshot_fields_and_stopped_snapshot_are_rejected(self):
        raw,expected=fixture()
        for name in (P['PROOF'],P['PLAN'],P['SNAPSHOT']):
            value=P['decode'](raw[name]);value['unknown_private_body']='DISALLOWED'
            with self.subTest(name=name),self.assertRaises(P['Held']):P['bindings'](rebound(raw,name,value),expected)
        value=P['decode'](raw[P['SNAPSHOT']]);value['status']='STOPPED_UNEXPECTED_RESULT'
        with self.assertRaises(P['Held']):P['bindings'](rebound(raw,P['SNAPSHOT'],value),expected)
if __name__=='__main__':unittest.main()
