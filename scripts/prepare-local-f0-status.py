"""Merge exact selected assertions with separately retained execution evidence.

The inventory remains a reproducible plan. This derived board never substitutes
dependency denials for missing positives or silently promotes compound cases.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/'context/reconciliation'

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
                path=ROOT/row['evidence_path']
                assert hashlib.sha256(path.read_bytes()).hexdigest()==row['evidence_sha256'],'Execution evidence changed'
                execution=json.loads(path.read_text(encoding='utf8'))
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
                if row['status']=='PASS':
                    assert execution.get('actual_result')=='PASS_FIRST01_THROUGH_FIRST10_SUBSET_ONLY','Unsupported successful evidence kind requires reviewed parser'
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
