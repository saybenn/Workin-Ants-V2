"""Merge exact selected assertions with separately retained execution evidence.

The inventory remains a reproducible plan. This derived board never substitutes
dependency denials for missing positives or silently promotes compound cases.
"""
import hashlib,json
from pathlib import Path
from local_f0_migration_evidence import validate_claim, EvidenceFailure
from local_f0_catalog_evidence import validate_claim as validate_catalog_claim, EvidenceFailure as CatalogEvidenceFailure
from local_f0_restricted_evidence import validate_claim as validate_restricted_claim, EvidenceFailure as RestrictedEvidenceFailure
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/'context/reconciliation'
SMALL_PASSES={(f'P0C-TABLE-{model}-ALLOW','positive.wa_app_runtime.insert') for model in ('CustomerProfile','CustomerProfileLifecycleEvent','RuntimeCommandReceipt','OwnerMutationEvidence','RuntimeOutboxMessage')}|{
    ('P0C-TABLE-CustomerProfile-DENY','denial.context.foreign_runtime_context'),
    ('P0C-BOOT-01','control.nonrecursive_create'),
    ('P0C-BOOT-01','vector.FIRST-SMALL-REHEARSAL.positive'),
    ('P0C-BOOT-01','vector.FIRST-SMALL-REHEARSAL.adversarial'),
    ('P0C-ATOMIC-01','control.complete_group'),
    ('P0C-ATOMIC-01','vector.MESSAGE-REVERSE.positive'),
    ('P0C-ATOMIC-01','vector.RESULT-VERSION.positive'),
    ('P0C-INSTALL-01','control.success_cleanup'),
    ('P0C-INSTALL-02','control.failed_cleanup'),
    ('P0C-INSTALL-02','vector.FUNCTION-ACL-FAILURE-CLEANUP.positive'),
}
EVIDENCE_RECORDS={
    'context/reconciliation/local-f0-small-rehearsal-0623028-execution.json':('269812ab154775e0cea58c3305ffbef141c2c0978590f8000c18c79cb2f0d28b','PASS_FIRST01_THROUGH_FIRST10_SUBSET_ONLY'),
    'context/reconciliation/local-f0-migration-6b8910d-execution.json':('e657bd4de3c288acbd86faa7ae9514f59e76566e1bba170a6ef19f7770c91158','PASS_GENUINE_FIRST_NOOP_FAILURE_REVIEWED_RESOLVE_SAME_CHECKSUM_RETRY'),
    'context/reconciliation/local-f0-catalog-b9703d7-23bd8979-execution.json':('bbf604e3eb2c7a066f2287a2f2f2ab825582d366dc5330394170b33a0fd22de8','PASS_LOCAL_NATIVE_CATALOG_SUBSET_ONLY'),
    'context/reconciliation/local-f0-restricted-b8f6b10-f161d454-execution.json':('9a090022c11f150cb133617af11cb9c6afafba1624313673ee3a5237ae637232','PASS_LOCAL_RESTRICTED_CONTROL_PACKETS_ONLY'),
}

def build():
    inventory=json.loads((REC/'local-f0-assertions.json').read_text(encoding='utf8'))
    ledger=json.loads((REC/'local-f0-assertion-evidence.json').read_text(encoding='utf8'))
    for source,expected in inventory['source_provenance']['files_sha256'].items():
        assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==expected,'Inventory source changed; regenerate and review evidence applicability'
    evidence={(row['case_id'],row['assertion_id']):row for row in ledger['assertions']}
    assert len(evidence)==len(ledger['assertions']),'Duplicate assertion evidence'
    identities={(case['id'],assertion['id']) for case in inventory['cases'] for assertion in case['assertions']}
    assert set(evidence)<=identities,'Unselected/unknown assertion evidence'
    cases=[];totals={s:0 for s in ('PASS','PARTIAL','FAILED','DEPENDENCY_BLOCKED','NOT_RUN','UNRESOLVED_SOURCE')}
    for case in inventory['cases']:
        assertions=[]
        for item in case['assertions']:
            row=evidence.get((case['id'],item['id']))
            status='DEPENDENCY_BLOCKED' if item['availability']=='DEPENDENCY_BLOCKED' else 'UNRESOLVED_SOURCE' if item['availability'] in ('SPECIFICATION_CONFLICT','SOURCE_PATH_REVIEW_REQUIRED') else 'NOT_RUN'
            if row:
                assert row['status'] in ('PASS','PARTIAL','FAILED')
                assert row['expected_assertion_sha256']==hashlib.sha256(item['expected_assertion'].encode()).hexdigest(),'Assertion requirement changed; review evidence mapping'
                assert row['evidence_path'] in EVIDENCE_RECORDS,'Unsupported execution evidence path requires reviewed parser'
                path=ROOT/row['evidence_path']
                expected_sha,expected_kind=EVIDENCE_RECORDS[row['evidence_path']]
                raw=path.read_bytes()
                assert hashlib.sha256(raw).hexdigest()==row['evidence_sha256']==expected_sha,'Execution evidence changed from independently reviewed record'
                execution=json.loads(raw)
                assert execution.get('actual_result')==expected_kind,'Execution evidence kind changed'
                for identity in ('run_id','source_commit','source_tree','packet_sha256'):
                    assert row[identity]==execution[identity],'Execution identity mismatch'
                pointer=row['json_pointer']
                assert type(pointer) is str and pointer.startswith('/'),'Evidence pointer invalid'
                value=execution
                for part in pointer[1:].split('/'):
                    part=part.replace('~1','/').replace('~0','~')
                    if isinstance(value,list):
                        assert part.isdigit() and str(int(part))==part and int(part)<len(value),'Evidence array pointer invalid'
                        value=value[int(part)]
                    else:
                        assert isinstance(value,dict) and part in value,'Evidence pointer missing'
                        value=value[part]
                assert type(value) is dict,'Evidence pointer must resolve to structured observation'
                if execution.get('actual_result')=='PASS_FIRST01_THROUGH_FIRST10_SUBSET_ONLY':
                    assert row['status']=='PASS' and (case['id'],item['id']) in SMALL_PASSES,'Unsupported small-rehearsal assertion promotion'
                elif execution.get('actual_result')=='PASS_LOCAL_NATIVE_CATALOG_SUBSET_ONLY':
                    expected_pointer='/sanitized_report/ledger_comparison' if (case['id'],item['id'])==('P0C-INSTALL-01','control.private_ledger') else '/sanitized_report/catalog_comparison'
                    assert pointer==expected_pointer,'Catalog evidence pointer does not identify the reviewed proof'
                    try:validate_catalog_claim(case['id'],item['id'],row['status'],execution,ROOT)
                    except CatalogEvidenceFailure as error:raise AssertionError(str(error)) from None
                elif execution.get('actual_result')=='PASS_LOCAL_RESTRICTED_CONTROL_PACKETS_ONLY':
                    try:validate_restricted_claim(case['id'],item['id'],row['status'],execution,ROOT,json_pointer=pointer)
                    except RestrictedEvidenceFailure as error:raise AssertionError(str(error)) from None
                else:
                    try:validate_claim(case['id'],item['id'],row['status'],execution,ROOT)
                    except EvidenceFailure as error:raise AssertionError(str(error)) from None
                assert row['application_sql_sha256']==inventory['source_provenance']['files_sha256']['review-output/foundation-application.review.sql'],'SQL changed; retain old evidence but review qualification before reuse'
                assert not (status in ('DEPENDENCY_BLOCKED','UNRESOLVED_SOURCE') and row['status']=='PASS'),'Unavailable positive cannot be passed by denial'
                status=row['status']
            totals[status]+=1
            assertions.append({'id':item['id'],'mandatory':item['mandatory_for_case'],'status':status,'dependency_ids':item['dependency_ids'],**({'evidence':row} if row else {})})
        statuses=[a['status'] for a in assertions if a['mandatory']]
        state='PASS' if statuses and all(s=='PASS' for s in statuses) else 'FAILED' if 'FAILED' in statuses else 'PARTIAL' if any(s in ('PASS','PARTIAL') for s in statuses) else 'DEPENDENCY_BLOCKED' if all(s=='DEPENDENCY_BLOCKED' for s in statuses) else 'NOT_RUN'
        assert state!='PASS' or all(a['status']=='PASS' for a in assertions if a['mandatory'])
        cases.append({'id':case['id'],'status':state,'assertions':assertions})
    assert len(cases)==94 and sum(totals.values())==inventory['summary']['mandatory_assertions']
    return {'scope':'ACTUAL_ASSERTION_EVIDENCE_OVER_EXACT_EXISTING94_IDS','database_posture':'D','Brain_acceptance':'PENDING','counts_are_obligations_not_experiments':True,'assertion_status_counts':totals,'case_status_counts':{s:sum(c['status']==s for c in cases) for s in ('PASS','PARTIAL','FAILED','DEPENDENCY_BLOCKED','NOT_RUN')},'selected_cases':94,'executions':ledger['executions'],'cases':cases}

if __name__=='__main__':
    result=build();(REC/'local-f0-qualification-status.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}))
