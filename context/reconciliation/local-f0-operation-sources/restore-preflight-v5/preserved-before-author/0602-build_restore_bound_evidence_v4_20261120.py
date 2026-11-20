"""Preserve existing bytes, then author only the NEW authorized V4 namespace."""
from pathlib import Path
from datetime import datetime,timezone
import ast,copy,hashlib,json
T=Path(__file__).resolve().parent;R=T/'workinants-correction-pass'
N3=('execute_local_f0_restore_20261119_bound_evidence_v3.py','local_f0_restore_operation_steps_bound_evidence_v3.py','prepare_local_f0_restore_plan_bound_evidence_v3.py','check_local_f0_restore_operation_bound_evidence_v3.py','pin_local_f0_restore_plan_20261119_bound_evidence_v3.py')
N4=tuple(name.replace('_v3.py','_v4.py') for name in N3)
A3='context/reconciliation/local-f0-operation-sources/restore-bound-evidence-v3';A4=A3[:-2]+'v4'
V3='context/reconciliation/local-f0-restore-bound-evidence-v3-source-validation.json';V4=V3.replace('-v3-','-v4-')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def new(path,raw):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as stream:stream.write(raw.encode() if isinstance(raw,str) else raw)
def checked(path,wanted):
 raw=path.read_bytes();assert sha(raw)==wanted,(str(path),'SOURCE_DRIFT');return raw
def data(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()
def funcs(text):return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(text).body if isinstance(node,(ast.FunctionDef,ast.ClassDef))}
def main():
 assert not any((T/name).exists() for name in N4) and not (R/A4).exists() and not (R/V4).exists()
 authorities={
  'restore980a_commit_boundary_source_correction_plan_20261119.json':'0206011e81e463dab2cb365ac3b20753a34fbf19e01fd728da409abfaafcabd4',
  'restore980a_commit_boundary_v4_independent_plan_review_20261119.json':'a7fb9bbf5017214693d885944ef2d1c903361a582cbd20fe3a4802a186a6633e',
  'restore980a_bound_evidence_v4_Root_implementation_ACK_20261119.json':'13ad95baee2df9164a88d34c694ed269407a0cb45f841ab0cd5244a7d8411b36'}
 for name,wanted in authorities.items():checked(T/name,wanted)
 hold_path=T/'restore-bound-evidence-v4-before-author-20261120';hold=json.loads(checked(hold_path/'partial-preservation-hold.json','9a72b44a5295438872c6ccb13f71d25f2c371d17f5e1c1f043dd0d650e4a8fa3'))
 protected={}
 for path,wanted in hold['snapshot_files_sha256'].items():
  checked(hold_path/path,wanted);prefix,relative=path.split('/',1);protected[str((T if prefix=='TASK' else R)/relative)]=wanted
 proposal=json.loads((R/'review-output/restore-control-rehearsal/proposal.json').read_bytes())
 assert len(proposal['source_files_sha256'])==67 and len(proposal['prepared_files_sha256'])==25
 protected.update({str(R/name):wanted for name,wanted in proposal['source_files_sha256'].items()})
 protected.update({str(R/'review-output/restore-control-rehearsal'/name):wanted for name,wanted in proposal['prepared_files_sha256'].items()})
 native_path=R/'scripts/local_f0_native_complete_evidence.py';native=checked(native_path,'50dfe9c1ae661785e408ad9707473028c6bc9b4d2ee308bdaad1844905668b76')
 maps={node.targets[0].id:ast.literal_eval(node.value) for node in ast.parse(native).body if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('PINS','AUDIT_PINS')}
 assert len(maps['PINS'])==303 and len(maps['AUDIT_PINS'])==3
 protected[str(native_path)]=sha(native)
 for value in maps.values():protected.update({str(R/name):wanted for name,wanted in value.items()})
 priv=json.loads(checked(T/'privilege_person_subject_v5_approved_committable_inventory_20261120.json','49678a1f53820fc63cb20a70f2bd75c0f9fe482a41b35ad9fddf81b52de08e6b'))
 assert len(priv['files_sha256'])==820;protected.update({str(R/name):wanted for name,wanted in priv['files_sha256'].items()})
 priv_live=json.loads((T/'privilege_person_subject_v5_frozen_author_delivery_20261119.json').read_bytes())
 protected.update({str(T/name):wanted for name,wanted in priv_live['new_owned5_sha256'].items()})
 app=json.loads(checked(T/'app_write_two_owned_resource_v1_frozen_source_plan_fix2_20261120.json','4642f1dbe94d357f0fa65958d31f0f71e2efffb83416567c694456c7372d481c'))
 protected.update({str(T/name):wanted for name,wanted in app['five_sha256'].items()})
 app_approved=json.loads(checked(T/'app_owned_fix2_source_approved_committable_inventory_20261120.json','a80aded1d049508cf72c6604bb70b371bdb582ba5a3296ce559875394b976d8f'))
 for key,value in app_approved.items():
  if key.endswith('sha256') and type(value) is dict and value and all(type(k) is str and type(v) is str and len(v)==64 for k,v in value.items()):
   for name,wanted in value.items():
    if (R/name).is_file():protected[str(R/name)]=wanted
 for path,wanted in protected.items():checked(Path(path),wanted)
 preservation={'schema':'workinants.restore-bound-evidence-v4-completed-before-author.v1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),'original137_physical_snapshots_verified':137,'protected_files_sha256':protected,'protected_count':len(protected),'Native_PINS':303,'Native_AUDIT_PINS':3,'Priv_approved_Root_inventory':820,'original_source67_artifacts25':'UNCHANGED','authorized_App_metadata':'Root approved inventorya80aded and validationf1d217ea; original c5d/67 retained in Fix2 freeze388. Five bytes unchanged.','authorities_sha256':authorities,'source_changes_before_preservation':False,'runtime':'NOT_RUN','Posture':'D'}
 new(hold_path/'completed-preservation.json',data(preservation))
 def namespace(text):return text.replace('_bound_evidence_v3.py','_bound_evidence_v4.py').replace('restore-bound-evidence-v3','restore-bound-evidence-v4')
 texts={newname:namespace((T/old).read_text(encoding='utf8')) for old,newname in zip(N3,N4)}
 steps=texts[N4[1]];helpers=(T/'restore_bound_v4_envelope_helpers.py.txt').read_text(encoding='utf8')
 steps=steps.replace('def bound_operation(',helpers+'\n\ndef bound_operation(',1)
 old="tail=WORKER['remove_redundant_begin'](text) if re.search(r'^BEGIN;\\s*$',text,re.M) else text.rstrip()+'\\nCOMMIT;'"
 assert steps.count(old)==1
 steps=steps.replace(old,"proof['transaction_envelope']={};tail=normalize_bound_envelope(text,proof['transaction_envelope']);save()")
 steps=steps.replace("'json_shape_matches':None,'json_matches':None,'diagnostic':bound_diagnostic(errors)","'json_shape_matches':None,'json_matches':None,'stderr_empty':type(errors) is str and errors=='','completion_comparisons':{'exit_zero':code_ok and code==0,'acknowledged':ack is True,'stderr_empty':type(errors) is str and errors==''},'diagnostic':bound_diagnostic(errors)")
 steps=steps.replace("need(type(code) is int and code==0 and ack is True and not errors.strip(),'RESTORE_BOUND_OPERATION_NOT_COMMITTED')","need(type(code) is int and code==0 and ack is True and errors=='','RESTORE_BOUND_OPERATION_NOT_COMMITTED')")
 texts[N4[1]]=steps
 # The pinner's four-source map is derived from the NEW actual bytes.
 for name in N4[:4]:compile(texts[name],str(T/name),'exec')
 pin=texts[N4[4]];node=next(node for node in ast.parse(pin).body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FROZEN' for t in node.targets));lines=pin.splitlines(keepends=True)
 pin=''.join(lines[:node.lineno-1])+'FROZEN='+repr({name:sha(texts[name].encode()) for name in N4[:4]})+'\n'+''.join(lines[node.end_lineno:]);texts[N4[4]]=pin
 for name,text in texts.items():compile(text,str(T/name),'exec');new(T/name,text)
 # Preserve the old closed archive and validation under the new namespace;
 # inherited physical/auth/safety reviews remain explicitly inherited only.
 oldval=json.loads((R/V3).read_bytes())
 for relative,wanted in oldval['archive_files_sha256'].items():new(R/A4/'preserved-bound-v3'/Path(relative).relative_to(A3),checked(R/relative,wanted))
 new(R/A4/'preserved-bound-v3/source-validation.json',(R/V3).read_bytes())
 for name,wanted in authorities.items():new(R/A4/'reviews'/name,checked(T/name,wanted))
 new(R/A4/'reviews/partial-preservation-hold.json',(hold_path/'partial-preservation-hold.json').read_bytes())
 new(R/A4/'reviews/completed-before-author-preservation.json',(hold_path/'completed-preservation.json').read_bytes())
 for name in N4:new(R/A4/(name+'.txt'),(T/name).read_bytes())
 validation=copy.deepcopy(oldval)
 for key in ('author_checks','Root_source_review','Root_actual_offline_checks','independent_bound_evidence_review'):validation['inherited_v3_'+key]=validation.pop(key,None)
 validation.update(source_version='bound-evidence-v4',source_root=A4,status='NEW_SOURCE_PENDING_AUTHOR_OFFLINE_INDEPENDENT_ROOT_REVIEW',operator_sources_sha256={name:sha((T/name).read_bytes()) for name in N4[:4]},all_five_sources_sha256={name:sha((T/name).read_bytes()) for name in N4},pin_helper_sha256=sha((T/N4[4]).read_bytes()),source_reviews=dict.fromkeys(('author','offline','independent','Root'),'PENDING'),independent_bound_evidence_review={'decision':'PENDING'},Root_source_review={'decision':'PENDING'},author_checks={'decision':'PENDING'},recorded_at_utc=datetime.now(timezone.utc).isoformat(),AST_scope={'base':'preserved-bound-v3','changed_functions':['bound_operation','bound_outcome'],'added_functions':['normalize_bound_envelope'],'canonical_business_SQL_or_guards_changed':False})
 validation['archive_files_sha256']={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in (R/A4).rglob('*') if p.is_file()}
 validation['archive_files_aggregate_sha256']=sha(''.join(k+'\0'+validation['archive_files_sha256'][k]+'\n' for k in sorted(validation['archive_files_sha256'])).encode())
 new(R/V4,data(validation))
 print(json.dumps({'status':'STATIC_SOURCE_AUTHORED_NOT_TESTED','five_sha256':validation['all_five_sources_sha256'],'archive_files':len(validation['archive_files_sha256']),'validation_sha256':sha((R/V4).read_bytes()),'protected':len(protected),'preservation_sha256':sha((hold_path/'completed-preservation.json').read_bytes()),'heavy_tests':'NOT_STARTED_WAIT_ROOT_V5_CLOSED'}))
if __name__=='__main__':main()
