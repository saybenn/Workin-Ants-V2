"""Environment-free source/projection checks; no process/database/network calls."""
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
from pglast import ast,parse_sql

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import privilege_ceiling_control_protocol as P
G=runpy.run_path(str(ROOT/'scripts/prepare-privilege-ceiling-control-rehearsal.py'))
CANARY='PRIVATE_PASSWORD_URI_HANDLE_SQL_CANARY'


class PrivilegeProtocolTests(unittest.TestCase):
    def setUp(self):
        guards=ExitStack();self.addCleanup(guards.close)
        for name in ('run','Popen','call','check_call','check_output'):guards.enter_context(patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN')))
        guards.enter_context(patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN')))
        guards.enter_context(patch.object(socket.socket,'connect',side_effect=AssertionError('NETWORK_FORBIDDEN')))

    def error(self,message,state='42501',location='aclcheck_error, aclchk.c:2841'):
        return 'ERROR:  '+state+': '+message+'\nLOCATION:  '+location+'\n'

    def verdict(self,text,contract=None,metadata=None,sql='SELECT 1;'):
        return P.diagnostic(text,contract or{'kind':'NATIVE_ACL','schema':'app','relation':'users'},metadata or{'schema_usage':True,'required_permission_missing':True,'missing_referenced_columns':['id']},sql,P.source_position_matches)

    def test_exact_native_schema_table_column_and_function_gates(self):
        self.assertTrue(self.verdict(self.error('permission denied for table users'))['matched'])
        self.assertTrue(self.verdict(self.error('permission denied for schema app'),metadata={'schema_usage':False})['matched'])
        self.assertTrue(self.verdict(self.error('permission denied for column "id" of relation "users"',location='aclcheck_error_col, aclchk.c:2841'))['matched'])
        self.assertTrue(self.verdict(self.error('permission denied for function bound_grant'),{'kind':'FUNCTION','schema':'platform_private','function':'bound_grant'},{'schema_usage':True,'function_execute':False})['matched'])

    def test_schema_CREATE_is_distinct_from_schema_USAGE_and_earlier_provider_gate(self):
        result=self.verdict(self.error('permission denied for schema public'),{'kind':'SCHEMA_CREATE','schema':'public'},{'schema_usage':True,'schema_create':False})
        self.assertEqual((result['matched'],result['gate']),(True,'SCHEMA_CREATE'))
        result=self.verdict(self.error('permission denied for schema platform_private'),{'kind':'FUNCTION','schema':'platform_private','function':'bound_grant'},{'schema_usage':False,'function_execute':False})
        self.assertEqual(result['gate'],'SCHEMA');self.assertNotEqual(result['gate'],'FUNCTION')

    def test_role_denial_requires_exact_target_native_location_and_absent_membership(self):
        contract={'kind':'SET_ROLE','target_role':'wa_track_verifier'};metadata={'role_assumption_allowed':False}
        good=self.error('permission denied to set role "wa_track_verifier"',location='call_string_check_hook, guc.c:6500')
        self.assertTrue(self.verdict(good,contract,metadata)['matched'])
        for wrong in (good.replace('wa_track_verifier','wa_customer_verifier'),good.replace('guc.c:6500','variable.c:950'),good.replace('42501','42704'),good.replace('call_string_check_hook','check_role')):
            self.assertFalse(self.verdict(wrong,contract,metadata)['matched'])
        self.assertFalse(self.verdict(good,contract,{'role_assumption_allowed':True})['matched'])

    def test_generic_guard_codes_wrong_objects_routines_types_and_multiple_headers_reject(self):
        good=self.error('permission denied for table users')
        bad=(self.error(CANARY),self.error('permission denied for table users','P0001'),self.error('permission denied for table other'),self.error('permission denied for table users',location='ExecConstraints, execMain.c:900'),self.error(CANARY,'23503'),self.error(CANARY,'22P02'),good+good,good.replace('users','users ERROR:  42501: '+CANARY),good+'DETAIL: '+CANARY+'\n',good+'\x1b[31m'+CANARY,good+'\r'+CANARY,good+'x'*17000)
        for text in bad:
            value=self.verdict(text);self.assertFalse(value['matched']);self.assertNotIn(CANARY,json.dumps(value))

    def test_immutable_grant_exact_source_RAISE_line_and_message_required(self):
        contract={'kind':'IMMUTABLE_GRANT','body_line':9,'body_sha256':'a'*64}
        text='ERROR:  P0001: immutable grant\nCONTEXT:  PL/pgSQL function platform_private.grant_guard() line 9 at RAISE\nLOCATION:  exec_stmt_raise, pl_exec.c:4000\n'
        self.assertTrue(self.verdict(text,contract)['matched'])
        for bad in (text.replace('line 9','line 8'),text.replace('immutable grant',CANARY),text.replace('grant_guard()','other_guard()'),text.replace('P0001','42501'),text+'CONTEXT: '+CANARY+'\n'):
            value=self.verdict(bad,contract);self.assertFalse(value['matched']);self.assertNotIn(CANARY,json.dumps(value))

    def test_valid_service_context_denial_has_exact_bind_frame_not_invalid_secret_shape(self):
        contract={'kind':'BIND_CURRENTNESS','body_line':8,'body_sha256':'a'*64}
        text='ERROR:  42501: invalid, stale or unsupported context\nCONTEXT:  PL/pgSQL function platform_private.bind_request_context(text) line 8 at RAISE\n'
        self.assertTrue(self.verdict(text,contract)['matched'])
        self.assertFalse(self.verdict(text.replace('invalid, stale or unsupported context','invalid context'),contract)['matched'])

    def test_pinned_source_position_matches_DML_reference_and_finite_DDL(self):
        native=runpy.run_path(str(ROOT/G['NATIVE_COORDINATOR']))
        sql='SELECT id FROM app.users;';position='LINE 1: '+sql;caret=' '*len('LINE 1: ')+'^'
        self.assertEqual(P.source_position_matches(position,caret,sql),native['source_position_matches'](position,caret,sql))
        sql='CREATE TABLE public.wa_priv_probe(id integer);';position='LINE 1: '+sql
        self.assertTrue(P.source_position_matches(position,caret,sql));self.assertFalse(native['source_position_matches'](position,caret,sql))
        text='ERROR:  42501: permission denied for schema public\n'+position+'\n'+caret+'\nLOCATION:  aclcheck_error, aclchk.c:2841\n'
        value=self.verdict(text,{'kind':'SCHEMA_CREATE','schema':'public'},{'schema_create':False},sql)
        self.assertTrue(value['matched']);self.assertTrue(value['source_position_verified']);self.assertFalse(self.verdict(text.replace(sql,CANARY),{'kind':'SCHEMA_CREATE','schema':'public'},{'schema_create':False},sql)['matched'])

    def test_typed_literals_quote_data_reject_controls_and_boolean_dimension(self):
        self.assertEqual(P.typed("a'b",{'name':'pg_catalog.text','array_dimensions':0}),"'a''b'::pg_catalog.text")
        self.assertEqual(P.typed(['a'],{'name':'pg_catalog.text','array_dimensions':1}),"ARRAY['a'::pg_catalog.text]::pg_catalog.text[]")
        for value,spec in (('a\x00b',{'name':'pg_catalog.text','array_dimensions':0}),('a',{'name':CANARY,'array_dimensions':0}),('a',{'name':'pg_catalog.text','array_dimensions':False})):
            with self.assertRaises(P.Refused):P.typed(value,spec)

    def test_unknown_failure_codes_and_raising_code_property_never_leak(self):
        class Bad(Exception):
            @property
            def code(self):raise ValueError(CANARY)
        for error in (ValueError(CANARY),Bad(CANARY),P.Refused(CANARY)):
            self.assertEqual(P.failure_class(error,{'FIXED_ALLOWED'}),'UNEXPECTED_PRIVILEGE_CONTROL_FAILURE')


class PrivilegeGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.files,cls.packet=G['generate'](ROOT)

    def test_exact_200_negatives_5_controls_40_umbrellas_and16_metadata(self):
        packet=self.packet;self.assertEqual(packet['finite_counts'],{'issuer_business':117,'runtime_escalation':34,'provider_reachability':18,'source_definers':16,'private_Identity_native_ceilings':4,'immutable_column_ceilings':20,'helper_calls':4,'immutable_guard_cases':3,'prepared_negative_cases':200})
        self.assertEqual(len(packet['control_links']),5);self.assertEqual(len(packet['issuer_umbrella_links']),40);self.assertEqual(len(packet['source_definers']),16)
        self.assertTrue(all(row['status']=='NOT_RUN'and row['whole_case_promoted']is False for row in packet['cases']))
        self.assertTrue(all(row['source_case_id']in{'P0C-PRIV-01'}|{link['case_id']for link in packet['issuer_umbrella_links']}for row in packet['cases']))

    def test_legitimate_issuer_grant_INSERT_is_never_a_negative_umbrella_case(self):
        rows=[row for row in self.packet['cases']if row['family']=='ISSUER_BUSINESS_DML']
        self.assertEqual(len(rows),117);self.assertFalse(any(row['table']=='platform.database_action_grant'for row in rows))
        exception=next(row for row in self.packet['issuer_umbrella_links']if row['model']=='DatabaseActionGrant')
        self.assertIn('UNDISAMBIGUATED',exception['planned_maximum'])
        self.assertIn('ACTUAL_ISSUER_INSERT_OWN_SELECT_SEPARATE_COMMIT',self.packet['positive_protocol'])

    def test_composite_primary_keys_use_actual_database_columns(self):
        row=next(row for row in self.packet['cases']if row['name']=='ISSUER-UserRole-UPDATE')
        self.assertIn('user_id',row['referenced_columns']);self.assertNotIn('userId',row['referenced_columns'])

    def test_runtime_grant_INSERT_never_selects_inert_native_tuple(self):
        rows=[row for row in self.packet['cases']if row.get('operation')=='GRANT_INSERT']
        self.assertEqual(len(rows),2)
        for row in rows:
            sql=self.files[row['file']].decode();self.assertTrue(row['actual_tuple_required']);self.assertIn('__WA_BACKEND_PID__',sql);self.assertIn('__WA_TRANSACTION_ID__',sql);self.assertNotIn('inert-native-acl-fixture',sql)

    def test_all_SQL_parses_and_factory_byte_reproduces_without_execution(self):
        folder=ROOT/G['OUTPUT'];self.assertEqual({path.name:path.read_bytes()for path in folder.iterdir()if path.is_file()},self.files)
        statements=0
        for name,raw in self.files.items():
            if name.endswith('.sql'):statements+=len(parse_sql(raw.decode()))
        self.assertEqual(sum(name.endswith('.sql')for name in self.files),200);self.assertEqual(statements,765)

    def test_only_source_progress_is_historical_all_SQL_and_assertion_pins_stay_closed(self):
        packet=self.packet;self.assertNotIn(G['HISTORICAL_PROGRESS'],packet['source_files_sha256']);self.assertFalse(packet['historical_progress_context']['runtime_input'])
        for path in ('context/reconciliation/local-f0-assertions.json','context/reconciliation/database-candidate-tests.json',G['APPLICATION'],G['NATIVE'],G['NATIVE_COORDINATOR'],G['CTX']):self.assertIn(path,packet['source_files_sha256'])
        self.assertEqual(hashlib.sha256((ROOT/G['APPLICATION']).read_bytes()).hexdigest(),G['APPLICATION_SHA'])


if __name__=='__main__':unittest.main(verbosity=2)
