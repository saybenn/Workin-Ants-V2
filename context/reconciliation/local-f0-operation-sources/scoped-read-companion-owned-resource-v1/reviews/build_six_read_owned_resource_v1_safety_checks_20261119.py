from pathlib import Path
TASK=Path(__file__).resolve().parent
s=(TASK/'check_owner_resource_mount_v2_safety_composed_20261119.py').read_text()
names={'execute_local_f0_owner_read_20261119_resource_mount_v2.py':'execute_local_f0_scoped_reads_owned_resource_v1_20261119.py','local_f0_owner_read_operation_steps_resource_mount_v2.py':'local_f0_scoped_reads_owned_resource_v1_operation_steps.py','prepare_local_f0_owner_read_plan_resource_mount_v2.py':'prepare_local_f0_scoped_reads_owned_resource_v1_plan.py','check_local_f0_owner_read_operation_resource_mount_v2.py':'check_local_f0_scoped_reads_owned_resource_v1_operation.py','pin_local_f0_owner_read_plan_20261119_resource_mount_v2.py':'pin_local_f0_scoped_reads_owned_resource_v1_plan_20261119.py'}
for a,b in names.items():s=s.replace(a,b)
s=s.replace("exec(compile(fixture,str(Path(__file__)),'exec'),globals())","fixture=fixture.replace('APPROVED_LOCAL_F0_OWNER_READ_ATTEMPT','APPROVED_LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_ATTEMPT')\nexec(compile(fixture,str(Path(__file__)),'exec'),globals())")
s=s.replace("old=TASK/'safety-sql-before-author-20261119/execute_local_f0_owner_read_20261118_finally_v2.py'","old=TASK/'execute_local_f0_owner_read_20261119_resource_mount_v2.py'")
p=TASK/'check_six_read_owned_resource_v1_safety_composed_20261119.py';assert not p.exists();p.write_text(s,encoding='utf8',newline='\n')
