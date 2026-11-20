"""Apply bounded new-family source layer only; accepted sources are read-only."""
from pathlib import Path
import ast
TASK=Path(__file__).resolve().parent
path=TASK/'local_f0_scoped_reads_owned_resource_v1_operation_steps.py'
text=path.read_text(encoding='utf8')
addition=(TASK/'six_read_owned_resource_v1_steps_additions_20261119.py.txt').read_text(encoding='utf8')
def function(text,node):return '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])+'\n'
def replace(text,name,replacement):
 node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name)
 lines=text.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+replacement+''.join(lines[node.end_lineno:])
nodes=ast.parse(addition).body
definitions=[n for n in nodes if isinstance(n,ast.FunctionDef)]
old_names={n.name for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
prefix=''.join(function(addition,n)if isinstance(n,ast.FunctionDef)else '\n'.join(addition.splitlines()[n.lineno-1:n.end_lineno])+'\n'for n in nodes if not isinstance(n,ast.FunctionDef))
extra=[]
for node in definitions:
 if node.name in old_names:text=replace(text,node.name,function(addition,node))
 else:extra.append(function(addition,node))
main=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='main')
lines=text.splitlines(keepends=True);text=''.join(lines[:main.lineno-1])+prefix+'\n'+'\n'.join(extra)+'\n'+''.join(lines[main.lineno-1:])
text=text.replace("need(owned['schema']=='workinants.scoped-read-companion-owned-resource-v1-source-validation.v1'", "need(owned['schema']=='workinants.scoped-read-companion-owned-resource-v1-source-validation.v1'")
text=text.replace("review=validation.get('independent_safety_sql_review')", "review=validation.get('independent_owned_resource_review')")
text=text.replace("def oracle_records(stdout):", "def oracle_records(stdout,prefix=''):\n    need(prefix in ('','post-'),'SCOPED_ORACLE_PREFIX')")
text=text.replace("write_safe(('oracle-preflight.json','oracle-results.json','oracle-closure.json')[index],value)", "write_safe(prefix+('oracle-preflight.json','oracle-results.json','oracle-closure.json')[index],value)")
text=text.replace("def catalog_experiment():\n    target", "def catalog_experiment():\n    need('first_install' not in SCOPED_STATE,'SCOPED_SINGLE_GENUINE_INSTALL_ONLY')\n    target")
needle="tools['catalog_expression_oracle'].validate_evidence(manifest, native, oracle_evidence, database=DB, grantor='postgres', root=ROOT)"
assert text.count(needle)==1
text=text.replace(needle,"oracle_registry = "+needle)
needle="    report['qualified_native_snapshot_sha256'] = digest(native)"
assert text.count(needle)==1
text=text.replace(needle,"    qualify_native_counts(comparison,ledger_result,oracle_registry,parts[1])\n    SCOPED_STATE['first_install']={'run_id':RUN_ID,'container_id':created_containers[name],'source_commit':COMMIT,'source_tree':TREE,'packet_sha256':PACKET,'installed':installed,'registration':registration,'native':native,'comparison':comparison,'ledger':ledger_result,'oracle_registry':oracle_registry}\n"+needle)
text=text.replace("if relative in HELPERS:\n        need", "if relative in HELPERS:\n        read_pinned(relative)\n        need")
assert 'def admit_scoped_read_sources' in text and 'def readonly_post_proof' in text
assert not any(isinstance(n,ast.FunctionDef)and n.name.startswith('owner_read')for n in ast.parse(text).body)
path.write_text(text,encoding='utf8',newline='\n')
print('NEW_STEPS_LAYER_APPLIED_UNREVIEWED')
