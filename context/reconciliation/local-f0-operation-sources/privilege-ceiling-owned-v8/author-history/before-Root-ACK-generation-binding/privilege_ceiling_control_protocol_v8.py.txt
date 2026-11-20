"""Pure finite privilege protocol: source identifiers and fixed verdicts only.

No filesystem, process, network or database boundary exists in this module.
The caller supplies the exact prehashed Native-v3 source-position verifier.
"""
import hashlib
import json
import re

SCHEMA='workinants.privilege-ceiling-fixtures.v1'
APP_ROLES=('wa_app_runtime','wa_worker')
PROVIDERS=('anon','authenticated','service_role')
ROLE_TARGETS=('wa_context_issuer','wa_private_helper_owner','wa_customer_verifier','wa_track_verifier','wa_schema_owner','wa_migrator','wa_identity_service_authority')
SCHEMAS=('app','platform','platform_private','public')
GRANT_COLUMNS=('id','token_hash','issuer_service','principal_user_id','service_principal','database_login_role','owner_module_id','action','purpose','target_kind','target_id','allowed_fields','policy_version','security_generation','source_generation','backend_pid','transaction_id','expires_at','revoked_at','created_at','mutation_transaction_id')
HEADER=re.compile(r'(?:psql:<stdin>:[1-9][0-9]{0,8}: )?ERROR:\s+([0-9A-Z]{5}):\s+(.*)')
ACL_LOCATION=re.compile(r'LOCATION:\s+(aclcheck_error|aclcheck_error_col), aclchk\.c:[1-9][0-9]{0,5}')
ROLE_LOCATION=re.compile(r'LOCATION:\s+call_string_check_hook, guc\.c:[1-9][0-9]{0,5}')
RAISE_LOCATION=re.compile(r'LOCATION:\s+exec_stmt_raise, pl_exec\.c:[1-9][0-9]{0,5}')


class Refused(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def require(value,code):
    if not value:raise Refused(code)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return sha(canonical(value).encode())
def quote(value):return "'"+str(value).replace("'","''")+"'"
def ident(value):return '"'+value.replace('"','""')+'"'
def table(value):return '.'.join(ident(part)for part in value.split('.'))


def typed(value,spec):
    """Emit only the current source's scalar/array column types and typed data."""
    name=spec['name'];arrays=spec['array_dimensions']
    require(type(name)is str and re.fullmatch(r'(?:pg_catalog|app|platform)\.[a-z_][a-z_0-9]*',name)and type(arrays)is int and arrays in (0,1),'SOURCE_COLUMN_TYPE')
    kind=name+('[]'if arrays else '')
    if value is None:return 'NULL::'+kind
    if arrays:
        require(type(value)is list and len(value)<=1024,'FINITE_ARRAY')
        return 'ARRAY['+','.join(typed(item,{**spec,'array_dimensions':0})for item in value)+']::'+kind
    if type(value)is bool:raw='true'if value else'false'
    elif type(value)is int:raw=str(value)
    elif type(value)is str:
        require(len(value)<=4096 and all(c.isprintable()for c in value),'BOUNDED_SOURCE_SCALAR');raw=quote(value)
    else:raise Refused('SOURCE_SCALAR_TYPE')
    return raw+'::'+kind


def reviewed_text(text,run_id):
    require(type(run_id)is str and re.fullmatch('[0-9a-f]{8}-[0-9a-f-]{27}',run_id),'RUN_ID_SHAPE')
    require(type(text)is str and '<run8>'not in text,'UNREPLACED_RUN_TEMPLATE')
    return text.replace('__WA_RUN8__',run_id[:8])


def error_rows(stderr):
    if type(stderr)is not str or len(stderr)>16384:return None
    text=stderr.replace('\r\n','\n')
    if not all(c in ('\n','\t')or c.isprintable()for c in text):return None
    rows=[line for line in text.split('\n')if line]
    heads=[m for line in rows if(m:=HEADER.fullmatch(line))]
    severity=re.compile(r'(?:^|\s)(?:(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL|PANIC|WARNING):)')
    if len(heads)!=1 or sum(len(list(severity.finditer(line)))for line in rows)!=1:return None
    if not rows or not HEADER.fullmatch(rows[0]):return None
    return rows,heads[0]


def source_position_matches(position,caret,sql):
    """Pinned libpq17.11 60/10 projection, with finite DDL/GUC verbs included.

    The Native-v3 algorithm is unchanged; only the admitted statement starters
    include this packet's CREATE/SET/TRUNCATE in addition to its DML. No source
    position, caret or statement body is returned to evidence.
    """
    match=re.fullmatch(r'LINE ([1-9][0-9]{0,3}): (.*)',position)
    if not match or int(match[1])>len(sql.splitlines())+1 or not re.fullmatch(r' *\^',caret):return False
    prefix='LINE '+match[1]+': '
    for line in sql.splitlines():
        if not re.match(r'^(SELECT|INSERT|UPDATE|DELETE|CREATE|SET|TRUNCATE)\b',line)or not line.isascii()or'\t'in line:continue
        for cursor in range(len(line)+1):
            start,end=0,len(line)
            if end>60:
                if 60>=cursor+10:end=60
                else:end=min(end,cursor+10);start=max(0,end-60)
            left,right='...'if start else'','...'if end<len(line)else''
            if match[2]==left+line[start:end]+right and caret==' '*(len(prefix)+len(left)+cursor-start)+'^':return True
    return False


def _unchanged_diagnostic(stderr,contract,metadata,sql,position_verifier):
    """Exact native/guard source messages; a code alone never satisfies a case."""
    result={'matched':False,'sqlstate':None,'kind':None,'gate':None,'object':None,'source_position_verified':False,'source_frame_verified':False,'selected_column_or_verb_isolation_claimed':False}
    decoded=error_rows(stderr)
    if decoded is None:return result
    rows,header=decoded;kind=contract['kind']
    if kind=='IMMUTABLE_GRANT':
        frame=re.compile(r'CONTEXT:\s+PL/pgSQL function platform_private\.grant_guard\(\) line '+str(contract['body_line'])+r' at RAISE')
        good=header[1]=='P0001'and header[2]=='immutable grant'and len(rows)in(2,3)and frame.fullmatch(rows[1])and(len(rows)==2 or RAISE_LOCATION.fullmatch(rows[2]))
        return {**result,'matched':bool(good),'sqlstate':'P0001'if good else None,'kind':'IMMUTABLE_GRANT'if good else None,'object':'platform_private.grant_guard'if good else None,'source_frame_verified':bool(good)}
    if kind=='BIND_CURRENTNESS':
        frame=re.compile(r'CONTEXT:\s+PL/pgSQL function platform_private\.bind_request_context\(text\) line '+str(contract['body_line'])+r' at RAISE')
        good=header[1]=='42501'and header[2]=='invalid, stale or unsupported context'and len(rows)in(2,3)and frame.fullmatch(rows[1])and(len(rows)==2 or RAISE_LOCATION.fullmatch(rows[2]))
        return {**result,'matched':bool(good),'sqlstate':'42501'if good else None,'kind':'BIND_CURRENTNESS'if good else None,'object':'platform_private.bind_request_context'if good else None,'source_frame_verified':bool(good)}
    location=ROLE_LOCATION if kind=='SET_ROLE'else ACL_LOCATION
    if len(rows)==4:
        if not position_verifier(rows[1],rows[2],sql):return result
        result['source_position_verified']=True
    elif len(rows)!=2:return result
    match=location.fullmatch(rows[-1])
    if not match or header[1]!='42501':return result
    message=header[2];gate=None;object_=None
    if kind=='SET_ROLE':
        target=contract['target_role']
        require(target in ROLE_TARGETS,'FIXED_ROLE_TARGET')
        if message=='permission denied to set role "'+target+'"'and metadata.get('role_assumption_allowed')is False:gate,object_='ROLE',target
    elif kind=='SCHEMA_CREATE':
        schema=contract['schema']
        if message=='permission denied for schema '+schema and match[1]=='aclcheck_error'and metadata.get('schema_create')is False:gate,object_='SCHEMA_CREATE',schema
    else:
        schema=contract['schema'];name=contract.get('relation')
        if message=='permission denied for schema '+schema and match[1]=='aclcheck_error'and metadata.get('schema_usage')is False:gate,object_='SCHEMA',schema
        elif kind=='FUNCTION':
            function=contract['function']
            if message=='permission denied for function '+function and match[1]=='aclcheck_error'and metadata.get('schema_usage')is True and metadata.get('function_execute')is False:gate,object_='FUNCTION',schema+'.'+function
        elif message=='permission denied for table '+name and match[1]=='aclcheck_error'and metadata.get('schema_usage')is True and metadata.get('required_permission_missing')is True:gate,object_='TABLE',schema+'.'+name
        else:
            column=re.fullmatch(r'permission denied for column "([a-z_][a-z_0-9]*)" of relation "'+re.escape(name or'')+'"',message)
            if column and match[1]=='aclcheck_error_col'and metadata.get('schema_usage')is True and column[1]in metadata.get('missing_referenced_columns',[]):gate,object_='COLUMN',schema+'.'+name
    return {**result,'matched':gate is not None,'sqlstate':'42501'if gate is not None else None,'kind':kind if gate is not None else None,'gate':gate,'object':object_}


PUBLIC_SCHEMA_REGISTRATION_CONTENT_SHA256='59a40e9472a828ceda6683c51be763c524ea98a761353b74d28c87fbaca4dbeb'


def registered_public_schema_acl(native,registration):
    """Exact admitted source registration and typed native ACL multiset only."""
    code='REGISTERED_PUBLIC_SCHEMA_ACL_REQUIRED'
    fields={'format','owner','requires_prebootstrap_verification','baseline_acl','source_added_acl','full_acl'}
    require(type(native)is dict and type(registration)is dict and set(registration)==fields,code)
    require(registration['format']=='workinants.public-schema-registration.v1'and type(registration['owner'])is str and registration['requires_prebootstrap_verification']is True,code)
    def rows(value):
        require(type(value)is list and 0<len(value)<=16,code)
        for row in value:
            require(type(row)is dict and set(row)=={'grantee','grantor','privilege','grant_option'}and all(type(row[key])is str and 0<len(row[key])<=64 for key in('grantee','grantor','privilege'))and type(row['grant_option'])is bool,code)
        return sorted(canonical(row)for row in value)
    for name in('baseline_acl','source_added_acl','full_acl'):rows(registration[name])
    require(digest(registration)==PUBLIC_SCHEMA_REGISTRATION_CONTENT_SHA256,code)
    require(type(native.get('public_schema_owner'))is str and native['public_schema_owner']==registration['owner'],code)
    actual=native.get('public_schema_acl');require(rows(actual)==rows(registration['full_acl']),code)
    return actual


def expected_acl(native,role,kind,object_,verb,column=None,*,public_registration=None):
    require(role in (*APP_ROLES,*PROVIDERS,'wa_context_issuer','wa_identity_service_authority'),'FIXED_ACL_ROLE')
    if kind=='SCHEMA'and object_=='public':
        require(column is None and verb in('USAGE','CREATE'),'REGISTERED_PUBLIC_SCHEMA_ACL_REQUIRED')
        rows=registered_public_schema_acl(native,public_registration)
        return any(row['grantee']in(role,'PUBLIC')and row['privilege']==verb for row in rows)
    rows=native['nonowner_acl']
    return any(row['kind']==kind and row['object']==object_ and row['grantee']in(role,'PUBLIC')and row['privilege']==verb and row.get('column')in((None,)if column is None else(None,column))for row in rows)


def source_metadata_contract(native,source16):
    """The full native comparator must already have established this snapshot."""
    require(type(source16)is list and len(source16)==16,'SIXTEEN_SOURCE_DEFINERS')
    functions={row['object']:row for row in native['functions']}
    outcomes=[]
    for spec in source16:
        actual=functions.get(spec['identity']);good=type(actual)is dict and actual.get('owner')==spec['owner']and actual.get('body_sha256')==spec['body_sha256']and actual.get('security_definer')is True and actual.get('settings')==['search_path=pg_catalog']
        outcomes.append({'function':spec['identity'],'owner_body_definer_path_match':bool(good)})
    return outcomes


def failure_class(error,allowed):
    try:code=getattr(error,'code',None)
    except BaseException:code=None
    return code if type(code)is str and code in allowed else'UNEXPECTED_PRIVILEGE_CONTROL_FAILURE'


# The generator continues importing the original faf980 protocol. These are
# separately admitted runtime-only projections of the eight unchanged leaves.
CREATE_TEMPLATE_SHA={
 'app':'7f501d14dbcc0400ed3d78a9842092ffc313d46c8fb85fad0a7f1f0beb7fb310',
 'platform':'c629879fb15b7fdaecfb41b8a3f28d43685fd50c5e069e38d3dbcf7f59fbb2d2',
 'platform_private':'e4bc54bfbf715687bfbf2632d32c386bbc70e9aaf5774a06a0cc71c24029847d',
 'public':'58db35534306fba3866397199cf5c8fa92c2b441ec3020a932d92552352d0c14'}


def create_projection_binding(case,template,rendered,run_id):
    """RAM-only fixed query; no generic SQL scan or evidence statement export."""
    require(type(case)is dict and type(template)is str and type(rendered)is str,'CREATE_SOURCE_BINDING')
    schema=case.get('schema');role=case.get('role')
    require(type(schema)is str and schema in CREATE_TEMPLATE_SHA and role in APP_ROLES,'CREATE_SOURCE_BINDING')
    require(case.get('name')=='CREATE-'+role+'-'+schema and case.get('operation')=='CREATE' and case.get('diagnostic')=={'kind':'SCHEMA_CREATE','schema':schema},'CREATE_SOURCE_BINDING')
    require(type(run_id)is str and re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',run_id),'CREATE_SOURCE_BINDING')
    fixed="BEGIN; SET LOCAL lock_timeout='1s'; SET LOCAL statement_timeout='5s'; CREATE TABLE "+schema+'.wa_priv___WA_RUN8___probe(id integer); ROLLBACK;'
    require(template==fixed and sha(template.encode())==case.get('sql_sha256')==CREATE_TEMPLATE_SHA[schema],'CREATE_SOURCE_BINDING')
    require(rendered==reviewed_text(template,run_id),'CREATE_SOURCE_BINDING')
    query='CREATE TABLE '+schema+'.wa_priv_'+run_id[:8]+'_probe(id integer);'
    return {'case':case['name'],'role':role,'schema':schema,'run_id':run_id,'query':query,'template_sha256':sha(template.encode()),'rendered_sha256':sha(rendered.encode()),'query_sha256':sha(query.encode())}


def create_binding_valid(binding,contract,sql):
    if type(binding)is not dict or set(binding)!={'case','role','schema','run_id','query','template_sha256','rendered_sha256','query_sha256'}:return False
    if any(type(v)is not str for v in binding.values()):return False
    try:
        schema=binding['schema'];role=binding['role']
        case={'name':binding['case'],'role':role,'schema':schema,'operation':'CREATE','diagnostic':contract,'sql_sha256':binding['template_sha256']}
        template="BEGIN; SET LOCAL lock_timeout='1s'; SET LOCAL statement_timeout='5s'; CREATE TABLE "+schema+'.wa_priv___WA_RUN8___probe(id integer); ROLLBACK;'
        return create_projection_binding(case,template,sql,binding['run_id'])==binding
    except (Refused,TypeError,KeyError,UnicodeError):return False


def create_position_matches(position,caret,binding):
    """Exact REL_17_11 psql query and RangeVar cursor, ASCII libpq60/10."""
    query=binding['query'];cursor=len('CREATE TABLE ');first=0;last=len(query)
    if last>60:
        if 60>=cursor+10:last=60
        else:last=min(last,cursor+10);first=max(0,last-60)
    left='...'if first else'';right='...'if last<len(query)else''
    return type(position)is str and type(caret)is str and position=='LINE 1: '+left+query[first:last]+right and caret==' '*(len('LINE 1: ')+len(left)+cursor-first)+'^'


def unavailable_match_receipt():
    return {'schema':'workinants.privilege-diagnostic-match-receipt.v1','single_header_valid':False,'sqlstate':None,'expected_message_matches':False,'native_location_matches':False,'position_presence':'MALFORMED','position_source':'UNAVAILABLE','source_statement_identity_matches':False,'position_projection_matches':None,'metadata_requirement_matches':False,'strict_match':False,'template_sha256':None,'rendered_source_sha256':None,'query_sha256':None}


def diagnostic_with_receipt(stderr,contract,metadata,sql,position_verifier,*,create_binding=None,source_identity=None):
    receipt=unavailable_match_receipt()
    # Source identity is a caller-supplied *verified* template/rendered hash
    # pair, independently compared with the actual same-RAM SQL here.
    source_ok=(type(source_identity)is dict and set(source_identity)=={'template_sha256','rendered_source_sha256'} and all(type(v)is str and re.fullmatch('[0-9a-f]{64}',v)for v in source_identity.values()) and type(sql)is str)
    if source_ok:
        try:source_ok=source_identity['rendered_source_sha256']==sha(sql.encode())
        except UnicodeError:source_ok=False
    kind=contract.get('kind')if type(contract)is dict else None
    create_ok=kind=='SCHEMA_CREATE' and create_binding_valid(create_binding,contract,sql)
    if kind=='SCHEMA_CREATE':source_ok=bool(source_ok and create_ok and source_identity['template_sha256']==create_binding['template_sha256'])
    verifier=(lambda position,caret,unused:create_position_matches(position,caret,create_binding))if create_ok else position_verifier
    # The old strict non-CREATE verdict is unchanged. A CREATE must also carry
    # the exact case/template/run binding even when its error has no position.
    result=_unchanged_diagnostic(stderr,contract,metadata,sql,verifier)
    if kind=='SCHEMA_CREATE' and not source_ok:
        result={key:(False if type(value)is bool else None)for key,value in result.items()}
    decoded=error_rows(stderr)
    if decoded is None:return result,receipt
    # A second malformed or embedded severity candidate cannot be retained as
    # a single observed header. This observation gate never relaxes verdicts.
    if len(list(re.finditer(r'\b(?:ERROR|FATAL|PANIC|WARNING)(?=:|\s|$)',stderr)))!=1:return result,receipt
    rows,header=decoded;receipt['single_header_valid']=True
    receipt['sqlstate']=header[1]if header[1]in('42501','P0001')else None
    guard_without_position=kind in('IMMUTABLE_GRANT','BIND_CURRENTNESS') and len(rows)in(2,3) and result['source_frame_verified']is True
    receipt['position_presence']='ABSENT'if len(rows)==2 or guard_without_position else'PRESENT'if len(rows)==4 and rows[1].startswith('LINE ')else'MALFORMED'
    receipt['position_source']='VERIFIED_CREATE_QUERY'if create_ok else'EXISTING_SOURCE'if source_ok else'UNAVAILABLE'
    receipt['source_statement_identity_matches']=bool(source_ok)
    if source_ok:receipt.update(source_identity)
    if create_ok:receipt['query_sha256']=create_binding['query_sha256']
    if receipt['position_presence']=='PRESENT':
        receipt['position_projection_matches']=bool(verifier(rows[1],rows[2],sql))if source_ok else False
    if kind=='SCHEMA_CREATE':
        receipt['expected_message_matches']=header[2]=='permission denied for schema '+contract['schema']
        receipt['native_location_matches']=bool(ACL_LOCATION.fullmatch(rows[-1])and rows[-1].split(',')[0].split()[-1]=='aclcheck_error')
        receipt['metadata_requirement_matches']=metadata.get('schema_create')is False
    else:
        # Preserve exact existing native/function/role/source-RAISE criteria;
        # these flags are conservative when a diagnostic did not match.
        receipt['expected_message_matches']=result['matched']is True
        receipt['native_location_matches']=result['matched']is True
        receipt['metadata_requirement_matches']=result['matched']is True
    receipt['strict_match']=result['matched']is True
    return result,receipt


def diagnostic(stderr,contract,metadata,sql,position_verifier,*,create_binding=None,source_identity=None):
    return diagnostic_with_receipt(stderr,contract,metadata,sql,position_verifier,create_binding=create_binding,source_identity=source_identity)[0]
