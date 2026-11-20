"""Plan/source-preservation assertions for the complete new package."""
from pathlib import Path
import ast,hashlib,json,runpy,unittest
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass'
def sha(b):return hashlib.sha256(b).hexdigest()
def nodes(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
class SourcePreservationTests(unittest.TestCase):
    def test_old_outer_root_sources_and_all_old_packet_bytes_remain_exact(self):
        pins=json.loads((T/'install_review_ready_v3_before_author_preservation_20261119.json').read_bytes())['files_sha256']
        for p,h in pins.items():self.assertEqual(sha(Path(p).read_bytes()),h,p)
    def test_unchanged_core_normal_sql_main_cleanup_and_exact_accepted_common_ast(self):
        old=nodes(T/'execute_local_f0_install_controls_20261119_safety_sql_v1.py');new=nodes(T/'execute_local_f0_install_controls_20261119_review_ready_v3.py');allowed={'initialize','save','finish_report','launch'}
        self.assertEqual(set(new)-set(old),{'_remember_first_save_io'})
        for name in set(old)-allowed:self.assertEqual(new[name],old[name],name)
        oldsteps=nodes(T/'local_f0_install_controls_operation_steps_safety_sql_v1.py');newsteps=nodes(T/'local_f0_install_controls_operation_steps_review_ready_v3.py');allowed={'verify_common_packet','verify_packet','install_coordinator_experiment'}
        self.assertEqual(set(oldsteps),set(newsteps))
        for name in set(oldsteps)-allowed:self.assertEqual(oldsteps[name],newsteps[name],name)
    def test_coordinator_sql_roles_finalizers_activation_failure_recovery_and_finally_ast_unchanged(self):
        a=ast.parse((R/'scripts/sql-review/run-install-control-rehearsal-v2.py').read_bytes());b=ast.parse((R/'scripts/sql-review/run-install-control-rehearsal-v3.py').read_bytes())
        x=next(n for n in a.body if isinstance(n,ast.ClassDef) and n.name=='Coordinator');y=next(n for n in b.body if isinstance(n,ast.ClassDef) and n.name=='Coordinator');old={n.name:ast.dump(n,include_attributes=False) for n in x.body if isinstance(n,ast.FunctionDef)};new={n.name:ast.dump(n,include_attributes=False) for n in y.body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(set(old),set(new))
        for name in set(old)-{'review'}:self.assertEqual(old[name],new[name],name)
    def test_ledger_helper_only_namespace_changes_and_original_authority_exact(self):
        old=(R/'scripts/sql-review/install_ledger_proof_v2.py').read_text();new=(R/'scripts/sql-review/install_ledger_proof_v3.py').read_text().replace('install_ledger_proof_v3','install_ledger_proof_v2').replace('install-control-rehearsal-v3','install-control-rehearsal-v2');self.assertEqual(old,new)
        self.assertEqual(sha((R/'scripts/install_control_protocol_v2.py').read_bytes()),'6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f')
    def test_all_eleven_actual_sql_and_reproduced_bytes_are_identical(self):
        G=runpy.run_path(str(R/'scripts/prepare-install-control-rehearsal-v3.py'));files,packet=G['build'](R);old=json.loads((R/'review-output/install-control-rehearsal-v2/fixtures.json').read_bytes());names=[n for n in old['prepared_files_sha256'] if n.endswith('.sql')];self.assertEqual(len(names),11)
        for name in names:self.assertEqual(files[name],(R/'review-output/install-control-rehearsal-v2'/name).read_bytes());self.assertEqual(files[name],(R/'review-output/install-control-rehearsal-v3'/name).read_bytes())
    def test_all_ten_root_sources_and_five_physical_snapshots_are_admitted_before_compile(self):
        G=runpy.run_path(str(R/'scripts/prepare-install-control-rehearsal-v3.py'));C=runpy.run_path(str(R/'scripts/sql-review/run-install-control-rehearsal-v3.py'));P=runpy.run_path(str(T/'prepare_local_f0_install_controls_plan_review_ready_v3.py'));S=runpy.run_path(str(T/'execute_local_f0_install_controls_20261119_review_ready_v3.py'))['launch'].__globals__;exec(compile((T/'local_f0_install_controls_operation_steps_review_ready_v3.py').read_bytes(),'new_steps','exec'),S);v=json.loads((R/'context/reconciliation/local-f0-install-controls-review-ready-v3-source-validation.json').read_bytes())
        self.assertEqual(len(v['root_sources_sha256']),10);self.assertLessEqual(set(v['root_sources_sha256']),set(G['INPUTS']));self.assertEqual(set(C['MODULES']),set(P['MODULES']));self.assertEqual(P['MODULES'],S['FIXED_RUNTIME'])
        for p,h in P['MODULES'].items():self.assertEqual(sha((R/p).read_bytes()),h,p)
        for name,h in v['all_five_sources_sha256'].items():self.assertEqual((R/v['source_root']/(name+'.txt')).read_bytes(),(T/name).read_bytes());self.assertEqual(sha((T/name).read_bytes()),h)
    def test_closed_archive_and_all_four_production_review_gates_remain_pending(self):
        v=json.loads((R/'context/reconciliation/local-f0-install-controls-review-ready-v3-source-validation.json').read_bytes());actual={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in (R/v['source_root']).rglob('*') if p.is_file()};self.assertEqual(actual,v['archive_files_sha256'])
        for gate in ('independent_source_review','independent_ledger_source_review','independent_safety_sql_review','independent_review_publication_source_review'):self.assertEqual(v[gate],{'decision':'PENDING'})
    def test_preserved_actual_watcher_newline_and_unknown_actual_cause_are_not_rewritten(self):
        p=T/'install7923-catalog-stopped-watch-review-20261119/original-watch-stdin.py';self.assertEqual(sha(p.read_bytes()),'c2736ecd0224bdfc33bf5393de8acbea060eb6817f10b127de2401763fd7a026');tree=ast.parse(p.read_bytes());self.assertTrue(any(isinstance(n,ast.Constant) and n.value=='\n' for n in ast.walk(tree)))
if __name__=='__main__':unittest.main(verbosity=2)
