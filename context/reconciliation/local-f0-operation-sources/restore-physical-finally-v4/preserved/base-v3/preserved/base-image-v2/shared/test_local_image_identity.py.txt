"""Environment-free regression for Docker manifest-ID and config-ID stores."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('image_identity', HERE / 'local_image_identity.py')
identity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identity)
RAW = (HERE / 'fixtures/postgres-17.11-approved-manifest.json').read_bytes()
CANARY = 'UNRESTRICTED_IMAGE_METADATA_PASSWORD_CANARY'


def current():
    return [{'Id': identity.MANIFEST_DIGEST, 'Os': 'linux', 'Architecture': 'amd64',
             'RepoDigests': ['postgres@' + identity.MANIFEST_DIGEST],
             'Descriptor': {'mediaType': identity.MEDIA, 'digest': identity.MANIFEST_DIGEST, 'size': len(RAW)},
             'Config': {'Env': ['PG_VERSION=17.11-1.pgdg13+2', 'UNRELATED=' + CANARY]}, 'Unrestricted': CANARY}]


class Tests(unittest.TestCase):
    def setUp(self):
        for name in ('run', 'Popen', 'check_call', 'check_output', 'call'):
            mock = patch.object(subprocess, name, side_effect=AssertionError('NO_REAL_PROCESS'))
            mock.start(); self.addCleanup(mock.stop)
        mock = patch.object(socket, 'create_connection', side_effect=AssertionError('NO_NETWORK'))
        mock.start(); self.addCleanup(mock.stop)

    def rejects(self, value, raw=RAW):
        with self.assertRaises(identity.ImageIdentityError) as failure:
            identity.validate_cached_image(value, raw)
        self.assertNotIn(CANARY, str(failure.exception))

    def test_exact_approved_fixture(self):
        self.assertEqual('sha256:' + hashlib.sha256(RAW).hexdigest(), identity.MANIFEST_DIGEST)
        self.assertEqual(json.loads(RAW)['config']['digest'], identity.CONFIG_DIGEST)

    def test_current_manifest_store_and_old_fault_regression(self):
        value = current()
        self.assertFalse(value[0]['Id'] == identity.CONFIG_DIGEST)
        result = identity.validate_cached_image(value, RAW)
        self.assertEqual(result['image_store_identity'], 'MANIFEST')
        self.assertNotEqual(result['image_id'], result['config_digest'])

    def test_legacy_config_store(self):
        value = current(); value[0]['Id'] = identity.CONFIG_DIGEST; value[0].pop('Descriptor')
        self.assertEqual(identity.validate_cached_image(value, RAW)['image_store_identity'], 'CONFIG')

    def test_one_cli_newline(self):
        self.assertTrue(identity.validate_cached_image(current(), RAW + b'\n')['manifest_content_hash_verified'])

    def test_two_cli_newlines_reject(self): self.rejects(current(), RAW + b'\n\n')
    def test_wrong_store_id(self):
        value = current(); value[0]['Id'] = 'sha256:' + 'a' * 64; self.rejects(value)
    def test_wrong_os(self):
        value = current(); value[0]['Os'] = 'windows'; self.rejects(value)
    def test_wrong_architecture(self):
        value = current(); value[0]['Architecture'] = 'arm64'; self.rejects(value)
    def test_wrong_repository_digest(self):
        value = current(); value[0]['RepoDigests'] = ['postgres@sha256:' + '0' * 64]; self.rejects(value)
    def test_manifest_byte_tamper(self): self.rejects(current(), RAW.replace(b'17.11', b'17.12'))
    def test_changed_config_descriptor_rejects(self):
        self.rejects(current(), RAW.replace(identity.CONFIG_DIGEST.encode(), ('sha256:' + '0' * 64).encode()))
    def test_wrong_descriptor_digest(self):
        value = current(); value[0]['Descriptor']['digest'] = identity.CONFIG_DIGEST; self.rejects(value)
    def test_wrong_descriptor_size(self):
        value = current(); value[0]['Descriptor']['size'] += 1; self.rejects(value)
    def test_boolean_descriptor_size(self):
        value = current(); value[0]['Descriptor']['size'] = True; self.rejects(value)
    def test_missing_manifest_store_descriptor(self):
        value = current(); value[0].pop('Descriptor'); self.rejects(value)
    def test_wrong_patch_version(self):
        value = current(); value[0]['Config']['Env'] = ['PG_VERSION=17.110']; self.rejects(value)
    def test_duplicate_version(self):
        value = current(); value[0]['Config']['Env'] *= 2; self.rejects(value)
    def test_multiple_inspections(self): self.rejects(current() * 2)
    def test_bounded_raw_bytes(self):
        self.rejects(current(), 'unsafe' + CANARY); self.rejects(current(), b'x' * 65537)
    def test_allowlisted_retention(self):
        value = current(); before = copy.deepcopy(value)
        result = identity.validate_cached_image(value, RAW)
        self.assertNotIn(CANARY, json.dumps(result)); self.assertEqual(value, before)
        self.assertEqual(set(result), {'reference', 'image_id', 'config_digest', 'manifest_content_hash_verified',
            'pinned_repo_digest_verified', 'image_store_identity', 'os', 'architecture', 'pg_version', 'pulled_this_run', 'removed'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
