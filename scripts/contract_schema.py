#!/usr/bin/env python3
"""Offline evaluator for the explicitly supported JSON Schema subset in contract fixtures.
Not the production runtime parser. Unsupported assertion keywords fail preflight.
"""
import base64
import datetime
import json
import math
import re
from pathlib import Path

ASSERTIONS={'$schema','$id','$defs','$ref','title','description','type','properties','required','additionalProperties','items','minItems','maxItems','uniqueItems','enum','const','oneOf','anyOf','minimum','maximum','minLength','maxLength','pattern','format','contentEncoding'}

class SchemaError(ValueError): pass

class Registry:
    def __init__(self, root):
        self.root=Path(root);self.documents={}
        for p in sorted((self.root/'contracts/shared').glob('*.schema.json')):
            doc=json.loads(p.read_text());uri=doc.get('$id')
            if not uri or uri in self.documents:raise SchemaError('Missing/duplicate schema identity '+str(p))
            self.documents[uri]=doc
        for uri,doc in self.documents.items():self.preflight(doc,doc)
    def resolve(self, ref, current):
        uri,_,fragment=ref.partition('#');doc=self.documents.get(uri) if uri else current
        if doc is None:raise SchemaError('Unregistered local schema URI '+uri)
        target=doc
        for part in fragment.strip('/').split('/') if fragment else []:
            try:target=target[part.replace('~1','/').replace('~0','~')]
            except (KeyError,TypeError):raise SchemaError('Unresolved schema reference '+ref)
        return target,doc
    def preflight(self,s,current):
        if not isinstance(s,dict):raise SchemaError('Schema must be an object')
        annotations={'$schema','$id','$defs','title','description'}
        for combinator in ['$ref','oneOf','anyOf']:
            if combinator in s and set(s)-annotations-{combinator}:raise SchemaError('Unsupported sibling assertions with '+combinator)
        unknown=set(s)-ASSERTIONS
        if unknown:raise SchemaError('Unsupported schema keywords '+str(sorted(unknown)))
        if '$ref'in s:self.resolve(s['$ref'],current)
        if s.get('type')=='object':
            if s.get('additionalProperties') is not False:raise SchemaError('Contract object is not closed')
            if set(s.get('required',[]))-set(s.get('properties',{})):raise SchemaError('Required field lacks type')
        if 'enum'in s and not s['enum']:raise SchemaError('Empty enum')
        for k in ['$defs','properties']:
            for child in s.get(k,{}).values():self.preflight(child,current)
        if 'items'in s:self.preflight(s['items'],current)
        for k in ['oneOf','anyOf']:
            if k in s:
                if not s[k]:raise SchemaError('Empty '+k)
                for child in s[k]:self.preflight(child,current)
    def errors(self,value,s,current=None,path='$'):
        current=current or s
        if '$ref'in s:
            target,doc=self.resolve(s['$ref'],current);return self.errors(value,target,doc,path)
        if 'const'in s and json.dumps(value,sort_keys=True)!=json.dumps(s['const'],sort_keys=True):return [path+': const mismatch']
        if 'enum'in s and not any(json.dumps(value,sort_keys=True)==json.dumps(x,sort_keys=True) for x in s['enum']):return [path+': enum mismatch']
        if 'oneOf'in s:
            matches=sum(not self.errors(value,x,current,path) for x in s['oneOf'])
            return [] if matches==1 else [path+': oneOf matched '+str(matches)]
        if 'anyOf'in s:return [] if any(not self.errors(value,x,current,path) for x in s['anyOf']) else [path+': anyOf failed']
        k=s.get('type');valid={'null':value is None,'boolean':type(value)is bool,'integer':type(value)is int,'number':type(value)in [int,float] and math.isfinite(value),'string':type(value)is str,'object':type(value)is dict,'array':type(value)is list}
        if k and not valid[k]:return [path+': expected '+k]
        errors=[]
        if k=='object':
            props=s.get('properties',{})
            for name in s.get('required',[]):
                if name not in value:errors.append(path+': missing '+name)
            if s.get('additionalProperties') is False:
                for name in set(value)-set(props):errors.append(path+': extra '+name)
            for name,item in value.items():
                if name in props:errors+=self.errors(item,props[name],current,path+'.'+name)
        if k=='array':
            if len(value)<s.get('minItems',0) or len(value)>s.get('maxItems',float('inf')):errors.append(path+': array bound')
            if s.get('uniqueItems') and len({json.dumps(v,sort_keys=True) for v in value})!=len(value):errors.append(path+': duplicate items')
            for i,item in enumerate(value):errors+=self.errors(item,s['items'],current,path+'['+str(i)+']')
        if k=='string':
            if len(value)<s.get('minLength',0) or len(value)>s.get('maxLength',float('inf')):errors.append(path+': string bound')
            if 'pattern'in s and not re.search(s['pattern'],value):errors.append(path+': pattern mismatch')
            if s.get('format')=='date-time':
                try:
                    if datetime.datetime.fromisoformat(value.replace('Z','+00:00')).tzinfo is None:raise ValueError('no zone')
                except ValueError:errors.append(path+': invalid timestamp')
            if s.get('contentEncoding')=='base64':
                try:base64.b64decode(value,validate=True)
                except ValueError:errors.append(path+': invalid base64')
        if k in ['number','integer']:
            if value<s.get('minimum',-float('inf')) or value>s.get('maximum',float('inf')):errors.append(path+': numeric bound')
        return errors
    def check(self,contract,part,value):
        doc=self.documents['urn:workin-ants:'+contract+':v1'];return self.errors(value,doc['$defs'][part],doc)
