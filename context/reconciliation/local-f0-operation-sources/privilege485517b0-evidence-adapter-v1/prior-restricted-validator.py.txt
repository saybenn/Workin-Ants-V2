"""Pure exact-record adapter for the independently audited f161 SQL protocols.

Root independently approved 45 PASS and 25 PARTIAL mappings against unchanged
assertion texts. Historical raw NOT_RUN/proposal labels are retained: this adapter
maps only actual exercised criteria. Exact cases pass later aggregation only if
all mandatory assertions have independently admitted PASS evidence, including
the Unique SQL-storage and named DatabaseActionGrant ALLOW cases.
Nothing here qualifies an API replay response, Customer CAS, a production worker
loop, later owner adapters, hosted services or the whole 94/451 registers.

All 34 assets, the independent audit and 244 source files are hashed each call.
The accepted whole-record pins refuse unmodeled data. No retained operator code
is imported; no process, database, Git or network operation is performed.
"""
import hashlib
import json
from pathlib import Path
import re

RESULT = 'PASS_LOCAL_RESTRICTED_CONTROL_PACKETS_ONLY'
RUN = 'f161d454-13dd-453f-a9ee-6e92f95ea8d6'
COMMIT = 'b8f6b1039c743706f70278dd8b598cab6cbcd9db'
TREE = 'b0dd6288af19b0ae2d524e0332245922f5b25ca2'
PACKET = 'd2582c07eb74f3c010e8b42cbecad9abd81a8380d37cde1a855b1fdfde6e31fa'
SQL = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'
NATIVE = 'a048478f5e834dc1686b558954ea9bdaeaba4278afcf63976510c114680f1fc6'
NATIVE_FILE = 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8'
REPORT_SHA = 'f4e414015f51f978ed40676f9f036af2b60851c6d478ce38dd4cc60cefc7e0fa'
EXECUTION_CANONICAL_SHA = '2ad2a03bac354fd379ba3aed9995affb5b6b5fd0aced349ec4fee7b498c5048f'
AUDIT = 'context/reconciliation/local-f0-restricted-b8f6b10-f161d454-audit.json'
AUDIT_SHA = '9f217bb9064ed941ef932aa9298e8c7b6bfe0ca7dbeae8f292eea3158ba0bebd'
ASSETS = 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454'
TARGET = 'wa-p0c-f161d454-controls'
CID = '4fc7d96656376b9174d377ffcdf95a0bdbf3677ff52e4f1cd167f011749aa037'
TOOL_PACKAGES = {
    'node_modules/@prisma/engines-version/package.json': '2dd9793255d6bbb5c399a624ecbfb6323d39233860863d172946b7f750f528bd',
    'node_modules/prisma/package.json': '6cdfef6df08d9a37f28908855797fe8bfc97a2d3d886a8d5cbe2e502d6848151',
}

WHITELIST = {('P0C-ATOMIC-01', 'control.message_reverse'): {'assertion_sha256': '68936c884cfa744a1cf0dcf9851b78b6f5046a3b3559b51115f5dd99b51ba19b',
                                                'pointer': '/sanitized_report/control_packets/customer',
                                                'status': 'PARTIAL'},
 ('P0C-ATOMIC-01', 'control.omit_each_piece'): {'assertion_sha256': 'b2edab0fec53d5d164421c553019df815b77b5144b7468495ae10b380a4901be',
                                                'pointer': '/sanitized_report/control_packets/customer',
                                                'status': 'PARTIAL'},
 ('P0C-ATOMIC-01', 'vector.MESSAGE-REVERSE.adversarial'): {'assertion_sha256': 'e70fdb2980f5cc9aad98e226e49c0e29b41759c30fb2b3bc6b3ba9b92d506527',
                                                           'pointer': '/sanitized_report/control_packets/customer',
                                                           'status': 'PARTIAL'},
 ('P0C-ATOMIC-01', 'vector.RESULT-VERSION.adversarial'): {'assertion_sha256': '2b578ec95f7c6e2969f08b0e0c695a02afbffcdf50744ca55b7e1686dd9800e2',
                                                          'pointer': '/sanitized_report/control_packets/customer',
                                                          'status': 'PASS'},
 ('P0C-BOOT-01', 'control.missing_piece_denial'): {'assertion_sha256': 'ee2642b6882fcb56c745f0f4092abe4f5af1b1e52ad462b0ce7706c301f61041',
                                                   'pointer': '/sanitized_report/control_packets/customer',
                                                   'status': 'PASS'},
 ('P0C-BOOT-01', 'vector.FIRST-CUSTOMER.adversarial'): {'assertion_sha256': '0610ab41f729a0b3da0b488c1b86e54d14de4da0d1692f7344ab8f01c65721a7',
                                                        'pointer': '/sanitized_report/control_packets/customer',
                                                        'status': 'PARTIAL'},
 ('P0C-BOOT-01', 'vector.FIRST-CUSTOMER.positive'): {'assertion_sha256': 'c82cdd2c52a7018eba8486dd7da06d49f3a5f584d38b457c923aecdb64f6ce2e',
                                                     'pointer': '/sanitized_report/control_packets/customer',
                                                     'status': 'PARTIAL'},
 ('P0C-CTX-01', 'control.backend_pool_lifetime'): {'assertion_sha256': 'ba4d1be9d4b98114966c8e90b3d449a5dc325f7cb6034e58dc7b94868b3ae43c',
                                                   'pointer': '/sanitized_report/control_packets/context',
                                                   'status': 'PASS'},
 ('P0C-CTX-01', 'control.fresh_tuple'): {'assertion_sha256': '59be3cbc0417a9e84678280987443d95b6cff70fe7690af911d51ec4f4e0ae6b',
                                         'pointer': '/sanitized_report/control_packets/context',
                                         'status': 'PASS'},
 ('P0C-CTX-01', 'control.no_authority_from_transport'): {'assertion_sha256': '6aa4ae445ea46c233809a2251108dee9df0c51a1293d839879219d77c710c243',
                                                         'pointer': '/sanitized_report/control_packets/context',
                                                         'status': 'PARTIAL'},
 ('P0C-CTX-01', 'control.rollback_lifetime'): {'assertion_sha256': 'fc39256796f9783edb6711d483737187c1a7262b783b556a65090c0f0906f9e9',
                                               'pointer': '/sanitized_report/control_packets/context',
                                               'status': 'PASS'},
 ('P0C-CTX-01', 'control.wrong_isolation'): {'assertion_sha256': 'df201db96ed82a1d71ee6a5cff4299b0f06b615e99d758c18b447cd69c33b93f',
                                             'pointer': '/sanitized_report/control_packets/context',
                                             'status': 'PASS'},
 ('P0C-CTX-01', 'vector.POOL-LIFETIME.adversarial'): {'assertion_sha256': '75cb2be0bd3f4699411695169f553487e5feda9e3cb8aa79a580b4d40db6b0e3',
                                                      'pointer': '/sanitized_report/control_packets/context',
                                                      'status': 'PASS'},
 ('P0C-CTX-01', 'vector.POOL-LIFETIME.positive'): {'assertion_sha256': '4d214a536fcc76d070f53378a05d068c98920f733706967aceeef5d6aedbce79',
                                                   'pointer': '/sanitized_report/control_packets/context',
                                                   'status': 'PASS'},
 ('P0C-CTX-01', 'vector.READ-PURPOSE-NO-WRITE.adversarial'): {'assertion_sha256': 'ff56088c937816e1cf71df7d98d02ff3020b6d3171627dd3bd353172ad5827c9',
                                                              'pointer': '/sanitized_report/control_packets/context',
                                                              'status': 'PASS'},
 ('P0C-CTX-01', 'vector.READ-PURPOSE-NO-WRITE.positive'): {'assertion_sha256': '7a8ed48429dbd1351a6a35ae58bf7c4b7eaa568d09a36560d80baadaac7f637c',
                                                           'pointer': '/sanitized_report/control_packets/context',
                                                           'status': 'PARTIAL'},
 ('P0C-CTX-01', 'vector.SCOPE-PURPOSE.adversarial'): {'assertion_sha256': 'c578943adc5a1b91f0ad963e37de21926e1befa85e76caba7795619e83190b73',
                                                      'pointer': '/sanitized_report/control_packets/context',
                                                      'status': 'PASS'},
 ('P0C-CTX-01', 'vector.SCOPE-PURPOSE.positive'): {'assertion_sha256': 'ce459b066b38a262ea1254f0239586b92f9bde2c76bc1078d99e43afd1b02dea',
                                                   'pointer': '/sanitized_report/control_packets/context',
                                                   'status': 'PASS'},
 ('P0C-CTX-01', 'vector.SERVICE-BOOTSTRAP.adversarial'): {'assertion_sha256': 'd07c56332e3f395a8a0b2b5744ad82966522a95149c1c606529017f8cbbb4f9a',
                                                          'pointer': '/sanitized_report/control_packets',
                                                          'status': 'PARTIAL'},
 ('P0C-CTX-01', 'vector.SERVICE-BOOTSTRAP.positive'): {'assertion_sha256': 'd416db608fc95572fa5e9d9fb419467838c33d3afad9735442b2258225f2055f',
                                                       'pointer': '/sanitized_report/control_packets',
                                                       'status': 'PASS'},
 ('P0C-CTX-02', 'control.independent_service_currentness'): {'assertion_sha256': '985ce860c53025f783c7ac2a8454ffce82e95d806709baa1bf3fc4b2dd9b02e6',
                                                             'pointer': '/sanitized_report/control_packets',
                                                             'status': 'PASS'},
 ('P0C-CTX-02', 'control.revocation_schedule'): {'assertion_sha256': '18fc01dc3e8301f0a76a23b044c329daaf92cb599ed911d72387765ef33adc99',
                                                 'pointer': '/sanitized_report/control_packets/worker',
                                                 'status': 'PARTIAL'},
 ('P0C-CTX-02', 'control.role_appropriate_positive'): {'assertion_sha256': 'd49a91eb05a291b6b10334875da96b2f325cbcc8032012e8aa0a807f946388ad',
                                                       'pointer': '/sanitized_report/control_packets',
                                                       'status': 'PASS'},
 ('P0C-CTX-02', 'vector.SERVICE-REVOKE.adversarial'): {'assertion_sha256': 'b4bb2406df14242a57c68a4edaa42f8141291e14e4c30a753b69b09d5e2dd6e5',
                                                       'pointer': '/sanitized_report/control_packets',
                                                       'status': 'PASS'},
 ('P0C-CTX-02', 'vector.SERVICE-REVOKE.positive'): {'assertion_sha256': '3382cbcb1a73833062c4ae08e7f2a70af5c3b37252faf96132b7295ea3db240c',
                                                    'pointer': '/sanitized_report/control_packets',
                                                    'status': 'PASS'},
 ('P0C-EVIDENCE-01', 'control.closed_codec'): {'assertion_sha256': 'add7daca8cc6d40199835016edec5b7df2b889f268534f062f00de383be4764d',
                                               'pointer': '/sanitized_report/control_packets',
                                               'status': 'PARTIAL'},
 ('P0C-EVIDENCE-01', 'control.invented_evidence'): {'assertion_sha256': '9e0e7f21bc38eda3372edca4b24ce335e2ad7d6ec9a10f4acdcee149656878de',
                                                    'pointer': '/sanitized_report/control_packets/customer',
                                                    'status': 'PARTIAL'},
 ('P0C-EVIDENCE-01', 'control.worker_reverse'): {'assertion_sha256': '6c6e2b30c24eca99a199469afd2e659fc5cd9975cf401246f4ea5b00e4b6560e',
                                                 'pointer': '/sanitized_report/control_packets/worker',
                                                 'status': 'PARTIAL'},
 ('P0C-EVIDENCE-01', 'vector.EVIDENCE-CODEC.adversarial'): {'assertion_sha256': '8cf9802630fc002a19d68f0ab73ab83f8d65bdfd69924ad71a04b0ed53d99799',
                                                            'pointer': '/sanitized_report/control_packets/customer',
                                                            'status': 'PARTIAL'},
 ('P0C-EVIDENCE-01', 'vector.EVIDENCE-CODEC.positive'): {'assertion_sha256': '475a8949175bca13cc2501d024b7b371d39e1d67d1f668d288f2ad37e8d72ae0',
                                                         'pointer': '/sanitized_report/control_packets',
                                                         'status': 'PARTIAL'},
 ('P0C-EVIDENCE-01', 'vector.WORKER-REVERSE-PROOF.adversarial'): {'assertion_sha256': 'ba48c8ecb891905dfb2d919fd3b9bfe2f2a3b85ecb83d1c2bd5a1cf80490d5a8',
                                                                  'pointer': '/sanitized_report/control_packets/worker',
                                                                  'status': 'PARTIAL'},
 ('P0C-EVIDENCE-01', 'vector.WORKER-REVERSE-PROOF.positive'): {'assertion_sha256': 'b42437544d4f87a43646d33e19a2599dfba4a14aa39d8d95ed87ad727a5194cf',
                                                               'pointer': '/sanitized_report/control_packets/worker',
                                                               'status': 'PARTIAL'},
 ('P0C-INSTALL-01', 'vector.FUNCTION-ACL-AUTHORITY.positive'): {'assertion_sha256': '5a9eb59284dc1fb7c13e86ffac4352efa9d6d2963707668df921b318c15fe5eb',
                                                                'pointer': '/sanitized_report',
                                                                'status': 'PASS'},
 ('P0C-PRIV-01', 'control.direct_ports'): {'assertion_sha256': 'dfc62e53ad9e7a0f1ce005633346d3b0d89d8a1eadc719966ce69617365d9886',
                                           'pointer': '/sanitized_report/control_packets/worker',
                                           'status': 'PARTIAL'},
 ('P0C-PRIV-01', 'control.issuer_ceiling'): {'assertion_sha256': 'b06127c94dbf189ee0cf10b8bd131780e8612230f89c0efca6d4dbd94477f4c6',
                                             'pointer': '/sanitized_report/control_packets',
                                             'status': 'PARTIAL'},
 ('P0C-PRIV-01', 'vector.BOOLEAN-PORTS.adversarial'): {'assertion_sha256': '60788754672d1dc3dd5ca18b33f196f0f453e1f50bd189207001240e4736fb7d',
                                                       'pointer': '/sanitized_report/control_packets/worker',
                                                       'status': 'PARTIAL'},
 ('P0C-PRIV-01', 'vector.BOOLEAN-PORTS.positive'): {'assertion_sha256': '22dab74bf7d5a09f355694e22817e4e9c31a6fae8634a1997f1e3e45b2744ee0',
                                                    'pointer': '/sanitized_report/control_packets/worker',
                                                    'status': 'PARTIAL'},
 ('P0C-PRIV-01', 'vector.DIRECT-PORT-CAPS.adversarial'): {'assertion_sha256': 'cf98b9c5ef4cbafbd122d4fb40081fb0a9a6083e7872e2447d1df9bfa5eb815b',
                                                          'pointer': '/sanitized_report/control_packets/worker',
                                                          'status': 'PARTIAL'},
 ('P0C-PRIV-01', 'vector.DIRECT-PORT-CAPS.positive'): {'assertion_sha256': '02ffbb3ad84e0c3847ad4d3aef202bff3453af44f62c1e782aa4c199c0cc7902',
                                                       'pointer': '/sanitized_report/control_packets/worker',
                                                       'status': 'PARTIAL'},
 ('P0C-TABLE-CustomerProfile-ALLOW', 'positive.wa_app_runtime.select'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                         'pointer': '/sanitized_report/control_packets/context',
                                                                         'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_app_runtime.context'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                              'pointer': '/sanitized_report/control_packets/context',
                                                                              'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_app_runtime.execute'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                              'pointer': '/sanitized_report/control_packets/context',
                                                                              'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_context_issuer.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                                'pointer': '/sanitized_report/control_packets',
                                                                                'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_context_issuer.select'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                                'pointer': '/sanitized_report/control_packets',
                                                                                'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_context_issuer.update'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                                'pointer': '/sanitized_report/control_packets',
                                                                                'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_private_helper_owner.select'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                                      'pointer': '/sanitized_report/control_packets/context',
                                                                                      'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_worker.context'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                         'pointer': '/sanitized_report/control_packets/context',
                                                                         'status': 'PASS'},
 ('P0C-TABLE-DatabaseActionGrant-ALLOW', 'positive.wa_worker.execute'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                         'pointer': '/sanitized_report/control_packets/context',
                                                                         'status': 'PASS'},
 ('P0C-TABLE-OwnerMutationEvidence-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                          'pointer': '/sanitized_report/control_packets/worker',
                                                                          'status': 'PASS'},
 ('P0C-TABLE-RuntimeAttempt-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                   'pointer': '/sanitized_report/control_packets/worker',
                                                                   'status': 'PASS'},
 ('P0C-TABLE-RuntimeCommandReceipt-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                          'pointer': '/sanitized_report/control_packets/worker',
                                                                          'status': 'PASS'},
 ('P0C-TABLE-RuntimeEffectReceipt-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                         'pointer': '/sanitized_report/control_packets/worker',
                                                                         'status': 'PASS'},
 ('P0C-TABLE-RuntimeInboxReceipt-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                        'pointer': '/sanitized_report/control_packets/worker',
                                                                        'status': 'PASS'},
 ('P0C-TABLE-RuntimeWorkItem-ALLOW', 'positive.wa_app_runtime.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                         'pointer': '/sanitized_report/control_packets/worker',
                                                                         'status': 'PASS'},
 ('P0C-TABLE-RuntimeWorkItem-ALLOW', 'positive.wa_worker.select'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                    'pointer': '/sanitized_report/control_packets/worker',
                                                                    'status': 'PASS'},
 ('P0C-TABLE-RuntimeWorkItem-ALLOW', 'positive.wa_worker.update'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                    'pointer': '/sanitized_report/control_packets/worker',
                                                                    'status': 'PASS'},
 ('P0C-TABLE-TrackBaseSelection-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                       'pointer': '/sanitized_report/control_packets/worker',
                                                                       'status': 'PASS'},
 ('P0C-TABLE-TrackEnrollmentReceipt-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                           'pointer': '/sanitized_report/control_packets/worker',
                                                                           'status': 'PASS'},
 ('P0C-TABLE-TrackEntitlementGrant-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                          'pointer': '/sanitized_report/control_packets/worker',
                                                                          'status': 'PASS'},
 ('P0C-TABLE-TrackSubscription-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                      'pointer': '/sanitized_report/control_packets/worker',
                                                                      'status': 'PASS'},
 ('P0C-TABLE-TrackSubscriptionEvent-ALLOW', 'positive.wa_worker.insert'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                           'pointer': '/sanitized_report/control_packets/worker',
                                                                           'status': 'PASS'},
 ('P0C-TABLE-UserSecurityProfile-ALLOW', 'positive.wa_private_helper_owner.select'): {'assertion_sha256': '2236f315d3df2a396b663522bb48f170d88ee4acbe2513d4f4b691d848dad47c',
                                                                                      'pointer': '/sanitized_report/control_packets/context',
                                                                                      'status': 'PASS'},
 ('P0C-TRACK-01', 'control.actual_worker_enrollment'): {'assertion_sha256': '2e56f0bda58ace6bd6ae0cc5bf86ad110fcda17315c44305156705516c31b9d1',
                                                        'pointer': '/sanitized_report/control_packets/worker',
                                                        'status': 'PASS'},
 ('P0C-TRACK-01', 'control.lease_transitions'): {'assertion_sha256': 'df9e9f2c60b682774fdd018332716e082e50412579b2df0db9d78c1b98a2b929',
                                                 'pointer': '/sanitized_report/control_packets/worker',
                                                 'status': 'PARTIAL'},
 ('P0C-TRACK-01', 'vector.DIRECT-TRACK-SNAPSHOT.adversarial'): {'assertion_sha256': '2c9e7ec2826ad4ca45e540603c241bb7210290693574a750c521e16201a7ea1f',
                                                                'pointer': '/sanitized_report/control_packets/worker',
                                                                'status': 'PARTIAL'},
 ('P0C-TRACK-01', 'vector.DIRECT-TRACK-SNAPSHOT.positive'): {'assertion_sha256': 'd720ac20b774472efca54a24d8fe0d3c429808f0b0ac4967aa15ead0d272e50d',
                                                             'pointer': '/sanitized_report/control_packets/worker',
                                                             'status': 'PARTIAL'},
 ('P0C-TRACK-01', 'vector.LEASE-ATTACH.positive'): {'assertion_sha256': '1c29c26244fb54b716d00571cda3e13a2cd85cc2d50f41da11b75e755d8ea129',
                                                    'pointer': '/sanitized_report/control_packets/worker',
                                                    'status': 'PASS'},
 ('P0C-UNIQUE-01', 'control.changed_fingerprint'): {'assertion_sha256': '5992b6233b23134c1dcde93be5f86cca2582d7934990b55bbd4ff6f2ba2a3736',
                                                    'pointer': '/sanitized_report/control_packets/unique',
                                                    'status': 'PASS'},
 ('P0C-UNIQUE-01', 'control.different_scope'): {'assertion_sha256': '2987930f7a9d1687b7fd1679aca99069c36504a2fd4f2ca1dc0c1a109a914a6f',
                                                'pointer': '/sanitized_report/control_packets/unique',
                                                'status': 'PASS'},
 ('P0C-UNIQUE-01', 'control.same_semantic_identity'): {'assertion_sha256': '4b8bad1de72b6b0eb7f80c80917ede54db62ae20681f8a2628e250a1daf6e90f',
                                                       'pointer': '/sanitized_report/control_packets/unique',
                                                       'status': 'PASS'}}

SNAPSHOTS = {'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/authentication-ok/authentication-results-ok.json': '0472672f1c5a5a1c78564b5e5266a00a331bb9de6603056241a0fbb8036edee7',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/context-after-native.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/context-native-attestation.json': '3c04385a5c6716d6fed4c3da837f964e993c06f03e0004e94edfcbd28367cde2',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/context-run-plan.json': '7efb38ca08fb44c967792e9e7cdedd76b0b4cdeec3092f178ddeec23998273b5',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/control-context/context-control-results.json': '4fc8c736e2ec194935b068dad9708fe694a050c6a9c9b4a0a838e61de55c7ea6',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/control-customer/customer-control-results.json': 'd98f6eccfaa3baa9e8bf332458d6447727e74180863086366eee3184ae43ced9',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/control-unique/unique-control-results.json': '5ac085084b99e73e5a7d4614102abe137ce8248d50166d3901c9819e84cef68b',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/control-worker/worker-control-results.json': 'b7db8f04cdcfd53605160cb90589a53e23e2c42ac8890b417c627408e3c1fd15',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/customer-after-native.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/customer-run-plan.json': 'acdc3128f32393e99d953f160e12cd06b0ecda203fae34e43cdd5559b2a676c0',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/ledger-evidence.json': '4c40a66a400101b43c870a861bfbb712c52978e15c0817872c1ae18b2e6776d1',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/ledger-registration.json': '1c7474606e172c4085b583871243b22ee2af5bd5e32cc4d2bb067bb9684d85af',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/native-after-ledger.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/native-after-oracle.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/run-evidence.json': 'f4e414015f51f978ed40676f9f036af2b60851c6d478ce38dd4cc60cefc7e0fa',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/unique-after-native.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/unique-native-attestation.json': 'e59a350d064b9ecb6b2c08ede3601d935816d4bb796ea24b2f30e394176e29c8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/unique-run-plan.json': '3a0a0b348b24855992f3c9f3442813942d1f5e66ebe7c9499ba3d1abc4a68354',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/worker-after-native.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/evidence/worker-run-plan.json': '049ff21248350608d785f35b1c6cf08fbe15aefdbef2f7cf653ff0f6169066e2',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/plan/ok-history-manifest.json': '960f5e42fc55d9c41a1193d5e04ca2190cc4500a49efc42d4b2237d8e7bdc067',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/plan/ok-migration-manifest.json': '771493dfeaa8185f6931070fa91946f7357f0b0645347e211b1ede22abc80af5',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/plan/operation-manifest-before-head-repin.json': 'd6dca248d9f137edef315785f58ae4c2df14de32803a2bae4accfc07b2af1382',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/plan/operation-manifest.json': '92f5fbb9de5d11c086b3e7afe0e5f4f716fe19c6d420b59950d9bbb643596bc6',
 'context/reconciliation/local-f0-run-assets/b8f6b10-restricted-controls-f161d454/plan/operational-review.json': 'd8ef3c74fe1ad761cdce24fdf7195f1f3583386b6ea7ea5e1bc18320fcd5d077'}

RECORD_FIELDS = {'recorded_at', 'scope', 'source_tree', 'safe_raw_report_sha256', 'component_result_records', 'sanitized_report', 'packet_sha256', 'run_id', 'local_date', 'actual_steps', 'application_sql_sha256', 'source_commit', 'timezone', 'limits', 'actual_result', 'counting_limit', 'unexpected', 'snapshot_files_sha256'}

STEPS = {'CATALOG-ACL-COMPAT': 'PASS_NEW_SOURCE_COMPATIBILITY_CONTROL',
 'CATALOG-AUTH': 'PASS',
 'CATALOG-CLEANUP': 'PASS',
 'CATALOG-COMPARE': 'PASS_SOURCE_BOUND_NATIVE_CATALOG_ONLY',
 'CATALOG-INSTALL': 'PASS',
 'CATALOG-LEDGER': 'PASS_SOURCE_BOUND_NATIVE_SUBSET',
 'CATALOG-NATIVE': 'PASS_OBSERVED_NOT_QUALIFIED',
 'CATALOG-ORACLE': 'PASS_ROLLBACK_OBSERVED_NOT_WHOLE_CASE',
 'CATALOG-SANITIZED_EXPORT': 'PASS',
 'CATALOG-SETUP': 'PASS',
 'CATALOG-TEXT-COMPAT': 'PASS_NEW_SOURCE_COMPATIBILITY_CONTROL',
 'CATALOG-TOOLS': 'PASS',
 'CONTROL-CONTEXT': 'PASS_FINITE_PACKET_ONLY',
 'CONTROL-CUSTOMER': 'PASS_FINITE_PACKET_ONLY',
 'CONTROL-UNIQUE': 'PASS_FINITE_PACKET_ONLY',
 'CONTROL-WORKER': 'PASS_FINITE_PACKET_ONLY'}

CLAIMS = {key: value['status'] for key, value in WHITELIST.items()}
POINTERS = {key: value['pointer'] for key, value in WHITELIST.items()}


class EvidenceFailure(ValueError):
    """Only fixed refusal codes leave this boundary."""


def _need(value, code):
    if not value:
        raise EvidenceFailure(code)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def _same(actual, expected, code):
    _need(_json(actual) == _json(expected), code)


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _digest(value):
    return _hash(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8'))


def _read(root, relative, expected):
    _need(type(relative) is str and ':' not in relative and chr(92) not in relative and not relative.startswith('/') and all(p not in ('', '.', '..') for p in relative.split('/')), 'RESTRICTED_EVIDENCE_PATH')
    path = (root / relative).resolve(strict=True)
    _need(path.is_relative_to(root), 'RESTRICTED_EVIDENCE_PATH')
    raw = path.read_bytes()
    _need(_hash(raw) == expected, 'RESTRICTED_EVIDENCE_FILE_HASH')
    return raw


def _inventory(root, key):
    inventory = json.loads((root / 'context/reconciliation/local-f0-assertions.json').read_bytes())
    items = [a for c in inventory['cases'] if c['id'] == key[0] for a in c['assertions'] if a['id'] == key[1]]
    _need(len(items) == 1 and items[0]['mandatory_for_case'] is True and items[0]['availability'] not in ('DEPENDENCY_BLOCKED', 'SOURCE_PATH_REVIEW_REQUIRED', 'SPECIFICATION_CONFLICT'), 'RESTRICTED_ASSERTION_REQUIREMENT')
    _same(_hash(items[0]['expected_assertion'].encode('utf8')), WHITELIST[key]['assertion_sha256'], 'RESTRICTED_ASSERTION_REQUIREMENT')


def _assets(root, execution):
    _same(execution['snapshot_files_sha256'], SNAPSHOTS, 'RESTRICTED_SNAPSHOT_BINDING')
    # Hash every artifact, but parse duplicate native catalogs only once.
    documents, parsed = {}, {}
    for relative, digest in SNAPSHOTS.items():
        raw = _read(root, relative, digest)
        if digest not in parsed:
            parsed[digest] = json.loads(raw)
        documents[relative.removeprefix(ASSETS + '/')] = parsed[digest]
    audit = json.loads(_read(root, AUDIT, AUDIT_SHA))
    _same(audit['run_id'], RUN, 'RESTRICTED_AUDIT_BINDING')
    _same(audit['status'], 'PASS_EXACT_FINITE_SQL_PROTOCOLS_ONLY', 'RESTRICTED_AUDIT_BINDING')
    return documents


def _source(root, execution, report, assets):
    for key, expected in {'run_id': RUN, 'source_commit': COMMIT, 'source_tree': TREE, 'packet_sha256': PACKET, 'application_sql_sha256': SQL}.items():
        _same(execution[key], expected, 'RESTRICTED_SOURCE_IDENTITY')
    for key, expected in {'run_id': RUN, 'approved_commit': COMMIT, 'approved_tree': TREE, 'approved_packet_sha256': PACKET}.items():
        _same(report[key], expected, 'RESTRICTED_REPORT_IDENTITY')
    manifest = assets['plan/operation-manifest.json']
    _same(report['run_manifest'], manifest, 'RESTRICTED_MANIFEST_BINDING')
    _same(report['run_manifest_sha256'], SNAPSHOTS[ASSETS + '/plan/operation-manifest.json'], 'RESTRICTED_MANIFEST_BINDING')
    hashes = manifest['packet_files_sha256']
    _need(type(hashes) is dict and len(hashes) == 244 and all(type(p) is str and type(h) is str and re.fullmatch('[0-9a-f]{64}', h) for p, h in hashes.items()), 'RESTRICTED_PACKET_FIELDS')
    _same(_hash(''.join(p + '\0' + hashes[p] + '\n' for p in sorted(hashes)).encode('utf8')), PACKET, 'RESTRICTED_PACKET_AGGREGATE')
    _same(report['source_verification'], {'commit': COMMIT, 'tree': TREE, 'packet_sha256': PACKET, 'files_sha256': hashes, 'file_count': 244}, 'RESTRICTED_SOURCE_VERIFICATION')
    for path, digest in hashes.items():
        _read(root, path, digest)
    # Preserved node_modules junction: permit only the two fixed package JSONs.
    _same(manifest['catalog']['tool_source_files_sha256'], TOOL_PACKAGES, 'RESTRICTED_TOOL_BINDING')
    for relative, digest in TOOL_PACKAGES.items():
        _same(_hash((root / relative).read_bytes()), digest, 'RESTRICTED_TOOL_HASH')
    _need(report['packet_unchanged_after_run'] is True and report['tool_source_data_unchanged_after_run'] is True, 'RESTRICTED_SOURCE_PRESERVATION')
    _same(hashes['review-output/foundation-application.review.sql'], SQL, 'RESTRICTED_SQL_IDENTITY')


def _native(report, assets):
    snapshot = assets['evidence/native-before.json']
    _same(_digest(snapshot), NATIVE, 'RESTRICTED_NATIVE_IDENTITY')
    for name in ('native-after-oracle', 'native-after-ledger', 'customer-after-native', 'worker-after-native', 'context-after-native', 'unique-after-native'):
        _same(assets['evidence/' + name + '.json'], snapshot, 'RESTRICTED_NATIVE_PRESERVATION')
    comparison = assets['evidence/catalog-comparison.json']
    _same(report['catalog_comparison'], comparison, 'RESTRICTED_NATIVE_COMPARISON')
    for key, value in {'status': 'PASS', 'native_snapshot_sha256': NATIVE, 'source_expected_sha256': '3be81a13d3bb2abb41bf03ef68398da6d92fbdbccffec3d74508e91dd455f433', 'check_counts': {'PASS': 29089}, 'findings': []}.items():
        _same(comparison[key], value, 'RESTRICTED_NATIVE_COMPARISON')
    proof = report['ledger_comparison']
    _need(proof['status'] == 'PASS' and len(proof['checks']) == 22 and all(c['status'] == 'PASS' and c['expected_sha256'] == c['actual_sha256'] for c in proof['checks']), 'RESTRICTED_LEDGER_PROOF')
    oracle = assets['evidence/oracle-evidence.json']
    _need(oracle['connection_closed_before_observation'] is True and len(oracle['results']['expressions']) == 416 and all(v is True for v in oracle['preflight']['outcomes'].values()) and oracle['closure']['all_oracle_tables_absent'] is True and oracle['closure']['all_oracle_functions_absent'] is True, 'RESTRICTED_ORACLE_CLOSURE')
    _same(oracle['pre_oracle_catalog_sha256'], NATIVE, 'RESTRICTED_ORACLE_PRESERVATION')
    _same(oracle['post_rollback_catalog_sha256'], NATIVE, 'RESTRICTED_ORACLE_PRESERVATION')


def _authentication(value):
    rows = value['authentication']
    _need(len(rows) == 6 and all(r['correct_password'] == 'PASS_SCRAM' and r['wrong_password'] == 'PASS_REJECTED' and type(r['wrong_password_exit_code']) is int and r['wrong_password_exit_code'] == 2 for r in rows), 'RESTRICTED_AUTHENTICATION')
    _need(all(v is True for v in value['authentication_comparison'].values()), 'RESTRICTED_AUTHENTICATION')


def _components(root, report, assets):
    counts = {'customer': 17, 'worker': 15, 'context': 31, 'unique': 5}
    statuses = {'customer': 'PASS_PREPARED_CREATE_SUBSET_ONLY_CONTROLS_NOT_RUN',
                'worker': 'PREPARED_FINITE_SUBSET_COMPLETED_NOT_FULL_CONTROL_QUALIFICATION',
                'context': 'PASS_CTX01_PREPARED_SQL_PROTOCOLS_ONLY_CONTROLS_NOT_RUN',
                'unique': 'COMPLETED_FIVE_SQL_STORAGE_RACES_ONLY_ASSERTIONS_NOT_RUN'}
    documents, packets = {}, {}
    _same(sorted(report['control_packets']), sorted(counts), 'RESTRICTED_COMPONENT_SET')
    for kind, count in counts.items():
        key = 'evidence/control-' + kind + '/' + kind + '-control-results.json'
        value = assets[key]
        documents[kind] = value
        descriptor = report['control_packets'][kind]
        _same(descriptor, {'component': kind, 'status': 'PASS_FINITE_PACKET_ONLY_NOT_SELECTED_CASES', 'exit_code': 0, 'evidence_file': 'control-' + kind + chr(92) + kind + '-control-results.json', 'completed_results': count, 'evidence_sha256': SNAPSHOTS[ASSETS + '/' + key], 'native_catalog_unchanged': True, 'all_operation_clients_absent': True}, 'RESTRICTED_COMPONENT_BINDING')
        _need(len(value['results']) == count and value['subsequent_cases_stopped'] is False and 'failure' not in value, 'RESTRICTED_COMPONENT_RESULT')
        _same(value['status'], statuses[kind], 'RESTRICTED_COMPONENT_STATUS')
        _same(value.get('container_id', value.get('resource', {}).get('container_id')), CID, 'RESTRICTED_COMPONENT_CID')
        _authentication(value)
        _need(all(row['status'] == 'NOT_RUN' for row in value['selected_controls']), 'RESTRICTED_HISTORICAL_LABELS')
        plan = assets['evidence/' + kind + '-run-plan.json']
        for p, h in plan['source_modules_sha256'].items():
            _same(report['run_manifest']['packet_files_sha256'][p], h, 'RESTRICTED_COMPONENT_SOURCE')
        _same(plan['native_snapshot']['sha256'], NATIVE_FILE, 'RESTRICTED_COMPONENT_NATIVE_GATE')
        _same(plan['native_comparison']['sha256'], SNAPSHOTS[ASSETS + '/evidence/catalog-comparison.json'], 'RESTRICTED_COMPONENT_NATIVE_GATE')
        if 'native_attestation' in plan:
            attestation = assets['evidence/' + kind + '-native-attestation.json']
            for key, expected in {'run_id': RUN, 'container_id': CID, 'source_commit': COMMIT, 'source_tree': TREE, 'packet_sha256': PACKET, 'native_snapshot_sha256': NATIVE, 'original_grantor_finalized': True, 'operation_backends_absent': True, 'comparison_status': 'PASS'}.items():
                _same(attestation[key], expected, 'RESTRICTED_COMPONENT_ATTESTATION')
        relative = 'review-output/' + kind + '-control-rehearsal/fixtures.json'
        raw = _read(root, relative, report['run_manifest']['packet_files_sha256'][relative])
        packets[kind] = json.loads(raw)
    closures = [{'stage': phase + '_' + kind.upper(), 'scope': 'ALL_DATABASES_ALL_ROLES_ALL_TAGS', 'observation_completed': True, 'all_other_client_backends_absent': True} for kind in counts for phase in ('BEFORE', 'AFTER')]
    _same(report['control_backend_closures'], closures, 'RESTRICTED_COMPONENT_CLOSURE')
    return documents, packets


def _installation(report):
    _same(sorted(report['targets']), [TARGET], 'RESTRICTED_INSTALL_TARGET')
    target = report['targets'][TARGET]
    for key, expected in {'container_id': CID, 'volume': TARGET + '-data', 'network_mode': 'none',
                          'published_ports': False, 'finalization': 'PASS',
                          'labels': {'workinants.rehearsal': 'p0c-local-f0', 'workinants.rehearsal.run': RUN}}.items():
        _same(target[key], expected, 'RESTRICTED_INSTALL_TARGET')
    _same(target['connections_before_finalization'], {'migrator': 0, 'tagged_other_clients': 0}, 'RESTRICTED_INSTALL_CLOSURE')
    _same(target['finalization_observation'], {'auth': 'scram-sha-256:postgres', 'grantor': 'postgres',
           'leaf_create': dict.fromkeys(('wa_track_verifier', 'wa_customer_verifier', 'wa_private_helper_owner'), False),
           'remaining_memberships': 0, 'active_install_connections': 0}, 'RESTRICTED_ORIGINAL_GRANTOR_FINALIZATION')
    _need(len(report['migration_operations']) == 1, 'RESTRICTED_INSTALL_OPERATION_SET')
    operation = report['migration_operations'][0]
    for key, expected in {'target': TARGET, 'stage': 'CATALOG_GENUINE_INITIAL_DEPLOY', 'operation': 'deploy',
                          'exit_code': 0, 'run_id': RUN, 'container_id': CID, 'source_sql_sha256': SQL,
                          'raw_output_discarded': True, 'database_qualification_claimed': False}.items():
        _same(operation[key], expected, 'RESTRICTED_INSTALL_OPERATION')


def _frame(case, application):
    intended = case['intended_diagnostic']
    if not intended or not intended['required_source_function']:
        return None
    name = intended['required_source_function']
    matches = list(re.finditer(r'CREATE FUNCTION ' + re.escape(name) + r'\(\)\s+RETURNS\b[^;]*?\bAS\s+(\$[a-z_0-9]*\$)(.*?)\1;', application, re.S))
    _need(len(matches) == 1, 'RESTRICTED_SOURCE_FRAME')
    body = matches[0][2]
    if intended['sqlstate'] == 'P0002':
        variable = 'e' if case['variation'] == 'missing-evidence' else 'h'
        lines = [n for n, line in enumerate(body.split('\n'), 1) if re.search(r'\bSELECT \* INTO STRICT ' + variable + r' FROM\b', line)]
        operation = 'SQL statement'
    else:
        lines = [n for n, line in enumerate(body.split('\n'), 1) if "RAISE EXCEPTION '" + intended['exact_source_message'] + "'" in line]
        operation = 'RAISE'
    _need(len(lines) == 1, 'RESTRICTED_SOURCE_FRAME')
    return {'function': name, 'body_line': lines[0], 'operation': operation, 'body_sha256': _hash(body.encode('utf8'))}


def _customer(value, packet, application):
    _same([r['name'] for r in value['results']], [r['name'] for r in packet['cases']], 'RESTRICTED_CUSTOMER_CASE_SET')
    for row, case in zip(value['results'], packet['cases']):
        _need(row['operation_closed'] is True and row['authenticated_login'] == 'wa_app_runtime' and row['issuer_committed'] is True and row['unexpected_stdout'] is False, 'RESTRICTED_CUSTOMER_CLOSURE')
        _same(row['stage_markers'], case['stage_marker_oracle']['expected_completed_markers'], 'RESTRICTED_CUSTOMER_MARKERS')
        for key in ('expected_failure_stage', 'expected_failure_timing'):
            _same(row[key], case['stage_marker_oracle'][key], 'RESTRICTED_CUSTOMER_STAGE')
        _same(row['counts'], case['observer_expected'], 'RESTRICTED_CUSTOMER_COMPLETE_STATE')
        _same(row['exit_code'], 0 if case['expected_commit'] else 3, 'RESTRICTED_CUSTOMER_COMMIT')
        _same(row['commit_ack_count'], 1 if case['expected_commit'] else 0, 'RESTRICTED_CUSTOMER_COMMIT')
        _same(row['commit_acknowledged'], case['expected_commit'], 'RESTRICTED_CUSTOMER_COMMIT')
        diagnostic = row['diagnostic']
        _need(diagnostic['matched'] is True and diagnostic['classification'] == 'EXPECTED_SOURCE_DIAGNOSTIC' and diagnostic['diagnostic_format_valid'] is True and diagnostic['source_frame_verified'] is True, 'RESTRICTED_CUSTOMER_DIAGNOSTIC')
        _same(diagnostic['source_frame'], _frame(case, application), 'RESTRICTED_CUSTOMER_SOURCE_FRAME')
        _same(diagnostic['sqlstate'], case['intended_diagnostic']['sqlstate'] if case['intended_diagnostic'] else None, 'RESTRICTED_CUSTOMER_DIAGNOSTIC')
    _need(value['trigger_restoration_verified'] is True and value['fresh_synthetic_ids_verified'] is True and value['native_catalog_unchanged'] is True, 'RESTRICTED_CUSTOMER_FIXTURES')
    for row in value['transactions'].values():
        _need(row['operation_closed'] is True and row['commit_acknowledged'] is True and row['exit_code'] == 0 and row['stderr_empty'] is True and row['unexpected_stdout'] is False, 'RESTRICTED_CUSTOMER_ISSUER')


def _worker(value, packet, binder_hash):
    for row in value['results']:
        _need(row['operation_closed'] is True and row['actual_login_verified'] is True, 'RESTRICTED_WORKER_CLOSURE')
        if 'WORKER_COMPLETE_STATE' in row:
            _same(row['WORKER_COMPLETE_STATE'], packet['positive_observer_expected'], 'RESTRICTED_WORKER_COMPLETE_STATE')
            _same(row['FIXTURE_GUARDS'], {'owner_guards_reenabled': True, 'no_project_user_trigger_disabled': True}, 'RESTRICTED_WORKER_FIXTURES')
            _need(row['native_catalog_unchanged'] is True and row['catalog_and_usage_unchanged'] is True, 'RESTRICTED_WORKER_CEILING')
        if 'diagnostic' in row:
            _same(row['exit_code'], 3, 'RESTRICTED_WORKER_DIAGNOSTIC')
            diagnostic = row['diagnostic']
            _need(row['acknowledgement'] is False and diagnostic['matched'] is True and diagnostic['sqlstate'] == '42501' and diagnostic['source_frame_verified'] is True and diagnostic['body_sha256'] == binder_hash and diagnostic['body_line'] == 7, 'RESTRICTED_WORKER_DIAGNOSTIC')
        else:
            _same(row['exit_code'], 0, 'RESTRICTED_WORKER_COMMIT')
            _need(row['commit_or_rollback_acknowledged'] is True and row['output_comparisons']['row_count_matches'] is True and all(r['object'] is True and r['fields'] is True and all(v is True for v in r['comparisons'].values()) for r in row['output_comparisons']['rows']), 'RESTRICTED_WORKER_OUTPUT')
    _same(value['unprepared_vectors'], packet['mandatory_unprepared_vectors'], 'RESTRICTED_WORKER_UNPREPARED')
    _need(len(value['operations']) == 19 and all(r['failure_code'] is None and r['failure_stage'] is None and r['operation_closed'] is True for r in value['operations']), 'RESTRICTED_WORKER_OPERATIONS')


def _context(value, packet, binder_hash):
    _same([r['name'] for r in value['results']], [r['name'] for r in packet['cases']], 'RESTRICTED_CONTEXT_CASE_SET')
    observers = {'COMPLETE_' + Path(row['file']).stem.upper().replace('-', '_'): row['expected'] for row in packet['mandatory_after_case_observers']}
    counts = dict.fromkeys(observers, 0)
    totals = {'SEPARATE_ISSUER_COMMIT': 0, 'ISSUER_ROW_RETENTION': 0, 'OLD_INSTANCE_RETIREMENT': 0, 'EXPECTED_BINDER_FAILURE': 0}
    segment = []
    for row in value['operations']:
        stage = row['stage']; segment.append(row)
        if stage in totals: totals[stage] += 1
        if stage in observers:
            counts[stage] += 1
            _need(row['shape_and_values_match'] is True and row['observation']['fields_match'] is True, 'RESTRICTED_CONTEXT_OBSERVER')
            _same(row['observation']['values'], observers[stage], 'RESTRICTED_CONTEXT_COMPLETE_STATE')
        if stage == 'SEPARATE_ISSUER_COMMIT':
            _need(all(row[k] is True for k in ('issuer_committed', 'commit_acknowledged', 'created_at_return_verified', 'operation_closed')), 'RESTRICTED_CONTEXT_ISSUER_COMMIT')
        if stage == 'ISSUER_ROW_RETENTION':
            _need(row['immutable_issuer_rows_match'] is True and row['observation']['fields_match'] is True, 'RESTRICTED_CONTEXT_ISSUER_RETENTION')
            _same(row['observation']['values'], {'exact_count': row['instances'], 'all_immutable_fields_equal': True, 'issuer_owned': True, 'revoked_false': True, 'unexpired': True}, 'RESTRICTED_CONTEXT_ISSUER_RETENTION')
        if stage == 'OLD_INSTANCE_RETIREMENT':
            _need(row['stale_source_guard'] is True and row['operation_closed'] is True, 'RESTRICTED_CONTEXT_RETIREMENT')
        if stage == 'EXPECTED_BINDER_FAILURE':
            z = row['diagnostic']
            _same(row['exit_code'], 3, 'RESTRICTED_CONTEXT_DIAGNOSTIC')
            _need(row['acknowledged'] is False and row['unexpected_stdout'] is False and z['matched'] is True and z['source_frame_verified'] is True and z['sqlstate'] == '42501' and z['source_body_sha256'] == binder_hash, 'RESTRICTED_CONTEXT_DIAGNOSTIC')
        if stage == 'PROTOCOL_COMPLETE':
            _need(row['all_retirement_probes_closed'] is True, 'RESTRICTED_CONTEXT_CLOSURE')
            lines = [s['diagnostic']['source_body_line'] for s in segment if s['stage'] == 'EXPECTED_BINDER_FAILURE']
            malformed = row['scenario'] in ('app-malformed-secret', 'worker-malformed-secret')
            _need((lines.count(4) == 1 and all(n in (4, 7) for n in lines)) if malformed else all(n == 7 for n in lines), 'RESTRICTED_CONTEXT_SOURCE_LINE')
            segment = []
    _same(totals, {'SEPARATE_ISSUER_COMMIT': 30, 'ISSUER_ROW_RETENTION': 59, 'OLD_INSTANCE_RETIREMENT': 30, 'EXPECTED_BINDER_FAILURE': 50}, 'RESTRICTED_CONTEXT_OPERATION_SET')
    _same(counts, dict.fromkeys(observers, 32), 'RESTRICTED_CONTEXT_OBSERVER_SET')
    _same(value['unprepared_obligations'], packet['unprepared_obligations'], 'RESTRICTED_CONTEXT_UNPREPARED')


def _unique(value, packet):
    _same([r['name'] for r in value['results']], [r['name'] for r in packet['races']], 'RESTRICTED_UNIQUE_RACE_SET')
    for row, race in zip(value['results'], packet['races']):
        _same(row['bindings'], {'A': True, 'B': True}, 'RESTRICTED_UNIQUE_BINDING')
        _same(row['closed'], {'A': True, 'B': True}, 'RESTRICTED_UNIQUE_CLOSURE')
        _need(row['stage'] == 'COMPLETE' and row['runtime_assertion_status'] == 'NOT_RUN' and all(v is True for v in row['comparisons'].values()), 'RESTRICTED_UNIQUE_VERDICT')
        if race['name'] != 'different-subjects-identical-text-key':
            _same(row['barrier_observations'], 1, 'RESTRICTED_UNIQUE_WAIT')
            if race['holder_outcome'] == 'COMMIT':
                _same(row['B_exit_code'], 3, 'RESTRICTED_UNIQUE_DUPLICATE')
                _need(row['B_acknowledged'] is False, 'RESTRICTED_UNIQUE_DUPLICATE')
    totals = {'NATIVE_WAIT_OBSERVATION': 0, 'SEPARATE_ISSUER_COMMIT': 0, 'ACTUAL_APP_BOUND': 0, 'OPERATION_CLOSURE': 0, 'NATIVE_DUPLICATE_VERDICT': 0, 'WAITING_COMMAND_RELEASED': 0}
    complete, ends = [], []
    for row in value['operations']:
        stage = row['stage']
        if stage in totals: totals[stage] += 1
        if stage == 'NATIVE_WAIT_OBSERVATION':
            _need(row['shape_matches'] is True, 'RESTRICTED_UNIQUE_WAIT')
            _same(row['comparisons'], {'fields_match': True, 'values': dict.fromkeys(('A_idle_in_transaction', 'B_active', 'B_wait_event_type_lock', 'B_wait_event_transactionid', 'B_blocked_only_by_A'), True)}, 'RESTRICTED_UNIQUE_WAIT')
        if stage == 'SEPARATE_ISSUER_COMMIT':
            _need(all(row[k] is True for k in ('issuer_committed', 'commit_acknowledged', 'created_at_return_verified', 'operation_closed')), 'RESTRICTED_UNIQUE_ISSUER')
        if stage == 'ACTUAL_APP_BOUND':
            _need(row['issuer_commit_and_closure_verified'] is True and row['same_tuple'] is True, 'RESTRICTED_UNIQUE_TUPLE')
        if stage == 'OPERATION_CLOSURE':
            _need(row['exact_backend_absent'] is True and row['expected_exit'] is True, 'RESTRICTED_UNIQUE_CLOSURE')
        if stage == 'NATIVE_DUPLICATE_VERDICT':
            _same(row['exit_code'], 3, 'RESTRICTED_UNIQUE_DUPLICATE')
            _need(row['acknowledgement'] is False and row['before_only'] is True, 'RESTRICTED_UNIQUE_DUPLICATE')
            _same(row['diagnostic'], {'matched': True, 'sqlstate': '23505', 'schema_table_constraint_exact': True, 'native_location_exact': True, 'detail_absent': True}, 'RESTRICTED_UNIQUE_DUPLICATE')
        if stage.startswith('WINNER_ACTUAL_TRANSACTION'):
            _need(row['matches'] is True and row['observation']['fields_match'] is True and all(v is True for v in row['observation']['values'].values()), 'RESTRICTED_UNIQUE_XID_WITNESS')
        if stage == 'ISSUER_ROW_RETENTION':
            _need(row['immutable_issuer_rows_match'] is True and row['observation']['values']['all_immutable_fields_equal'] is True and row['observation']['values']['exact_count'] == row['instances'], 'RESTRICTED_UNIQUE_ISSUER_RETENTION')
        if stage == 'EXACT_COMPLETE_GROUP_COUNTS': complete.append(row)
        if stage == 'TRANSACTION_END':
            _need(row['acknowledged'] is True and row['exact_output'] is True, 'RESTRICTED_UNIQUE_TERMINAL')
            ends.append([row['side'], row['outcome']])
    _same(totals, {'NATIVE_WAIT_OBSERVATION': 4, 'SEPARATE_ISSUER_COMMIT': 10, 'ACTUAL_APP_BOUND': 10, 'OPERATION_CLOSURE': 10, 'NATIVE_DUPLICATE_VERDICT': 2, 'WAITING_COMMAND_RELEASED': 2}, 'RESTRICTED_UNIQUE_OPERATION_SET')
    _same(ends, [['A', 'COMMIT'], ['A', 'ROLLBACK'], ['B', 'COMMIT'], ['A', 'COMMIT'], ['A', 'ROLLBACK'], ['B', 'COMMIT'], ['A', 'COMMIT'], ['B', 'COMMIT']], 'RESTRICTED_UNIQUE_TERMINAL')
    _need(len(complete) == 5 and len(value['committed_groups']) == 6, 'RESTRICTED_UNIQUE_GROUP_SET')
    for row, race in zip(complete, packet['races']):
        _need(row['matches'] is True and row['observation']['fields_match'] is True, 'RESTRICTED_UNIQUE_COMPLETE_STATE')
        _same(row['observation']['values'], race['observer_expected'], 'RESTRICTED_UNIQUE_COMPLETE_STATE')


def _cleanup(report):
    _same(report['cleanup'], {TARGET: {'removed': True, 'verified_id': CID, 'name_and_both_labels_verified': True}, TARGET + '-data': {'removed': True, 'name_labels_creation_identity_verified': True}}, 'RESTRICTED_CLEANUP_IDENTITY')
    _same(report['cleanup_summary'], {'resource_presence_after': {TARGET: False, TARGET + '-data': False}, 'test_owned_secret_files_deleted': ['ok-bootstrap-password'], 'private_directory_absent': True, 'image_removed': False, 'unrelated_resources_changed': False}, 'RESTRICTED_CLEANUP_ABSENCE')
    _same(report['host_secret_cleanup'], {'deleted': ['ok-bootstrap-password'], 'private_directory_absent': True}, 'RESTRICTED_SECRET_CLEANUP')
    _same(report['sanitization'], {'files_scanned': 30, 'actual_password_values_found': False, 'unrestricted_subprocess_output_persisted': False, 'raw_context_handles_persisted': False, 'coordinator_evidence_uses_reviewed_allowlist': True}, 'RESTRICTED_SANITIZATION')


def validate_claim(case_id, assertion_id, status, execution, root, json_pointer=None):
    """Validate one approved exact claim and its mandatory structured reference.

    PARTIAL records exercised subsets while leaving omitted criteria unfinished.
    The caller alone aggregates cases after validating every mandatory assertion;
    unsupported assertions and whole-case labels are refused before file reads.
    """
    try:
        _need(all(type(v) is str for v in (case_id, assertion_id, status)), 'RESTRICTED_CLAIM_FIELDS')
        key = (case_id, assertion_id)
        _need(CLAIMS.get(key) == status, 'RESTRICTED_CLAIM_NOT_SUPPORTED')
        _same(json_pointer, POINTERS[key], 'RESTRICTED_PROOF_POINTER')
        _need(type(execution) is dict and execution.get('actual_result') == RESULT, 'RESTRICTED_RECORD_KIND')
        _need(set(execution) == RECORD_FIELDS, 'RESTRICTED_RECORD_FIELDS')
        _same(execution['actual_steps'], STEPS, 'RESTRICTED_STEPS')
        _same(execution['unexpected'], [], 'RESTRICTED_UNEXPECTED')
        base = Path(root).resolve(strict=True)
        _inventory(base, key)
        report = execution['sanitized_report']
        _need(type(report) is dict and report.get('status') == RESULT, 'RESTRICTED_REPORT_KIND')
        _same(report['steps'], STEPS, 'RESTRICTED_STEPS')
        _same(report['unexpected'], [], 'RESTRICTED_UNEXPECTED')
        _same(report['limits'], {'posture': 'D', '451_register': 'NOT_PROMOTED', '94_selection': 'NOT_PROMOTED', 'hosted_changes': False, 'migration_adoption': False, 'worker_loop': False, 'production_readiness': False}, 'RESTRICTED_SCOPE_HOLD')
        assets = _assets(base, execution)
        _same(assets['evidence/run-evidence.json'], report, 'RESTRICTED_RETAINED_REPORT_BINDING')
        _source(base, execution, report, assets)
        _native(report, assets)
        _installation(report)
        documents, packets = _components(base, report, assets)
        application = (base / 'review-output/foundation-application.review.sql').read_bytes().decode('utf8')
        _same(_hash(application.encode('utf8')), SQL, 'RESTRICTED_SQL_IDENTITY')
        binder_hash = '9583ab7231a98780ac8d8160394fb8bc8185c4f3208dd4af62b43a6425079009'
        _customer(documents['customer'], packets['customer'], application)
        _worker(documents['worker'], packets['worker'], binder_hash)
        _context(documents['context'], packets['context'], binder_hash)
        _unique(documents['unique'], packets['unique'])
        _cleanup(report)
        _same(execution['safe_raw_report_sha256'], REPORT_SHA, 'RESTRICTED_RETAINED_REPORT_HASH')
        _same(_hash((json.dumps(report, indent=2) + '\n').encode('utf8')), REPORT_SHA, 'RESTRICTED_RETAINED_REPORT_HASH')
        _same(_hash(_json(execution).encode('utf8')), EXECUTION_CANONICAL_SHA, 'RESTRICTED_RETAINED_EXECUTION_HASH')
        return True
    except EvidenceFailure:
        raise
    except BaseException:
        raise EvidenceFailure('RESTRICTED_EVIDENCE_REJECTED') from None
