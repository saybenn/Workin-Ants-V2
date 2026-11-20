"""Static NEW offline-test derivation, no tests/processes are run here."""
from pathlib import Path
import ast
T=Path(__file__).resolve().parent
def fresh(name,text):
 compile(text,str(T/name),'exec')
 with (T/name).open('x',encoding='utf8',newline='\n') as stream:stream.write(text)
focused=(T/'check_restore_bound_evidence_v3_focused_20261119.py').read_text(encoding='utf8')
focused=focused.replace("CORE=T/'execute_local_f0_restore_20261119_bound_evidence_v3.py';STEPS=T/'local_f0_restore_operation_steps_bound_evidence_v3.py'","CORE=T/'execute_local_f0_restore_20261119_bound_evidence_v4.py';STEPS=T/'local_f0_restore_operation_steps_bound_evidence_v4.py'")
tree=ast.parse(focused);process=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Process');flush=next(x for x in process.body if isinstance(x,ast.FunctionDef) and x.name=='flush');lines=focused.splitlines(keepends=True)
focused=''.join(lines[:flush.lineno-1])+(T/'restore_bound_v4_stateful_transport.py.txt').read_text(encoding='utf8').rstrip()+'\n'+''.join(lines[flush.end_lineno:])
focused=focused.replace("self.rows=['WA_CUSTOMER_CONTROL_READY_TO_COMMIT'];self.error=None;","self.rows=None;self.error=None;self.warning=None;self.emissions=[];self.source_customer_committed=False;self.source_schedule_committed=False;")
focused=focused.replace("if __name__=='__main__':unittest.main(verbosity=2)",(T/'restore_bound_v4_envelope_tests.py.txt').read_text(encoding='utf8')+"\nif __name__=='__main__':unittest.main(verbosity=2)\n")
fresh('check_restore_bound_evidence_v4_focused_20261120.py',focused)
gates=(T/'check_restore_bound_evidence_v3_source_gates_20261119.py').read_text(encoding='utf8').replace('_bound_evidence_v3.py','_bound_evidence_v4.py').replace('restore-bound-evidence-v3','restore-bound-evidence-v4').replace('check_restore_bound_evidence_v3_focused_20261119.py','check_restore_bound_evidence_v4_focused_20261120.py')
# The old author preservation and old scope comparison are historical; V4 has
# its own exact, closed scope check below rather than inventing a V4 history.
node=next(x for x in ast.parse(gates).body if isinstance(x,ast.ClassDef));method=next(x for x in node.body if isinstance(x,ast.FunctionDef) and x.name=='test_new_five_scope_old_recipe_and_archive_are_exact');lines=gates.splitlines(keepends=True)
replacement='''    def test_new_five_scope_old_recipe_and_archive_are_exact(self):
        root=ROOT;hold=TASK/'restore-bound-evidence-v4-before-author-20261120';pres=json.loads((hold/'completed-preservation.json').read_bytes())
        for path,wanted in pres['protected_files_sha256'].items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),wanted,path)
        def funcs(raw):return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(raw).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
        for prefix in ('execute_local_f0_restore_20261119','prepare_local_f0_restore_plan','pin_local_f0_restore_plan_20261119'):
            old=funcs((TASK/(prefix+'_bound_evidence_v3.py')).read_text());new=funcs((TASK/(prefix+'_bound_evidence_v4.py')).read_text().replace('_bound_evidence_v4.py','_bound_evidence_v3.py').replace('restore-bound-evidence-v4','restore-bound-evidence-v3'));self.assertEqual(old,new,prefix)
        old=funcs((TASK/'local_f0_restore_operation_steps_bound_evidence_v3.py').read_bytes());new=funcs((TASK/'local_f0_restore_operation_steps_bound_evidence_v4.py').read_text().replace('_bound_evidence_v4.py','_bound_evidence_v3.py').replace('restore-bound-evidence-v4','restore-bound-evidence-v3'))
        self.assertEqual(set(new)-set(old),{'normalize_bound_envelope'})
        for name in set(old)-{'bound_operation','bound_outcome'}:self.assertEqual(old[name],new[name],name)
        record=json.loads((root/'context/reconciliation/local-f0-restore-bound-evidence-v4-source-validation.json').read_bytes());self.assertEqual(record['independent_bound_evidence_review'],{'decision':'PENDING'});self.assertEqual(set(record['source_reviews'].values()),{'PENDING'})
        actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/record['source_root']).rglob('*') if p.is_file()};self.assertEqual(record['archive_files_sha256'],actual)
        for name,wanted in record['all_five_sources_sha256'].items():self.assertEqual((TASK/name).read_bytes(),(root/record['source_root']/(name+'.txt')).read_bytes());self.assertEqual(hashlib.sha256((TASK/name).read_bytes()).hexdigest(),wanted)
'''
gates=''.join(lines[:method.lineno-1])+replacement+''.join(lines[method.end_lineno:]);fresh('check_restore_bound_evidence_v4_source_gates_20261120.py',gates)
print('STATIC_TEST_SOURCES_CREATED_NOT_RUN')
