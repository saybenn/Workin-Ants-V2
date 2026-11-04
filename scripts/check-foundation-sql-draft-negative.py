#!/usr/bin/env python3
"""Independent mutations of SQL/ACL evidence; no SQL execution or database."""
from pathlib import Path
import tempfile,shutil,json,runpy
ROOT=Path(__file__).resolve().parents[1]
CHECK=runpy.run_path(str(ROOT/'scripts/check-foundation-sql-draft.py'))['checks']
manifest=json.loads((ROOT/'context/reconciliation/foundation-sql-draft-manifest.json').read_text())
APP='review-output/foundation-application.review.sql';BOOT='review-output/foundation-bootstrap.review.sql'
cases=[
 ('remove tuple login',APP,'database_login_role=session_user::text','database_login_role=database_login_role'),
 ('remove tuple backend',APP,'backend_pid=pg_backend_pid()','backend_pid=backend_pid'),
 ('remove tuple xid',APP,'transaction_id=pg_current_xact_id()::text','transaction_id=transaction_id'),
 ('remove current generation',APP,'s.security_generation=g.security_generation','s.security_generation=s.security_generation'),
 ('remove revoke check',APP,'revoked_at IS NULL','true'),
 ('remove expiry check',APP,'expires_at > clock_timestamp()','true'),
 ('lock at bind before revoker',APP,'bound_grant(false)','bound_grant(true)'),
 ('remove forced RLS',APP,'ALTER TABLE "app"."customer_profiles" FORCE ROW LEVEL SECURITY;',''),
 ('wrong helper owner',APP,'ALTER FUNCTION platform_private.bind_request_context(text) OWNER TO wa_private_helper_owner;','ALTER FUNCTION platform_private.bind_request_context(text) OWNER TO wa_schema_owner;'),
 ('remove default execute revocation',BOOT,'ALTER DEFAULT PRIVILEGES FOR ROLE wa_schema_owner REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;',''),
 ('remove null-safe consent',APP,'p.context_id IS DISTINCT FROM NEW.context_id','p.context_id<>NEW.context_id'),
 ('remove durable unknown noncommit',APP,"r.state='fenced_noncommit' AND r.fence>=OLD.fence","r.state='unknown' AND r.fence>=OLD.fence"),
 ('raw grant function exposure',APP,'RESET ROLE;','GRANT EXECUTE ON FUNCTION platform_private.bound_grant(boolean) TO wa_worker;\nRESET ROLE;'),
 ('forbidden worker usage',APP,'RESET ROLE;','GRANT SELECT (id) ON app.track_usage_events TO wa_worker;\nRESET ROLE;'),
 ('runtime privileged membership',BOOT,'COMMIT;','GRANT wa_private_helper_owner TO wa_worker;\nCOMMIT;'),
 ('helper writes',APP,'g:=platform_private.bound_grant(true);','UPDATE platform.database_action_grant SET revoked_at=now();\n g:=platform_private.bound_grant(true);'),
 ('helper foreign source read',APP,'RESET ROLE;','GRANT SELECT ON app.customer_profiles TO wa_private_helper_owner;\nRESET ROLE;'),
 ('PUBLIC helper execution',APP,'RESET ROLE;','GRANT EXECUTE ON FUNCTION platform_private.bind_request_context(text) TO PUBLIC;\nRESET ROLE;'),
 ('remove server mutation stamp',APP,'NEW.mutation_transaction_id:=pg_current_xact_id()::text;','NEW.mutation_transaction_id:=NEW.mutation_transaction_id;'),
 ('nullable capability membership',APP,"COALESCE(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields),false)","(model_name||'/'||row_key||'/'||verb||'/'||f = ANY(g.allowed_fields))"),
]
results=[]
with tempfile.TemporaryDirectory(prefix='wa-p0c03-offline-') as folder:
 target=Path(folder).resolve();assert target.parent==Path(tempfile.gettempdir()).resolve()
 paths=set(manifest['preserved_reviewed_inputs_sha256'])|set(manifest['outputs_sha256'])
 paths|={str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'context/reconciliation').glob('foundation-sql-draft-*.json')}
 for p in paths:
  dest=target/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/p,dest)
 for label,path,before,after in cases:
  original=(target/path).read_text(encoding='utf8');assert before in original,label
  (target/path).write_text(original.replace(before,after),encoding='utf8')
  # Fingerprints deliberately ignored: semantic assertions must detect mutation.
  try:r=CHECK(target,verify_fingerprints=False);rejected=bool(r['errors']);why=r['errors'][:2]
  except Exception as e:rejected=False;why=['unexpected checker failure '+str(e)]
  results.append({'case':label,'rejected_semantically':rejected,'evidence':why})
  (target/path).write_text(original,encoding='utf8')
 # Deliberately coherent SQL + evidence mutation. Original permission oracle must win.
 path='context/reconciliation/foundation-sql-draft-access.json';original=(target/path).read_text();app=(target/APP).read_text()
 acl=json.loads(original);acl.append({'model':'TrackUsageEvent','role':'wa_worker','operation':'SELECT','fields':['id'],'columns':['id']})
 (target/path).write_text(json.dumps(acl));(target/APP).write_text(app+'\nGRANT SELECT ("id") ON "app"."track_usage_events" TO wa_worker;\n')
 r=CHECK(target,verify_fingerprints=False)
 results.append({'case':'coherent forbidden usage SQL and ACL map','rejected_semantically':any('Track worker privilege broadening' in x or 'worker usage permission' in x for x in r['errors']),'evidence':r['errors'][:3]})
 (target/path).write_text(original);(target/APP).write_text(app)
result={'status':'PASS' if all(r['rejected_semantically'] for r in results) else 'FAIL','cases':len(results),'scope':'OFFLINE_SQL_SOURCE_MUTATIONS_FINGERPRINT_CHECK_DISABLED','database_contacted':False,'sql_executed':False,'results':results}
print(json.dumps(result,indent=2));raise SystemExit(result['status']!='PASS')
