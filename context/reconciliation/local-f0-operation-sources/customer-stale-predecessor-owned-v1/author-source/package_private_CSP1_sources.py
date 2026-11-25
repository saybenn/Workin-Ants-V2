"""Private PENDING source metadata only; no external API."""
import hashlib,json,pathlib,shutil,sys
sys.dont_write_bytecode=True
A=pathlib.Path(__file__).parent;P=A/'workinants-correction-pass';T=A.parent
sha=lambda b:hashlib.sha256(b).hexdigest();enc=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
plan=json.loads((A/'owning-plan.json').read_bytes());archive=P/plan['new_archive'];five={n:sha((A/n).read_bytes())for n in plan['new_owned_five']}
for n in plan['new_owned_five']:
 dst=archive/(n+'.txt');dst.write_bytes((A/n).read_bytes())
for n in('owning-plan.json','Root-plan-ACK.json','transport-private-plan-addendum.json','transport-closure-composition-addendum.json','before-author-preservation.json','build_private_CSP1_sources.py','CSP1_steps_extension.py.txt','CSP1_prepare_extension.py.txt','assemble_CSP1_private_checker.py','CSP1_checker_extension.py.txt','run_private_CSP1_prepare.py','run_CSP1_focused_checks.py','check_blocked_spawn_limit.py','package_private_CSP1_sources.py'):
 dst=archive/'author-source'/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes((A/n).read_bytes())
profile={'schema':'workinants.CSP1-closed-Git-profile-private-addendum.v1','Root_ruling_reference':'Root message during CSP1 implementation: measure actual full Git framing, use exact closed command-profile cap, at-limit/overflow/wrong-profile vectors; no arbitrary general cap inflation','native_profile':'16 MiB per channel; strict UTF8 facade and existing 180-second maximum caller','Git_profile':'exact readonly cat-file --batch command/payload/commit/map; actual closed current-file hash and byte-length recheck; exact sum(blob bytes + 48 + decimal length digits) stdout bound; 65536 stderr bound; complete framing and actual Git SHA1 plus expected SHA256 verified','source_only':'PENDING distinct code review; no actual Git/Docker/database/network call','runtime':'NOT_RUN','Posture':'D'}
(archive/'author-source/closed-Git-profile-addendum.json').write_bytes(enc(profile))
for n,h in plan['reuse_basis_five_sha256'].items():
 raw=(A/'preserved-read13-base'/n).read_bytes();assert sha(raw)==h;dst=archive/'reuse-basis'/(n+'.txt');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
for n,h in {'execute_local_f0_lease_mechanism_v1_20261120.py':'8e2c2529727fd8270f709737c3129c1ad650e09c6f70914dedd0ea46354250e9','runtime_lease_mechanism_v1_transport_v2_independent_code_security_source_review_20261123.json':'8b1324feeae4a81e2b2918473aa166b1acbb7c540a16d6ec52a3f1c902936aee'}.items():
 raw=(T/n).read_bytes();assert sha(raw)==h;dst=archive/'reuse-basis'/(n+'.txt'if n.endswith('.py')else n);dst.write_bytes(raw)
for p in (A/'author-history').rglob('*')if(A/'author-history').exists()else():
 if p.is_file():dst=archive/'author-history'/p.relative_to(A/'author-history');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
owned={'schema':'workinants.customer-stale-predecessor-owned-v1-source-validation.v1','status':'SOURCE_UNDER_PRIVATE_IMPLEMENTATION_PENDING_REVIEW','operator_sources_sha256':five,'archive_files_sha256':{p.relative_to(P).as_posix():sha(p.read_bytes())for p in sorted(archive.rglob('*'))if p.is_file()},'accepted_child_validation':{'path':plan['child_source']['current_validation_path'],'sha256':plan['child_source']['current_validation_sha256']},'source_plan_sha256':'d089410ed89417b80a5009b431135ef8aba4298a258e2babdfc2d77309be4595','Root_plan_ACK_sha256':'4af1e28337986f904d1c8c1e3a4a2c63bd72a821a323b85166c00c07688579dd','operation_run_id':plan['proposed_identity']['run_id'],'fixture_run_id':plan['proposed_identity']['fixture_run_id'],'runtime':'NOT_RUN','Posture':'D','maximum_prospective_assertion':'P0C-CAS-01/control.stale_predecessor','assertion_promotions':0}
for key in('independent_source_review','independent_owned_resource_review','independent_safety_sql_review','independent_binary_transport_review','Root_source_review'):owned[key]={'decision':'PENDING'}
(P/plan['new_validation']).write_bytes(enc(owned))
baseline=json.loads((A/'catalog-baseline.json').read_bytes())
for n,h in baseline['catalog']['tool_source_files_sha256'].items():
 raw=(T/'workinants-correction-pass'/n).read_bytes();assert sha(raw)==h;dst=P/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
print(json.dumps({'owned_validation_sha256':sha((P/plan['new_validation']).read_bytes()),'archive_files':len(owned['archive_files_sha256']),'five_sha256':five,'runtime':'NOT_RUN','all_new_gates':'PENDING'}))
