"""Pure selected-F0 read verdicts. No files, process, clock or network access."""
import hashlib
import json
import re

APPLICATION_SHA='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
SCOPE_SPECS=(
 ('professional-query','ProfessionalProfile','SH-003.v1','owner:queryOwnerFacts'),
 ('professional-result','ProfessionalProfile','SH-015.v1','owner:returnDecisionResult'),
 ('professional-pure','ProfessionalProfile','SH-016.v1','owner:evaluateProfessionalReadiness'),
 ('professional-projection','ProfessionalProfile','SH-094.v1','owner:buildSourceProjection'),
 ('professional-history','ProfessionalProfile','SH-031.v1','owner:appendDomainLifecycleEvent'),
 ('candidate-query','CandidateProfile','SH-003.v1','owner:queryOwnerFacts'),
 ('candidate-aggregate','CandidateProfile','SH-115.v1','owner:buildAggregateProjection'),
 ('candidate-access','CandidateProfile','SH-125.v1','owner:recordDomainAccessEvent'),
 ('user-actor','User','SH-001.v1','owner:resolveAuthenticatedActor'),
 ('security-actor','UserSecurityProfile','SH-001.v1','owner:resolveAuthenticatedActor'),
 ('plan-app','TrackPlan','SH-005.v1','owner:resolveEntitlement'),
 ('definition-app','TrackEntitlementDefinition','SH-005.v1','owner:resolveEntitlement'),
 ('benefit-app','TrackPlanEntitlement','SH-005.v1','owner:resolveEntitlement'),
 ('consent-content','ConsentContentRevision','SH-009.v1','owner:resolveActiveConsentVersion'),
 ('consent-presentation','ConsentPresentation','SH-010.v1','owner:presentStandaloneConsent'),
 ('consent-proof','ConsentLog','SH-008.v1','owner:queryConsentProof'),
 ('privacy-query','PrivacyRequest','SH-003.v1','owner:queryOwnerFacts'))
REVISION_MODELS={'ProfessionalProfile','CandidateProfile','User','UserSecurityProfile','TrackPlan','TrackEntitlementDefinition','TrackPlanEntitlement','PrivacyRequest'}
DIAGNOSTICS={
 'privacy-completion-gate':('0A000','request completion requires qualified full owner accounting','privacy_guard'),
 'content-query-insert':('42501','new row violates row-level security policy for table "consent_content_revision"',None),
 'presentation-query-insert':('42501','new row violates row-level security policy for table "consent_presentation"',None)}

class HeldFailure(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)

def need(value,code):
    if not value:raise HeldFailure(code)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(value):return sha(canonical(value).encode())
def quote(value):return "'"+str(value).replace("'","''")+"'"

def unique_json(raw):
    def pairs(items):
        value={}
        for key,item in items:need(key not in value,'DUPLICATE_RESPONSE_FIELD');value[key]=item
        return value
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(HeldFailure('NONFINITE_RESPONSE')))
    except HeldFailure:raise
    except BaseException:raise HeldFailure('MALFORMED_RESPONSE') from None

def exact(actual,expected,code):need(canonical(actual)==canonical(expected),code)

def marker(name,position):
    need(type(name) is str and re.fullmatch('[a-z][a-z0-9-]{0,79}',name) and position in ('BEFORE','AFTER'),'FIXED_CASE_MARKER')
    return 'WA_OR_'+position+'_'+name.upper().replace('-','_')

def operation_sql(name,body):
    return 'SELECT '+quote(marker(name,'BEFORE'))+';\n'+body.rstrip()+'\nSELECT '+quote(marker(name,'AFTER'))+';\nCOMMIT;\n'

def diagnostic(name,stderr,application):
    need(name in DIAGNOSTICS and sha(application.encode())==APPLICATION_SHA,'DIAGNOSTIC_SOURCE_REQUIRED')
    state,message,function=DIAGNOSTICS[name]
    normalized=stderr.replace('\r\n','\n')
    clean=all(c in ('\n','\t') or c.isprintable() for c in normalized)
    header=re.compile(r'(?:psql:(?:<stdin>|-):[0-9]+: )?ERROR:[ \t]+([0-9A-Z]{5}):[ \t]+(.*)')
    lines=normalized.rstrip('\n').split('\n')
    # Verbose psql appends fixed native metadata. Do not retain it or permit
    # arbitrary trailing text, statement bodies, names or terminal controls.
    locations={'privacy-completion-gate':r'LOCATION:[ \t]+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}',
               'content-query-insert':r'LOCATION:[ \t]+ExecWithCheckOptions, execMain\.c:[1-9][0-9]{0,5}',
               'presentation-query-insert':r'LOCATION:[ \t]+ExecWithCheckOptions, execMain\.c:[1-9][0-9]{0,5}'}
    if lines and re.fullmatch(locations[name],lines[-1]):lines.pop()
    matched=False;body_sha=None;body_line=None
    if function:
        bodies=list(re.finditer(r'CREATE FUNCTION platform_private\.'+function+r'\(\).*?AS (\$[a-z_0-9]*\$)(.*?)\1;',application,re.S))
        need(len(bodies)==1,'DIAGNOSTIC_SOURCE_BODY')
        body=bodies[0][2];locations=[i for i,line in enumerate(body.split('\n'),1) if 'RAISE EXCEPTION '+quote(message) in line]
        need(len(locations)==1,'DIAGNOSTIC_SOURCE_LINE')
        frame='CONTEXT:  PL/pgSQL function platform_private.'+function+'() line '+str(locations[0])+' at RAISE'
        frame_pattern=r'CONTEXT:[ \t]+PL/pgSQL function platform_private\.'+function+r'\(\) line '+str(locations[0])+r' at RAISE'
        matched=clean and len(lines)==2 and header.fullmatch(lines[0]) is not None and re.fullmatch(frame_pattern,lines[1]) is not None
        if matched:body_sha=sha(body.encode());body_line=locations[0]
    else:matched=clean and len(lines)==1 and header.fullmatch(lines[0]) is not None
    found=header.fullmatch(lines[0]) if lines else None
    matched=bool(matched and found and found.groups()==(state,message))
    return {'matched':matched,'sqlstate':state if matched else None,'classification':name if matched else 'UNLISTED_OR_INCOMPLETE_DISCARDED','source_frame_verified':bool(matched and function),'body_sha256':body_sha if matched else None,'body_line':body_line if matched else None}

def verdict(case,code,lines,ack,stderr,application):
    need(type(code) is int and type(ack) is bool and type(lines) is list and all(type(x) is str for x in lines),'TYPED_OPERATION_RESULT')
    before,after=marker(case['name'],'BEFORE'),marker(case['name'],'AFTER')
    if case['kind']=='diagnostic':
        proof=diagnostic(case['name'],stderr,application)
        need(code==3 and ack is False and lines==[before] and proof['matched'],'EXACT_INTENDED_GUARD_REQUIRED')
        return {'status':'PASS_PREPARED_SQL_SUBSET_ONLY','expected_guard':proof,'stage_markers':{'before':True,'after':False},'complete_result_match':True}
    need(code==0 and ack is True and stderr=='' and len(lines)==3 and lines[0]==before and lines[2]==after,'READ_OPERATION_TERMINAL_MARKERS')
    actual=unique_json(lines[1]);exact(actual,case['expected'],'EXACT_READ_COUNTS_REQUIRED')
    return {'status':'PASS_PREPARED_SQL_SUBSET_ONLY','expected_guard':None,'stage_markers':{'before':True,'after':True},'complete_result_match':True,'counts':actual}
