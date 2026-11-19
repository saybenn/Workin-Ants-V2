"""Pure admission of the approved Postgres image; performs no process or IO."""
import hashlib
import json
import re

IMAGE = 'docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'
MANIFEST_DIGEST = IMAGE.split('@')[1]
CONFIG_DIGEST = 'sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d'
MEDIA = 'application/vnd.oci.image.manifest.v1+json'


class ImageIdentityError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(condition, code):
    if not condition:
        raise ImageIdentityError(code)


def validate_cached_image(inspections, raw_manifest):
    """Require pinned manifest/config plus platform; return allowlisted facts.

    Docker's classic store identifies images by configuration digest. Its
    containerd store can identify this image by the manifest digest instead.
    Neither representation substitutes for verifying the actual manifest bytes
    and their independent config descriptor.
    """
    need(type(inspections) is list and len(inspections) == 1 and type(inspections[0]) is dict,
         'PINNED_IMAGE_SINGLE_IDENTITY')
    value = inspections[0]
    need(value.get('Os') == 'linux' and value.get('Architecture') == 'amd64', 'PINNED_IMAGE_PLATFORM_MISMATCH')
    need(value.get('Id') in (MANIFEST_DIGEST, CONFIG_DIGEST), 'PINNED_IMAGE_STORE_ID_MISMATCH')
    repositories = value.get('RepoDigests')
    allowed = {name + '@' + MANIFEST_DIGEST for name in ('postgres', 'library/postgres', 'docker.io/library/postgres')}
    need(type(repositories) is list and any(type(item) is str and item in allowed for item in repositories),
         'PINNED_IMAGE_DIGEST_MISSING')
    need(type(raw_manifest) is bytes and 0 < len(raw_manifest) <= 65536, 'PINNED_MANIFEST_BOUNDED_BYTES_REQUIRED')
    candidates = (raw_manifest, raw_manifest[:-1]) if raw_manifest.endswith(b'\n') else (raw_manifest,)
    exact = next((raw for raw in candidates if 'sha256:' + hashlib.sha256(raw).hexdigest() == MANIFEST_DIGEST), None)
    need(exact is not None, 'PINNED_MANIFEST_CONTENT_HASH_MISMATCH')
    try:
        manifest = json.loads(exact)
    except (UnicodeError, ValueError):
        raise ImageIdentityError('PINNED_MANIFEST_JSON_INVALID') from None
    need(type(manifest) is dict and manifest.get('schemaVersion') == 2 and manifest.get('mediaType') == MEDIA,
         'PINNED_MANIFEST_TYPE_MISMATCH')
    config = manifest.get('config')
    need(type(config) is dict and config.get('digest') == CONFIG_DIGEST, 'PINNED_IMAGE_CONFIG_MISMATCH')
    descriptor = value.get('Descriptor')
    if descriptor is not None:
        need(type(descriptor) is dict and descriptor.get('digest') == MANIFEST_DIGEST
             and descriptor.get('mediaType') == MEDIA and type(descriptor.get('size')) is int
             and descriptor['size'] == len(exact), 'PINNED_IMAGE_DESCRIPTOR_MISMATCH')
    else:
        need(value['Id'] == CONFIG_DIGEST, 'PINNED_MANIFEST_STORE_DESCRIPTOR_REQUIRED')
    configuration = value.get('Config')
    need(type(configuration) is dict and type(configuration.get('Env')) is list, 'PINNED_IMAGE_VERSION_MISMATCH')
    versions = [item[len('PG_VERSION='):] for item in configuration['Env']
                if type(item) is str and item.startswith('PG_VERSION=')]
    need(len(versions) == 1 and re.fullmatch(r'17\.11(?:[-+][A-Za-z0-9.+~_-]{1,48})?', versions[0]) is not None,
         'PINNED_IMAGE_VERSION_MISMATCH')
    return {'reference': IMAGE, 'image_id': value['Id'], 'config_digest': CONFIG_DIGEST,
            'manifest_content_hash_verified': True, 'pinned_repo_digest_verified': True,
            'image_store_identity': 'MANIFEST' if value['Id'] == MANIFEST_DIGEST else 'CONFIG',
            'os': 'linux', 'architecture': 'amd64', 'pg_version': versions[0],
            'pulled_this_run': False, 'removed': False}
