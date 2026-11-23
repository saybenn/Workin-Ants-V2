"""Environment-free tests of the real new source APIs; all services forbidden."""
from pathlib import Path
from types import ModuleType
import contextlib,copy,hashlib,io,json,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
def module(relative):
    m=ModuleType('_source_only_'+Path(relative).stem.replace('-','_'));m.__file__=str(ROOT/relative)
    exec(compile((ROOT/relative).read_bytes(),m.__file__,'exec'),m.__dict__);return m
def sha(b):return hashlib.sha256(b).hexdigest()
class SourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prep=module('scripts/prepare-local-f0-runtime-lease-history-v1.py')
        cls.native=module('scripts/prepare-native-runtime-lease-history-v1-review.py')
        cls.pins={n:sha((ROOT/n).read_bytes())for n in cls.native.REQUIRED_FILES}
        cls.files,cls.summary=cls.native.prepare(ROOT,cls.pins)
        cls.expected=json.loads(cls.files['expected.json'])
        cls.original,cls.tools,cls.effective,cls.ledger,cls.blobs=cls.native.load_tools(ROOT,cls.pins)
        cls.loader=module('scripts/sql-review/run-local-f0-runtime-lease-history-v1.py')
        cls.closure=json.loads((ROOT/'context/reconciliation/local-f0-tooling/prisma-tools-closure.json').read_bytes())
        cls.run_id='2e4d7cc4-cef1-428e-8a1d-b9eeb7fc48c8'
        cls.manifest={'schema':'workinants.local-f0-runtime-lease-history-run.v1',
          'purpose':'LOCAL_F0_RUNTIME_LEASE_TWO_MIGRATION_REHEARSAL','run_id':cls.run_id,
          'target':{'container_name':'wa-p0c-2e4d7cc4-twohistory','volume_name':'wa-p0c-2e4d7cc4-twohistory-data','database':'wa_p0c_rehearsal',
            'image':cls.prep.IMAGE,'network':'none','labels':{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':cls.run_id},
            'bootstrap_secret_host_path':str(ROOT.parent/'test-owned-evidence/private/bootstrap-password')},
          'history':{'path':cls.prep.HISTORY,'ordered':cls.prep.ordered_rows()},
          'source':{'initial_sql_sha256':cls.prep.INITIAL,'append_sql_sha256':cls.prep.PATCH,
            'ordered_history_sha256':sha(cls.prep.canonical(cls.prep.ordered_rows()).encode()),
            'effective_expected_sha256':cls.summary['source_expected_sha256'],'foundation_schema_sha256':cls.prep.SCHEMA_SHA,
            'runtime_files_sha256':{n:sha((ROOT/n).read_bytes())for n in cls.prep.RUNTIME_FILES}},
          'tools':{k:cls.closure[k]for k in('node_version','prisma_version','engine_commit')}|{'files_sha256':cls.closure['tools_files_sha256']}}
        cls.raw=json.dumps(cls.manifest,sort_keys=True,separators=(',',':')).encode()
    def snapshot(self,base):
        files,h=self.prep.prepare_plan(self.manifest,self.raw,(ROOT/self.prep.INITIAL_PATH).read_bytes(),
          (ROOT/self.prep.PATCH_PATH).read_bytes(),(ROOT/self.prep.SCHEMA).read_bytes(),
          {n:(ROOT/n).read_bytes()for n in self.prep.RUNTIME_FILES})
        for n in(self.prep.SCHEMA,*self.prep.RUNTIME_FILES):files[n]=(ROOT/n).read_bytes()
        files[self.prep.MANIFEST]=(json.dumps(h,sort_keys=True,indent=2)+'\n').encode()
        for n,b in files.items():
            p=base/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        return files,h
    def test_complete_source_manifest(self):
        value=self.expected
        self.assertNotEqual(value['expected_sha256'],self.effective.OLD_EXPECTED)
        self.assertEqual(value['expected']['functions'][self.effective.IDENTITY]['body_sha256'],self.effective.NEW_BODY)
        self.assertEqual(value['ordered_source']['worker_acl_rows'],32)
        self.assertEqual(value['ordered_source']['external_trigger_count'],100)
        self.assertEqual(len(value['inputs_sha256']),9)
    def test_reproduction_of_all_six_assets(self):
        again,summary=self.native.prepare(ROOT,self.pins)
        self.assertEqual(again,self.files);self.assertEqual(summary,self.summary)
        self.assertEqual(set(again),set(self.native.ASSETS))
    def test_exact_eight_source_snapshot_and_old7_reject(self):
        with tempfile.TemporaryDirectory()as d:
            base=Path(d);files,h=self.snapshot(base)
            self.assertEqual(len(files),8);self.assertEqual(len(h['files_sha256']),7)
            self.assertEqual(self.loader.verify_source8(base,self.manifest,self.raw,self.prep),files)
            (base/self.prep.ordered_rows()[1]['path']).unlink()
            with self.assertRaisesRegex(Exception,'EXACT_SOURCE8_CLOSURE'):self.loader.verify_source8(base,self.manifest,self.raw,self.prep)
    def test_exact_source_tar_bytes_no_extraction(self):
        import tarfile
        with tempfile.TemporaryDirectory()as d:
            base=Path(d);files,_=self.snapshot(base);out=io.BytesIO()
            with tarfile.open(fileobj=out,mode='w',format=tarfile.USTAR_FORMAT)as archive:
                for name,raw in sorted(files.items()):
                    info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o444;info.uid=info.gid=0;info.mtime=0
                    archive.addfile(info,io.BytesIO(raw))
            with tarfile.open(fileobj=io.BytesIO(out.getvalue()),mode='r:')as archive:
                rows=archive.getmembers();self.assertEqual(len(rows),8)
                self.assertTrue(all(r.isfile()and not r.issym()and r.mode==0o444 for r in rows))
                self.assertEqual({r.name:archive.extractfile(r).read()for r in rows},files)
    def test_old_manifest_API_rejects_new_and_new_preparer_rejects_CRLF(self):
        old=module('scripts/prepare-local-f0-history.py')
        with self.assertRaises(Exception):old.validate_manifest(self.manifest)
        raw=(ROOT/self.prep.INITIAL_PATH).read_bytes()
        self.assertIn(b'\n',raw)
        with self.assertRaisesRegex(Exception,'UNCHANGED_INITIAL_AND_EXACT_APPEND'):
            self.prep.prepare_plan(self.manifest,self.raw,raw.replace(b'\n',b'\r\n'),(ROOT/self.prep.PATCH_PATH).read_bytes(),
              (ROOT/self.prep.SCHEMA).read_bytes(),{n:(ROOT/n).read_bytes()for n in self.prep.RUNTIME_FILES})
    def test_manifest_unknown_legacy_order_and_types_reject(self):
        mutations=[]
        for field in('schema','purpose'):
            m=copy.deepcopy(self.manifest);m[field]='workinants.local-f0-run.v1';mutations.append(m)
        m=copy.deepcopy(self.manifest);m['history']['ordered'].reverse();mutations.append(m)
        m=copy.deepcopy(self.manifest);m['history']['ordered']=m['history']['ordered'][:1];mutations.append(m)
        m=copy.deepcopy(self.manifest);m['history']['ordered'].append(m['history']['ordered'][0]);mutations.append(m)
        m=copy.deepcopy(self.manifest);m['unknown']=True;mutations.append(m)
        m=copy.deepcopy(self.manifest);m['source']['effective_expected_sha256']=self.effective.OLD_EXPECTED;mutations.append(m)
        m=copy.deepcopy(self.manifest);m['source']['runtime_files_sha256']['old-config.mjs']='0'*64;mutations.append(m)
        for m in mutations:
            with self.subTest(m=m['history']['ordered']):
                with self.assertRaises(Exception):self.prep.validate_manifest(m)
    def test_strict_json_duplicates_nonfinite_overflow(self):
        for raw in(b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e9999}'):
            with self.subTest(raw=raw):
                with self.assertRaises(Exception):self.prep.unique_json(raw)
                with self.assertRaises(Exception):self.loader.unique_json(raw)
    def test_exact_source_bytes_BOM_and_extra_reject(self):
        with self.assertRaisesRegex(Exception,'EXACT_ORDERED_MIGRATION_BYTES'):
            bad=dict(self.blobs);bad[self.effective.PATCH_PATH]=b'\xef\xbb\xbf'+bad[self.effective.PATCH_PATH]
            self.effective.build_manifest(self.tools['catalog_manifest'],{n:bad[n]for n in(*self.tools['catalog_manifest'].INPUTS,self.effective.PATCH_PATH)},{n:sha(b)for n,b in bad.items()})
        with tempfile.TemporaryDirectory()as d:
            base=Path(d);self.snapshot(base);(base/'extra.sql').write_text('SELECT 1;')
            with self.assertRaisesRegex(Exception,'EXACT_SOURCE8_CLOSURE'):self.loader.verify_source8(base,self.manifest,self.raw,self.prep)
    def test_old_template_and_preloaded_cache_refuse(self):
        sys.modules['catalog_manifest']=ModuleType('catalog_manifest')
        try:
            with self.assertRaisesRegex(Exception,'PRELOADED_HELPER_CACHE_REJECTED'):self.native.prepare(ROOT,self.pins)
        finally:sys.modules.pop('catalog_manifest')
        bad=copy.deepcopy(self.pins);bad[self.native.PATCH]='0'*64
        with self.assertRaises(Exception):self.native.prepare(ROOT,bad)
    def test_PENDING_before_any_process(self):
        calls=[]
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);p=root/self.loader.VALIDATION;p.parent.mkdir(parents=True)
            p.write_text('{"review_gate":"PENDING"}')
            pins={self.loader.VALIDATION:sha(p.read_bytes()),self.loader.PREPARER:'0'*64,self.loader.NATIVE:'0'*64}
            with self.assertRaisesRegex(Exception,'SOURCE_REVIEW_PENDING'):
                self.loader.coordinate(self.raw,'deploy',source8_root=root,source_pins=pins,root=root,process=lambda *a,**k:calls.append(a))
        self.assertEqual(calls,[])
    def test_recovery_operations_refuse_before_any_process(self):
        for operation in('resolve-rolled-back','resolve-applied','reset','db push','custom-sql'):
            with self.assertRaisesRegex(Exception,'OPERATION_DENIED'):
                self.loader.coordinate(self.raw,operation,source8_root=ROOT,source_pins={},process=lambda *a,**k:self.fail('process'))
    def test_two_real_source_ledger_registration(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);self.snapshot(root)
            reg=self.ledger.registration(self.tools['prisma_ledger_proof'],root=root,run_id=self.run_id,
              target_attestation_sha256='a'*64,source_expected_sha256=self.expected['expected_sha256'])
            self.assertEqual(len(reg['history_expected']),2)
            self.assertEqual([r['migration_name']for r in reg['migrations']],[r['id']for r in self.prep.ordered_rows()])
            (root/self.prep.ordered_rows()[1]['path']).write_bytes(b'SELECT 1;')
            with self.assertRaises(Exception):self.ledger.registration(self.tools['prisma_ledger_proof'],root=root,run_id=self.run_id,target_attestation_sha256='a'*64,source_expected_sha256=self.expected['expected_sha256'])
    def test_exact_two_tool_metadata_snapshot_and_10300_binding(self):
        for relative,(leaf,wanted)in self.native.TOOL_METADATA.items():
            self.assertEqual(sha((ROOT/relative).read_bytes()),wanted)
            self.assertEqual(self.closure['tools_files_sha256'][relative],wanted)
            self.assertEqual((ROOT/relative).read_bytes(),(ROOT/(self.native.TOOL_SNAPSHOT_ROOT+leaf)).read_bytes())
        self.assertFalse(any(n.startswith('node_modules/')for n in self.native.REQUIRED_FILES))
        self.assertEqual(len(self.loader.SOURCE8),8)
    def test_missing_or_changed_ignored_metadata_rejects_without_program_fallback(self):
        for relative in self.native.TOOL_METADATA:
            path=ROOT/relative;raw=path.read_bytes();held=path.with_name(path.name+'.test-held')
            try:
                path.rename(held)
                with self.assertRaises(Exception):self.native.verified_sources(ROOT,self.pins)
            finally:
                if held.exists():held.rename(path)
            try:
                path.write_bytes(raw+b' ')
                with self.assertRaisesRegex(Exception,'TWO_TOOL_METADATA_BYTES'):self.native.verified_sources(ROOT,self.pins)
            finally:path.write_bytes(raw)
    def test_changed_tracked_snapshot_rejects_even_with_updated_outer_hash(self):
        relative=next(iter(self.native.TOOL_METADATA.values()))[0];path=ROOT/(self.native.TOOL_SNAPSHOT_ROOT+relative);raw=path.read_bytes()
        try:
            path.write_bytes(raw+b' ');pins=dict(self.pins);pins[self.native.TOOL_SNAPSHOT_ROOT+relative]=sha(path.read_bytes())
            with self.assertRaisesRegex(Exception,'PINNED_TWO_TOOL_SNAPSHOTS'):self.native.verified_sources(ROOT,pins)
        finally:path.write_bytes(raw)
    def test_metadata_changed_after_generic_registration_rejects(self):
        relative=next(iter(self.native.TOOL_METADATA));path=ROOT/relative;raw=path.read_bytes();original=Path.read_bytes;seen=[0]
        def read(p,*args,**kwargs):
            value=original(p,*args,**kwargs)
            if p==path:
                seen[0]+=1
                if seen[0]==2:p.write_bytes(value+b' ')
            return value
        try:
            with tempfile.TemporaryDirectory()as d:
                root=Path(d);self.snapshot(root)
                with patch.object(Path,'read_bytes',read),self.assertRaisesRegex(Exception,'TOOL_METADATA_CHANGED_DURING_REGISTRATION'):
                    self.ledger.registration(self.tools['prisma_ledger_proof'],root=root,run_id=self.run_id,target_attestation_sha256='a'*64,source_expected_sha256=self.expected['expected_sha256'])
        finally:path.write_bytes(raw)
    def test_noop_full_row_and_typed_source_identity(self):
        rows=sorted([{'name_sha256':sha(n.encode()),'checksum_sha256':sha(h.encode()),'row_sha256':str(i+1)*64}for i,(n,h)in enumerate(self.ledger.ORDERED)],key=lambda r:(r['name_sha256'],r['checksum_sha256']))
        before={'schema':'workinants.runtime-lease-history-fingerprints.v1','server_version_num':170011,'database':'wa_p0c_rehearsal','collected_as':'postgres','collector_is_superuser':True,'read_only':True,'history_count':2,'rows':rows}
        self.assertEqual(self.ledger.compare_noop(before,copy.deepcopy(before))['history_count'],2)
        for bad in('row','name','count','extra'):
            after=copy.deepcopy(before)
            if bad=='row':after['rows'][0]['row_sha256']='f'*64
            elif bad=='name':after['rows'][0]['name_sha256']='f'*64
            elif bad=='count':after['history_count']=True
            else:after['rows'].append(after['rows'][0])
            with self.assertRaises(Exception):self.ledger.compare_noop(before,after)
    def test_readonly_fingerprint_SQL(self):
        from pglast.parser import parse_sql_json
        raw=(ROOT/'scripts/sql-review/collect_runtime_lease_history_fingerprints_v1.sql').read_bytes()
        statements=json.loads(parse_sql_json(raw.decode()))['stmts']
        self.assertEqual([next(iter(s['stmt']))for s in statements],['TransactionStmt','DoStmt','SelectStmt','TransactionStmt'])
        self.assertIn(b'READ ONLY',raw);self.assertTrue(raw.endswith(b'ROLLBACK;\n'))

    def coordinate_fixture(self, base):
        """Real source/API clone. Only SOURCE_APPROVED review records are mock-only.

        Actual production gates stay PENDING. This fixture never admits Git or
        claims that modeled process replies establish tool/container identity.
        """
        root=base/'program';root.mkdir()
        for name in self.native.REQUIRED_FILES:
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/name).read_bytes())
        prep=ModuleType('_unit_only_real_preparer');prep.__file__=str(root/self.loader.PREPARER)
        exec(compile((root/self.loader.PREPARER).read_bytes(),prep.__file__,'exec'),prep.__dict__)
        source={n:sha((root/n).read_bytes())for n in self.native.REQUIRED_FILES}
        pins=dict(source);records={}
        for key in('independent_source_review','Root_source_review'):
            name=self.loader.REVIEW_PREFIX+key+'-MOCK-ONLY.json'
            raw=json.dumps({'decision':'SOURCE_APPROVED','scope':'UNIT_FIXTURE_ONLY_NOT_REAL_REVIEW',
                            'source_files_sha256':source},sort_keys=True).encode()
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
            pins[name]=sha(raw);records[key]={'path':name,'sha256':sha(raw),'decision':'SOURCE_APPROVED'}
        validation={'review_gate':'SOURCE_APPROVED','scope':'UNIT_FIXTURE_ONLY_NOT_REAL_REVIEW',
            'source_files_sha256':source,'source_expected_sha256':self.summary['source_expected_sha256'],**records}
        path=root/self.loader.VALIDATION;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(json.dumps(validation,sort_keys=True).encode());pins[self.loader.VALIDATION]=sha(path.read_bytes())
        manifest=copy.deepcopy(self.manifest)
        manifest['target']['bootstrap_secret_host_path']=str(base/'private/bootstrap-password')
        raw=json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()
        files,history=prep.prepare_plan(manifest,raw,(root/prep.INITIAL_PATH).read_bytes(),
          (root/prep.PATCH_PATH).read_bytes(),(root/prep.SCHEMA).read_bytes(),
          {n:(root/n).read_bytes()for n in prep.RUNTIME_FILES})
        files.update({n:(root/n).read_bytes()for n in(prep.SCHEMA,*prep.RUNTIME_FILES)})
        files[prep.MANIFEST]=(json.dumps(history,sort_keys=True,indent=2)+'\n').encode()
        snapshot=base/'source8'
        for n,b in files.items():
            path=snapshot/n;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
        loader=ModuleType('_unit_only_real_coordinator');loader.__file__=str(root/'scripts/sql-review/run-local-f0-runtime-lease-history-v1.py')
        exec(compile(Path(loader.__file__).read_bytes(),loader.__file__,'exec'),loader.__dict__)
        return {'root':root,'loader':loader,'prep':prep,'manifest':manifest,'raw':raw,'pins':pins,'snapshot':snapshot,'files':files}

    def modeled_outer_process(self, fixture, *, fault=None):
        """Model all seven Docker process boundaries; never model inner APIs."""
        from types import SimpleNamespace
        loader=fixture['loader'];manifest=fixture['manifest'];target=manifest['target'];cid='a'*64;calls=[]
        image_id='sha256:'+manifest['target']['image'].split('@sha256:')[1]
        context={'Name':'desktop-linux','Endpoints':{'docker':{'Host':loader.ENDPOINT}}}
        container={'Id':cid,'Name':'/'+target['container_name'],'Image':image_id,'Platform':'linux','State':{'Running':True},
          'Config':{'Image':target['image'],'Labels':target['labels']},
          'HostConfig':{'NetworkMode':'none','Privileged':False,'IpcMode':'private',
                       'Tmpfs':{loader.PRIVATE_ROOT:'noexec,nosuid,nodev,mode=0700'}},
          'NetworkSettings':{'Ports':{}},'Mounts':[
            {'Type':'volume','Name':target['volume_name'],'Destination':'/var/lib/postgresql/data','RW':True},
            {'Type':'bind','Source':target['bootstrap_secret_host_path'],'Destination':'/run/bootstrap-password','RW':False},
            {'Type':'tmpfs','Destination':loader.PRIVATE_ROOT,'RW':True}]}
        volume={'Name':target['volume_name'],'Driver':'local','Options':{},'Scope':'local','Labels':target['labels']}
        approved=(fixture['root']/'scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json').read_bytes()
        image={'Id':image_id,'Os':'linux','Architecture':'amd64','RepoDigests':['postgres@'+image_id],
          'Descriptor':{'mediaType':'application/vnd.oci.image.manifest.v1+json','digest':image_id,'size':len(approved)},
          'Config':{'Env':['PG_VERSION=17.11-1.pgdg13+2']}}
        if fault=='image':image['Architecture']='arm64'
        def process(args,**kwargs):
            calls.append((args,kwargs));i=len(calls)
            self.assertEqual(args[:3],['docker','--context','desktop-linux'])
            self.assertIs(kwargs.get('shell'),False);self.assertIs(kwargs.get('capture_output'),True)
            self.assertNotIn('env',kwargs)
            if i<=4:
                expected=[['context','inspect','desktop-linux'],['inspect',target['container_name']],
                  ['volume','inspect',target['volume_name']],['image','inspect',target['image']]][i-1]
                self.assertEqual(args[3:],expected)
                out=json.dumps([[context,container,volume,image][i-1]])
            elif i==5:
                self.assertEqual(args[3:7],['exec',cid,'/usr/bin/sha256sum','--'])
                hashes={loader.SOURCE_ROOT+'/'+n:sha(b)for n,b in fixture['files'].items()}
                hashes[loader.TOOLS_ROOT+'/node/bin/node']=manifest['tools']['files_sha256']['node/bin/node']
                self.assertEqual(args[7:],sorted(hashes))
                if fault=='copied_hash':hashes[sorted(hashes)[0]]='0'*64
                out=''.join(h+'  '+n+'\n'for n,h in sorted(hashes.items()))
            elif i==6:
                self.assertEqual(args[3:8],['exec',cid,'/usr/bin/stat','--format=%s','--'])
                lengths={loader.SOURCE_ROOT+'/'+n:len(b)for n,b in fixture['files'].items()}
                self.assertEqual(args[8:],sorted(lengths));out=''.join(str(lengths[n])+'\n'for n in sorted(lengths))
            elif i==7:
                self.assertEqual(args[3:8],['exec','-i',cid,loader.TOOLS_ROOT+'/node/bin/node',
                    loader.SOURCE_ROOT+'/scripts/sql-review/local-f0-runtime-lease-history-v1-runner.mjs'])
                self.assertEqual(args[8:10],['--execute-reviewed-local-f0-runtime-lease-history-v1','--operation'])
                attestation=loader.unique_json(kwargs['input']);self.assertEqual(attestation['planned'],manifest)
                self.assertEqual(attestation['observed']['container_id'],cid)
                flags={n:False for n in loader.DIAGNOSTIC_FLAGS};flags.update(text_valid=True,headers_valid=True)
                out=json.dumps({'schema':'workinants.local-f0-runtime-lease-history-migrate-result.v1',
                  'operation':args[-1],'status':'CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS','exit_code':0,
                  'prisma_codes':[],'sqlstates':[],'no_pending_message_observed':args[-1]=='deploy',
                  'raw_output_discarded':True,'database_qualification_claimed':False,'run_id':manifest['run_id'],
                  'container_id':cid,**{k:manifest['source'][k]for k in('initial_sql_sha256','append_sql_sha256','ordered_history_sha256','effective_expected_sha256')},
                  'attestation_sha256':sha(kwargs['input'].encode()),'diagnostic_format':flags})
                if fault=='raw_output':out='postgresql://secret-canary@127.0.0.1/db statement-body-canary'
                if fault=='program_drift':(fixture['root']/loader.PREPARER).write_bytes(b'changed-source-canary')
                if fault=='snapshot_drift':(fixture['snapshot']/self.prep.ordered_rows()[1]['path']).write_bytes(b'changed-source-canary')
            else:self.fail('unplanned process boundary')
            return SimpleNamespace(returncode=1 if fault=='exit'and i==7 else 0,stdout=out,stderr='password-canary raw-stderr-canary')
        return process,calls

    def test_real_coordinate_complete_positive_trace(self):
        for operation in('deploy','status'):
            with self.subTest(operation=operation),tempfile.TemporaryDirectory()as d:
                f=self.coordinate_fixture(Path(d));process,calls=self.modeled_outer_process(f)
                got=f['loader'].coordinate(f['raw'],operation,source8_root=f['snapshot'],source_pins=f['pins'],root=f['root'],process=process)
                self.assertEqual(len(calls),7);self.assertEqual(got['operation'],operation)
                self.assertFalse(got['database_qualification_claimed'])
                self.assertEqual(f['manifest']['tools']['files_sha256'],self.closure['tools_files_sha256'])
                self.assertEqual(len(f['manifest']['tools']['files_sha256']),10300)
                for secret in('password-canary','raw-stderr-canary','bootstrap-password'):
                    self.assertNotIn(secret,json.dumps(got))

    def test_real_coordinate_stops_on_outer_boundary_and_current_source_faults(self):
        for fault,maximum in(('image',4),('copied_hash',5),('exit',7),('raw_output',7),('program_drift',7),('snapshot_drift',7)):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory()as d:
                f=self.coordinate_fixture(Path(d));process,calls=self.modeled_outer_process(f,fault=fault)
                with self.assertRaises(Exception):f['loader'].coordinate(f['raw'],'deploy',source8_root=f['snapshot'],source_pins=f['pins'],root=f['root'],process=process)
                self.assertEqual(len(calls),maximum)

    def test_real_coordinate_genuine_tool_map_required_before_process(self):
        with tempfile.TemporaryDirectory()as d:
            f=self.coordinate_fixture(Path(d));m=copy.deepcopy(f['manifest']);m['tools']['files_sha256']['node/bin/node']='0'*64
            with self.assertRaisesRegex(Exception,'EXACT_PINNED_TOOL_CLOSURE'):
                f['loader'].coordinate(json.dumps(m).encode(),'deploy',source8_root=f['snapshot'],source_pins=f['pins'],root=f['root'],process=lambda *a,**k:self.fail('process'))

    def test_real_prepared_eight_source_PENDING_refuses_before_process(self):
        with tempfile.TemporaryDirectory()as d:
            f=self.coordinate_fixture(Path(d));path=f['root']/f['loader'].VALIDATION
            pending=json.loads(path.read_bytes());pending['review_gate']='PENDING'
            path.write_bytes(json.dumps(pending).encode());f['pins'][f['loader'].VALIDATION]=sha(path.read_bytes())
            self.assertEqual(len(f['loader'].verify_source8(f['snapshot'],f['manifest'],f['raw'],f['prep'])),8)
            with self.assertRaisesRegex(Exception,'SOURCE_REVIEW_PENDING'):
                f['loader'].coordinate(f['raw'],'deploy',source8_root=f['snapshot'],source_pins=f['pins'],root=f['root'],process=lambda *a,**k:self.fail('process'))

    def test_real_main_evidence_write_and_sanitized_failure(self):
        for fault in(None,'raw_output'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory()as d:
                base=Path(d);f=self.coordinate_fixture(base);process,calls=self.modeled_outer_process(f,fault=fault)
                manifest=base/'run.json';manifest.write_bytes(f['raw']);pins=base/'pins.json';pins.write_text(json.dumps(f['pins']))
                evidence=base/'evidence.json';out=io.StringIO()
                args=['--execute-reviewed-two-history','--run-manifest',str(manifest),'--operation','deploy',
                      '--source-pins',str(pins),'--source8-root',str(f['snapshot']),'--evidence-file',str(evidence)]
                with contextlib.redirect_stdout(out):status=f['loader'].main(args,process=process)
                got=json.loads(out.getvalue());self.assertEqual(len(calls),7)
                if fault is None:
                    self.assertEqual(status,0);self.assertEqual(json.loads(evidence.read_bytes()),got)
                    self.assertTrue(evidence.read_bytes().endswith(b'\n'));self.assertFalse(evidence.read_bytes().endswith(b'\\n'))
                else:self.assertEqual(status,1);self.assertFalse(evidence.exists());self.assertEqual(got['status'],'REFUSED_OR_INCOMPLETE')
                for secret in('secret-canary','password-canary','raw-stderr-canary','statement-body-canary'):
                    self.assertNotIn(secret,out.getvalue())

    def test_restoring_old_hash_pattern_or_evidence_newline_breaks_real_API(self):
        import ast
        original=(ROOT/'scripts/sql-review/run-local-f0-runtime-lease-history-v1.py').read_text(encoding='utf8')
        for defect in('hash_pattern','evidence_newline'):
            with self.subTest(defect=defect),tempfile.TemporaryDirectory()as d:
                base=Path(d);f=self.coordinate_fixture(base);process,calls=self.modeled_outer_process(f)
                if defect=='hash_pattern':
                    old='[^'+chr(92)*2+'r'+chr(92)*2+'n]+'
                    corrected='[^'+chr(92)+'r'+chr(92)+'n]+'
                    self.assertEqual(original.count(corrected),2)
                    mutated=original.replace(corrected,old)
                else:
                    marker="newline='"+chr(92)+"n'"
                    self.assertEqual(original.count(marker),1)
                    mutated=original.replace(marker,"newline='"+chr(92)*2+"n'")
                loader=ModuleType('_restored_old_source_mutant');loader.__file__=f['loader'].__file__
                exec(compile(mutated,loader.__file__,'exec'),loader.__dict__)
                if defect=='hash_pattern':
                    with self.assertRaisesRegex(Exception,'COPIED_SOURCE_HASH_OUTPUT'):
                        loader.coordinate(f['raw'],'deploy',source8_root=f['snapshot'],source_pins=f['pins'],root=f['root'],process=process)
                    self.assertEqual(len(calls),5)
                else:
                    manifest=base/'run.json';manifest.write_bytes(f['raw']);pins=base/'pins.json';pins.write_text(json.dumps(f['pins']))
                    evidence=base/'evidence.json';out=io.StringIO()
                    with contextlib.redirect_stdout(out):status=loader.main(['--execute-reviewed-two-history','--run-manifest',str(manifest),
                      '--operation','deploy','--source-pins',str(pins),'--source8-root',str(f['snapshot']),'--evidence-file',str(evidence)],process=process)
                    self.assertEqual(status,1);self.assertEqual(len(calls),7)
                    self.assertEqual(json.loads(out.getvalue())['code'],'NEW_INPUT_IO_OR_UNCONFIRMED_PROCESS')

    def test_resealed_append_header_body_and_target_mutations_reject(self):
        source=self.tools['catalog_manifest'];paths=(*source.INPUTS,self.effective.PATCH_PATH)
        for before,after in((b'wa_schema_owner',b'wa_worker'),(b'runtime_transition',b'runtime_transition_extra'),
                            (b'CREATE OR REPLACE FUNCTION',b'CREATE FUNCTION'),(b'COMMIT;',b'ROLLBACK;')):
            with self.subTest(after=after):
                blobs={n:self.blobs[n]for n in paths};raw=blobs[self.effective.PATCH_PATH]
                self.assertIn(before,raw);blobs[self.effective.PATCH_PATH]=raw.replace(before,after,1)
                pins={n:sha(b)for n,b in blobs.items()}
                with self.assertRaisesRegex(Exception,'EXACT_ORDERED_MIGRATION_BYTES'):
                    self.effective.build_manifest(source,blobs,pins)

    def test_generic_oracle_and_comparator_use_new_source_body(self):
        oracle=self.tools['catalog_expression_oracle'];compare=self.tools['compare_native_catalog']
        sql=self.files['expression-oracle.sql'].decode()
        self.assertIn(self.effective.NEW_BODY,sql);self.assertNotIn(self.effective.OLD_BODY,sql)
        self.assertIn(self.expected['expected_sha256'],sql)
        want=self.expected['expected']['functions'][self.effective.IDENTITY]
        # Deliberately incomplete synthetic native input exercises one field;
        # neither this fixture nor the overall comparison qualifies a catalog.
        row={'object':self.effective.IDENTITY,'body_sha256':self.effective.NEW_BODY}
        native={'functions':[row]}
        got=compare.compare_manifest(self.expected,native,bootstrap_grantor='postgres')
        self.assertEqual(got['source_expected_sha256'],self.expected['expected_sha256'])
        self.assertNotEqual(got['status'],'PASS')
        matches=lambda r:[f for f in r['findings']if f['category']=='functions'and f['subject']==self.effective.IDENTITY and f['field']=='body_sha256']
        self.assertEqual(matches(got),[])
        native['functions'][0]['body_sha256']=self.effective.OLD_BODY
        bad=compare.compare_manifest(self.expected,native,bootstrap_grantor='postgres')
        self.assertEqual(len(matches(bad)),1);self.assertEqual(matches(bad)[0]['status'],'FAIL')

    def test_real_generic_two_row_comparison_measured_and_mutations(self):
        proof=self.tools['prisma_ledger_proof']
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);self.snapshot(root)
            reg=self.ledger.registration(proof,root=root,run_id=self.run_id,target_attestation_sha256='a'*64,
              source_expected_sha256=self.expected['expected_sha256'])
            native={} # explicit unit-only native-binding fixture, no catalog claim
            got={**proof.schema_expectation(),'format':proof.NATIVE_FORMAT,'server_version_num':170011,
              'database':'wa_p0c_rehearsal','read_only':True,'isolation':'repeatable read','collected_as':'postgres',
              'session_user':'postgres','collector_is_superuser':True,'history_ids_unique':True,'history':copy.deepcopy(reg['history_expected'])}
            evidence={'format':proof.EVIDENCE_FORMAT,'registration_sha256':proof.digest(reg),
              'collector_sql_sha256':reg['tool_source_files_sha256'][proof.COLLECTOR],'run_id':self.run_id,
              'target_attestation_sha256':'a'*64,'native_catalog_before_sha256':proof.digest(native),
              'native_catalog_after_sha256':proof.digest(native),'observation':got}
            compare=lambda e:proof.compare_proof(reg,e,native,bootstrap_grantor='postgres',
              source_expected_sha256=self.expected['expected_sha256'],root=root)
            result=compare(evidence);self.assertEqual(result['status'],'PASS')
            self.__class__.measured_ledger_checks=len(result['checks'])
            for fault in('missing','third','duplicate','checksum','finished','logs','steps','time','type','catalog_binding'):
                with self.subTest(fault=fault):
                    bad=copy.deepcopy(evidence);rows=bad['observation']['history']
                    if fault=='missing':rows.pop()
                    elif fault=='third':rows.append(copy.deepcopy(rows[0]))
                    elif fault=='duplicate':rows[1]=copy.deepcopy(rows[0])
                    elif fault=='catalog_binding':bad['native_catalog_after_sha256']='0'*64
                    else:
                        field,value={'checksum':('checksum_sha256','0'*64),'finished':('finished',False),
                          'logs':('logs_state','NONEMPTY'),'steps':('steps',0),'time':('time_order_valid',False),'type':('steps',True)}[fault]
                        rows[0][field]=value
                    self.assertEqual(compare(bad)['status'],'FAIL')
if __name__=='__main__':unittest.main(verbosity=2)
