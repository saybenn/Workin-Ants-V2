from pathlib import Path
TASK=Path(__file__).resolve().parent
for name in ('local_f0_scoped_reads_owned_resource_v1_operation_steps.py','six_read_owned_resource_v1_steps_additions_20261119.py.txt'):
 path=TASK/name;text=path.read_text()
 text=text.replace("len(fixtures['prepared_files_sha256'])==77","len(fixtures['prepared_files_sha256'])==76").replace('SCOPED_READ_CLOSED_23_77_PACKET','SCOPED_READ_CLOSED_23_SOURCES_76_SQL_77_ARTIFACTS')
 text=text.replace("first['source_commit']==COMMIT and first['packet_sha256']==PACKET","first['source_commit']==COMMIT and first['source_tree']==TREE and first['packet_sha256']==PACKET")
 text=text.replace("unique_json(native_path.read_bytes())==first['native']and unique_json(comparison_path.read_bytes())==first['comparison']","canonical(unique_json(native_path.read_bytes()))==canonical(first['native'])and canonical(unique_json(comparison_path.read_bytes()))==canonical(first['comparison'])")
 text=text.replace("if failure is not None:raise failure\n    need(details['component_closure_confirmed']","if failure is not None:raise failure\n    _required_safety_barrier()\n    need(details['component_closure_confirmed']")
 path.write_text(text,encoding='utf8',newline='\n')
print('NEW_UNFROZEN_ADMISSION_AND_IO_BARRIER_TIGHTENED')
