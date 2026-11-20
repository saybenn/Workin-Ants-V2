"""Pure qualification of exactly six independently audited local SQL SELECT assertions.

Reads only the literal closed graph. It never runs project source, a process,
SQL or a network operation. Results remain provisional until the final fresh
all-byte barrier; no cached mutable proof is exposed to callers.
"""
from pathlib import Path
from types import MappingProxyType
import collections
import hashlib
import json
import math
import os
import re
import stat

ARCHIVE='context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1'
DERIVED='context/reconciliation/local-f0-six-read-5f189aa-c662f807-qualified-evidence.json'
RECORD='context/reconciliation/local-f0-six-read-5f189aa-c662f807-execution.json'
BASE='context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807'
RUN='c662f807-c784-41ef-b937-ff2cce9bfd37'
COMMIT='5f189aa6262bd5ecbffda0940e404038993fce05'
TREE='fd736f36633b28267602759c0da0d368bd625ef6'
PACKET='3c5d2bccc05b994a761dd8db98714f315e7b10319b38bfb1f3aff0e68a50cef0'
NATIVE='a048478f5e834dc1686b558954ea9bdaeaba4278afcf63976510c114680f1fc6'
MODELS=('AgeGateAttempt', 'AgeGateBlock', 'AccessAuditLog', 'UserRole', 'AuditEvent', 'AuthProviderAccount')
PINS={'context/clusters/Moderation holds Audits and Ops/Audit Event Ledger Module/audit-event-ledger-module-architecture.md': 'c57324436ba0b155b62f0781443735c98882d62235c4949f520bbe62ea29f3ed',
 'context/clusters/identity, authority, & consent/Identity & Access module/identity-access-module-architecture.md': 'a99147effb732761118bb4959bfee4810239a88359660f68cea434e7f4609e52',
 'context/context-map.md': '91ae472067d5336f0b0bf6d73c4a9e86b235df85aa2634adec74e93bf6f0ad6d',
 'context/reconciliation/database-candidate-tests.json': 'bba9bef6b94e9f4974f2a3a0b19a3277df54ac04aa77ceaa6b70ffcf75d988b8',
 'context/reconciliation/foundation-sql-draft-access.json': 'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea',
 'context/reconciliation/foundation-sql-draft-models.json': 'd04bf44bd67dceda35199fd1ff1e494eed3016e80d180144018e879f5aee778d',
 'context/reconciliation/foundation-sql-scope-policy.json': 'a1c56896b12e15e03eb04bef6d5c9254692cdc3918167e024e54006b6fa38b1b',
 'context/reconciliation/foundation-sql-verifier-access.json': 'f84421c4957fcb4cf7fa5b04d3b5f804f8810ee58da2c1529e98daba8ab36bde',
 'context/reconciliation/local-f0-assertions.json': '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558',
 'context/reconciliation/local-f0-catalog-eb2aae6-2e4f5d40-execution.json': '76923eea9f3a68cb6157a0ed23432662492d79c068a7b58be507309edbe3e452',
 'context/reconciliation/local-f0-cli-diagnostics-validation.json': '8bf070ea0473fa41cd815737de96920f70ecf6896bf9188c52d90dbd42ed6e7b',
 'context/reconciliation/local-f0-migration-tooling-validation.json': '83d079ae068a04aee70c2d307ba7352a58a20409aef47df4f6a8866c25c2ce33',
 'context/reconciliation/local-f0-native-catalog-acl-correction.json': '017c9ee8c46de01c8a70ffbd68c0c80c27a1508cf4f1887fffaafcdba8d54f85',
 'context/reconciliation/local-f0-native-catalog-metadata-diagnostics.json': '5acadf4bbcc01b6133ebc0c81cb72e806a2c3d6f3840fd8f752353bde9c1735d',
 'context/reconciliation/local-f0-native-catalog-text-correction.json': '83766af0fc699b88a56081ccebd59eff59b6c850678506f6ffe67c3d04b38565',
 'context/reconciliation/local-f0-native-catalog-validation.json': 'cbc26b6d1935ced05a03b3d186658864cb687de6b49af888c92c551976279d75',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/check_local_f0_owner_read_operation_resource_mount_v2.py.txt': '1e35b2e9d9423af23b2c5d0f64dc0435c96c44719d3aac1db797e39de165c254',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/execute_local_f0_owner_read_20261119_resource_mount_v2.py.txt': 'b73dd1d9ecfec97edc9433e93cd4328298abe8af2e98cd24f943450ec6c24fb4',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/local_f0_owner_read_operation_steps_resource_mount_v2.py.txt': '85ac46ef87bfbd944b18fcc672e7543ab58917edcf3b27710047467c12f7313f',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/pin_local_f0_owner_read_plan_20261119_resource_mount_v2.py.txt': 'dcebd187aa643f39d0f2ed97286a3a1b3d0385fe7874581d4efbaf90a77ab3ad',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/prepare_local_f0_owner_read_plan_resource_mount_v2.py.txt': 'f3a81036574407c7fba91f1b22e29322cdb1464e53afbfc5057c12cbbb71bb1c',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/check_local_f0_owner_read_operation_safety_sql_v1.py.txt': '8425fb5f58cae333c40c85541321518871abcd33d6cf437f9d449f16d01c74ec',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/execute_local_f0_owner_read_20261119_safety_sql_v1.py.txt': '7d3dd946a950003ad93b9f58a152532d0332846e290d45753bb013da70dc594d',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/local_f0_owner_read_operation_steps_safety_sql_v1.py.txt': '85fe0992743806757cef39fac2a24d3b08166d741d60993209b1c5b033e4d935',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/pin_local_f0_owner_read_plan_20261119_safety_sql_v1.py.txt': '9dee0e646338b155c6a8805271b69b8b02e8932a1e7e57824002b9537ca6c6cc',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/prepare_local_f0_owner_read_plan_safety_sql_v1.py.txt': '21cdf556fde8adb92ecdfa8cbbb27ade7bc26281506af17679d10bbcbaba58d3',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/check_owner_safety_sql_v1_composed_20261119.py': '65e26d13330e2edf1ed84539239b5ddcbb1e186657f4720bf6a5ba74adb2a49d',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_helpers.py.txt': 'a3cf85cfd4802d9eb293fc957672b1ba7f842e49b6b15985cd81be6cbe1ee537',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_install_eligibility.py.txt': '7118431c80fc5954ba314f1ed3634d5f3398dc2b35749dff5360ee52162052e7',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_recipe_origins_20261119.json': '92d4eb01d78febbfdb13352aa08139471f0c0e8511f71dffdb4365ae7e388d99',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_root_source_review_20261119.json': '322044efdf4fdac96636c2275c1cbf6f1c038839b76378bb1525f9d4a9c67ae0',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/common_safety_sql_v3_independent_source_review_20261119.json': '99009f9a2f29f52db3815b113810dc00f2ad24a3370479105b21091227432d01',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/image-proof-independent-source.json': 'b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/owner_safety_sql_v1_independent_offline_probe_20261119.json': 'e1fc2c27f264e2950485e1e4c72b85951342a12b39caa65ee9bac3f6fdab0a2f',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/owner_safety_sql_v1_independent_source_review_20261119.json': '58a5a8c6eab9b586b7b1cbd78760d953cf219293f0faeb17532d75af5af985f8',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/owner_safety_sql_v1_root_source_review_20261119.json': '4829caff75e1dbe12c97aa83134e833f18711d60c55a1f7fe1b29e015399e0fd',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/source-author-results.json': '19e7662091dc2edbb9533aeb9f68191c95b851afc20678e73c4ac2881e6f0db3',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/accepted-owner-archive/reviews/validation-author-pending.json': '59fbde6aa157d496ff60b07ac5922c3e7a49fead82fdff1d97fb4407067aecbd',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/check_local_f0_owner_read_operation_safety_sql_v1.py.txt': '8425fb5f58cae333c40c85541321518871abcd33d6cf437f9d449f16d01c74ec',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/execute_local_f0_owner_read_20261119_safety_sql_v1.py.txt': '7d3dd946a950003ad93b9f58a152532d0332846e290d45753bb013da70dc594d',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/held-owner-entry-validation.json': 'fdbdff93256756681a492aadc1774441f84e526300bb1b98b56bdd2934ad0d97',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/historical-reviewed-owner-validation.json': '57c8e8dbb6624c71fc5146c200e82c23056f5b1874f8c46cd82424677d2b877e',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/immutable-top-files.json': 'e480c4d1057c33b070ee23130a398ce00a4394473a5d2ecbd26b3e405cad2cd9',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/local_f0_owner_read_operation_steps_safety_sql_v1.py.txt': '85fe0992743806757cef39fac2a24d3b08166d741d60993209b1c5b033e4d935',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/manifest.json': '927b14eb6abf7594d8ecbda9803eb99c45c8ceb0408e68676395d8a621cbb85c',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/pin_local_f0_owner_read_plan_20261119_safety_sql_v1.py.txt': '9dee0e646338b155c6a8805271b69b8b02e8932a1e7e57824002b9537ca6c6cc',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/preserved/prepare_local_f0_owner_read_plan_safety_sql_v1.py.txt': '21cdf556fde8adb92ecdfa8cbbb27ade7bc26281506af17679d10bbcbaba58d3',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/build_owner_resource_mount_v2_20261119.py.txt': '00629dbaf02587b9c50c213495d5956ff3d2e2917dd049bd4a56af09a7c2c494',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/check_owner_resource_mount_v2_safety_composed_20261119.py.txt': '33f383b3d1270748ca4db4dfecaa7b45061012b609ca81870d34b49b6e891e5c',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/image-proof-independent-source.json': 'b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_checks_additions.py.txt': '4c492123a7e9112bc1401004f81e239d6583604ecd4d02ade98a31a42a605705',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_independent_plan_review_20261119.json': '57169379194ddce270b9db37836c8acffe6880b7ac52415fa6134aff85512d3e',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_independent_source_review_20261119.json': 'c893926f6e9bbb42e247296ec8b3b5ce6418f60b79ba8a6b764c2c39bb4603ee',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_inspection.py.txt': '0e991c3d6a96688543042430b69a443704cdd8146b0ddba8038a4de22f81d8ff',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_preservation_audit_20261119.json': 'b8079924da39e7b91dc51ad5245ead6d9648a515533a6fcc85325feb9ae6bfa6',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_root_source_review_20261119.json': '488725cd28fd6e9855078248220e4eb8b1e7cf033051c0208427a5f5e8f747d2',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_source_author_review_20261119.json': '5716272c50487fc79977a83603239055067bfadbf5fe68aa7d71f01eb5baaa87',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_resource_mount_v2_source_plan_20261119.json': '7b9fa625958973c5d6a4db5ea05afcfd20c2149220ab331d9b0085c68df0ac92',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_safety_sql_v1_independent_source_review_20261119.json': '58a5a8c6eab9b586b7b1cbd78760d953cf219293f0faeb17532d75af5af985f8',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/owner_safety_sql_v1_root_source_review_20261119.json': '4829caff75e1dbe12c97aa83134e833f18711d60c55a1f7fe1b29e015399e0fd',
 'context/reconciliation/local-f0-operation-sources/owner-read-resource-mount-v2/reviews/validation-author-pending.json': 'e19dfc0d5e8bcd269750715aa7693e8b235f1c60a9a7da357027fec34b7fa77c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/check_local_f0_scoped_reads_owned_resource_v1_operation.py.txt': '6d69f6df83eee156605766d82683a29a5890b7436bac4428d890c28cca3b9aa9',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/execute_local_f0_scoped_reads_owned_resource_v1_20261119.py.txt': 'd35491a05064d58c05ec7437b16668554394854f0e7b3d7ee2675fbb963b64ec',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/local_f0_scoped_reads_owned_resource_v1_operation_steps.py.txt': '6cdbffd04fa950663ba94f40503b2d987284b57ff6ea0a8619f4a3c9eaa5bb71',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/pin_local_f0_scoped_reads_owned_resource_v1_plan_20261119.py.txt': '9f644efc10b9e5e68756d51e38c744e06404ac84fc0c4e36386c82c608c33bdd',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/prepare_local_f0_scoped_reads_owned_resource_v1_plan.py.txt': '009f41028bea52513e1050efce4662b3de9167818e1f95a1fffb4830e5e49ab0',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/check_local_f0_owner_read_operation_resource_mount_v2.py.txt': '1e35b2e9d9423af23b2c5d0f64dc0435c96c44719d3aac1db797e39de165c254',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/execute_local_f0_owner_read_20261119_resource_mount_v2.py.txt': 'b73dd1d9ecfec97edc9433e93cd4328298abe8af2e98cd24f943450ec6c24fb4',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/local_f0_owner_read_operation_steps_resource_mount_v2.py.txt': '85ac46ef87bfbd944b18fcc672e7543ab58917edcf3b27710047467c12f7313f',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/pin_local_f0_owner_read_plan_20261119_resource_mount_v2.py.txt': 'dcebd187aa643f39d0f2ed97286a3a1b3d0385fe7874581d4efbaf90a77ab3ad',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/prepare_local_f0_owner_read_plan_resource_mount_v2.py.txt': 'f3a81036574407c7fba91f1b22e29322cdb1464e53afbfc5057c12cbbb71bb1c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/check_local_f0_owner_read_operation_safety_sql_v1.py.txt': '8425fb5f58cae333c40c85541321518871abcd33d6cf437f9d449f16d01c74ec',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/execute_local_f0_owner_read_20261119_safety_sql_v1.py.txt': '7d3dd946a950003ad93b9f58a152532d0332846e290d45753bb013da70dc594d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/local_f0_owner_read_operation_steps_safety_sql_v1.py.txt': '85fe0992743806757cef39fac2a24d3b08166d741d60993209b1c5b033e4d935',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/pin_local_f0_owner_read_plan_20261119_safety_sql_v1.py.txt': '9dee0e646338b155c6a8805271b69b8b02e8932a1e7e57824002b9537ca6c6cc',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/prepare_local_f0_owner_read_plan_safety_sql_v1.py.txt': '21cdf556fde8adb92ecdfa8cbbb27ade7bc26281506af17679d10bbcbaba58d3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/check_owner_safety_sql_v1_composed_20261119.py': '65e26d13330e2edf1ed84539239b5ddcbb1e186657f4720bf6a5ba74adb2a49d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_helpers.py.txt': 'a3cf85cfd4802d9eb293fc957672b1ba7f842e49b6b15985cd81be6cbe1ee537',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_install_eligibility.py.txt': '7118431c80fc5954ba314f1ed3634d5f3398dc2b35749dff5360ee52162052e7',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_recipe_origins_20261119.json': '92d4eb01d78febbfdb13352aa08139471f0c0e8511f71dffdb4365ae7e388d99',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/common_safety_sql_v1_root_source_review_20261119.json': '322044efdf4fdac96636c2275c1cbf6f1c038839b76378bb1525f9d4a9c67ae0',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/common_safety_sql_v3_independent_source_review_20261119.json': '99009f9a2f29f52db3815b113810dc00f2ad24a3370479105b21091227432d01',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/image-proof-independent-source.json': 'b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/owner_safety_sql_v1_independent_offline_probe_20261119.json': 'e1fc2c27f264e2950485e1e4c72b85951342a12b39caa65ee9bac3f6fdab0a2f',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/owner_safety_sql_v1_independent_source_review_20261119.json': '58a5a8c6eab9b586b7b1cbd78760d953cf219293f0faeb17532d75af5af985f8',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/owner_safety_sql_v1_root_source_review_20261119.json': '4829caff75e1dbe12c97aa83134e833f18711d60c55a1f7fe1b29e015399e0fd',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/source-author-results.json': '19e7662091dc2edbb9533aeb9f68191c95b851afc20678e73c4ac2881e6f0db3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/accepted-owner-archive/reviews/validation-author-pending.json': '59fbde6aa157d496ff60b07ac5922c3e7a49fead82fdff1d97fb4407067aecbd',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/check_local_f0_owner_read_operation_safety_sql_v1.py.txt': '8425fb5f58cae333c40c85541321518871abcd33d6cf437f9d449f16d01c74ec',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/execute_local_f0_owner_read_20261119_safety_sql_v1.py.txt': '7d3dd946a950003ad93b9f58a152532d0332846e290d45753bb013da70dc594d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/held-owner-entry-validation.json': 'fdbdff93256756681a492aadc1774441f84e526300bb1b98b56bdd2934ad0d97',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/historical-reviewed-owner-validation.json': '57c8e8dbb6624c71fc5146c200e82c23056f5b1874f8c46cd82424677d2b877e',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/immutable-top-files.json': 'e480c4d1057c33b070ee23130a398ce00a4394473a5d2ecbd26b3e405cad2cd9',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/local_f0_owner_read_operation_steps_safety_sql_v1.py.txt': '85fe0992743806757cef39fac2a24d3b08166d741d60993209b1c5b033e4d935',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/manifest.json': '927b14eb6abf7594d8ecbda9803eb99c45c8ceb0408e68676395d8a621cbb85c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/pin_local_f0_owner_read_plan_20261119_safety_sql_v1.py.txt': '9dee0e646338b155c6a8805271b69b8b02e8932a1e7e57824002b9537ca6c6cc',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/preserved/prepare_local_f0_owner_read_plan_safety_sql_v1.py.txt': '21cdf556fde8adb92ecdfa8cbbb27ade7bc26281506af17679d10bbcbaba58d3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/build_owner_resource_mount_v2_20261119.py.txt': '00629dbaf02587b9c50c213495d5956ff3d2e2917dd049bd4a56af09a7c2c494',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/check_owner_resource_mount_v2_safety_composed_20261119.py.txt': '33f383b3d1270748ca4db4dfecaa7b45061012b609ca81870d34b49b6e891e5c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/image-proof-independent-source.json': 'b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_checks_additions.py.txt': '4c492123a7e9112bc1401004f81e239d6583604ecd4d02ade98a31a42a605705',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_independent_plan_review_20261119.json': '57169379194ddce270b9db37836c8acffe6880b7ac52415fa6134aff85512d3e',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_independent_source_review_20261119.json': 'c893926f6e9bbb42e247296ec8b3b5ce6418f60b79ba8a6b764c2c39bb4603ee',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_inspection.py.txt': '0e991c3d6a96688543042430b69a443704cdd8146b0ddba8038a4de22f81d8ff',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_preservation_audit_20261119.json': 'b8079924da39e7b91dc51ad5245ead6d9648a515533a6fcc85325feb9ae6bfa6',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_root_source_review_20261119.json': '488725cd28fd6e9855078248220e4eb8b1e7cf033051c0208427a5f5e8f747d2',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_source_author_review_20261119.json': '5716272c50487fc79977a83603239055067bfadbf5fe68aa7d71f01eb5baaa87',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_resource_mount_v2_source_plan_20261119.json': '7b9fa625958973c5d6a4db5ea05afcfd20c2149220ab331d9b0085c68df0ac92',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_safety_sql_v1_independent_source_review_20261119.json': '58a5a8c6eab9b586b7b1cbd78760d953cf219293f0faeb17532d75af5af985f8',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/owner_safety_sql_v1_root_source_review_20261119.json': '4829caff75e1dbe12c97aa83134e833f18711d60c55a1f7fe1b29e015399e0fd',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/owner-basis/reviews/validation-author-pending.json': 'e19dfc0d5e8bcd269750715aa7693e8b235f1c60a9a7da357027fec34b7fa77c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/author-frozen-review-request.json': '6135887c536aeb3d849caf96209dbc6a2c935d205d4a021a086a058a0587acf4',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/author-restoration-validation.json': '388739f7ac9fee7e3c6277bd0a672cf54a249593ff1468a527332063f81670ee',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/independent-review-before-explicit-artifact-inventory.json': 'f7ae11a73b3276400b210c8d38b5e76244615bc8c89282744b9913b776b11551',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/independent-root-source-review.json': 'ae37a4f11b55971de2835205019a0fe60492c2dac7f45e9abfcae50f7fdd1249',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/sources/check-scoped-read-companion-coordinator.py.txt': '9df73c6b62d6b407ec127bc4fef1762d72d314dc951c555a5e2edcc837a1b819',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/sources/check-scoped-read-companion-rehearsal.py.txt': '3d0d7fc3642f4b7ade6113e99057b7f7e2198b07a7f697572a03b128de5ea0e3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/sources/prepare-scoped-read-companion-rehearsal.py.txt': 'b0c4c3f971b4bd3962da5c677ff5242abaf4afab9558ac7736369c7e7652e94d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/sources/run-scoped-read-companion-rehearsal.py.txt': '4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/sources/scoped_read_companion_protocol.py.txt': '514327052c085a87348bfafc895baa321e631b32746090ca6ebe18652f10488f',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/preserved/sixread-basis/validation-before-explicit-artifact-inventory.json': 'fd700c05082208183e823cebc8dcccde6b456e570fb4ba25d2f3079faedb2026',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-actual-prepare-validate-metadata-correction.json': 'a6931a946ddf793edf66fddc808cac82d85c510be9e1b27f6b5bed63f87ed27c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-close-review-gate-metadata-helper.py.txt': '6726a18652569af9f98e5fa9997453bf5f8726236ba525771f0d77fbdc6cd30c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-offline-pin-stop-before-Git.json': 'cf3020b5890a69996636329cb3a1cf7c3324f132b936bde13c54428c2c69782b',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-owned-source-review.json': '21392ada43850d405745c169f2bb4c438fa2b2eeb2bc1f77d6546a9120f18300',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-review-gate-metadata-correction-helper.py.txt': '536203612d3d54512ba960e5c059fdabb710ad3f1b311b07de1e18b9bf840760',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-review-gate-metadata-correction.json': '72645c2cea8ff2d6e4cd97324189b127a46bbd673be5d153fddbdb120493f25c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-source-metadata-helper.py.txt': 'c895af30414070696b428ae9d58a4bb69b4b3edf1e199d86512575931a9b4180',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-validation-before-complete-gate-binding.json': '58d728cb15ec8ca6ffaad2533cd3c3e71ac4e113b52d0e3ff3aeb32efd67b931',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/Root-validation-before-metadata-review-attachment.json': '759ce7d31199f32a2b106c62487a1630fba4c52315138b071d2fabe8a7ba3c1f',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/accepted-owner-validation.json': '3f98020c74944b7c8c6705ec16239498cde03513dac6fa435a43263281ffac0b',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/accepted-sixread-validation.json': '6c4cb8155864984d12ae8985b66fea4402ca7329501d8b818975caa09e7db6dd',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/apply_six_read_owned_resource_v1_steps_20261119.py': 'e7d265224ce4f7ef511734ba759e825e24ef28e9267e590fb048a59ce45323c8',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/approved-metadata-Root-check-harness.py.txt': '34f1be754ddad90490e44abb7ca68fde6234b3285f35c3c5b18ee134405fe2ab',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/approved-metadata-Root-checks.json': '58fb7cc00f9b40384c50a77cb6c59fb19ea6e545893c382790d70dbecac16049',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/approved-metadata-Root-checks.log.txt': '7fd164fff446f03780e89b9ad9c2c1b98675cfe205bdd335fe4d040874ae95d5',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/approved-metadata-Root-record-helper.py.txt': '3a38ab8854b6a7f9d58dbd8e1fdca1281e800b01dbeb3e398215f53d694173be',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/audit_six_read_owned_resource_v1_source_20261119.py': 'ae1dcb3cc4e3fb61bb74e652d0f7795abefcb576a96ea0a36dda9aa72a873130',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/build_six_read_owned_resource_v1_20261119.py': '0972c9a4bf72a23579394b33d464a5c8867f3593e8458422d3a662540d130ad2',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/build_six_read_owned_resource_v1_checks_20261119.py': '6406aa76955c212101672cf0a5cb7df695ba086f88203516403529ded366b3e5',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/build_six_read_owned_resource_v1_safety_checks_20261119.py': '9b7a90360021e24bc5473e3373c30b6e67544a9f448f3d6437725b5490e5debf',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/check_six_read_owned_resource_v1_child_composed_20261119.py': '00c15cf95f59e85761280cb139cd6ce831c359c4bdd48a72b1ab647fe9ff6349',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/check_six_read_owned_resource_v1_safety_composed_20261119.py': 'a2ae340c2a7563ad3a1be64971292a11d21e79279c8555110c4f6d92a5d4e13c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/check_sixread_owned_resource_v1_final_graph_20261119.py': '83525566a2672247359f82fcb4a623fc13f49ad26d582307bbfb6d304fabef27',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/check_sixread_owned_resource_v1_full_composed_20261119.py': '267c2b5300f403b903a69d561ad463dcebecbd18d19100ee6d9c7e03e0c9c61d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/check_sixread_owned_resource_v1_preparer_pinner_20261119.py': 'a41f7b7b360e60fb34e3aecef4ff71f174db318e6f5fd30774f40d881775701c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/check_sixread_owned_resource_v1_source_admission_20261119.py': '968981e0dd51c96d77a6f976390d7a91bf7e32c82680e542c40ff27b5b708477',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/image-proof-independent-source.json': 'b628b6d98ad22ea7def4dd7a51264025c50bde116451ae516f3e52f55ba9542a',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/independent-offline-checks.json': 'd411c124fe2fd283eea8dd92e674124b7e3da055dfa9d5b844efd9f3730daba3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/independent-owned-source-review.json': '91f426c7cfbeedffee7c7eba173fb734ca82e09140e491b55d83938f34d0b4bc',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/independent-review-gate-metadata-closure.json': 'b6c8b9548557b2315da6901b2dafdb6e9a6dc6940c483e7dbc900c5a00016d90',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/historical-owner-execution-record.json': 'f9e20b2da4af9ec2bf9981f7ecd0fdca9392d91b8b242be75d72e54eadb7390b',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/ledger-evidence.json': 'e7ac11919f598c05700eee225c73b6ef2bda87a5aa3da0809ecf7351ce5e305e',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/ledger-registration.json': '49d09af0a41c5bcd51306b357fd2304c09e40e9f1f19c452d48c6c92b68859b2',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/lineage.json': 'f6e9aee63612cf107763ffd9dbd3bb23763038d8dd808110b8e10dff2ef0fd9d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/mock-fixtures/text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/run_sixread_owned_resource_v1_final_composed_20261119.py': '3427537093174a2113c331f717eedf987636155d755128e875e665933df7a85c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six-read-owned-resource-v1-source-plan-v2-20261119.json': '451316095be5ac6a32dcfdbfa947b217155d92714178d058a2a494b388155037',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_Root_source_implementation_ACK_20261119.json': '0fb6d5970309f66837b877e0b4c2c76e1b376ec2f41a00cd82b29b287a55091f',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_checks_additions_20261119.py.txt': 'fe475772f17ef58ef727f032a9dc5c73e0d5959f7e8d7086af98711e08761240',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_child_composed_author_report_20261119.json': '1ef0409b2e9a39de170d18fa766353ce8fa6122adcafed03fd1ff0124f63a8d2',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_child_composed_schema_v1_20261119.json': '2dc8f48c7f0c5cb10f170308ab1914f248a56cfb77aa1ed25285625f018bb73b',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_child_composed_trace_v1_20261119.json': 'de3a807a052c5a22fd9f55e502e174976fd8d4891121ccef388736290702c1b1',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_final_composed_author_probe_20261119.json': '1a6aa54011bde15100ea1d33cec6e6ef8ed94b34b78712fa54837bc09f740325',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_independent_plan_review_20261119.json': '2281b4a1c25385842173c23b7cd1f341ca27424b1c5ed80d2a2dc1675d12f577',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_parallel_preservation_20261119.json': '1ec9b1395a99416965438402b794ad5dea332d4f3ad0419782b85312828ca3f7',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_source_audit_20261119.json': '1339b6b6530ce4a604f2d6cd9b0c26942ec78218cfffb58b5b95cc91406c20ca',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/six_read_owned_resource_v1_steps_additions_20261119.py.txt': 'e22da4ea4b9d1091d56267d4515699347e9bb172d2039cbdd18d6c6901d19a79',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/sixread-owned-full-cli-first-pass-author-record-20261119.json': 'f867f285060e9f9beaef0003a78331c1461135cb9f5af33ed171ab99cf8c06dc',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/sixread-owned-full-composed-author-probe-35d59d27-20261119.json': '21d2db9d7d5be89e203b4bc378792bb5a545d35cfdaa1c070d40235546464399',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/sixread-owned-full-composed-author-probe-584deb7d-20261119.json': '8b19c89f1d13cb4cc6e7a8132da7fc1ce1cf354e66576376e80a3c9266f4a04b',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/sixread-owned-full-composition-capture2-20261119.json': '1af04b3ba5857fba8036d0078517a0eec957e1e101889ac7a7398cd0dba9aa9c',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/sixread-owned-full-composition-tool-data-projection-20261119.json': '115f1bffe3635b8002b21807b198662b871ae0edc4b16d3d30174d054824fb08',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/sixread-owned-resource-v1-coauthor-delivery-20261119.json': '4c59468f49b7190e2c01fb78c5ef21c9848b7fbd5616c1ddc4a7fab9d092cac3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/stage_six_read_owned_resource_v1_archive_20261119.py': '037b55af5d5699a103e6a425bce1bdb85d9f24ea45d4e184a08f5ea4629bef91',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/tighten_six_read_owned_resource_v1_20261119.py': 'cfc3e7cefe7c90d1a0f03870dddef8e5a717a26c559e030c36cf02d5072c0359',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-owned-resource-v1/reviews/validation-before-Root-review.json': 'a5eda74928625f91141b896097d06cbe3ff8f16549bd57fe1a2013b3c2086313',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/author-frozen-review-request.json': '6135887c536aeb3d849caf96209dbc6a2c935d205d4a021a086a058a0587acf4',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/author-restoration-validation.json': '388739f7ac9fee7e3c6277bd0a672cf54a249593ff1468a527332063f81670ee',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/independent-review-before-explicit-artifact-inventory.json': 'f7ae11a73b3276400b210c8d38b5e76244615bc8c89282744b9913b776b11551',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/independent-root-source-review.json': 'ae37a4f11b55971de2835205019a0fe60492c2dac7f45e9abfcae50f7fdd1249',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/sources/check-scoped-read-companion-coordinator.py.txt': '9df73c6b62d6b407ec127bc4fef1762d72d314dc951c555a5e2edcc837a1b819',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/sources/check-scoped-read-companion-rehearsal.py.txt': '3d0d7fc3642f4b7ade6113e99057b7f7e2198b07a7f697572a03b128de5ea0e3',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/sources/prepare-scoped-read-companion-rehearsal.py.txt': 'b0c4c3f971b4bd3962da5c677ff5242abaf4afab9558ac7736369c7e7652e94d',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/sources/run-scoped-read-companion-rehearsal.py.txt': '4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/sources/scoped_read_companion_protocol.py.txt': '514327052c085a87348bfafc895baa321e631b32746090ca6ebe18652f10488f',
 'context/reconciliation/local-f0-operation-sources/scoped-read-companion-source-v1/validation-before-explicit-artifact-inventory.json': 'fd700c05082208183e823cebc8dcccde6b456e570fb4ba25d2f3079faedb2026',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/Root-exact6-proposal.json': '60de534fae2be06a2c0a30dfb056e96b38af47feef96f6fb7749cca6d0f77e72',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/Root-proposal-audit-source.py.txt': '77a24c53adada501c3aa0c1c0a03880af3e601fadcc5889cf2d3bf53a4cf816e',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/independent-actual-audit-source.py.txt': 'c514901cce6d14ebfa8e5f2d1b6a9a3bf9527a07cd4df8e9adf61730d2fa4010',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/independent-actual-audit.json': '0bacaf1de96ed87f6f0c7c61b553b5c6d49b2d4c8ee879a682f9a56b0b4af4e6',
 'context/reconciliation/local-f0-owner-read-resource-mount-v2-source-validation.json': '3f98020c74944b7c8c6705ec16239498cde03513dac6fa435a43263281ffac0b',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/Root-independent-cleanup-helper.py.txt': '6528bec352518babab8a6947a66912eae4fc126590ad1ff7b32ae40a2305ce82',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/Root-literal-approval.json': '2beaebc45a96006205e9d36f19488aacbc7f84660f055d011efe35f8bcc6d4e3',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/audit/Root-observed-unadmitted-results.json': '97002a99ea3934ddd7794ac3d291266fd1c898d7433a8439dd956a797c3b25bc',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/audit/preservation-helper.py.txt': '4a036d909fda8391a00674392e38aef3145a53b4210d872bdb4740f98f0b76a8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/ledger-evidence.json': '5ca1352b53d2400b3d47bc375acd936d2620b5377f73e44e9c83be8e245c5c0e',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/ledger-registration.json': '65bf8ffccdb04a8acc86efe4b8284b970b8603fb80099e4f76fe05f87e7781e6',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/native-after-ledger.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/native-after-oracle.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-ledger-evidence.json': '5ca1352b53d2400b3d47bc375acd936d2620b5377f73e44e9c83be8e245c5c0e',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-native-after-ledger.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-native-after-oracle.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-state-after.json': 'be37aa9e3b557ec4048b75db3f4665282c621e299e2481900a3b7f06605057b6',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/post-state-before.json': 'be37aa9e3b557ec4048b75db3f4665282c621e299e2481900a3b7f06605057b6',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/run-evidence.json': '87305f5dd4bc87de248c7ae999bfb1dc218a29a7fd0e6c45e03db1eb1fa649f3',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/scoped-read-component-result.json': '0f708f55935f5e710b6836841ed207d3fa83107f1fa020b22b095290a9efe1dd',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/scoped-read-component/scoped-read-companion-results.json': '0da12d353efc4ae71474cb2f9637ce0870ea0813e456637d22fc8861e45b7dde',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/scoped-read-native-attestation.json': '4fb109053610a3e5edae4559ce82eb81dc20312bf78f476d2cedd0dfa9c5d3e7',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/scoped-read-run-plan.json': '4551a22df568d14d522e6c7b89d3e072bb6c46a31ae1d94e105480b8c27a0452',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/set-private-acl.ps1.txt': 'd5ef58e51c12b4371601557f027a44e9ca206b81444724f8aab65365bf9c057f',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/evidence/text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/independent-cleanup.json': 'f01e5406fa4be4f02539b35cecc5f608ee3f61bfd36452f4aa7fec20f7e37405',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/independent-literal-review-bundle.json': 'ce0fec6879ce9b1022a9ef2d6ad5a3f3db67dace60be2b6fdd5a2f1fabdbb1ac',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/independent-literal-review.json': '6a8e36f5c2f43313766af6e1f8ddd166174ce5784ca2fb03389a084e12ea3ae4',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/manifest/migration-ok.json': 'b4d90b7d84bbb28b2bb96da36ac87e49d08b26b91c3462a652e71c9d5a4ca4fd',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/manifest/ok-migration-manifest.json': 'b4d90b7d84bbb28b2bb96da36ac87e49d08b26b91c3462a652e71c9d5a4ca4fd',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/manifest/operation-manifest-before-operational-review.json': 'e856ea94dab5c92288425354417018f4defc21eaee0b8300b99187c28436ec73',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/manifest/operation-manifest-before-source-pin.json': '71274f9397a91b32a662049d9f856e25d7e5913d448939d4fef447496db0df56',
 'context/reconciliation/local-f0-run-assets/5f189aa-six-c662f807/manifest/operation-manifest.json': 'b9500e3827dd3261ea4c4cfad3eb8a371cae2f73d3e71251aa2175e3dba3e689',
 'context/reconciliation/local-f0-run-assets/eb2aae6-native-catalog-2e4f5d40/source-prefix-analysis.json': 'b3931b71fe3d0560d6864ce20aa64cc88086563c4399a34e4b442ed108c4fc4d',
 'context/reconciliation/local-f0-scoped-read-companion-owned-resource-v1-source-validation.json': '7b25a40fd92e2d875fa85a2b65a2193f95bdcbc7dab2636b9bdbdc33d60e403e',
 'context/reconciliation/local-f0-scoped-read-companion-source-validation.json': '6c4cb8155864984d12ae8985b66fea4402ca7329501d8b818975caa09e7db6dd',
 'context/reconciliation/local-f0-server-diagnostics-validation.json': '560504eea761a06864edea01fba42e2e2a9a086ecfaab583309868f8f2f9c027',
 'context/reconciliation/local-f0-six-read-5f189aa-c662f807-execution.json': 'acac8f669272f99e2903adad529366b0e156b18fe39de8c90982e921ffc1b7f8',
 'context/reconciliation/local-f0-six-read-5f189aa-c662f807-qualified-evidence.json': '07b49506e56918515816949e628569f89ba12066d2b7ecc2ecf60977bf92fe7f',
 'context/reconciliation/local-f0-tooling/linux-tooling-manifest.json': 'e8fcce8f3ed4eaad0f7834e908166a0947b997e75513d589078f0d79c9a940d0',
 'context/reconciliation/local-f0-tooling/prisma-tools-closure.json': '610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b',
 'context/shared/contracts/SH-003.md': '493a3524f33224cfd774192535789ad95cb04c56e1e0e15a11ae5e067c7bf1b2',
 'contracts/shared/SH-003.v1.schema.json': '3a56484bfb5362977b0d373d4d245582eda71dfaa819e53d319b6e50c2447e1f',
 'contracts/shared/types.v1.schema.json': '606d2f772bedf96ae59e82995831e741435dc573fdca477c8e735b5a63c30cf2',
 'prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'prisma/foundation/history-manifest.json': '7b7d385b978f43d06ad519be34c00144ae6b3101f92ce6032dc32202353f971e',
 'prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'prisma/review/physical-candidate.prisma': '4be26783cd127f82163bb31a9e180549e32c1ba97ebd40e55c0c3adfdae9c8cb',
 'review-output/first-rehearsal/diagnostic-identifiers.json': '204b7c9f5888fd253c338286cc5446e1a346fb02073930124ccaf097f6bd9bb2',
 'review-output/first-rehearsal/fixtures.json': 'df00d519f11cd0a443dba906d724216d0e9d4f16f3ccbd9a703f9d02d0f3b3be',
 'review-output/first-rehearsal/fixtures.sql': 'bf637caeba37917457e5fd478241bc63a5416e47cee4b2275106f8e8ebe5cdbe',
 'review-output/first-rehearsal/missing-outbox-observe.sql': '98ce1d902133e1466e620379b3afef4d282b69b91e22e495af21fd9874c21d68',
 'review-output/first-rehearsal/missing-outbox.sql': '94fd0787e51cdcc3c47834d3a35f5294e0b9bcdb0cf6ca90c8db993d7e6116c0',
 'review-output/first-rehearsal/positive-observe.sql': '7541fb01e3f4ce3c50d61788e0a625a7fae140823ab81054d34a867541546487',
 'review-output/first-rehearsal/positive.sql': '1641b0501892abc2c64e95d2a80bc94e9f9ed3b109976a0e4abd1599980a4405',
 'review-output/first-rehearsal/wrong-person-observe.sql': 'ba36174fd70332ac0fbf896c3ba82f0396afa07a14cffd1f2f9546ea90db9611',
 'review-output/first-rehearsal/wrong-person.sql': 'e9c7e17816bc17bf714a28ae0a215f09632ab5809c52117649d5c7748e1a2d42',
 'review-output/foundation-application.review.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'review-output/foundation-bootstrap-finalize.review.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'review-output/foundation-bootstrap.review.sql': '05c7d98aac1a13158ac2e6a28dcf7b377de8e1c881f347155421e5dd24e39893',
 'review-output/foundation-structure.sql': 'ccc737d7483070b00715dc8cf7e08cef4722f43d9ebad70aa90dcdaefcf973ae',
 'review-output/native-catalog/README.md': '89e82bb70f53d6e959109c1e249bb4dda0101d22470d68211715baf5b1c74388',
 'review-output/native-catalog/expected.json': '9ad2129c9b7b7b5fd99f2088ae94215326f6ccbf40550945694c44538d8d0976',
 'review-output/native-catalog/expression-oracle-plan.json': 'cce4b19c1931472841de2fec2662fa4b002278b275341815782078689a1af36f',
 'review-output/native-catalog/expression-oracle.sql': '74d585741e1e097ac0614621b86c7ec97673697eb7dde344023e1dbe0ca613d2',
 'review-output/native-catalog/public-schema-registration.json': 'f0a46eef94da5f4836f46e64fe3a1c11a700fc158d40e36381e30bbdc0ec28d3',
 'review-output/native-catalog/source-pins.json': 'a0e9c36eecf61b1d4ce717744c29f4b72424ecd8d9db5ce0519b6bdaf9f58d00',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-cross-model-complete-caps.sql': 'e4d5fbf59e749bb35f6067f098d02ceebaa37df253a5cc389863d2b0d6f55fcf',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-missing-createdAt.sql': 'a3b8bd72e4b50894e09b17e18a3bc805b2d82c777ba6606eceeb59965acc8d96',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-missing-mutationTransactionId.sql': '3c1b180b90b80b73225f24ef791f4750dae2c5dffc74a99fb0b15db5e156e80b',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-missing-primary-field.sql': '65710bb1147275122d4444a0d7bf765b340d13f413165ea0acc589c195201cdc',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-other-existing-root.sql': 'cc93039d617a444f9edad35fafb5556f42f305e1cfac2093568fec7611994127',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-positive-root.sql': 'dc13f1ea3f93394ad9fbbc02c6ea88c25008334abb4dda3c26cac8dd06084035',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-principal-generation-mismatch.sql': '88a4ff04ea13215533d35a85f580837bcd3c9e12cf8e919c95df3b9369ab3860',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-principalB-current-control.sql': '5d1c4dbb21bddf666d393289695d5f916232d4718de073294b0ff504fe8fc2e9',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-wrong-action.sql': 'daa91a15784ce3508bf0feb5f885dfa354e67f3c22760499780e5b6fb71b8399',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-wrong-owner.sql': 'e54654ab3b1307a59d149f78a9df526aef78db5576494fd473ff90f0cfeac093',
 'review-output/scoped-read-companion-rehearsal/accessauditlog-wrong-purpose.sql': '2dcf76727c624b86bf856708e82612489e8fb31b21ce9964bd244761f1e60270',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-cross-model-complete-caps.sql': 'cdbd8c5983b2bbde0a390932002e037ed58b3feee3c973a77eafc5038f0568c7',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-missing-createdAt.sql': '9785b0f3f624ce5e837be6b65b53f591f17bfc21a1125eb457d97d4044736ad2',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-missing-mutationTransactionId.sql': 'c368378d3003cf9241a285c5cc534b31a0a736eb397d55fdf551896270a1079d',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-missing-primary-field.sql': 'e5e11c1088986248c070072b164edd976a175218beac149c8be31a2d465432f1',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-other-existing-root.sql': '2325f4aaa4856f436378c927f4af5cd95d7278519f2816a0243990116696c818',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-positive-root.sql': 'db23f506fe8cf84a127040032d9ac9cae0347235562079edd5ff9ef25b2a433e',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-principal-generation-mismatch.sql': 'd2c888caf0c6ac686e8168e39b4f20c58596a71929d308c2ac83ec568517932e',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-principalB-current-control.sql': 'b7101be05137a87a74e9c2d23dce452f412da1c24dc115282b9a42eb262c093b',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-wrong-action.sql': 'efde2ec18bcbe75e570654cfc2e7d87b7c807d513530d9a80c80cab8531b8120',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-wrong-owner.sql': 'a069eaa679fd710a818b11b10ea27e216d0f7d9ff539b9e64710bce32c1df294',
 'review-output/scoped-read-companion-rehearsal/agegateattempt-wrong-purpose.sql': 'eeee6272e072e56b66a29315becc6ad9ad20f7391131835438bb1bc09bf81ed5',
 'review-output/scoped-read-companion-rehearsal/agegateblock-cross-model-complete-caps.sql': '24c4af584c1cdccbc9501ebb487e33a97a4658aa12c7a9e159548ec1dbf32cd2',
 'review-output/scoped-read-companion-rehearsal/agegateblock-missing-createdAt.sql': 'ee889b4a8a23a23fa2a60986eedb707b8385e992d0797ae83498b4b3c4fb6c6e',
 'review-output/scoped-read-companion-rehearsal/agegateblock-missing-mutationTransactionId.sql': '490cef26476c4a99fc8d78f8f2300d4e7fe3919c43fcc1c43f47d21e848a3e70',
 'review-output/scoped-read-companion-rehearsal/agegateblock-missing-primary-field.sql': '7722a4e6ca026c2586d9b509e21b260dfb6835a31fff4dd3a3ee000bb0d279df',
 'review-output/scoped-read-companion-rehearsal/agegateblock-other-existing-root.sql': 'a80fa704fd803ea47d1ff21ef8cbc8fe39f959a08e5805c2ac8693c7c6fc84cf',
 'review-output/scoped-read-companion-rehearsal/agegateblock-positive-root.sql': 'f80b12252a846f7b7038b9c7899cb4699ac7501abe863dc1681e891597206112',
 'review-output/scoped-read-companion-rehearsal/agegateblock-principal-generation-mismatch.sql': '2f7c18cdf040a3c354768d2729c28707a08739c2d3b2d950ce014246014c40c7',
 'review-output/scoped-read-companion-rehearsal/agegateblock-principalB-current-control.sql': '4704ecd8440bda33ed3e33f007f747b70a8a75af8a1bbdc77947d90f7da42392',
 'review-output/scoped-read-companion-rehearsal/agegateblock-wrong-action.sql': 'f21993f5142dba3839f89d032ae2d817714da79b42271c845e901049415c35de',
 'review-output/scoped-read-companion-rehearsal/agegateblock-wrong-owner.sql': '47b9f700801420a768da5a63f70cb41f00fa5ce6dd1a2a1a59ca8543cb1ddec6',
 'review-output/scoped-read-companion-rehearsal/agegateblock-wrong-purpose.sql': 'b720a7247e7764acb90591b7d1f41b039b01ff786732978d7da44036321984c1',
 'review-output/scoped-read-companion-rehearsal/auditevent-cross-model-complete-caps.sql': 'eeb596434f33be9498f53ea8df100b9837966ed819a0a20393be5ce42b48c6df',
 'review-output/scoped-read-companion-rehearsal/auditevent-missing-createdAt.sql': '01f5b8e7dc8381b02d1ee26583340dbc89439d0497fa43819de207f96b762d78',
 'review-output/scoped-read-companion-rehearsal/auditevent-missing-mutationTransactionId.sql': '3dc8f7a05e3846a09f041417844cc33b36117c1ff1e0ae36de365484a408ffe5',
 'review-output/scoped-read-companion-rehearsal/auditevent-missing-primary-field.sql': 'c1773627bde615a5cc9ac45b976035e4998c65ec095fdc0e44c211867ceaa515',
 'review-output/scoped-read-companion-rehearsal/auditevent-other-existing-root.sql': '033a04f92604253bbe7cbc3ee58fad80dab82b1d8ddd62494eb63e63eee58c76',
 'review-output/scoped-read-companion-rehearsal/auditevent-positive-root.sql': '30d5edb7e6df7402f1b50acb8b90473ca9dbddf4ef07efd1d1b917d08e7205aa',
 'review-output/scoped-read-companion-rehearsal/auditevent-principal-generation-mismatch.sql': '8c1b5e0578863a4ac91dfc2fbe2a4045195c85e73f1c3e958f26b105f85cd7a8',
 'review-output/scoped-read-companion-rehearsal/auditevent-principalB-current-control.sql': '755847692bc374f3f195df74e3abec43021b5e9dad0b561aa953805b5364fb09',
 'review-output/scoped-read-companion-rehearsal/auditevent-wrong-action.sql': 'b67f76581990dda7d520ac35639e87d43a70f2b1ced3ff65af7169cad6309aa3',
 'review-output/scoped-read-companion-rehearsal/auditevent-wrong-owner.sql': '9fd6db9f8fe347d331d16f2dd6c99fe5b9d509ec565fd764e99f3adc1c8541e8',
 'review-output/scoped-read-companion-rehearsal/auditevent-wrong-purpose.sql': 'a497fd4210c14d08a357632540e298ff9ce733396429b467c5ff69b97253d378',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-cross-model-complete-caps.sql': 'd953ff9f2d1aa5f3d41d1a42c22adb15882f9aac56a99c9b3c6e554431ce75a2',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-missing-createdAt.sql': '9ca8cb34da783095b3800136935b61a13e1fb6fe30cc81d8962c38889492c2b2',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-missing-mutationTransactionId.sql': '93a4a2b3efe13daf6ca8f2cc0620afed68bd69ecef024d6e048ca5383f4fcbef',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-missing-primary-field.sql': '6cb351756a68ae82d96795c2ebc8075341631d91701d1de32fa944b80d03083b',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-missing-revision-capability.sql': 'fec6e0dbefafb11b573b93686303e44a7b6f4768834e9d7b0c9e9a6436df1697',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-other-existing-root.sql': '8705e4c41dd79d1dbd42e96b3751310443dbeb5b40808ddac77424216a14ffa7',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-positive-root.sql': 'c05eb2e66103cc7cacd0bb3116cc2186ab9c07f985e412c53126d15b1cf97cd1',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-principal-generation-mismatch.sql': '178bab810426d829f431bba6ec3a597d45aee2d1b3abac916a54bc11c4736c8a',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-principalB-current-control.sql': '266681c76adee9157e40a2c2db48e152f8cf25157034b84a77b6bbf4e09bb42e',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-wrong-action.sql': 'd65dde6503d4060ac3abf9adf892ec0590e5eee0b73ce7febcaf449c8d45f165',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-wrong-owner.sql': 'd4afc5a1d82e382e598e05e500e296fa86a6d87e5e1070f59d4d1ee42ea6d484',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-wrong-purpose.sql': '9ebc026d35f683f181f9b0d859994ebaeb61770403fd05947464c6a978c42bc7',
 'review-output/scoped-read-companion-rehearsal/authprovideraccount-wrong-source-generation.sql': '9b4723fae0abe1d6eae6f6e4dabb68fdad38f9f69f1caa64871ae75e1d0b6fdd',
 'review-output/scoped-read-companion-rehearsal/complete-state-observe.sql': 'a9250848d105577e4eeda0c68cddd158196186ffa5a1d6c2dfbf5f9f82e7e0ac',
 'review-output/scoped-read-companion-rehearsal/exact-owner-trigger-restore.sql': '066acde0ea13fb9a8e270de2d7149561acee54bb813dff7a18937cfa5580b770',
 'review-output/scoped-read-companion-rehearsal/exact-trigger-observe.sql': '75d45ab441eff77001b858dd1f102cffe328251ab90dae875df986cb5d081477',
 'review-output/scoped-read-companion-rehearsal/existing-scoped-read-fixtures.sql': '380d082367bc74b234a5bf7b99f7e16d16c2563d6e7f3400567457ca6dc86705',
 'review-output/scoped-read-companion-rehearsal/fixture-coherence-observe.sql': '85fbbf4e40f1c8b70bb8b510f0a8f4c808a02ce739a0b35f875c9266de18367b',
 'review-output/scoped-read-companion-rehearsal/fixtures.json': '7f5bd6e713a1f0eaf330c2acf0267cd45aa2e8f47467e03d6f4c4c6dc754420c',
 'review-output/scoped-read-companion-rehearsal/userrole-cross-model-complete-caps.sql': '4a8d4970ffdf27bed0d1582d1d515de41deb61a27803f95b36ce7e1c0bdcb102',
 'review-output/scoped-read-companion-rehearsal/userrole-missing-createdAt.sql': 'dedc00593d8d4d06ea5fdf33d5dfeb29d0f8afdf4b26380518f5d44e5ecd22e4',
 'review-output/scoped-read-companion-rehearsal/userrole-missing-mutationTransactionId.sql': '319e29f78e3652ae45244f079d029da013e952cdfe24ae507e1801d48181c829',
 'review-output/scoped-read-companion-rehearsal/userrole-missing-primary-field.sql': '85d65a340ca0e4efe42e4de84fff5536a54344784c831c37d9742d3308e94b4f',
 'review-output/scoped-read-companion-rehearsal/userrole-missing-revision-capability.sql': '1f8ef52ae1b3af410a4dd143f0cc65a6b83aa519a3cb9ded91aba446a08a025f',
 'review-output/scoped-read-companion-rehearsal/userrole-other-existing-root.sql': '32aac2c374129d677170d5df04b100e4579e04cb0c85c4e9528ae5a08f14a483',
 'review-output/scoped-read-companion-rehearsal/userrole-positive-root.sql': 'fd7391766ceed9712ec00541e2bf95a88f6bd3eb250aaf4848727582b91bf981',
 'review-output/scoped-read-companion-rehearsal/userrole-principal-generation-mismatch.sql': '47e7478466729b1fa7ee7069187b3f0c1f5402e1f8466c19632a4d836f57534a',
 'review-output/scoped-read-companion-rehearsal/userrole-principalB-current-control.sql': 'bbe7a6134b15b557f15b1fa679e17b2df29d532a44ecc16639ded1112d99fc4a',
 'review-output/scoped-read-companion-rehearsal/userrole-wrong-action.sql': '553a312ece8c07c891c5ef7567c9cc5ec27d3b67e3dd804faa72e5cea366ae76',
 'review-output/scoped-read-companion-rehearsal/userrole-wrong-composite-target.sql': '9c58701506ef465172f37ef0b38a9cbbd13336a1a2727dcd2ec52565d6a8c450',
 'review-output/scoped-read-companion-rehearsal/userrole-wrong-owner.sql': '8cd6a6cc3e1c190ce81ba1e470602061744ac2e8cfd1762908f99e8a91fa0fa4',
 'review-output/scoped-read-companion-rehearsal/userrole-wrong-purpose.sql': '00dde4421724c02db1d2d2cd9b5e2b488f090288157dd0bc083557ee43ec512e',
 'review-output/scoped-read-companion-rehearsal/userrole-wrong-source-generation.sql': 'c8f640a8639ff65e61554e4a7274d45d35b44121fc3d2971822bcef1cea17b78',
 'scripts/assemble-foundation-sql-review.py': '136489b5fb966085020128bfbd7140dad5e0b340a2312319d346305311fc212f',
 'scripts/check-first-rehearsal-mocks.py': '777d9d74788c37c9b20891196180708400e4f58991026075e60bb6bc74a96adf',
 'scripts/check-local-f0-migrate.py': '59d890c145e1f14a62e296fba0139eaa22ab728b70fa76a7dbd7dc3883222a14',
 'scripts/check-migration-server-diagnostics.py': 'cb3ded2eaf6c1532691a41af241897b11072907c37aaeb2d3f2f1478da157163',
 'scripts/check-native-catalog-review.py': '05d39953bd26c61ef7d414a53bb5c0bc65cb2e59ec8513e17230ad5f7e4ef859',
 'scripts/check-scoped-read-companion-coordinator.py': '9df73c6b62d6b407ec127bc4fef1762d72d314dc951c555a5e2edcc837a1b819',
 'scripts/check-scoped-read-companion-rehearsal.py': '3d0d7fc3642f4b7ade6113e99057b7f7e2198b07a7f697572a03b128de5ea0e3',
 'scripts/check-trigger-row-shapes.py': '7e6c851630a65c9e07685138e03eca5d4fd5404e8a4bb2b36895e34069d52ce9',
 'scripts/database-candidate-correction-rules.py': '6b79a14ffa77c450c3864ba5e2d930d61d5a427a6b0c11545e1afdd37ccaabb3',
 'scripts/prepare-database-candidate-review-assets.py': 'dcb1544afc39cffbd9a8b052749f544c7531ff3dee2ff9cc738fd38d8d3bc9ed',
 'scripts/prepare-first-rehearsal.py': 'b03f4b7fda4e60ff7bafc2b6a7463d7bb9a3ee7bffc9f4e6c8f840f99b4116ce',
 'scripts/prepare-local-f0-history.py': '33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8',
 'scripts/prepare-native-catalog-review.py': 'cef4f4f191e478593a679e9b86c7eee410531b01501a896c0b6f0e1bc1ac4fa2',
 'scripts/prepare-rehearsal-diagnostics.py': '598bc556999a16f303171003324be8763cb00a0fff2bb54de8a1195e1e7c852b',
 'scripts/prepare-scoped-read-companion-rehearsal.py': 'b0c4c3f971b4bd3962da5c677ff5242abaf4afab9558ac7736369c7e7652e94d',
 'scripts/scoped_read_companion_protocol.py': '514327052c085a87348bfafc895baa321e631b32746090ca6ebe18652f10488f',
 'scripts/sql-review/catalog-acl-preflight.sql': '7018c8f415923533dc461b212a0df0f9a0f4144457e410c4505c9322df4647f4',
 'scripts/sql-review/catalog-text-preflight.sql': 'f1cab9adf94fe5aa2452f34213eea43cf4ecfe35c9ce5f5289486b7d4f859823',
 'scripts/sql-review/catalog_expression_oracle.py': 'c5034cc982a5523e42cd721214cbca5820980fafd2c233f83f7706fcee826dfc',
 'scripts/sql-review/catalog_manifest.py': '1f1deb607dd2b2b4583cabeeae6be3205964d8a5ad897fe7bb1003699bfc9c16',
 'scripts/sql-review/check-local-f0-migrate-guard.mjs': 'bf7c166a23eaf29ed2ac084def03115e30d308439566d2f29af10d5fd22496cc',
 'scripts/sql-review/collect_native_catalog.sql': '9313c892ae3e5ade97167aa1818ed4b371d04b835ac736be7c13c3206bc85b3f',
 'scripts/sql-review/collect_prisma_ledger.sql': '6dfa02fa375da4a126b996fc547dfff063c61b41c854db6b07ea62f52d63286b',
 'scripts/sql-review/compare_native_catalog.py': '20441930b769d93eb00d762861018878d18d8c0f64194d65c468f0e320c204f6',
 'scripts/sql-review/fixtures/postgres-17.11-approved-manifest.json': '996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1',
 'scripts/sql-review/foundation-bootstrap-finalize.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'scripts/sql-review/foundation-invariants.sql': '8fc28f505bf100db89c8d441a507f3a8d58532dfb5ef960c8790d729a73f9904',
 'scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'scripts/sql-review/local_image_identity.py': 'a0742d4f25271cc5c4b8bced19909415181a76fb9856948a3dffed28abb80604',
 'scripts/sql-review/migration_server_diagnostics.py': '6d4d08362f3f4527138fb166324f03b5720cf912a9c38d987a28164e3a54e54d',
 'scripts/sql-review/pg17_catalog_rules.py': '448b46b7b5a8d6bc62dd25fc85cb12ad488f3e9dfabd70d028a5f6f49afea342',
 'scripts/sql-review/prisma-ledger-proof.md': '05ed0aff941305f5e2800b49633f029a8a68ca05ec2b80171060632917577992',
 'scripts/sql-review/prisma_ledger_proof.py': '1cb05b1d82b67580671cccf5f9289fbc481fef2d77532b049658912428604b21',
 'scripts/sql-review/rehearsal-diagnostics.py': 'c595883eb8013defc967feb0fc94db1366227ce89b843eeea2235b5a3adbeb7e',
 'scripts/sql-review/run-context-control-rehearsal.py': '5ec53d01d7c5b19bea0a584ef9f5b4e6742d9509c21ac7e2250b9bdd62511f33',
 'scripts/sql-review/run-first-rehearsal.py': '279b8384c7847ec5e2411013dc5def4b0cdd155de4bff75586a29a156f87bf6e',
 'scripts/sql-review/run-local-f0-migrate.py': '4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f',
 'scripts/sql-review/run-scoped-read-companion-rehearsal.py': '4160760bb319e4389182ed5cfcb6c0fae028480bd3d6d418be0130e8156a0f15',
 'scripts/sql-review/test_catalog_collector_acl.py': 'd9ac90cb8c335bd70b04056e422692c55bf73569ef109d3f8fb2bd73e9e1b57b',
 'scripts/sql-review/test_catalog_collector_text.py': 'fe7a29132b7d69b69213f61ccfda3e14a7339735c202f3cae1334c92dc6e24a7',
 'scripts/sql-review/test_catalog_expression_oracle.py': 'a758a17b8cd92922e7a599dc06679e6309dc107028c151387e533dcf8a5f5c85',
 'scripts/sql-review/test_catalog_manifest.py': '633e4f8c8f3b93d7e44d7c8abff7aa5ca1f3caa063cc354d592d1913d4ba9750',
 'scripts/sql-review/test_compare_native_catalog.py': '38d0e26ac030a1024c739c8ea79e0c653b3f0bf9aee54e9815bf314b8887ce37',
 'scripts/sql-review/test_local_image_identity.py': '0edae319a544aaaa8ed112e2ec477fe7ac428b58a7970ca8cd0e33ff006abe93',
 'scripts/sql-review/test_pg17_catalog_rules.py': 'c6879cd715df8bb45b26bbeec90352189e339d87be2f37c869cf471e42cfbb4a',
 'scripts/sql-review/test_prisma_ledger_proof.py': '62685fbff83d42cad600de2d1f387647737a42bd5cffc50c2240eb1c66006095'}
AUDIT_PINS={'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/Root-exact6-proposal.json': '60de534fae2be06a2c0a30dfb056e96b38af47feef96f6fb7749cca6d0f77e72',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/Root-proposal-audit-source.py.txt': '77a24c53adada501c3aa0c1c0a03880af3e601fadcc5889cf2d3bf53a4cf816e',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/independent-actual-audit-source.py.txt': 'c514901cce6d14ebfa8e5f2d1b6a9a3bf9527a07cd4df8e9adf61730d2fa4010',
 'context/reconciliation/local-f0-operation-sources/six-c662-evidence-adapter-v1/independent-actual-audit.json': '0bacaf1de96ed87f6f0c7c61b553b5c6d49b2d4c8ee879a682f9a56b0b4af4e6'}
CLOSED_CLAIMS={('P0C-TABLE-AgeGateAttempt-ALLOW', 'positive.wa_app_runtime.select'): 0,
 ('P0C-TABLE-AgeGateBlock-ALLOW', 'positive.wa_app_runtime.select'): 1,
 ('P0C-TABLE-AccessAuditLog-ALLOW', 'positive.wa_app_runtime.select'): 2,
 ('P0C-TABLE-UserRole-ALLOW', 'positive.wa_app_runtime.select'): 3,
 ('P0C-TABLE-AuditEvent-ALLOW', 'positive.wa_app_runtime.select'): 4,
 ('P0C-TABLE-AuthProviderAccount-ALLOW', 'positive.wa_app_runtime.select'): 5}

class EvidenceFailure(Exception):
    """Fixed, secret-safe rejection code only."""

def need(value,code):
    if not value:raise EvidenceFailure(code)

def sh(raw):return hashlib.sha256(raw).hexdigest()

def _typed_json(value,depth=0,budget=None):
    if budget is None:budget=[2000000]
    budget[0]-=1
    need(depth<=48 and budget[0]>=0,'JSON_BOUNDS')
    kind=type(value)
    if kind is dict:
        need(all(type(k)is str for k in value),'JSON_KEYS')
        for x in value.values():_typed_json(x,depth+1,budget)
    elif kind is list:
        for x in value:_typed_json(x,depth+1,budget)
    else:need(value is None or kind in(str,int,bool)or kind is float and math.isfinite(value),'JSON_TYPES')

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def same(actual,expected,code):need(canonical(actual)==canonical(expected),code)

def doc(raw):
    need(type(raw)is bytes and len(raw)<=8*1024*1024,'JSON_BYTES_LIMIT')
    def pairs(items):
        value={}
        for k,v in items:need(k not in value,'DUPLICATE_JSON');value[k]=v
        return value
    value=json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(EvidenceFailure('NONFINITE_JSON')))
    _typed_json(value)
    return value

def identity(value,packet_key):
    same([value['run_id'],value['source_commit'],value['source_tree'],value[packet_key]],[RUN,COMMIT,TREE,PACKET],'IDENTITY')

def _read(root,relative,wanted):
    need(type(relative)is str and relative and not Path(relative).is_absolute()and ':'not in relative and '\\'not in relative and all(x not in('','.','..')for x in relative.split('/')),'RELATIVE_PATH')
    path=root/relative
    keys=('st_mode','st_dev','st_ino','st_size','st_mtime_ns','st_nlink')
    def confined_metadata():
        need(not any(x.is_symlink()for x in(path,*path.parents)if x.is_relative_to(root)),'SYMLINK')
        need(path.resolve(strict=True).is_relative_to(root),'PATH_ESCAPE')
        return path.lstat()
    def version(value):
        need(all(type(getattr(value,key,None))is int for key in(*keys,'st_ctime_ns'))and stat.S_ISREG(value.st_mode)and value.st_nlink==1 and 0<=value.st_size<=8*1024*1024,'REGULAR_SINGLE_LINK_BOUNDED_FILE')
        return tuple(getattr(value,key)for key in keys)
    def closed_read(expected=None):
        before=confined_metadata();identity=version(before)
        if expected is not None:need((identity,before.st_ctime_ns)==expected,'FILE_CHANGED_DURING_READ')
        with path.open('rb')as reader:
            opened=os.fstat(reader.fileno());need(version(opened)==identity,'FILE_CHANGED_DURING_READ')
            raw=reader.read(8*1024*1024+1)
            after_handle=os.fstat(reader.fileno())
            # Windows path and descriptor ctime can use different representations.
            # Identity compares across APIs; ctime compares only within each API.
            need(version(after_handle)==identity and after_handle.st_ctime_ns==opened.st_ctime_ns,'FILE_CHANGED_DURING_READ')
        after_path=confined_metadata()
        need(version(after_path)==identity and after_path.st_ctime_ns==before.st_ctime_ns,'FILE_CHANGED_DURING_READ')
        need(type(raw)is bytes and len(raw)==before.st_size and sh(raw)==wanted,'FILE_BYTES')
        return raw,(identity,before.st_ctime_ns)
    raw,identity=closed_read()
    # Re-open only after the first handle closes. Do not accept its stale bytes
    # when an in-place write preserved inode, length and modification time.
    checked,_=closed_read(identity)
    need(checked==raw and sh(checked)==wanted,'FILE_CHANGED_DURING_READ')
    return checked

def _capture(root):
    blobs={n:_read(root,n,h)for n,h in PINS.items()}
    need(sum(map(len,blobs.values()))<=64*1024*1024,'BUNDLE_SIZE')
    return blobs

def expected_operations(cases):
 glob={'stage':'GLOBAL_BACKEND_CLOSURE','other_clients_zero':True};trigger={'stage':'EXACT_EIGHT_TRIGGER_RESTORATION','owner_and_physical_enabled':True}
 def native(stage):return {'stage':stage,'native_catalog_match':True,'native_sha256':NATIVE}
 out=[glob,glob,native('PRE_FIXTURE_NATIVE_PARITY'),glob,trigger,glob,{'stage':'SYNTHETIC_EXISTING_ROWS_ONLY','actual_login':'postgres','commit_acknowledged':True,'operation_closed':True},glob,trigger,glob,native('POST_FIXTURE_NATIVE_PARITY'),glob]
 for index,c in enumerate(cases,1):
  actor={'stage':'BOUND_OPERATION','case':c['name'],'actual_login':'wa_app_runtime','issuer_committed':True,'same_tuple_verified':True,'bind_stage_marker':True,'query_stage_reached':c['kind']=='read','operation_closed':True,'terminal_exit':0 if c['kind']=='read'else 3,'result_validated':True}
  issuer={'stage':'SEPARATE_ISSUER_COMMIT','issuer_committed':True,'created_at_return_verified':True,'commit_acknowledged':True,'operation_closed':True}
  current={'stage':'IMMUTABLE_ISSUER_RETENTION','instances':1,'all_21_fields_match':True,'issuer_owned':True,'unrevoked':True,'unexpired_required':True,'current_unexpired_match':True}
  out.extend([actor,issuer,current,glob,current,glob,{**current,'instances':index,'unexpired_required':False,'current_unexpired_match':None},trigger])
 out.extend([glob,native('FINAL_NATIVE_PARITY'),glob,trigger,glob,native('FINALLY_FULL_NATIVE_PARITY')]);return out

def check_bundle(blobs):
 cache={}
 def j(n):
  raw=blobs[n]
  if raw not in cache:cache[raw]=doc(raw)
  return cache[raw]
 def asset(n):return j(BASE+'/'+n)
 record=j(RECORD);identity(record,'operation_packet_sha256');need(record['known_executor_exit']['exit_code']==0 and type(record['known_executor_exit']['exit_code'])is int,'KNOWN_EXIT0')
 m=asset('manifest/operation-manifest.json');identity(m,'packet_sha256');pins=m['packet_files_sha256'];need(len(pins)==354,'SOURCE354')
 need(sh(''.join(n+'\0'+pins[n]+'\n'for n in sorted(pins)).encode())==PACKET,'SOURCE_AGGREGATE')
 need(len(record['assets_sha256'])==43 and all(sh(blobs[n])==h for n,h in {**pins,**record['assets_sha256']}.items()),'FULL_SOURCE_AND43_ASSET_HASHES')
 need(m['review_status']=='APPROVED_LOCAL_F0_SCOPED_READ_COMPANION_OWNED_RESOURCE_V1_ATTEMPT','APPROVED_EXACT_LITERAL')
 raw=asset('evidence/run-evidence.json');c=asset('evidence/scoped-read-component/scoped-read-companion-results.json');identity(c,'packet_sha256')
 same([raw['run_id'],raw['approved_commit'],raw['approved_tree'],raw['approved_packet_sha256']],[RUN,COMMIT,TREE,PACKET],'WRAPPER_IDENTITY')
 need(raw['status']=='PASS_LOCAL_SCOPED_READ_SQL_SUBSET_ONLY'and raw['unexpected']==[]and raw['evidence_complete']is True and raw['output_complete']is True and raw['persistence_failure']is False,'COMPLETE_WRAPPER')
 need(c['status']=='PASS_FINITE_SCOPED_READ_COMPANION_SQL_SUBSET_ONLY'and c['current_stage']=='COMPLETE'and c['current_case']is None and c['unexpected']==[]and c['subsequent_cases_stopped']is False and c['evidence_complete']is True and c['fixture_owner_bypass_restored']is True and c['source_packet_unchanged_after']is True,'COMPLETE_CHILD')
 same(c['sanitization'],{'context_secrets_or_hashes_found':False,'raw_stderr_statement_bodies_or_handles_retained':False},'SANITIZATION')
 f=j('review-output/scoped-read-companion-rehearsal/fixtures.json');need(len(f['cases'])==len(c['results'])==71 and collections.Counter(x['kind']for x in f['cases'])=={'read':65,'binder-denial':6},'FINITE71')
 need(len(f['grants'])==71 and len(f['fixture_tables'])==8 and len(f['expected_counts'])==42 and sum(f['expected_counts'].values())==16,'FINITE_FIXTURES')
 need(len(f['worker_acl_ceiling_rows'])==32 and len(f['prepared_files_sha256'])==76 and len(f['source_files_sha256'])==23,'SOURCES_SQL_ACL')
 for n,h in f['source_files_sha256'].items():need(pins.get(n)==h,'SOURCE_INPUT_PIN')
 for n,h in f['prepared_files_sha256'].items():need(pins.get('review-output/scoped-read-companion-rehearsal/'+n)==h,'SQL_PIN')
 same(c['limits'],f['scope_limits'],'SCOPE_LIMITS');same(c['selected_controls'],[{'id':x,'status':'NOT_RUN'}for x in f['selected_control_ids']],'NO_CASE_PROMOTION')
 roles=['postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker']
 auth=[{'role':x,'transport':'TCP_127.0.0.1_5432','correct_password':'PASS_SCRAM','wrong_password':'PASS_REJECTED','wrong_password_exit_code':2}for x in roles]
 same(c['authentication'],auth,'CHILD_AUTH_SIX');same(raw['authentication'],auth,'PARENT_AUTH_SIX')
 same(raw['effective_hba_selections'],c['effective_hba_selections'],'PARENT_CHILD_HBA_CONTROLS')
 need(len(c['effective_hba_selections'])==12,'HBA12')
 for row,(address,role)in zip(c['effective_hba_selections'],((address,role)for address in('127.0.0.1','::1')for role in roles)):
  need(set(row)=={'role','address','rule_number','method'}and row['role']==role and row['address']==address and row['method']=='scram-sha-256'and type(row['rule_number'])is int and row['rule_number']>0,'STRICT_HBA')
 need(c['current_auth_role']=='wa_worker'and all(type(v)is bool and v for v in c['authentication_comparison'].values())and set(c['authentication_comparison'])=={'json_parsed','object','fields','string_fields','login','scram_identity','database','client_loopback','server_loopback'},'ACTUAL_METHOD_LOGIN_LOOPBACK')
 native=asset('evidence/native-before.json');need(sh(canonical(native).encode())==NATIVE and len(native['relations'])==42,'FULL_NATIVE_FIXED_SOURCE_IDENTITY')
 for n in ('native-after-oracle.json','native-after-ledger.json','post-native-before.json','post-native-after-oracle.json','post-native-after-ledger.json'):same(asset('evidence/'+n),native,'FULL_NATIVE_BEFORE_AFTER_PARITY')
 app=blobs['review-output/foundation-application.review.sql'].decode();need(sh(app.encode())=='5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad','CANONICAL_APPLICATION')
 bodies=list(re.finditer(r'CREATE FUNCTION platform_private\.bind_request_context\(secret text\).*?AS\s+(\$[a-z_0-9]*\$)(.*?)\1;',app,re.S));need(len(bodies)==1,'BINDER_DECLARATION');body=bodies[0][2]
 need(sh(body.encode())=='9583ab7231a98780ac8d8160394fb8bc8185c4f3208dd4af62b43a6425079009'and [i for i,line in enumerate(body.split('\n'),1)if "RAISE EXCEPTION 'invalid, stale or unsupported context'"in line]==[7],'BINDER_EXACT_BODY_LINE')
 for index,(case,row)in enumerate(zip(f['cases'],c['results']),1):
  expected={'case':case['name'],'case_id':case['case_id'],'assertion_id':'positive.wa_app_runtime.select','actual_login':'wa_app_runtime','operation_closed_before_observers':True,'tables_observed':42,'complete_state_sha256':row['complete_state_sha256'],'issued_grants':index,'status':'PASS_FINITE_SCOPED_READ_ONLY','diagnostic':None,'query_stage_reached':case['kind']=='read','counts':case['expected']if case['kind']=='read'else None}
  need(type(row['complete_state_sha256'])is str and re.fullmatch('[0-9a-f]{64}',row['complete_state_sha256']),'STATE_SHA')
  if case['kind']=='read':expected['stage_markers']={'before':True,'after':True};need(all(type(v)is int and v>=0 for v in row['counts'].values()),'TYPED_COUNTS')
  else:expected['diagnostic']={'matched':True,'sqlstate':'42501','classification':'EXACT_PRINCIPAL_CURRENTNESS_BINDER_GUARD','source_body_sha256':sh(body.encode()),'source_body_line':7,'native_location':'exec_stmt_raise@pl_exec.c'}
  same(row,expected,'EXACT71_RESULT_FIELDS_AND_VERDICT')
 same(c['operations'],expected_operations(f['cases']),'EXACT586_OPERATION_TYPES_ORDER_BINDING_CLOSURE_RETENTION')
 same(c['baseline']['tables'],{k:v for k,v in c['baseline']['tables'].items()},'BASELINE_OBJECT')
 need(len(c['baseline']['tables'])==42 and sh(json.dumps(c['baseline']['tables'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==c['baseline']['sha256'],'BASELINE42_SHA')
 for table,count in f['expected_counts'].items():
  b=c['baseline']['tables'][table];need(set(b)=={'count','rows_sha256'}and type(b['count'])is int and b['count']==count and re.fullmatch('[0-9a-f]{64}',b['rows_sha256']),'BASELINE42_COUNTS')
 post=asset('evidence/post-state-before.json');same(post,asset('evidence/post-state-after.json'),'POST_READONLY_STATE_PARITY')
 need(len(post)==42 and sh(canonical(post).encode())==c['results'][-1]['complete_state_sha256'],'POST_CHILD_FINAL_STATE_BINDING')
 for table,count in f['expected_counts'].items():
  if table!='platform.database_action_grant':same(post[table],c['baseline']['tables'][table],'NON_GRANT_DATA_UNCHANGED')
  else:need(type(post[table]['count'])is int and post[table]['count']==71,'ONLY71_RETAINED_GRANTS')
 for n in ('catalog-comparison.json','post-catalog-comparison.json'):
  x=asset('evidence/'+n);need(x['status']=='PASS'and x['findings']==[]and set(x['check_counts'])=={'PASS'}and type(x['check_counts']['PASS'])is int and x['check_counts']['PASS']==29089 and x['native_snapshot_sha256']==NATIVE,'NATIVE29089')
 for n in ('oracle-results.json','post-oracle-results.json'):
  x=asset('evidence/'+n);need(type(x['expression_count'])is int and x['expression_count']==416 and len(x['expressions'])==416 and type(x['server_version_num'])is int and x['server_version_num']==170011,'ORACLE416')
 same(raw['ledger_comparison']['status'],'PASS','LEDGER_PASS');need(len(raw['ledger_comparison']['checks'])==22 and all(x['status']=='PASS'and x['expected_sha256']==x['actual_sha256']for x in raw['ledger_comparison']['checks']),'LEDGER22')
 migration=raw['migration_operations'];need(len(migration)==1 and migration[0]['operation']=='deploy'and migration[0]['stage']=='CATALOG_GENUINE_INITIAL_DEPLOY'and type(migration[0]['exit_code'])is int and migration[0]['exit_code']==0 and migration[0]['run_id']==RUN and migration[0]['container_id']==c['container_id'],'GENUINE_SINGLE_INSTALL')
 target=raw['targets']['wa-p0c-c662f807-scopedreads'];need(target['container_id']==c['container_id']and target['finalization']=='PASS','SAME_TARGET_FINALIZED')
 same(target['finalization_observation'],{'auth':'scram-sha-256:postgres','grantor':'postgres','leaf_create':{'wa_track_verifier':False,'wa_customer_verifier':False,'wa_private_helper_owner':False},'remaining_memberships':0,'active_install_connections':0},'ORIGINAL_GRANTOR_FINALIZATION')
 proof=raw['scoped_read']['post_proof'];same(proof,{'status':'PASS_READ_ONLY_SOURCE_BOUND_SUBSET','same_first_install_registration_sha256':sh(canonical(asset('evidence/ledger-registration.json')).encode()),'same_installer_attestation_sha256':migration[0]['attestation_sha256'],'native_sha256':NATIVE,'native_checks':29089,'oracle_expressions':416,'ledger_checks':22,'independent_tables':42,'before_state_sha256':c['results'][-1]['complete_state_sha256'],'after_state_sha256':c['results'][-1]['complete_state_sha256'],'child_final_state_sha256':c['results'][-1]['complete_state_sha256'],'second_deploy':False},'READONLY_SAME_INSTALL_AFTER')
 att=asset('evidence/scoped-read-native-attestation.json');identity(att,'packet_sha256');need(att['container_id']==c['container_id']and att['original_grantor_finalized']is True and att['operation_backends_absent']is True and att['native_snapshot_sha256']==NATIVE,'NATIVE_ATTESTATION_IDENTITY')
 need(raw['scoped_read']['component_closure_confirmed']is True and raw['scoped_read']['component_closure_attempted']is True and raw['scoped_read']['component_report_sha256']==sh(canonical(c).encode())and record['raw_child_canonical_sha256']==sh(canonical(c).encode()),'CHILD_CLOSED_BYTES_AND_CANONICAL_SERIALIZATION')
 for key in('packet_unchanged_after_run','tool_source_data_unchanged_after_run','external_sources_unchanged_after_run','external_inputs_unchanged_after_run'):need(raw[key]is True,'PRESERVED_SOURCE')
 need(all(all(type(x[k])is bool and x[k]for k in x if k!='phase')for x in raw['resource_kernel_checks'])and len(raw['resource_kernel_checks'])==2,'OWN_CID_TMPFS_KERNEL_TWO')
 cleanup=asset('independent-cleanup.json');identity(cleanup,'packet_sha256');need(cleanup['status']=='PASS_INDEPENDENT_PHYSICAL_CLEANUP'and cleanup['private_directory_absent']is True and cleanup['pinned_image_retained']is True and all(x['absent_exact_known_diagnostic']is True for x in cleanup['exact_name_observations'].values()),'INDEPENDENT_PHYSICAL_CLEANUP')
 need(raw['cleanup_actions_confirmed']is True and raw['cleanup_summary']['private_directory_absent']is True and all(v is False for v in raw['cleanup_summary']['resource_presence_after'].values())and raw['cleanup_summary']['image_removed']is False and raw['cleanup_summary']['unrelated_resources_changed']is False,'EXACT_TEST_OWNED_CLEANUP')
 inventory=j('context/reconciliation/local-f0-assertions.json');claims=[]
 for index,model in enumerate(MODELS):
  cid='P0C-TABLE-'+model+'-ALLOW';case=next(x for x in inventory['cases']if x['id']==cid);item=next(x for x in case['assertions']if x['id']=='positive.wa_app_runtime.select')
  need(item['availability']=='CANDIDATE_LOCAL_SQL_PATH'and item['dependency_ids']==[]and item['role']=='wa_app_runtime'and item['declared_operation']=='SELECT_EXACT_AUTHORIZED_TARGET','EXACT_SQL_SELECT_REQUIREMENT')
  chosen=[(i,x)for i,x in enumerate(c['results'])if x['case_id']==cid and x['case'].endswith('-positive-root')];need(len(chosen)==1,'EXACT_POSITIVE_PER_MODEL');i,positive=chosen[0];same(positive['counts'],{'root':1,'foreign':0},'POSITIVE_AUTHORIZED_TARGET_ONLY')
  claims.append({'case_id':cid,'assertion_id':item['id'],'status':'PASS','expected_assertion_sha256':sh(item['expected_assertion'].encode()),'complete_source_assertion_sha256':sh(canonical(item).encode()),'positive_protocol':positive['case'],'positive_result_pointer':'/results/'+str(i),'model_protocols':sum(x['case_id']==cid for x in c['results']),'whole_case_promoted':False})
 return claims

def validate_bundle(blobs):
    need(type(blobs)is dict and set(blobs)==set(PINS),'EXACT_CLOSED_GRAPH')
    need(all(type(v)is bytes and sh(v)==PINS[n]for n,v in blobs.items()),'CAPTURED_HASHES')
    expected_claims=check_bundle(blobs)
    derived=doc(blobs[DERIVED]);identity(derived,'packet_sha256')
    same(sorted(derived),sorted(('schema','derivation','actual_result','run_id','source_commit','source_tree','packet_sha256','source_record','independent_audit_files_sha256','claims','limits')),'DERIVED_FIELDS')
    need(derived['schema']=='workinants.six-c662-derived-qualified-evidence.v1'and derived['derivation']=='EXPLICIT_DERIVED_WRAPPER_NOT_RAW_RUNTIME_EVIDENCE'and derived['actual_result']=='DERIVED_REVIEWED_SCOPED6_SQL_READ_ASSERTIONS_ONLY','DERIVED_KIND')
    same(derived['source_record'],{'path':RECORD,'sha256':PINS[RECORD],'packet_alias_from':'operation_packet_sha256'},'SOURCE_RECORD_ALIAS')
    same(derived['independent_audit_files_sha256'],AUDIT_PINS,'EXACT_AUDIT_GRAPH')
    audit=doc(blobs[ARCHIVE+'/independent-actual-audit.json']);need(audit['decision']=='PASS_EXACT6_RESTRICTED_SQL_SELECT_ASSERTION_LINKS_ONLY'and audit['findings']==[],'INDEPENDENT_EVIDENCE_AUDIT')
    proposal=doc(blobs[ARCHIVE+'/Root-exact6-proposal.json'])
    same(audit['claims'],expected_claims,'INDEPENDENT_AUDITED_CLAIMS')
    need(len(derived['claims'])==len(proposal['claims'])==len(expected_claims)==6,'EXACT_SIX_CLAIMS')
    fixture=doc(blobs['review-output/scoped-read-companion-rehearsal/fixtures.json'])
    child_path=BASE+'/evidence/scoped-read-component/scoped-read-companion-results.json'
    for index,(claim,expected,proposal_row)in enumerate(zip(derived['claims'],expected_claims,proposal['claims'])):
        case=next(c for c in fixture['cases']if c['name']==expected['positive_protocol'])
        same(claim,{**expected,'component':{'path':child_path,'sha256':PINS[child_path],'json_pointer':expected['positive_result_pointer']},'source_statement_sha256':fixture['prepared_files_sha256'][case['sql']],'independent_mapping':{'path':ARCHIVE+'/independent-actual-audit.json','sha256':AUDIT_PINS[ARCHIVE+'/independent-actual-audit.json'],'json_pointer':'/claims/'+str(index)}},'EXACT_CLAIM_LINK')
        same([claim['case_id'],claim['assertion_id'],claim['status'],claim['expected_assertion_sha256'],claim['positive_protocol'],claim['model_protocols']],[proposal_row['case_id'],proposal_row['assertion_id'],proposal_row['proposed_status'],proposal_row['expected_assertion_sha256'],proposal_row['actual_positive_protocol'],proposal_row['completed_finite_protocols']],'ROOT_EXACT6_PROPOSAL')
    same(derived['limits'],{'Posture':'D','whole_case_promoted':False,'generic_vector_claimed':False,'owner_write_SH_API_worker_claimed':False,'privileged_fixture_seed_is_owner_creation_proof':False,'maximum_claims':6},'FINITE_LIMITS')
    return canonical(derived)

class QualificationBatch:
    """Immutable private byte capture, sticky rejection and final all-file barrier."""
    def __init__(self,root,_single=None):
        path=Path(root);need(not path.is_symlink(),'ROOT_SYMLINK')
        self.__root=path.resolve(strict=True)
        blobs=_capture(self.__root)
        self.__execution=validate_bundle(blobs)
        self.__snapshot=MappingProxyType(blobs)
        self.__expected=frozenset(CLOSED_CLAIMS)
        if _single is not None:
            need(_single in CLOSED_CLAIMS,'UNSUPPORTED_CLAIM');self.__expected=frozenset((_single,))
        self.__seen=set();self.__failed=False;self.__finalized=False

    def validate_claim(self,case_id,assertion_id,status,execution,root=None,json_pointer=None):
        try:
            need(not self.__failed and not self.__finalized,'BATCH_CLOSED')
            need(all(type(v)is str for v in(case_id,assertion_id,status,json_pointer))and status=='PASS','CLAIM_FIELDS')
            key=(case_id,assertion_id);need(key in self.__expected,'UNSUPPORTED_CLAIM')
            need(key not in self.__seen,'DUPLICATE_CLAIM')
            need(json_pointer=='/claims/'+str(CLOSED_CLAIMS[key]),'CLAIM_POINTER')
            if root is not None:need(Path(root).resolve(strict=True)==self.__root,'BATCH_ROOT')
            need(type(execution)is dict,'EXACT_DERIVED_RECORD')
            _typed_json(execution)
            need(canonical(execution)==self.__execution,'EXACT_DERIVED_RECORD')
            self.__seen.add(key);return True
        except EvidenceFailure:self.__failed=True;raise
        except Exception:self.__failed=True;raise EvidenceFailure('SCOPED_READ_EVIDENCE_REJECTED')from None

    def verify_unchanged(self):
        try:
            need(not self.__failed and not self.__finalized,'BATCH_CLOSED')
            need(self.__seen==self.__expected,'INCOMPLETE_BATCH')
            again=_capture(self.__root)
            need(all(again[n]==self.__snapshot[n]for n in PINS),'FINAL_BYTE_DRIFT')
            self.__snapshot=None;self.__finalized=True;return True
        except EvidenceFailure:self.__failed=True;raise
        except Exception:self.__failed=True;raise EvidenceFailure('SCOPED_READ_EVIDENCE_REJECTED')from None

    def require_finalized(self):
        need(not self.__failed and self.__finalized,'FINAL_BYTE_BARRIER_REQUIRED');return True

def prepare_batch(root):
    try:return QualificationBatch(root)
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('SCOPED_READ_EVIDENCE_REJECTED')from None

def validate_claim(case_id,assertion_id,status,execution,root,json_pointer=None):
    try:
        need(all(type(v)is str for v in(case_id,assertion_id,status,json_pointer))and status=='PASS','CLAIM_FIELDS')
        key=(case_id,assertion_id);need(key in CLOSED_CLAIMS,'UNSUPPORTED_CLAIM')
        need(json_pointer=='/claims/'+str(CLOSED_CLAIMS[key]),'CLAIM_POINTER')
        batch=QualificationBatch(root,_single=key)
        batch.validate_claim(case_id,assertion_id,status,execution,root,json_pointer=json_pointer)
        batch.verify_unchanged();return batch.require_finalized()
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('SCOPED_READ_EVIDENCE_REJECTED')from None
