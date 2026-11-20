"""Build diagnostic identifiers from parsed DDL declarations, never free text."""
import hashlib
import json
from pathlib import Path
from pglast import ast, parse_sql

ROOT=Path(__file__).resolve().parents[1]
SOURCE='review-output/foundation-application.review.sql'
text=(ROOT/SOURCE).read_text(encoding='utf8')
columns=set();functions={}
for raw in parse_sql(text):
    node=raw.stmt
    if isinstance(node,ast.CreateStmt):
        columns.update(item.colname for item in node.tableElts or () if isinstance(item,ast.ColumnDef))
    elif isinstance(node,ast.CreateFunctionStmt):
        names=[part.sval for part in node.funcname]
        options={option.defname:option.arg for option in node.options}
        # Only no-argument PL/pgSQL frames can be emitted by this minimal parser.
        # Argument signatures/values are deliberately never accepted or exported.
        if len(names)!=2 or node.parameters or options.get('language').sval!='plpgsql':continue
        body=options['as'][0].sval
        functions['.'.join(names)]={'schema':names[0],'function':names[1],
            'body_sha256':hashlib.sha256(body.encode('utf8')).hexdigest(),
            'max_body_line':len(body.splitlines())}
output={'scope':'DECLARED_DDL_IDENTIFIERS_ONLY_NO_RUNTIME_VALUES',
    'source':SOURCE,'source_sha256':hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest(),
    'columns':sorted(columns),'no_argument_plpgsql_functions':dict(sorted(functions.items()))}
target=ROOT/'review-output/first-rehearsal/diagnostic-identifiers.json'
target.write_text(json.dumps(output,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'columns':len(columns),'functions':len(functions),'output':str(target.relative_to(ROOT))}))
