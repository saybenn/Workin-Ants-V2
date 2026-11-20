"""Bounded source diagnostics. Raw PostgreSQL bytes are never returned or saved.

Unknown messages/identifiers/frames become fixed classes. Only declared DDL
identifiers and source-bound no-argument PL/pgSQL frames may cross this boundary.
This metadata never changes the coordinator's SQLSTATE+exact-message verdict.
"""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
HEADER=re.compile(r'(?:psql:<stdin>:[0-9]+: )?(?:ERROR|FATAL):\s+([0-9A-Z]{5}):\s+(.*)')
MISSING=re.compile(r'record "(new|old)" has no field "([a-z_][a-z0-9_]*)"')
FRAME=re.compile(r'(?:CONTEXT:\s+|\s*)PL/pgSQL function ([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\(\) line ([1-9][0-9]{0,3}) at (IF|assignment|RETURN|SQL statement|PERFORM|RAISE)')

def source_metadata(stderr):
    """Emit only fixed keys/classes, allowlisted names and source-bounded lines."""
    result={'classification':'UNRECOGNIZED','frame_classification':'NOT_RETAINED'}
    # Fail closed if the declarations no longer describe the executable SQL.
    declared=json.loads((ROOT/'review-output/first-rehearsal/diagnostic-identifiers.json').read_text(encoding='utf8'))
    source_hash=hashlib.sha256((ROOT/declared['source']).read_bytes()).hexdigest()
    if source_hash!=declared['source_sha256']:
        result['classification']='SOURCE_MAP_MISMATCH';return result
    headers=[match for line in stderr.splitlines() if (match:=HEADER.fullmatch(line))]
    if len(headers)!=1:
        result['classification']='NO_SINGLE_ERROR';return result
    header=headers[0]
    missing=MISSING.fullmatch(header[2])
    if header[1]=='42703' and missing:
        result['classification']='RECORD_FIELD_MISSING_REDACTED'
        if missing[2] in declared['columns']:
            result.update(classification='RECORD_FIELD_MISSING',record_alias=missing[1],column=missing[2],source_sha256=source_hash)
    frames=[];saw_context=False;unrecognized=False
    for line in stderr.splitlines():
        if line.startswith('CONTEXT:'):saw_context=True
        # PostgreSQL may precede a function frame with a SQL-expression context
        # line. Discard that line without interpreting/exporting any of its SQL.
        # Only function-frame candidates participate in frame validity.
        if 'PL/pgSQL function ' in line:
            saw_context=True
            frame=FRAME.fullmatch(line)
            if frame:
                name=frame[1]+'.'+frame[2]
                function=declared['no_argument_plpgsql_functions'].get(name)
                if function and int(frame[3])<=function['max_body_line']:
                    frames.append({'schema':function['schema'],'function':function['function'],
                        'body_line':int(frame[3]),'body_sha256':function['body_sha256'],
                        'source_sha256':source_hash})
                else:unrecognized=True
            else:unrecognized=True
    # Do not export partial context if any candidate frame is malformed or if
    # multiple frames are supplied. This first experiment needs one frame only.
    if len(frames)==1 and not unrecognized:
        result.update(frame_classification='SOURCE_BOUND_FRAME',frame=frames[0])
    elif saw_context:result['frame_classification']='REDACTED_CONTEXT'
    return result
