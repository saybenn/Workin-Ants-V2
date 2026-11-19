"""Environment-free emitted-SQL deferred-event regression; no engine execution.

This deliberately models only the PG17.11 pending-event/ALTER ordering rule,
not PostgreSQL acceptance or infrastructure-owner semantics. Existing native
factory tests are rerun against the NEW generator with every process forbidden.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import socket
import subprocess
import unittest
from unittest.mock import patch

from pglast import ast, parse_sql
import catalog_manifest

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'review-output/native-table-denials'
NEW=ROOT/'review-output/native-table-denials-v2'
GENERATOR=runpy.run_path(str(ROOT/'scripts/prepare-native-table-denials-v2.py'))
BF='bf542f88525e96d7d1c93ef06425278a82e1328043d60879ac34191f1bee3000'


class OrderingStop(Exception):
    def __init__(self,code,relation=None):self.code,self.relation=code,relation;super().__init__(code)


class PendingEventModel:
    """Consume actual parsed SQL and source trigger metadata, never case verdicts."""
    def __init__(self,expected,check=None):
        self.triggers=list(expected['triggers'].values());self.check=check or (lambda table,name:True)
        self.disabled=set();self.pending=[];self.validated=0;self.inserted=0;self.restored=0;self.deferred=True
        self.queued_relations=set();self.barrier_after_insert_count=None;self.first_restore_pending=None
    @staticmethod
    def relation(value):return value.schemaname+'.'+value.relname
    def validate(self,table,name):
        if self.check(table,name) is not True:raise OrderingStop('P0001',table)
        self.validated+=1
    def drain(self):
        for table,name in self.pending:self.validate(table,name)
        self.pending=[]
    def execute(self,text):
        for raw in parse_sql(text):
            node=raw.stmt
            if isinstance(node,ast.AlterTableStmt):
                table=self.relation(node.relation)
                if self.pending and any(relation==table for relation,_ in self.pending):raise OrderingStop('55006',table)
                for command in node.cmds:
                    key=(table,command.name)
                    assert any((row['table'],row['name'])==key for row in self.triggers),'UNKNOWN_USER_TRIGGER'
                    if command.subtype.name=='AT_DisableTrig':self.disabled.add(key)
                    elif command.subtype.name=='AT_EnableTrig':
                        if self.first_restore_pending is None:self.first_restore_pending=len(self.pending)
                        self.disabled.remove(key);self.restored+=1
                    else:raise AssertionError('UNMODELED_TRIGGER_ALTER')
            elif isinstance(node,ast.InsertStmt):
                self.inserted+=1;table=self.relation(node.relation)
                for trigger in self.triggers:
                    if trigger['table']!=table or (table,trigger['name']) in self.disabled:continue
                    if trigger['constraint'] and trigger['deferrable'] and trigger['initially_deferred'] and trigger['event_bits'] & 4:
                        self.queued_relations.add(table)
                        if self.deferred:self.pending.append((table,trigger['name']))
                        else:self.validate(table,trigger['name'])
            elif isinstance(node,ast.ConstraintsSetStmt):
                assert node.constraints is None and node.deferred is False,'ONLY_ALL_IMMEDIATE_REVIEWED'
                self.barrier_after_insert_count=self.inserted;self.drain();self.deferred=False
            elif isinstance(node,ast.TransactionStmt) and node.kind.name=='TRANS_STMT_COMMIT':self.drain()
        return self


def factory_test_parent():
    namespace=runpy.run_path(str(ROOT/'scripts/sql-review/test_native_deny_fixture_factory.py'))
    parent=namespace['NativeDenyFixtureTests']
    parent.setUpClass.__func__.__globals__['generator']=GENERATOR
    return parent


class NewPacketFactoryTests(factory_test_parent()):
    def setUp(self):
        for name in ('run','Popen','check_output','check_call','call'):
            guard=patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
        guard=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)


class DeferredRestoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected=catalog_manifest.build_manifest()['expected'];cls.files,cls.packet=GENERATOR['build']()
    def setUp(self):
        for name in ('run','Popen','check_output','check_call','call'):
            guard=patch.object(subprocess,name,side_effect=AssertionError('PROCESS_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
        guard=patch.object(socket,'create_connection',side_effect=AssertionError('NETWORK_FORBIDDEN'));guard.start();self.addCleanup(guard.stop)
    def test_executed_old_source_order_reproduces_pending_user_trigger_55006_only_in_model(self):
        model=PendingEventModel(self.expected)
        with self.assertRaises(OrderingStop) as found:model.execute((OLD/'native-fact-setup.sql').read_text())
        self.assertEqual(found.exception.code,'55006');self.assertEqual(found.exception.relation,'platform.runtime_outbox_message')
        self.assertEqual(model.queued_relations,{'platform.owner_mutation_evidence','platform.runtime_outbox_message'})
        self.assertEqual(model.inserted,205);self.assertGreater(len(model.pending),0)
    def test_new_sql_drains_retained_checks_before_any_restore_and_commits(self):
        model=PendingEventModel(self.expected).execute(self.files['native-fact-setup.sql'])
        self.assertEqual(model.inserted,205);self.assertEqual(model.barrier_after_insert_count,205)
        self.assertEqual(model.first_restore_pending,0);self.assertEqual(model.pending,[])
        self.assertGreater(model.validated,0);self.assertEqual(model.restored,60);self.assertFalse(model.disabled)
    def test_removed_or_too_late_barrier_rejects_actual_parsed_statement_order(self):
        text=self.files['native-fact-setup.sql'];without=text.replace('SET CONSTRAINTS ALL IMMEDIATE;\n','')
        for mutant in (without,without.replace('COMMIT;','SET CONSTRAINTS ALL IMMEDIATE;\nCOMMIT;')):
            with self.assertRaises(OrderingStop) as found:PendingEventModel(self.expected).execute(mutant)
            self.assertEqual(found.exception.code,'55006')
    def test_retained_check_failure_still_stops_before_restoration_and_never_passes(self):
        model=PendingEventModel(self.expected,check=lambda table,name:False)
        with self.assertRaises(OrderingStop) as found:model.execute(self.files['native-fact-setup.sql'])
        self.assertEqual(found.exception.code,'P0001');self.assertEqual(model.restored,0)
        self.assertIsNone(model.first_restore_pending);self.assertEqual(model.validated,0);self.assertTrue(model.pending)
    def test_no_fk_deferral_no_new_bypass_and_retained_guards_unchanged(self):
        original=json.loads((OLD/'packet.json').read_bytes())
        self.assertEqual(self.packet['setup_bypassed_user_triggers'],original['setup_bypassed_user_triggers'])
        self.assertEqual(self.packet['setup_retained_user_triggers'],original['setup_retained_user_triggers'])
        self.assertEqual(self.packet['synthetic_facts'],original['synthetic_facts']);self.assertEqual(self.packet['cases'],original['cases'])
        text=self.files['native-fact-setup.sql'];self.assertNotIn('SET CONSTRAINTS ALL DEFERRED',text)
        self.assertNotIn('DISABLE TRIGGER ALL',text);self.assertNotIn('DISABLE TRIGGER USER',text)
        self.assertNotIn('session_replication_role',text);self.assertNotIn('DROP CONSTRAINT',text)
        constraints=[row.stmt for row in parse_sql(text) if isinstance(row.stmt,ast.ConstraintsSetStmt)]
        self.assertEqual(len(constraints),1);self.assertIs(constraints[0].deferred,False)
    def test_only_setup_sql_changes_relative_to_exact_BF83_and_corrected_barrier_has_exact_placement(self):
        packet=json.loads((OLD/'packet.json').read_bytes());self.assertEqual(hashlib.sha256((OLD/'packet.json').read_bytes()).hexdigest(),BF)
        self.assertEqual(set(self.packet['files_sha256']),set(packet['files_sha256']))
        changed=[name for name in packet['files_sha256'] if self.files[name].encode()!=(OLD/name).read_bytes()]
        self.assertEqual(changed,['native-fact-setup.sql'])
        original=(OLD/'native-fact-setup.sql').read_text();corrected=self.files['native-fact-setup.sql']
        self.assertEqual(corrected.replace('SET CONSTRAINTS ALL IMMEDIATE;\n',''),original)
        statements=[row.stmt for row in parse_sql(corrected)];barrier=next(i for i,row in enumerate(statements) if isinstance(row,ast.ConstraintsSetStmt))
        last_insert=max(i for i,row in enumerate(statements) if isinstance(row,ast.InsertStmt));first_enable=min(i for i,row in enumerate(statements) if isinstance(row,ast.AlterTableStmt) and any(c.subtype.name=='AT_EnableTrig' for c in row.cmds))
        self.assertLess(last_insert,barrier);self.assertLess(barrier,first_enable)
    def test_new_artifacts_reproduce_and_all_source_statuses_remain_unexecuted(self):
        files,packet=GENERATOR['build']();self.assertEqual(files,self.files);self.assertEqual(packet,self.packet)
        if NEW.exists():
            self.assertEqual({p.name for p in NEW.iterdir()},set(files))
            for name,value in files.items():self.assertEqual((NEW/name).read_bytes(),value.encode())
        self.assertTrue(all(case['status']=='NOT_RUN' and all(p['status']=='NOT_RUN' for p in case['probes']) for case in packet['cases']))
        self.assertFalse(packet['database_contacted']);self.assertFalse(packet['sql_executed'])
        self.assertEqual(len(packet['preparation_blocks']),4)


if __name__=='__main__':unittest.main(verbosity=2)
