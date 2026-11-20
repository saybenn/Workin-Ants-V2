"""Environment-free, every Docker/database boundary mocked."""
import copy,importlib.util,json,subprocess,unittest
from pathlib import Path
from unittest.mock import Mock
p=Path(__file__).with_name('sql-review')/'migration_server_diagnostics.py'
spec=importlib.util.spec_from_file_location('diagnostics',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prefix='WA_F0_DIAG|'
def line(state,message,login='wa_migrator',db=m.DATABASE):return prefix+state+'|'+login+'|'+db+'|ERROR:  '+message+'\n'
def baseline():return m.summarize('',prefix+'00000|postgres|'+m.DATABASE+'|LOG:  server ready\n')
def failed(logs='NULL'):
    return {'application_relations':0,'application_functions':0,'application_types':0,'application_enums':0,'active_migrators':0,'rows':[{'name':'20261117000100_f0_local_initial','checksum':'a'*64,'finished':False,'rolled_back':False,'steps':0,'logs_state':logs,'expected_error_code':logs=='NONEMPTY','expected_set_role_error':logs=='NONEMPTY'}]}
def cli(status='CLI_OUTPUT_REJECTED_STOP_AND_INSPECT',code=1):return {'schema':'workinants.local-f0-migrate-result.v2','operation':'deploy','run_id':'0c223ddc-80bb-4ed6-adb2-736a4baef0ee','container_id':'b'*64,'source_sql_sha256':'a'*64,'status':status,'exit_code':code,'prisma_codes':[],'sqlstates':[]}
class Tests(unittest.TestCase):
    def proof(self):
        identity={'run_id':'0c223ddc-80bb-4ed6-adb2-736a4baef0ee','container_id':'b'*64,'source_commit':'c'*40,'source_tree':'d'*40,'packet_sha256':'e'*64,'application_sql_sha256':'a'*64,'module_sha256':'f'*64,'migration_id':'20261117000100_f0_local_initial'}
        before=baseline();after=m.summarize('',prefix+'00000|postgres|'+m.DATABASE+'|LOG:  server ready\n'+line('42501',m.SET_ROLE)+line('25P02',m.ABORTED))
        return m.build_proof(identity,cli(),failed(),before,after,dict.fromkeys(m.VERIFIED_FIELDS,True))
    def test_proof_strict_identity_and_fixed_protocol(self):
        proof=self.proof();self.assertIs(m.validate_proof(proof,{k:proof[k] for k in m.IDENTITY_FIELDS}),proof)
        for key in m.IDENTITY_FIELDS:
            expected={k:proof[k] for k in m.IDENTITY_FIELDS};expected[key]='0'*len(expected[key])
            with self.assertRaises(m.DiagnosticFailure):m.validate_proof(proof,expected)
        self.assertNotIn('raw',json.dumps(proof).replace('raw_output_discarded',''))
    def test_proof_extra_raw_missing_flags_and_wrong_classification_reject(self):
        proof=self.proof()
        for key,value in [('secret','SECRET_CANARY'),('application_object_count',False),('cli_closed_nonzero',1),('cli_exit_code',True),('classification','NORMAL_P3018_PERSISTENCE'),('failed_row_logs_state','NONEMPTY'),('phase','OTHER')]:
            changed=copy.deepcopy(proof);changed[key]=value
            with self.assertRaises(m.DiagnosticFailure):m.validate_proof(changed)
    def test_constructor_cli_target_and_ledger_checksum_binding(self):
        proof=self.proof();identity={k:proof[k] for k in m.IDENTITY_FIELDS}
        for key in ('schema','operation','run_id','container_id','source_sql_sha256'):
            changed=cli();changed[key]='SECRET_CANARY'
            with self.assertRaises(m.DiagnosticFailure):m.build_proof(identity,changed,failed(),proof['before'],proof['after'],dict.fromkeys(m.VERIFIED_FIELDS,True))
        for key in ('name','checksum'):
            changed=failed();changed['rows'][0][key]='SECRET_CANARY'
            with self.assertRaises(m.DiagnosticFailure):m.build_proof(identity,cli(),changed,proof['before'],proof['after'],dict.fromkeys(m.VERIFIED_FIELDS,True))
        for key in m.VERIFIED_FIELDS:
            changed=copy.deepcopy(proof);del changed[key]
            with self.assertRaises(m.DiagnosticFailure):m.validate_proof(changed)
    def test_impossible_or_nonmonotonic_classified_counts_reject(self):
        bad=dict.fromkeys(m.FIELDS,0);bad.update(expected_set_role_42501=1,aborted_transaction_25p02=1)
        with self.assertRaises(m.DiagnosticFailure):m.classify_failure(cli(),failed(),bad)
        old=baseline();after=m.summarize('',line('42501',m.SET_ROLE)+line('25P02',m.ABORTED))
        with self.assertRaises(m.DiagnosticFailure):m.difference(old,after)
        proof=self.proof();proof['delta']['registered_lines']=0
        with self.assertRaises(m.DiagnosticFailure):m.validate_proof(proof)
    def test_exact_guard_and_secondary_with_crlf_and_numeric_position(self):
        raw=line('42501',m.SET_ROLE+' at character 123')+line('25P02',m.ABORTED)
        after=m.summarize('',(prefix+'00000|postgres|'+m.DATABASE+'|LOG:  server ready\n'+raw).replace('\n','\r\n'))
        delta=m.difference(baseline(),after);self.assertEqual(delta['expected_set_role_42501'],1);self.assertEqual(delta['aborted_transaction_25p02'],1)
        self.assertEqual(m.classify_failure(cli(),failed(),delta),'SERVER_42501_WITH_SECONDARY_25P02_UNWRITTEN_FAILURE_LOGS')
    def test_normal_path_still_requires_cli_and_exact_ledger_diagnostics(self):
        delta=dict.fromkeys(m.FIELDS,0);delta.update(registered_lines=1,expected_set_role_42501=1)
        value=cli('CLI_FAILED_STOP_AND_INSPECT');value.update(prisma_codes=['P3018'],sqlstates=['42501'])
        self.assertEqual(m.classify_failure(value,failed('NONEMPTY'),delta),'NORMAL_P3018_PERSISTENCE')
        for key in ('prisma_codes','sqlstates'):
            broken=copy.deepcopy(value);broken[key]=[]
            with self.assertRaises(m.DiagnosticFailure):m.classify_failure(broken,failed('NONEMPTY'),delta)
    def test_wrong_code_message_role_database_and_suffix_do_not_prove_guard(self):
        raws=[line('P0001',m.SET_ROLE),line('42501','SECRET_CANARY'),line('42501',m.SET_ROLE,login='postgres'),line('42501',m.SET_ROLE,db='wrong'),line('42501',m.SET_ROLE+' SECRET_CANARY'),line('42501',m.SET_ROLE.replace('customer','track')),line('42501',m.SET_ROLE+' at character 0'),line('42501',m.SET_ROLE+' at character 999999999')]
        for raw in raws:self.assertEqual(m.summarize('',raw)['counts']['expected_set_role_42501'],0)
    def test_continuation_or_quoted_injected_prefix_is_not_a_server_line(self):
        for pre in ('\t',' ','"',"'"):
            self.assertEqual(m.summarize('',pre+line('42501',m.SET_ROLE))['counts']['expected_set_role_42501'],0)
    def test_unrelated_error_or_duplicate_guard_rejects(self):
        for raw in (line('42501',m.SET_ROLE)*2,line('42501',m.SET_ROLE)+line('25P02',m.ABORTED)+line('P0001','SECRET_CANARY')):
            delta=m.summarize('',raw)['counts']
            with self.assertRaises(m.DiagnosticFailure):m.classify_failure(cli(),failed(),delta)
    def test_mask_requires_secondary_and_null_unwritten_logs(self):
        delta=dict.fromkeys(m.FIELDS,0);delta.update(registered_lines=2,expected_set_role_42501=1,aborted_transaction_25p02=1)
        for logs in ('EMPTY','NONEMPTY','SECRET_CANARY'):
            with self.assertRaises(m.DiagnosticFailure):m.classify_failure(cli(),failed(logs),delta)
        delta['aborted_transaction_25p02']=0
        with self.assertRaises(m.DiagnosticFailure):m.classify_failure(cli(),failed(),delta)
    def test_unclosed_or_success_cli_and_nonrollback_state_reject(self):
        delta=dict.fromkeys(m.FIELDS,0);delta.update(registered_lines=2,expected_set_role_42501=1,aborted_transaction_25p02=1)
        for value in (cli(code=0),cli(code=False),cli(code=None),cli(code=-1),cli(code=256),cli('CLI_CLOSURE_UNCONFIRMED_STOP_AND_CLEAN_EXACT_RESOURCE')):
            with self.assertRaises(m.DiagnosticFailure):m.classify_failure(value,failed(),delta)
        for key in ('application_relations','application_functions','application_types','application_enums','active_migrators'):
            for wrong in (1,False,0.0):
                state=failed();state[key]=wrong
                with self.assertRaises(m.DiagnosticFailure):m.classify_failure(cli(),state,delta)
    def test_forbidden_details_or_malformed_channel_and_reset_reject(self):
        for raw in (prefix+'42501|wa_migrator|'+m.DATABASE+'|STATEMENT:  SECRET_CANARY\n',prefix+'broken\n'):
            after=m.summarize('',prefix+'00000|||LOG:  ready\n'+raw)
            with self.assertRaises(m.DiagnosticFailure):m.difference(baseline(),after)
        with self.assertRaises(m.DiagnosticFailure):m.difference(baseline(),m.summarize('',''))
    def test_controls_limits_types_and_extra_evidence_fields_reject(self):
        for raw in ('\x1b[31m','\x1b]0;SECRET_CANARY\x07','\r','\u202e','\ud800','\ufffd','x'*(m.MAX_BYTES+1)):
            with self.assertRaises(m.DiagnosticFailure):m.summarize('',raw)
        for value in ({**baseline(),'raw':'SECRET_CANARY'},{**baseline(),'counts':{**baseline()['counts'],'registered_lines':True}}):
            with self.assertRaises(m.DiagnosticFailure):m.validate_counts(value)
    def test_only_exact_immutable_id_and_fixed_process_boundary(self):
        process=Mock(return_value=subprocess.CompletedProcess([],0,'',prefix+'00000|||LOG:  ready\n'))
        value=m.read_owned('a'*64,process);self.assertTrue(value['raw_output_discarded'])
        process.assert_called_once_with(['docker','--context','desktop-linux','logs','a'*64],text=True,encoding='utf8',errors='strict',capture_output=True,timeout=30,shell=False)
        for identity in ('wa-p0c-name','a'*63,'A'*64):
            with self.assertRaises(m.DiagnosticFailure):m.read_owned(identity,Mock())
    def test_failures_exclude_raw_process_and_secret_metadata(self):
        for process in (Mock(side_effect=RuntimeError('SECRET_CANARY')),Mock(return_value=subprocess.CompletedProcess([],1,'SECRET_CANARY','SECRET_CANARY'))):
            with self.assertRaises(m.DiagnosticFailure) as found:m.read_owned('a'*64,process)
            self.assertNotIn('SECRET_CANARY',str(found.exception))
        value=m.summarize('SECRET_CANARY\n',line('P0001','SECRET_CANARY'))
        self.assertNotIn('SECRET_CANARY',json.dumps(value))
if __name__=='__main__':unittest.main(verbosity=2)
