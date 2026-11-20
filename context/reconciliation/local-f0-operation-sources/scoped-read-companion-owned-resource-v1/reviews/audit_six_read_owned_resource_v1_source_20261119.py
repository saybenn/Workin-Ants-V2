"""Read-only author verification of derived AST and preserved source bindings."""
from pathlib import Path
import ast,hashlib,json
TASK=Path(__file__).resolve().parent;ROOT=TASK/'workinants-correction-pass'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def nodes(path):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(path.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def audit():
 plan=json.loads((TASK/'six-read-owned-resource-v1-source-plan-v2-20261119.json').read_bytes());old=list(plan['exact_basis']['accepted_owner_validation']['operator_sources_sha256']);new=plan['new_outputs_after_ACK']['TASK_five']
 core_before=nodes(TASK/old[0]);core_after=nodes(TASK/new[0]);step_before=nodes(TASK/old[1]);step_after=nodes(TASK/new[1])
 protected_core=('Stop','need','save','remember_failure','persist_best_effort','emit_best_effort','event_best_effort','event','command','docker','json_ok','inventory','owned','inspect_container','inspect_volume','psql_args','sql','observe','secure_private_directory','preflight','ensure_image','create_resources','_required_safety_evidence_complete','_required_safety_save','_required_safety_event','_required_safety_failure','_required_safety_first_exception','_required_safety_barrier','_required_safety_decode','_required_safety_text','_required_safety_sql','_required_zero_backends','closed_backends','_RequiredSafetyBoundary','finalize','secret_scan','cleanup')
 core_exact={name:core_before[name]==core_after[name]for name in protected_core}
 # MountV2 stage/error names differ with the family; no executable expression changes.
 protected_steps=('validate_archive','read_target_manifest','bootstrap_all','provision_migration_tools','migrate','migrate_success','unique_json','verify_tool_data','metadata_allowlist','generated_identifier','filter_metadata','metadata_vocabulary_diagnostics','row_shapes','write_safe','safe_rejection','run_catalog_query','successful_query','collect_native','observe_public_baseline','acl_compatibility_preflight','text_compatibility_preflight')
 steps_exact={name:step_before[name]==step_after[name]for name in protected_steps}
 # verify_catalog_packet differs solely in exact target name after namespace derivation.
 old_text=(TASK/old[1]).read_text();new_text=(TASK/new[1]).read_text()
 def function_text(text,name):return ast.get_source_segment(text,next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name))
 projections={name:ast.dump(ast.parse(function_text(old_text,name).replace('OWNER_READ','SCOPED_READ').replace('ownerreads','scopedreads')),include_attributes=False)==ast.dump(ast.parse(function_text(new_text,name)),include_attributes=False)for name in('inspect_owner','verify_running_secret_tmpfs','source_authentication_preflight','verify_catalog_packet')}
 preservation=json.loads((TASK/'six-read-owned-resource-v1-plan-preservation-20261119/preservation.json').read_bytes());originals={name:sha((TASK/'six-read-owned-resource-v1-plan-preservation-20261119'/name).read_bytes())==wanted for name,wanted in preservation['files_sha256'].items()}
 parallel=json.loads((TASK/'app-write-two-APPWRITE2-01-source-correction-plan-20261119.json').read_bytes());allowed=set(parallel['bounded_source_changes_after_ACK']['paths']);current={name:sha((ROOT/name).read_bytes())==wanted for name,wanted in preservation['current_ROOT_files_sha256'].items()if name not in allowed and not name.startswith('review-output/app-write-two-control-rehearsal/')};current.update({'TASK/'+name:sha((TASK/name).read_bytes())==wanted for name,wanted in preservation['current_TASK_files_sha256'].items()})
 six=json.loads((ROOT/'context/reconciliation/local-f0-scoped-read-companion-source-validation.json').read_bytes());sixcurrent={name:sha((ROOT/name).read_bytes())==wanted for name,wanted in six['source_files_sha256'].items()};sixarchive={name:sha((ROOT/name).read_bytes())==wanted for name,wanted in six['archive_files_sha256'].items()}
 expected_functions={n.name for n in ast.parse((TASK/new[1]).read_bytes()).body if isinstance(n,ast.FunctionDef)};no_shadow=not bool(expected_functions&{'finalize','closed_backends','cleanup','sql','observe','_required_safety_sql'})
 assert all(core_exact.values()),{k:v for k,v in core_exact.items()if not v}
 assert all(steps_exact.values()),{k:v for k,v in steps_exact.items()if not v}
 assert all(projections.values()),projections
 assert all(originals.values())and all(current.values())and all(sixcurrent.values())and all(sixarchive.values())and no_shadow
 value={'schema':'workinants.sixread-owned-resource-author-source-audit.v1','status':'PASS_SOURCE_ONLY_AUTHOR_CHECKS_NOT_INDEPENDENT_APPROVAL','exact_core_AST':core_exact,'exact_ordinary_steps_AST':steps_exact,'namespace_only_resource_and_catalog_AST':projections,'Steps_shadow_common_functions':not no_shadow,'preserved_historical_snapshots':len(originals),'current_non_AppWrite_bindings':len(current),'approved_SixRead100_unchanged':all(sixcurrent.values()),'approved_SixRead_archive10_unchanged':all(sixarchive.values()),'authorized_parallel_AppWrite_exclusion':'Root explicit ACK53f8/fd23 five+generated App namespace only; current bytes not read/admitted','new_five_sha256':{name:sha((TASK/name).read_bytes())for name in new},'runtime':'NOT_RUN','Posture':'D'}
 target=TASK/'six_read_owned_resource_v1_source_audit_20261119.json';target.write_text(json.dumps(value,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':value['status'],'protected_core':len(core_exact),'ordinary_steps':len(steps_exact),'namespace_projection':len(projections),'current_bindings':len(current),'sha256':sha(target.read_bytes())}))
if __name__=='__main__':audit()
