"""Pure exact520 Native qualifier: closed byte snapshots and final unchanged barrier.
No project code/process/SQL/network execution; no proof dictionary or live reader is exposed.
"""
import hashlib
import json
from pathlib import Path
import re
from collections import Counter
from types import MappingProxyType

ARCHIVE = 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1'

ASSET_BASE = 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba'

RECORD = 'context/reconciliation/local-f0-native-1110fa4-4c894dba-execution.json'

DERIVED = 'context/reconciliation/local-f0-native-1110fa4-4c894dba-qualified-evidence.json'

PINS = {'context/reconciliation/database-candidate-corrections-first-replay-selection.json': '2bed2825a3918db0da6b426bfb7d129d256455afca3f6e0bbdd387057fc2d762',
 'context/reconciliation/database-candidate-tests.json': 'bba9bef6b94e9f4974f2a3a0b19a3277df54ac04aa77ceaa6b70ffcf75d988b8',
 'context/reconciliation/foundation-sql-draft-access.json': 'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea',
 'context/reconciliation/foundation-sql-draft-models.json': 'd04bf44bd67dceda35199fd1ff1e494eed3016e80d180144018e879f5aee778d',
 'context/reconciliation/foundation-sql-verifier-access.json': 'f84421c4957fcb4cf7fa5b04d3b5f804f8810ee58da2c1529e98daba8ab36bde',
 'context/reconciliation/local-f0-assertions.json': '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558',
 'context/reconciliation/local-f0-catalog-eb2aae6-2e4f5d40-execution.json': '76923eea9f3a68cb6157a0ed23432662492d79c068a7b58be507309edbe3e452',
 'context/reconciliation/local-f0-cli-diagnostics-validation.json': '8bf070ea0473fa41cd815737de96920f70ecf6896bf9188c52d90dbd42ed6e7b',
 'context/reconciliation/local-f0-migration-tooling-validation.json': '83d079ae068a04aee70c2d307ba7352a58a20409aef47df4f6a8866c25c2ce33',
 'context/reconciliation/local-f0-native-1110fa4-4c894dba-execution.json': '051967fdccf01ffddcbab671962472583f2672dcda38c77e0e8c14f498eab46a',
 'context/reconciliation/local-f0-native-1110fa4-4c894dba-qualified-evidence.json': '1586330d18837b060f8968f85747151c4239271ef1c3cb3caad276773ddb1538',
 'context/reconciliation/local-f0-native-access-resource-set-v2-source-validation.json': 'e1b39bf92a9c9ff0021d117fd086a318b2ae5c8ebc9bd95e47757757c2c2c41b',
 'context/reconciliation/local-f0-native-catalog-acl-correction.json': '017c9ee8c46de01c8a70ffbd68c0c80c27a1508cf4f1887fffaafcdba8d54f85',
 'context/reconciliation/local-f0-native-catalog-metadata-diagnostics.json': '5acadf4bbcc01b6133ebc0c81cb72e806a2c3d6f3840fd8f752353bde9c1735d',
 'context/reconciliation/local-f0-native-catalog-text-correction.json': '83766af0fc699b88a56081ccebd59eff59b6c850678506f6ffe67c3d04b38565',
 'context/reconciliation/local-f0-native-catalog-validation.json': 'cbc26b6d1935ced05a03b3d186658864cb687de6b49af888c92c551976279d75',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/audit-source/audit_closed_native_4c894_20261119.py.txt': 'faf9842ee9708e1d98c5180656f0d49103e6ae67e8e394b24826b04c58830582',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/audit-source/audit_closed_native_4c894_binding_supplement_20261119.py.txt': 'a13e9298d4959e52bd54212f9dd33cbf31aafebf307003db6abdc949e7fa4909',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/audited-finite-source-contract.json': 'f5f16e545b4bac8c4eba655445ed528e64e60849841a7d100734df82380376d5',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/binding-supplement.json': '83fd14252d4d2c588deedc5f81d5cd1a4ef9e94349babaf37af6d1de6ae6f14e',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/exact520-proposal.json': '0dac36bbcbe7088a35e35044afb3a41b261d3d6b2dca4ace7fcc6f1a93f56468',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/independent-audit.json': '9aa08dc7d26a89a108436eedaa0ecdc5139e74ba99c3a8d58e9ff77417b15649',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/preserved/assertion-evidence.before259.json': 'bf24c70872204981b7ed910ad75e61a8a674d18431e64496a2f794d1d4b35ca1',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/check_native_access_operation_resource_set_v2.py.txt': '01ea54e7af601c419a28219e7f88b67466586f7b2bdd797d798ba934a84cd58f',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/execute_local_f0_native_access_20261119_resource_set_v2.py.txt': 'c39d23d8d401cee5c35dea8b76cb572ff2e63ea50849d7515663d509fd3c0353',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/local_f0_native_access_operation_steps_resource_set_v2.py.txt': '3978b638fb4b449a6782128367899f87e00ba458de44ea9216ffa653d8d8ec73',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/pin_native_access_plan_20261119_resource_set_v2.py.txt': '07be7655dd5627141602b7f605048acb687cea2ec1cf6b13460e9361440e408b',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/prepare_local_f0_native_access_plan_resource_set_v2.py.txt': 'efddad2e8988cf26327b7d2757c333bb0236f0c343841331a661c3b700ce4f66',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-native-access-safety-sql-v1-source-validation.json': 'c3dd246042aaec551c7502c3dd613e18ac41f0b694bbc14cf9cb9b056ae58acc',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/check_native_access_operation_safety_sql_v1.py.txt': '415baef53ea13d12273b4879aadffe9683d0eb42d5c32e4a62d6b49e0f81843d',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/execute_local_f0_native_access_20261119_safety_sql_v1.py.txt': '82ff221e2b740ffeac248474c84bfab80253c34e3234a6a2cf584e6162397574',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/local_f0_native_access_operation_steps_safety_sql_v1.py.txt': '991210f073adecb1ca0b9dda208f56fba218feb56ab3d6c18db16b437ad8072a',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/pin_native_access_plan_20261119_safety_sql_v1.py.txt': '173da2a5a166f67beba5c0d38cfa1a15d57dff6b5f5fb868c26cb0cf4dab85c9',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/prepare_local_f0_native_access_plan_safety_sql_v1.py.txt': '3276f27248c81fcb128c0f3f9654a97e398e54dd4007f92e0da2cb8aca49ca18',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/author-actual-pinner4.json': '05cc09bbd8785ec5feb8e121517fd46e4559d6326e7dfb25e4df2de022104318',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/author-boundary14.json': '19e1cceab37ec038829090d9ff724f9f42d4e2f6f19ae3bc8e8066135f52cf31',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/author-exact-derivation.json': 'f13a5871818777b7703ae4fd7835c7df7cd882a452c67b3b358b9f1a41b83610',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/author-external-preservation2.json': '6db82dfd526761280299fab5891701652bb3db7a43d5588da599c248019aebed',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/author-inherited52.json': '31906274e12005a6bf1a6fb836c09a1892e982e4f611f55aef7549bb89d5152a',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/check-derived-actual-safety-composition.py.txt': 'a8b8f22a2733987b62c72abe9fe6315f3ce504fb6cb56c79b35b31e16cc3d11a',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/check_derived_safety_sql_v1_composed_20261119.py': 'a8b8f22a2733987b62c72abe9fe6315f3ce504fb6cb56c79b35b31e16cc3d11a',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common-finally-independent-root.json': '1c7d763fcd5fd17221a3a01302ae0df3f0b4bdb2034b5d27c98fd1e0c97a1b83',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common-finally-root-ack-plan.json': '72fb2ef99d187fc74972d57a647dd93c4ede49ea664a4338e7d5aca85781ca69',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common_safety_sql_v1_helpers.py.txt': 'a3cf85cfd4802d9eb293fc957672b1ba7f842e49b6b15985cd81be6cbe1ee537',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common_safety_sql_v1_install_eligibility.py.txt': '7118431c80fc5954ba314f1ed3634d5f3398dc2b35749dff5360ee52162052e7',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common_safety_sql_v1_recipe_origins_20261119.json': '92d4eb01d78febbfdb13352aa08139471f0c0e8511f71dffdb4365ae7e388d99',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common_safety_sql_v1_root_source_review_20261119.json': '322044efdf4fdac96636c2275c1cbf6f1c038839b76378bb1525f9d4a9c67ae0',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/common_safety_sql_v3_independent_source_review_20261119.json': '99009f9a2f29f52db3815b113810dc00f2ad24a3370479105b21091227432d01',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/full-source-delta.diff': 'b6d4596a318ca76ef8e616462fa491b5c41c12605c64ffef8b4314140761fc48',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/independent-root-source-review.json': 'ee706f5845e63bbe318be84ad3205dab9f0924a810b206bfcd28760b82c350ef',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/native-session-author-final18.json': '35eddea65cad33b0dd8f306896621500516c76c5e50075d1bcb333e11c0f11da',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/native-session-author48.json': '506e6df535f5d728858f98ff3e80369dc5f81524552b60ec0a49cdac6ae029fa',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/native-session-independent-root.json': 'ea836f39cbb27f8e5f314d32cd74eab3e1116fc3ebea5ec7ca960ae693d0a9e0',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/remaining_safety_sql_v1_final_whole_source_verification_20261119.json': '581ebe5065b16b7f6bd1bc26d237ae6b661f4f9be6be488cc24e07adc3abf846',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/remaining_safety_sql_v1_independent_source_review_20261119.json': '4b9f4e1e5113623ab5e71e500732a7602be92a8d0878605a240793407d652093',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/remaining_safety_sql_v1_root_source_review_20261119.json': '1ae6c090e5587685a93b6c3c3bb7832cf03f8858710bc02fc267d558f8cd041c',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/source-author-results.json': '6fa63cde4f9a91f3c0cb96030b3c28f915db85c780eefa98568dc77a66b372c8',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/validation-before-independent-root-review.json': '84a8d45460887f1f13c8d66197b00ed1c2c2185d04ba4f17318c5aff5ad694fc',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/ROOT/context/reconciliation/local-f0-operation-sources/native-access-safety-sql-v1/reviews/validation-before-root-safety-decision.json': 'eca6588de59aa3540cd634121a7be0f60e718b3466a2748e96f5253926160990',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/check_native_access_operation_safety_sql_v1.py': '415baef53ea13d12273b4879aadffe9683d0eb42d5c32e4a62d6b49e0f81843d',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/execute_local_f0_native_access_20261119_safety_sql_v1.py': '82ff221e2b740ffeac248474c84bfab80253c34e3234a6a2cf584e6162397574',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/ok-migration-manifest.json': 'f461a6040f46dbf3a2cf29c01935ca4d80f142b05bffcf348696bc70d742e89d',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/operation-manifest-before-operational-review.json': 'e200cdc88596eebf8279068bd59f4eec6e98bef195e997cea595838a073f8bd6',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/operation-manifest-before-source-pin.json': '2a1ad8ac2934e92f9c2c94e046eb04b8cf2ecb8e17058644add70d32fc28ce92',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/operation-manifest.json': 'bd1e761a4a669035f91b5a3a0e1b129ab399589c306bad5562df03691c070119',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok.tar.gz': 'fb579dce6fa7da6c8c8339fcef0211d5a4e76450cefb44c525060004166b14e6',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/prisma/foundation/history-manifest.json': 'c39b07b92046992a9a26953b9d3d99282fd440da30dd322b39baa234215de837',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local-f0-native-access-plan-bd4d6720/source-ok/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/local_f0_native_access_operation_steps_safety_sql_v1.py': '991210f073adecb1ca0b9dda208f56fba218feb56ab3d6c18db16b437ad8072a',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/native_resource_set_v2_independent_source_plan_review_20261119.json': '4d6eb1ee1f606b30d6ccd3793af2d9ea3d24563033712fc006bf6ed49f62b85d',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/native_resource_set_v2_source_correction_plan_20261119.json': '9acbf4fa194dd659e8eb5b17952d2bca8fbeed166cfb5f371b7a0c145b2288ea',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/nativebd4d_independent_cleanup_20261119.json': '739091804218ac561e3a89044b30642920ca2b59f7f1838c8c20b9496ebf1985',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/nativebd4d_safety_resource_global_source_probe_v2_20261119.json': '269fcf2f5affce05b2d7b1edebcff05e10999c5c5238973665d5e2a927e5d2d1',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/nativebd4d_stopped_evidence_inventory_20261119.json': '7f26073fb97e9eea904951adae3d4a191be57cf08394646ab322d89276121f5d',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/pin_native_access_plan_20261119_safety_sql_v1.py': '173da2a5a166f67beba5c0d38cfa1a15d57dff6b5f5fb868c26cb0cf4dab85c9',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/prepare_local_f0_native_access_plan_safety_sql_v1.py': '3276f27248c81fcb128c0f3f9654a97e398e54dd4007f92e0da2cb8aca49ca18',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/probe_nativebd4d_safety_resource_global_20261119.py': '01b35e89b76f60b33d6c492688c99a2bab05c9c4ce66b25017c844809c6371ab',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/TASK/probe_nativebd4d_safety_resource_global_v2_20261119.py': '9dede0ba28b747623c00e15f1074e6865c25d4d1f5be81035d4d56748275fb08',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/author-initial-composition-harness/check_native_resource_set_v2_composed_20261119.py': '883a9955f67de89c93c3ec12fd480799a525565a6dffc58fb467bcb67f342277',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/author-initial-composition-harness/harness-correction.json': '02f83eff327c7c3dbc496fef4c29edf88a4a5d7977db9d4956c0e6f5cac062e9',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/preserved/preservation.json': 'e05e8af82a6a71cd83457daf01bafa1d95c26dff89b13fa6ed626a70641de7b9',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/check_native_resource_set_v2_composed_20261119.py.txt': '5259fef4eaf05373d26b8e4f134c1a280c65ad23e65b04aa1d7b012aa09eb278',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/check_native_resource_set_v2_full_graph_pinner_20261119.py.txt': 'd2239f906c2b2e2b4fc95925bcc6b4d59e6d17b782be447f279f65ca3516f17a',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/independent-offline/check_native_access_operation_resource_set_v2.py.test-output.txt': '06a52c1f1c53233d4c24028edd8c372bb239734d2386ec40b88ea586528ab514',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/independent-offline/check_native_resource_set_v2_composed_20261119.py.test-output.txt': 'fb5d3440ef5f0e3875b7543c67a6c7f6271a168b09de021bd4da8add4f911620',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/independent-offline/check_native_resource_set_v2_full_graph_pinner_20261119.py.test-output.txt': '465aa7a047d224572e60de18c950b21a2977324f3d9c8aeee2443fef20902854',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/independent-offline/checks.json': '4d9dd9f7d44c65a8839384c304a7f5edce922365313bc435cf1887b98f5af204',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_author_composition27_20261119.json': '65f6e1c26cdcd0ca341f0034690446ce0b7620b2581afa1efaacc71ab27b15ba',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_author_composition27_20261119.log': '946cbaf44db75934794ecd90591dfd628e84bae18e262befc7455dee5dd21c99',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_author_full_graph_pinner6_20261119.json': '2f30bbd30c13ff6986fd46d216d740445ca3abb395f1aece10114ef2e8954de2',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_author_owning75_20261119.json': '2913593761b2568c534f268450926cf5038a9bc2e3bb539a59efefe819589729',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_author_owning75_20261119.log': '317547f1f5f457fa9a2e908c2e0e3e6e8657fa554b01b104bf10d14b06111f5b',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_author_source_review_20261119.json': '444c903cecc2c8186eb03a78b9619cb3df1c246d9209dc5d191d0c866b017eac',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_exact_derivation_20261119.json': '9700cf8aa7cf9cdf7dbb3bdf893f168bc446b586c38b90c498d44504fb71b0c6',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_full_source_delta_20261119.diff': '8801d34800e8c2e97f238fc249534115a1ae87710d8674f4c4c9f1fba5229ba2',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_independent_source_plan_review_20261119.json': '4d6eb1ee1f606b30d6ccd3793af2d9ea3d24563033712fc006bf6ed49f62b85d',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_independent_source_review_20261119.json': 'eea3cfa4240253dadb96378cbbf0dbc0557e2f2a72e2358d22351a72190a024b',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_root_source_review_20261119.json': 'bc79514ecc2158df9e811edb1d2603107f8fa41f247bf5b4c8535cb44c90c163',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/native_resource_set_v2_source_correction_plan_20261119.json': '9acbf4fa194dd659e8eb5b17952d2bca8fbeed166cfb5f371b7a0c145b2288ea',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/validation-author-pending.json': '48495fd3b1481ef62431fe0be2a1b4d61129f68c5e825a9b698ca9d95408f05b',
 'context/reconciliation/local-f0-operation-sources/native-access-resource-set-v2/reviews/validation-before-author-offline-results.json': 'b4509dc0f025702af61f3a74fe80ec5ced994473e5266741ee9d31f0aa41d4c0',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/Root-literal-approval-receipt.json': '054499f93d653daa4fd5ff8e01aa5a5f739019c2066d8481a1e97a0332766d1b',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/authentication-ok/authentication-results-ok.json': 'f4e51bb2fc9b60fe81bd5c89cedf715fcc948fd80520718dc587bde0a8be2ee3',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/ledger-evidence.json': '34609aa8bfaf969f8350bad3af085330082cc7f4b1e6c3d26cd3456f1c9848f3',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/ledger-registration.json': 'edaab72f5fd237bbde8176d918a9b884a0638804e26ea65ddc50936efa1338a8',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-access-attestation.json': 'c58b1655519bd346fa41b3b5ba79991b7483a8adf8c6db0935dc64480aa93c84',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-after-ledger.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-after-oracle.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-denials/native-denial-results.json': '9ee4130e9ae7cc8cf90deec9c48fbb0a1d00c13fd3e067082d12ddda4e419e1e',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/native-deny-run-plan.json': 'db8133a118cbe7786e8be5af27e5c95e650551ad8460410e6a3981f755aadbd3',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/provider-preinstall-proof.json': 'eb1082ea657901a5095ba9b08811da6e8958f3171c1098d5e5ed5d09358943f7',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/run-evidence.json': 'c1a58ec24326cd9e885da9d7db358866d89d105def6a3b604d37668a60f50067',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/set-private-acl.ps1.txt': 'd5ef58e51c12b4371601557f027a44e9ca206b81444724f8aab65365bf9c057f',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/evidence/text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/independent-cleanup.json': 'e0156611278eb083a75322e1ec0e881e0a503bf14d5b4f5d65617f88c6d0fe47',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/independent-literal-review.json': 'cf0887d74665e5aa46648405203a9314823486f44d249b30bd235be0ced5aa5a',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/manifest/migration-ok.json': '8a1629bb457ec6c1e2a1b4282e2ff543bfc3c0c4fdfcfa7b7b11854f66ff03a1',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/manifest/ok-migration-manifest.json': '8a1629bb457ec6c1e2a1b4282e2ff543bfc3c0c4fdfcfa7b7b11854f66ff03a1',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/manifest/operation-manifest-before-operational-review.json': '113889b5b41c7b4e7d4f1924dc57254378f4a9763569bc523ce100a91b8c001b',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/manifest/operation-manifest-before-source-pin.json': 'fd5175140275340923ce9c87102a8b58702fd1a38ba35e6a2de88478dcd1b55b',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/manifest/operation-manifest.json': '74f118130c042bbda5729e59334f1667aa36951f2486af3fe7a156cd32071a67',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/operational-samples/exact-executor-sample1.json': '07e46a64542ca70d51663ccea5df468608966cb38544bf5c6f9fb0f3c66d773b',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/operational-samples/exact-executor-sample2.json': '0155831ca8065a8d57ec188ed2054620dab70ecebc64df81fccf8dbb28b6b56e',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/operational-samples/read-only-container-health.json': '80e9007aece8e8725d61a1aaed4132bf1337cd7f0fe0af2a64e962c7d18c85fb',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/source-analysis/publication-coordination-proposal-superseded.json': 'e8a316a26c5ba2c7aaeb310ff9c4fe1cbfb38724cd7a9d563ef9827878310c21',
 'context/reconciliation/local-f0-run-assets/1110fa4-native-4c894dba/source-analysis/static-workload-and-wait-analysis.json': 'e4345a2b445e5bc59832d68ceffee937e5633455296bfb7b4e167778ff35afa4',
 'context/reconciliation/local-f0-run-assets/eb2aae6-native-catalog-2e4f5d40/source-prefix-analysis.json': 'b3931b71fe3d0560d6864ce20aa64cc88086563c4399a34e4b442ed108c4fc4d',
 'context/reconciliation/local-f0-server-diagnostics-validation.json': '560504eea761a06864edea01fba42e2e2a9a086ecfaab583309868f8f2f9c027',
 'context/reconciliation/local-f0-tooling/linux-tooling-manifest.json': 'e8fcce8f3ed4eaad0f7834e908166a0947b997e75513d589078f0d79c9a940d0',
 'context/reconciliation/local-f0-tooling/prisma-tools-closure.json': '610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b',
 'contracts/database-review/foundation-payloads.v1.schema.json': 'a9e7eb1e44fd0cce0bff97b906d0c3cb98c49f63f2f07b95560e0d7013105cfe',
 'contracts/database-review/owner-mutation-evidence.v1.schema.json': '5b95ff84e970a9587b4c04f37f2730878164c8aa77e2311410556f7b8d3c99a2',
 'contracts/shared/SH-004.v1.schema.json': 'e7cd3008e84dce839f189ff882feb9bb68b42784e0f403981e652d239328667e',
 'contracts/shared/SH-114.v1.schema.json': '4df69f47f60f276d65c548c900590e06bf0530d4d03e16371972495bd7a2e78b',
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
 'review-output/native-table-denials-v2/00-ConsentLog-existing-observe.sql': '55e5a7c7b78844780cc9aba431b7b7505e4551ba428c0706b48782757793815d',
 'review-output/native-table-denials-v2/00-ConsentLog-native-controls.sql': '218cbd41788755c1ef8a0dd300613e06df4caa162b12e18e215ee9468f499b88',
 'review-output/native-table-denials-v2/01-PrivacyRequest-existing-observe.sql': 'fb98048abc7f33f7da73f10a5ad6c53fc1611898c4b9bf43da925d5b43d66135',
 'review-output/native-table-denials-v2/01-PrivacyRequest-native-controls.sql': 'c583806b8ee592ca179ad81d5f49de76d78fba1917f9fdd747a18af8c907b380',
 'review-output/native-table-denials-v2/02-AgeGateAttempt-existing-observe.sql': '0eb78169bb122be1f29fdbc7ea00fc1fe2b7228c996d4b998bfa34d1de6490fc',
 'review-output/native-table-denials-v2/02-AgeGateAttempt-native-controls.sql': '8d246278ef764b9cd0be3a6d3c39ec6dc23fe544a04421fabf2db8061cfee6ab',
 'review-output/native-table-denials-v2/03-AgeGateBlock-existing-observe.sql': '81d7d2732c4e4bd35df0f2ac966085edb1be9fa1855ac12c382769eb0c685129',
 'review-output/native-table-denials-v2/03-AgeGateBlock-native-controls.sql': '9248b8e4fe4ca61a2a1176f4486227ce0bee062de58b11cad5af44bb05489980',
 'review-output/native-table-denials-v2/04-AccessAuditLog-existing-observe.sql': 'a207add0a567c586c46d848b2391a5cc38334dabdec55624be218a2ccf3f09c1',
 'review-output/native-table-denials-v2/04-AccessAuditLog-native-controls.sql': '466137602af53d1198db1243661dc1e0e64d9c203187ccdf082d6aa354883288',
 'review-output/native-table-denials-v2/05-User-existing-observe.sql': 'cd74ed8f1e21afb3cdf4e916faf9b57c24861b34489c65c0c59c9eecb845d279',
 'review-output/native-table-denials-v2/05-User-native-controls.sql': '887082b9e7759e85c517c377b58ba2ebd8f95258d3846184462fb3be59334793',
 'review-output/native-table-denials-v2/06-UserRole-existing-observe.sql': '33423e25b41189db6247e9539c544e173dcdf730a218b22b51527977098487e8',
 'review-output/native-table-denials-v2/06-UserRole-native-controls.sql': '271322a4bfac48c43168eab83024396bb2d5250d131f5d12e049cc41f5b87671',
 'review-output/native-table-denials-v2/07-ProfessionalProfile-existing-observe.sql': '3e1c59e0a0a5bb2503533d4f04faf8177627d2b2f6431c1bebfc945c48c9018a',
 'review-output/native-table-denials-v2/07-ProfessionalProfile-native-controls.sql': '3ef87085ade359fad3f11624b8cab874cce957c5bd05e6da3fdeee1b672050f5',
 'review-output/native-table-denials-v2/08-CustomerProfile-existing-observe.sql': '8c6ddb7a0f011c34bd5e803feee16e1826978299965a9fdfaf0e66d870b9a464',
 'review-output/native-table-denials-v2/08-CustomerProfile-native-controls.sql': '17070f90afc1d082ad8e941b48d3089876183a20f28373e9edd6a9312eef7888',
 'review-output/native-table-denials-v2/09-CandidateProfile-existing-observe.sql': 'a50f3e3127e81d091849c573872f4cd8d630e2e1a70e864620bcf7e985cb4015',
 'review-output/native-table-denials-v2/09-CandidateProfile-native-controls.sql': '39bfe47603ca487cdb3bc6183ea6ebd164e5713e23c6e2e20bcf6dfa6d40fcbc',
 'review-output/native-table-denials-v2/10-AuditEvent-existing-observe.sql': '590944f17275ec9c9031efc1c6dee626e62d0626705de50dc1e3e6cb83b4230c',
 'review-output/native-table-denials-v2/10-AuditEvent-native-controls.sql': '2c89777889e5252989b50ca8466cfb9ee3749a17c1d259048577048b6a853926',
 'review-output/native-table-denials-v2/11-UserSecurityProfile-existing-observe.sql': '7fcb10bf0fca41539dfefcbf515d6bc2c302e21ba3bf48dbaf98f0b7465be2dc',
 'review-output/native-table-denials-v2/11-UserSecurityProfile-native-controls.sql': 'b0d30cdcc5a7c73d104025b7230b942b08e7739772834cba9160b76e4923ad32',
 'review-output/native-table-denials-v2/12-AuthProviderAccount-existing-observe.sql': 'f19717b853f3c31dc677ebdf2eeedc54c2c23334d96fc445d2aff60307b8ee14',
 'review-output/native-table-denials-v2/12-AuthProviderAccount-native-controls.sql': '7360c733d0324184d0e3ecb38bc64376533d8232cf3179cd41967469b77d0e7a',
 'review-output/native-table-denials-v2/13-TrackPlan-existing-observe.sql': '3a1c5a130e8d94bd35e840da0385c6d06fda648c943ef2012798fdb2c940fa3d',
 'review-output/native-table-denials-v2/13-TrackPlan-native-controls.sql': '3938722ab8c48e43a28a01cfc906acc3a811559c3fca4f33c30c61102ba33644',
 'review-output/native-table-denials-v2/14-TrackEntitlementDefinition-existing-observe.sql': '3633bb3274e8b94f573534c94097a479dfc10501b96f1b6a4629ee68db26bfbf',
 'review-output/native-table-denials-v2/14-TrackEntitlementDefinition-native-controls.sql': 'c5f488a568ee448d3754d22d80303edfa9afe57e1e07570c8dd3c8c0b6f796fe',
 'review-output/native-table-denials-v2/15-TrackPlanEntitlement-existing-observe.sql': '41c89def251a37846f7d020f702107c87a459ad62af0607cec54dc3dac265da7',
 'review-output/native-table-denials-v2/15-TrackPlanEntitlement-native-controls.sql': 'd54b31f8a118ca1d403456282763c8e1b5643e33b549a098f41ef018fa8e9144',
 'review-output/native-table-denials-v2/16-TrackSubscription-existing-observe.sql': '3e3124fd42575d5646bbc8720eab56aa8134cec883b7c2902274800160ca1e59',
 'review-output/native-table-denials-v2/16-TrackSubscription-native-controls.sql': '2e7716c51caca00be698d1aef074dfb9c75c11e5bc77c745f3320d901e2e9ee6',
 'review-output/native-table-denials-v2/17-TrackEntitlementGrant-existing-observe.sql': 'de8c4f7045c1c80b1dde91ef01e23c55f4f783e4eae3ce4f715429ffa939df5b',
 'review-output/native-table-denials-v2/17-TrackEntitlementGrant-native-controls.sql': '13300963a064fecca27bc4e4dc89ad556686b106b2ab67b9e07b215393928e4c',
 'review-output/native-table-denials-v2/18-TrackUsageEvent-existing-observe.sql': 'b1425f89c862a660c74dd129f5f33ecf6afb617d7a8035d52f2ae6e5c5103b3e',
 'review-output/native-table-denials-v2/18-TrackUsageEvent-native-controls.sql': 'c8d20d87adff3e1a191b6feb0872b2c26a2f0df8ff462e1b2ac598c7891d405a',
 'review-output/native-table-denials-v2/19-TrackUsageCounter-existing-observe.sql': '65003057473988054acb49e88fa223f56d75774be8f3330394bf3d5a3c6321fd',
 'review-output/native-table-denials-v2/19-TrackUsageCounter-native-controls.sql': 'f78955ca6a8359571014b00153bf95c6f21b037b64b2a9eb76cdbf3c468980b0',
 'review-output/native-table-denials-v2/20-TrackSubscriptionEvent-existing-observe.sql': '878cc8ba35c921d3d45f960aeee4393a2e79f822c22ebf011bc49e55fbce8ba1',
 'review-output/native-table-denials-v2/20-TrackSubscriptionEvent-native-controls.sql': 'a9525288fa6d6b5fcd6e0f023b6359e7ed2ee32a808021a6286497304dea6bc4',
 'review-output/native-table-denials-v2/21-ConsentContentRevision-existing-observe.sql': '5478800a3b3d46f577ecb353258a467988d3104db382d077d96e913e0c9c939c',
 'review-output/native-table-denials-v2/21-ConsentContentRevision-native-controls.sql': 'cf2521e9bd79d6e3e3c8bbed5f3ea4dccbb2f7651d95f397c0eaab1f33da37f8',
 'review-output/native-table-denials-v2/22-ConsentPresentation-existing-observe.sql': '360f72aa058a92911aabe0c19b57a8194b24aee71b973b1c3bfe4c2d7798891d',
 'review-output/native-table-denials-v2/22-ConsentPresentation-native-controls.sql': '7fc2a6abe4a7818570ee32054413c6dd6e7dea085683ac6429713fd30cb82135',
 'review-output/native-table-denials-v2/23-ConsentDisposition-existing-observe.sql': 'fa1410954dfc662d5fd10023b31a1a8c2045a7e92543a25ae710b7ca81634d26',
 'review-output/native-table-denials-v2/23-ConsentDisposition-native-controls.sql': '09e8e22452e52a6bab1465a14e499024aadc8cd536c25b8ebf189d48b81c886d',
 'review-output/native-table-denials-v2/24-DatabaseActionGrant-existing-observe.sql': '774e283cd0a31986a9352fcf776133ae88c67e66ac18175270ecf9be0ed29a58',
 'review-output/native-table-denials-v2/24-DatabaseActionGrant-native-controls.sql': '2e2d3547c3654cbd1fc686bb2013caafe4103d07bb795b04b874d8eb065f169f',
 'review-output/native-table-denials-v2/25-RuntimeCommandReceipt-existing-observe.sql': 'd576a20764dc7aa928ed9d48ef07a42fb44e0b51e9c81f6fa51e1ca0d8a2f846',
 'review-output/native-table-denials-v2/25-RuntimeCommandReceipt-native-controls.sql': '542cefc359a312a693e83223ae6029c2336c458a0c4d1ca759dda7f9657da0f3',
 'review-output/native-table-denials-v2/26-RuntimeOutboxMessage-existing-observe.sql': '4b52fb3d44c43928ef5f5d4d9ac3e19c9392ef3191f5a43b682d7ce1c09c248b',
 'review-output/native-table-denials-v2/26-RuntimeOutboxMessage-native-controls.sql': '2603194e29364fa82b36656b4e0dd18b15bff466c10c55ebe3c0ee19e6877237',
 'review-output/native-table-denials-v2/27-RuntimeEffectReceipt-existing-observe.sql': '6c971274711f9c8eab4ba11a2c987525b98f95cf41d3300b9db99fda9e1c86e5',
 'review-output/native-table-denials-v2/27-RuntimeEffectReceipt-native-controls.sql': '22e780421aae44c58c9d4067680d9a71730337ca833d7fd51039b3645c643233',
 'review-output/native-table-denials-v2/28-RuntimeWorkItem-existing-observe.sql': '872ca7eadfa65b5d7a8199aebe941467065bcbcdc38feead056e01f20a532039',
 'review-output/native-table-denials-v2/28-RuntimeWorkItem-native-controls.sql': '48b6b0ab2ce9210667a894e74b465fb5c65b44b03af02aa980ce0af995530869',
 'review-output/native-table-denials-v2/29-RuntimeAttempt-existing-observe.sql': '09d8485474e0a09891e59af9c7b38a4d774fad01d4bec1aab9c5ab221f10e7b3',
 'review-output/native-table-denials-v2/29-RuntimeAttempt-native-controls.sql': '9dc4e6e82926ff0575519493113b18f4c33df8eb66ff65ccf17f1e2aad1787e0',
 'review-output/native-table-denials-v2/30-RuntimeInboxReceipt-existing-observe.sql': 'b10f2d8d53440a3627f140cb5ac2b209ce1c6a35ba563519953a5b2549ba0a16',
 'review-output/native-table-denials-v2/30-RuntimeInboxReceipt-native-controls.sql': '3728fcace996cc8d4d60e7b22e2f9c15e84ccd59a79862a9e141ab43fbf7f6de',
 'review-output/native-table-denials-v2/31-RuntimeReservation-existing-observe.sql': 'fe494cc38dbadb9b859f1fb659fe9b6338ef7253e4268cb479ad938ad3327339',
 'review-output/native-table-denials-v2/31-RuntimeReservation-native-controls.sql': '1b04c6e23238580fc90cf6860d99419294f16e93d6d7647f094d853c4c100e21',
 'review-output/native-table-denials-v2/32-OwnerMutationEvidence-existing-observe.sql': '9c1bef439a9e01a83e7306b0e21afe0e36c67469899f19b46ab5c5365a0f41fa',
 'review-output/native-table-denials-v2/32-OwnerMutationEvidence-native-controls.sql': '2ea104c0acadaf4e797c5d6724d6faa9a78c4f22e22e405595316d8e7618cacc',
 'review-output/native-table-denials-v2/33-CustomerProfileLifecycleEvent-existing-observe.sql': '2e6bce436b043d7750d2243e13eba63617160d83ac991ac37975a9ffe5e38bd1',
 'review-output/native-table-denials-v2/33-CustomerProfileLifecycleEvent-native-controls.sql': 'd2ecd45a943c294d7d5ca98733025e7942ee6b752375f813537559f3dd9dd891',
 'review-output/native-table-denials-v2/34-TrackBaseSelection-existing-observe.sql': '6c0ec824ccb6a00478519dffc6594f5802e99319449cf96a1f13f8dbef68799c',
 'review-output/native-table-denials-v2/34-TrackBaseSelection-native-controls.sql': 'bc3f7bcf07b808a018a7b6847f81efb6e3931716132247448c31deb780bf5f13',
 'review-output/native-table-denials-v2/35-TrackEnrollmentReceipt-existing-observe.sql': '55340512b2c3d6623327c9f74b600545f18e5c235c2102bac5cbdc290e2570fe',
 'review-output/native-table-denials-v2/35-TrackEnrollmentReceipt-native-controls.sql': '0dd59ff3baf94c424bbcb714bdc7fdcbab949240e6fa6d39caae572cc2050975',
 'review-output/native-table-denials-v2/36-TrackUsageReservation-existing-observe.sql': 'b6d4b4876a02c7761c538e067bcc2827fd62ce781a4c3d227b3eaf041750c817',
 'review-output/native-table-denials-v2/36-TrackUsageReservation-native-controls.sql': '4a4c971e2b135a1f7c7386c5d101614b5288bc4b96554d9676d033ab29e85521',
 'review-output/native-table-denials-v2/37-PrivacyTargetInstruction-existing-observe.sql': '61db2cc5b4ad42f59afeee90a964c1985a10c439796be8d25451d3cf7507aed0',
 'review-output/native-table-denials-v2/37-PrivacyTargetInstruction-native-controls.sql': 'b6bf8afb8e30148f7d8bd4ed167f82b00e2b3112b263c6736ea0af553d1b6ca8',
 'review-output/native-table-denials-v2/38-PrivacyOwnerReceipt-existing-observe.sql': 'f0ddac1824cda9978003a740133c1ee05466fb188061bc089454e8290c02ce13',
 'review-output/native-table-denials-v2/38-PrivacyOwnerReceipt-native-controls.sql': 'ffab956b4f6b7679f119e81c5bccbafdbc2950257805c10fe7ba2f568e86c9b0',
 'review-output/native-table-denials-v2/39-PrivacyRestoreMarker-existing-observe.sql': '140ed8b0da00a5e2a87d5c734d65ae3da17a9a4f25743105e0c51d3c5bea6089',
 'review-output/native-table-denials-v2/39-PrivacyRestoreMarker-native-controls.sql': '63bcf652c0ecfd75c046a944225d8949ef7f0199c01e49e70a7697ee52dd3520',
 'review-output/native-table-denials-v2/all-user-trigger-closure.sql': '0f2a00899a87bb776bc647ad339772ebf058d635566e478097ae7b059b992a80',
 'review-output/native-table-denials-v2/native-fact-setup.sql': '50eff2a7b4ed74039bceb20093bbc9f1f700ac03ac741cde6500d70cee611c7e',
 'review-output/native-table-denials-v2/packet.json': '8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69',
 'review-output/native-table-denials-v2/provider-role-simulation-before-migrate.sql': '42b59ad2960aea933e1d72ff4707fcaae75eb7299e856ebbb9ea0097a8ed5156',
 'scripts/assemble-foundation-sql-review.py': '136489b5fb966085020128bfbd7140dad5e0b340a2312319d346305311fc212f',
 'scripts/check-first-rehearsal-mocks.py': '777d9d74788c37c9b20891196180708400e4f58991026075e60bb6bc74a96adf',
 'scripts/check-local-f0-migrate.py': '59d890c145e1f14a62e296fba0139eaa22ab728b70fa76a7dbd7dc3883222a14',
 'scripts/check-migration-server-diagnostics.py': 'cb3ded2eaf6c1532691a41af241897b11072907c37aaeb2d3f2f1478da157163',
 'scripts/check-native-catalog-review.py': '05d39953bd26c61ef7d414a53bb5c0bc65cb2e59ec8513e17230ad5f7e4ef859',
 'scripts/check-trigger-row-shapes.py': '7e6c851630a65c9e07685138e03eca5d4fd5404e8a4bb2b36895e34069d52ce9',
 'scripts/contract_schema.py': '27b91594ac3dc9e1345b5bde912b4a849f0a324e90819df56150f7e3d326bc8c',
 'scripts/database-candidate-correction-rules.py': '6b79a14ffa77c450c3864ba5e2d930d61d5a427a6b0c11545e1afdd37ccaabb3',
 'scripts/prepare-database-candidate-review-assets.py': 'dcb1544afc39cffbd9a8b052749f544c7531ff3dee2ff9cc738fd38d8d3bc9ed',
 'scripts/prepare-first-rehearsal.py': 'b03f4b7fda4e60ff7bafc2b6a7463d7bb9a3ee7bffc9f4e6c8f840f99b4116ce',
 'scripts/prepare-local-f0-history.py': '33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8',
 'scripts/prepare-native-catalog-review.py': 'cef4f4f191e478593a679e9b86c7eee410531b01501a896c0b6f0e1bc1ac4fa2',
 'scripts/prepare-native-table-denials-v2.py': 'ddf5a627a334bfb059ab63d71acc50b908c1891fe40c2825325f52147ed6d939',
 'scripts/prepare-rehearsal-diagnostics.py': '598bc556999a16f303171003324be8763cb00a0fff2bb54de8a1195e1e7c852b',
 'scripts/sql-review/catalog-acl-preflight.sql': '7018c8f415923533dc461b212a0df0f9a0f4144457e410c4505c9322df4647f4',
 'scripts/sql-review/catalog-text-preflight.sql': 'f1cab9adf94fe5aa2452f34213eea43cf4ecfe35c9ce5f5289486b7d4f859823',
 'scripts/sql-review/catalog_expression_oracle.py': 'c5034cc982a5523e42cd721214cbca5820980fafd2c233f83f7706fcee826dfc',
 'scripts/sql-review/catalog_manifest.py': '1f1deb607dd2b2b4583cabeeae6be3205964d8a5ad897fe7bb1003699bfc9c16',
 'scripts/sql-review/check-local-f0-migrate-guard.mjs': 'bf7c166a23eaf29ed2ac084def03115e30d308439566d2f29af10d5fd22496cc',
 'scripts/sql-review/collect_native_catalog.sql': '9313c892ae3e5ade97167aa1818ed4b371d04b835ac736be7c13c3206bc85b3f',
 'scripts/sql-review/collect_prisma_ledger.sql': '6dfa02fa375da4a126b996fc547dfff063c61b41c854db6b07ea62f52d63286b',
 'scripts/sql-review/compare_native_catalog.py': '20441930b769d93eb00d762861018878d18d8c0f64194d65c468f0e320c204f6',
 'scripts/sql-review/foundation-bootstrap-finalize.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'scripts/sql-review/foundation-invariants.sql': '8fc28f505bf100db89c8d441a507f3a8d58532dfb5ef960c8790d729a73f9904',
 'scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'scripts/sql-review/migration_server_diagnostics.py': '6d4d08362f3f4527138fb166324f03b5720cf912a9c38d987a28164e3a54e54d',
 'scripts/sql-review/native-table-denials-session-observation-v3.md': 'b62791ecc1edc8966b57b9edc0863eaa47fee57c568612bfb10c0f7a7ec55d40',
 'scripts/sql-review/native_deny_fixture_factory.py': '77655142f3fe56ba860a910e97815da048ad78ab9b4535a898206430072d37ff',
 'scripts/sql-review/pg17_catalog_rules.py': '448b46b7b5a8d6bc62dd25fc85cb12ad488f3e9dfabd70d028a5f6f49afea342',
 'scripts/sql-review/prisma-ledger-proof.md': '05ed0aff941305f5e2800b49633f029a8a68ca05ec2b80171060632917577992',
 'scripts/sql-review/prisma_ledger_proof.py': '1cb05b1d82b67580671cccf5f9289fbc481fef2d77532b049658912428604b21',
 'scripts/sql-review/rehearsal-diagnostics.py': 'c595883eb8013defc967feb0fc94db1366227ce89b843eeea2235b5a3adbeb7e',
 'scripts/sql-review/run-first-rehearsal.py': '279b8384c7847ec5e2411013dc5def4b0cdd155de4bff75586a29a156f87bf6e',
 'scripts/sql-review/run-local-f0-migrate.py': '4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f',
 'scripts/sql-review/run-native-table-denials-v3.py': '6e74115cc7a77e626c4379c5a5744efdede1257d04b206fc339e62a23fd49cd3',
 'scripts/sql-review/test_catalog_collector_acl.py': 'd9ac90cb8c335bd70b04056e422692c55bf73569ef109d3f8fb2bd73e9e1b57b',
 'scripts/sql-review/test_catalog_collector_text.py': 'fe7a29132b7d69b69213f61ccfda3e14a7339735c202f3cae1334c92dc6e24a7',
 'scripts/sql-review/test_catalog_expression_oracle.py': 'a758a17b8cd92922e7a599dc06679e6309dc107028c151387e533dcf8a5f5c85',
 'scripts/sql-review/test_catalog_manifest.py': '633e4f8c8f3b93d7e44d7c8abff7aa5ca1f3caa063cc354d592d1913d4ba9750',
 'scripts/sql-review/test_compare_native_catalog.py': '38d0e26ac030a1024c739c8ea79e0c653b3f0bf9aee54e9815bf314b8887ce37',
 'scripts/sql-review/test_native_deny_deferred_flush.py': 'c52d7275a02e66bddab09bb3e619f3583f7bf8543d743102f5b6e038591ec2ef',
 'scripts/sql-review/test_native_deny_fixture_factory.py': '54d645d500ab2b158cf789de4fdc7229a59298a1ea410909fbbfefff47fd1314',
 'scripts/sql-review/test_pg17_catalog_rules.py': 'c6879cd715df8bb45b26bbeec90352189e339d87be2f37c869cf471e42cfbb4a',
 'scripts/sql-review/test_prisma_ledger_proof.py': '62685fbff83d42cad600de2d1f387647737a42bd5cffc50c2240eb1c66006095',
 'scripts/sql-review/test_run_native_table_denials_v3.py': '56742be994a9966714a7f8e16859cbce7c6da9506b38b086cd627339f4da595f'}

AUDIT_PINS = {'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/binding-supplement.json': '83fd14252d4d2c588deedc5f81d5cd1a4ef9e94349babaf37af6d1de6ae6f14e',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/exact520-proposal.json': '0dac36bbcbe7088a35e35044afb3a41b261d3d6b2dca4ace7fcc6f1a93f56468',
 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/independent-audit.json': '9aa08dc7d26a89a108436eedaa0ecdc5139e74ba99c3a8d58e9ff77417b15649'}

CONTRACT = 'context/reconciliation/local-f0-operation-sources/native-1110-4c894-evidence-adapter-v1/audited-finite-source-contract.json'

INVENTORY = 'context/reconciliation/local-f0-assertions.json'

SQL = 'review-output/foundation-application.review.sql'

ACCESS = 'context/reconciliation/foundation-sql-draft-access.json'

RUN = '4c894dba-609e-4959-ad6c-d403dcab2280'

COMMIT = '1110fa461c663ff3050ac54b6d9507e1e789b6b4'

TREE = '6a3b962d2618af8962165883e1129800dabcb632'

OP = '6b8debbdffa54d182a956d1b663472e22ba633a5eb257ab1ddeea8b6ca9a3be2'

FINITE = '8044d43f25c4a449f662bbb467183aac86d6a619836aae0988458098d59e0b69'

SQL_SHA = '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad'

CID = '6204062e1c7cb6ec1c3b5b816d580925a7dc05955112b3b4b3a21033b5d77055'

CLOSED_CLAIMS = {('P0C-TABLE-AccessAuditLog-DENY', 'denial.anon.delete'): 51,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.anon.insert'): 49,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.anon.select'): 48,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.anon.update'): 50,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.authenticated.delete'): 55,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.authenticated.insert'): 53,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.authenticated.select'): 52,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.authenticated.update'): 54,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.service_role.delete'): 59,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.service_role.insert'): 57,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.service_role.select'): 56,
 ('P0C-TABLE-AccessAuditLog-DENY', 'denial.service_role.update'): 58,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.anon.delete'): 27,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.anon.insert'): 25,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.anon.select'): 24,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.anon.update'): 26,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.authenticated.delete'): 31,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.authenticated.insert'): 29,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.authenticated.select'): 28,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.authenticated.update'): 30,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.service_role.delete'): 35,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.service_role.insert'): 33,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.service_role.select'): 32,
 ('P0C-TABLE-AgeGateAttempt-DENY', 'denial.service_role.update'): 34,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.anon.delete'): 39,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.anon.insert'): 37,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.anon.select'): 36,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.anon.update'): 38,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.authenticated.delete'): 43,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.authenticated.insert'): 41,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.authenticated.select'): 40,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.authenticated.update'): 42,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.service_role.delete'): 47,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.service_role.insert'): 45,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.service_role.select'): 44,
 ('P0C-TABLE-AgeGateBlock-DENY', 'denial.service_role.update'): 46,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.anon.delete'): 123,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.anon.insert'): 121,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.anon.select'): 120,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.anon.update'): 122,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.authenticated.delete'): 127,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.authenticated.insert'): 125,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.authenticated.select'): 124,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.authenticated.update'): 126,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.service_role.delete'): 131,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.service_role.insert'): 129,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.service_role.select'): 128,
 ('P0C-TABLE-AuditEvent-DENY', 'denial.service_role.update'): 130,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.anon.delete'): 147,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.anon.insert'): 145,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.anon.select'): 144,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.anon.update'): 146,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.authenticated.delete'): 151,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.authenticated.insert'): 149,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.authenticated.select'): 148,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.authenticated.update'): 150,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.service_role.delete'): 155,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.service_role.insert'): 153,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.service_role.select'): 152,
 ('P0C-TABLE-AuthProviderAccount-DENY', 'denial.service_role.update'): 154,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.anon.delete'): 111,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.anon.insert'): 109,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.anon.select'): 108,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.anon.update'): 110,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.authenticated.delete'): 115,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.authenticated.insert'): 113,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.authenticated.select'): 112,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.authenticated.update'): 114,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.service_role.delete'): 119,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.service_role.insert'): 117,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.service_role.select'): 116,
 ('P0C-TABLE-CandidateProfile-DENY', 'denial.service_role.update'): 118,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.anon.delete'): 279,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.anon.insert'): 277,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.anon.select'): 276,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.anon.update'): 278,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.authenticated.delete'): 283,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.authenticated.insert'): 281,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.authenticated.select'): 280,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.authenticated.update'): 282,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.service_role.delete'): 287,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.service_role.insert'): 285,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.service_role.select'): 284,
 ('P0C-TABLE-ConsentContentRevision-DENY', 'denial.service_role.update'): 286,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.anon.delete'): 303,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.anon.insert'): 301,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.anon.select'): 300,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.anon.update'): 302,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.authenticated.delete'): 307,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.authenticated.insert'): 305,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.authenticated.select'): 304,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.authenticated.update'): 306,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.service_role.delete'): 311,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.service_role.insert'): 309,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.service_role.select'): 308,
 ('P0C-TABLE-ConsentDisposition-DENY', 'denial.service_role.update'): 310,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.anon.delete'): 3,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.anon.insert'): 1,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.anon.select'): 0,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.anon.update'): 2,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.authenticated.delete'): 7,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.authenticated.insert'): 5,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.authenticated.select'): 4,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.authenticated.update'): 6,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.service_role.delete'): 11,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.service_role.insert'): 9,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.service_role.select'): 8,
 ('P0C-TABLE-ConsentLog-DENY', 'denial.service_role.update'): 10,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.anon.delete'): 291,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.anon.insert'): 289,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.anon.select'): 288,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.anon.update'): 290,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.authenticated.delete'): 295,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.authenticated.insert'): 293,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.authenticated.select'): 292,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.authenticated.update'): 294,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.service_role.delete'): 299,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.service_role.insert'): 297,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.service_role.select'): 296,
 ('P0C-TABLE-ConsentPresentation-DENY', 'denial.service_role.update'): 298,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.anon.delete'): 99,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.anon.insert'): 97,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.anon.select'): 96,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.anon.update'): 98,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.authenticated.delete'): 103,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.authenticated.insert'): 101,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.authenticated.select'): 100,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.authenticated.update'): 102,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.service_role.delete'): 107,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.service_role.insert'): 105,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.service_role.select'): 104,
 ('P0C-TABLE-CustomerProfile-DENY', 'denial.service_role.update'): 106,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.anon.delete'): 432,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.anon.insert'): 430,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.anon.select'): 429,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.anon.update'): 431,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.authenticated.delete'): 436,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.authenticated.insert'): 434,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.authenticated.select'): 433,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.authenticated.update'): 435,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.service_role.delete'): 440,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.service_role.insert'): 438,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.service_role.select'): 437,
 ('P0C-TABLE-CustomerProfileLifecycleEvent-DENY', 'denial.service_role.update'): 439,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.anon.delete'): 315,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.anon.insert'): 313,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.anon.select'): 312,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.anon.update'): 314,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.authenticated.delete'): 319,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.authenticated.insert'): 317,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.authenticated.select'): 316,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.authenticated.update'): 318,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.service_role.delete'): 323,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.service_role.insert'): 321,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.service_role.select'): 320,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.service_role.update'): 322,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_app_runtime.delete'): 327,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_app_runtime.insert'): 325,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_app_runtime.select'): 324,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_app_runtime.update'): 326,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_context_issuer.delete'): 332,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_worker.delete'): 331,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_worker.insert'): 329,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_worker.select'): 328,
 ('P0C-TABLE-DatabaseActionGrant-DENY', 'denial.wa_worker.update'): 330,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.anon.delete'): 420,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.anon.insert'): 418,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.anon.select'): 417,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.anon.update'): 419,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.authenticated.delete'): 424,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.authenticated.insert'): 422,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.authenticated.select'): 421,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.authenticated.update'): 423,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.service_role.delete'): 428,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.service_role.insert'): 426,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.service_role.select'): 425,
 ('P0C-TABLE-OwnerMutationEvidence-DENY', 'denial.service_role.update'): 427,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.anon.delete'): 499,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.anon.insert'): 497,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.anon.select'): 496,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.anon.update'): 498,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.authenticated.delete'): 503,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.authenticated.insert'): 501,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.authenticated.select'): 500,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.authenticated.update'): 502,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.service_role.delete'): 507,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.service_role.insert'): 505,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.service_role.select'): 504,
 ('P0C-TABLE-PrivacyOwnerReceipt-DENY', 'denial.service_role.update'): 506,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.anon.delete'): 15,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.anon.insert'): 13,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.anon.select'): 12,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.anon.update'): 14,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.authenticated.delete'): 19,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.authenticated.insert'): 17,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.authenticated.select'): 16,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.authenticated.update'): 18,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.service_role.delete'): 23,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.service_role.insert'): 21,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.service_role.select'): 20,
 ('P0C-TABLE-PrivacyRequest-DENY', 'denial.service_role.update'): 22,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.anon.delete'): 511,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.anon.insert'): 509,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.anon.select'): 508,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.anon.update'): 510,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.authenticated.delete'): 515,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.authenticated.insert'): 513,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.authenticated.select'): 512,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.authenticated.update'): 514,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.service_role.delete'): 519,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.service_role.insert'): 517,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.service_role.select'): 516,
 ('P0C-TABLE-PrivacyRestoreMarker-DENY', 'denial.service_role.update'): 518,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.anon.delete'): 487,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.anon.insert'): 485,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.anon.select'): 484,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.anon.update'): 486,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.authenticated.delete'): 491,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.authenticated.insert'): 489,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.authenticated.select'): 488,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.authenticated.update'): 490,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.service_role.delete'): 495,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.service_role.insert'): 493,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.service_role.select'): 492,
 ('P0C-TABLE-PrivacyTargetInstruction-DENY', 'denial.service_role.update'): 494,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.anon.delete'): 87,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.anon.insert'): 85,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.anon.select'): 84,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.anon.update'): 86,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.authenticated.delete'): 91,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.authenticated.insert'): 89,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.authenticated.select'): 88,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.authenticated.update'): 90,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.service_role.delete'): 95,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.service_role.insert'): 93,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.service_role.select'): 92,
 ('P0C-TABLE-ProfessionalProfile-DENY', 'denial.service_role.update'): 94,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.anon.delete'): 384,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.anon.insert'): 382,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.anon.select'): 381,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.anon.update'): 383,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.authenticated.delete'): 388,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.authenticated.insert'): 386,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.authenticated.select'): 385,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.authenticated.update'): 387,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.service_role.delete'): 392,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.service_role.insert'): 390,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.service_role.select'): 389,
 ('P0C-TABLE-RuntimeAttempt-DENY', 'denial.service_role.update'): 391,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.anon.delete'): 336,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.anon.insert'): 334,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.anon.select'): 333,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.anon.update'): 335,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.authenticated.delete'): 340,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.authenticated.insert'): 338,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.authenticated.select'): 337,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.authenticated.update'): 339,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.service_role.delete'): 344,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.service_role.insert'): 342,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.service_role.select'): 341,
 ('P0C-TABLE-RuntimeCommandReceipt-DENY', 'denial.service_role.update'): 343,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.anon.delete'): 360,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.anon.insert'): 358,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.anon.select'): 357,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.anon.update'): 359,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.authenticated.delete'): 364,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.authenticated.insert'): 362,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.authenticated.select'): 361,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.authenticated.update'): 363,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.service_role.delete'): 368,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.service_role.insert'): 366,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.service_role.select'): 365,
 ('P0C-TABLE-RuntimeEffectReceipt-DENY', 'denial.service_role.update'): 367,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.anon.delete'): 396,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.anon.insert'): 394,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.anon.select'): 393,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.anon.update'): 395,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.authenticated.delete'): 400,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.authenticated.insert'): 398,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.authenticated.select'): 397,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.authenticated.update'): 399,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.service_role.delete'): 404,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.service_role.insert'): 402,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.service_role.select'): 401,
 ('P0C-TABLE-RuntimeInboxReceipt-DENY', 'denial.service_role.update'): 403,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.anon.delete'): 348,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.anon.insert'): 346,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.anon.select'): 345,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.anon.update'): 347,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.authenticated.delete'): 352,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.authenticated.insert'): 350,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.authenticated.select'): 349,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.authenticated.update'): 351,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.service_role.delete'): 356,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.service_role.insert'): 354,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.service_role.select'): 353,
 ('P0C-TABLE-RuntimeOutboxMessage-DENY', 'denial.service_role.update'): 355,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.anon.delete'): 408,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.anon.insert'): 406,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.anon.select'): 405,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.anon.update'): 407,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.authenticated.delete'): 412,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.authenticated.insert'): 410,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.authenticated.select'): 409,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.authenticated.update'): 411,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.service_role.delete'): 416,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.service_role.insert'): 414,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.service_role.select'): 413,
 ('P0C-TABLE-RuntimeReservation-DENY', 'denial.service_role.update'): 415,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.anon.delete'): 372,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.anon.insert'): 370,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.anon.select'): 369,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.anon.update'): 371,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.authenticated.delete'): 376,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.authenticated.insert'): 374,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.authenticated.select'): 373,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.authenticated.update'): 375,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.service_role.delete'): 380,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.service_role.insert'): 378,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.service_role.select'): 377,
 ('P0C-TABLE-RuntimeWorkItem-DENY', 'denial.service_role.update'): 379,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.anon.delete'): 444,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.anon.insert'): 442,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.anon.select'): 441,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.anon.update'): 443,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.authenticated.delete'): 448,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.authenticated.insert'): 446,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.authenticated.select'): 445,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.authenticated.update'): 447,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.service_role.delete'): 452,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.service_role.insert'): 450,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.service_role.select'): 449,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.service_role.update'): 451,
 ('P0C-TABLE-TrackBaseSelection-DENY', 'denial.wa_worker.delete'): 453,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.anon.delete'): 457,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.anon.insert'): 455,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.anon.select'): 454,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.anon.update'): 456,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.authenticated.delete'): 461,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.authenticated.insert'): 459,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.authenticated.select'): 458,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.authenticated.update'): 460,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.service_role.delete'): 465,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.service_role.insert'): 463,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.service_role.select'): 462,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.service_role.update'): 464,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.wa_worker.delete'): 467,
 ('P0C-TABLE-TrackEnrollmentReceipt-DENY', 'denial.wa_worker.update'): 466,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.anon.delete'): 174,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.anon.insert'): 172,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.anon.select'): 171,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.anon.update'): 173,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.authenticated.delete'): 178,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.authenticated.insert'): 176,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.authenticated.select'): 175,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.authenticated.update'): 177,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.service_role.delete'): 182,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.service_role.insert'): 180,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.service_role.select'): 179,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.service_role.update'): 181,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.wa_worker.delete'): 185,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.wa_worker.insert'): 183,
 ('P0C-TABLE-TrackEntitlementDefinition-DENY', 'denial.wa_worker.update'): 184,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.anon.delete'): 218,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.anon.insert'): 216,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.anon.select'): 215,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.anon.update'): 217,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.authenticated.delete'): 222,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.authenticated.insert'): 220,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.authenticated.select'): 219,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.authenticated.update'): 221,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.service_role.delete'): 226,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.service_role.insert'): 224,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.service_role.select'): 223,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.service_role.update'): 225,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.wa_worker.delete'): 228,
 ('P0C-TABLE-TrackEntitlementGrant-DENY', 'denial.wa_worker.update'): 227,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.anon.delete'): 159,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.anon.insert'): 157,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.anon.select'): 156,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.anon.update'): 158,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.authenticated.delete'): 163,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.authenticated.insert'): 161,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.authenticated.select'): 160,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.authenticated.update'): 162,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.service_role.delete'): 167,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.service_role.insert'): 165,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.service_role.select'): 164,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.service_role.update'): 166,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.wa_worker.delete'): 170,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.wa_worker.insert'): 168,
 ('P0C-TABLE-TrackPlan-DENY', 'denial.wa_worker.update'): 169,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.anon.delete'): 189,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.anon.insert'): 187,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.anon.select'): 186,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.anon.update'): 188,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.authenticated.delete'): 193,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.authenticated.insert'): 191,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.authenticated.select'): 190,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.authenticated.update'): 192,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.service_role.delete'): 197,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.service_role.insert'): 195,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.service_role.select'): 194,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.service_role.update'): 196,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.wa_worker.delete'): 200,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.wa_worker.insert'): 198,
 ('P0C-TABLE-TrackPlanEntitlement-DENY', 'denial.wa_worker.update'): 199,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.anon.delete'): 204,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.anon.insert'): 202,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.anon.select'): 201,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.anon.update'): 203,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.authenticated.delete'): 208,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.authenticated.insert'): 206,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.authenticated.select'): 205,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.authenticated.update'): 207,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.service_role.delete'): 212,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.service_role.insert'): 210,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.service_role.select'): 209,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.service_role.update'): 211,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.wa_worker.delete'): 214,
 ('P0C-TABLE-TrackSubscription-DENY', 'denial.wa_worker.update'): 213,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.anon.delete'): 264,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.anon.insert'): 262,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.anon.select'): 261,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.anon.update'): 263,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.authenticated.delete'): 268,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.authenticated.insert'): 266,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.authenticated.select'): 265,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.authenticated.update'): 267,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.service_role.delete'): 272,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.service_role.insert'): 270,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.service_role.select'): 269,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.service_role.update'): 271,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.wa_worker.delete'): 275,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.wa_worker.select'): 273,
 ('P0C-TABLE-TrackSubscriptionEvent-DENY', 'denial.wa_worker.update'): 274,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.anon.delete'): 248,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.anon.insert'): 246,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.anon.select'): 245,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.anon.update'): 247,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.authenticated.delete'): 252,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.authenticated.insert'): 250,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.authenticated.select'): 249,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.authenticated.update'): 251,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.service_role.delete'): 256,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.service_role.insert'): 254,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.service_role.select'): 253,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.service_role.update'): 255,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.wa_worker.delete'): 260,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.wa_worker.insert'): 258,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.wa_worker.select'): 257,
 ('P0C-TABLE-TrackUsageCounter-DENY', 'denial.wa_worker.update'): 259,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.anon.delete'): 232,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.anon.insert'): 230,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.anon.select'): 229,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.anon.update'): 231,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.authenticated.delete'): 236,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.authenticated.insert'): 234,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.authenticated.select'): 233,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.authenticated.update'): 235,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.service_role.delete'): 240,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.service_role.insert'): 238,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.service_role.select'): 237,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.service_role.update'): 239,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.wa_worker.delete'): 244,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.wa_worker.insert'): 242,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.wa_worker.select'): 241,
 ('P0C-TABLE-TrackUsageEvent-DENY', 'denial.wa_worker.update'): 243,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.anon.delete'): 471,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.anon.insert'): 469,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.anon.select'): 468,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.anon.update'): 470,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.authenticated.delete'): 475,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.authenticated.insert'): 473,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.authenticated.select'): 472,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.authenticated.update'): 474,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.service_role.delete'): 479,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.service_role.insert'): 477,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.service_role.select'): 476,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.service_role.update'): 478,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.wa_worker.delete'): 483,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.wa_worker.insert'): 481,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.wa_worker.select'): 480,
 ('P0C-TABLE-TrackUsageReservation-DENY', 'denial.wa_worker.update'): 482,
 ('P0C-TABLE-User-DENY', 'denial.anon.delete'): 63,
 ('P0C-TABLE-User-DENY', 'denial.anon.insert'): 61,
 ('P0C-TABLE-User-DENY', 'denial.anon.select'): 60,
 ('P0C-TABLE-User-DENY', 'denial.anon.update'): 62,
 ('P0C-TABLE-User-DENY', 'denial.authenticated.delete'): 67,
 ('P0C-TABLE-User-DENY', 'denial.authenticated.insert'): 65,
 ('P0C-TABLE-User-DENY', 'denial.authenticated.select'): 64,
 ('P0C-TABLE-User-DENY', 'denial.authenticated.update'): 66,
 ('P0C-TABLE-User-DENY', 'denial.service_role.delete'): 71,
 ('P0C-TABLE-User-DENY', 'denial.service_role.insert'): 69,
 ('P0C-TABLE-User-DENY', 'denial.service_role.select'): 68,
 ('P0C-TABLE-User-DENY', 'denial.service_role.update'): 70,
 ('P0C-TABLE-UserRole-DENY', 'denial.anon.delete'): 75,
 ('P0C-TABLE-UserRole-DENY', 'denial.anon.insert'): 73,
 ('P0C-TABLE-UserRole-DENY', 'denial.anon.select'): 72,
 ('P0C-TABLE-UserRole-DENY', 'denial.anon.update'): 74,
 ('P0C-TABLE-UserRole-DENY', 'denial.authenticated.delete'): 79,
 ('P0C-TABLE-UserRole-DENY', 'denial.authenticated.insert'): 77,
 ('P0C-TABLE-UserRole-DENY', 'denial.authenticated.select'): 76,
 ('P0C-TABLE-UserRole-DENY', 'denial.authenticated.update'): 78,
 ('P0C-TABLE-UserRole-DENY', 'denial.service_role.delete'): 83,
 ('P0C-TABLE-UserRole-DENY', 'denial.service_role.insert'): 81,
 ('P0C-TABLE-UserRole-DENY', 'denial.service_role.select'): 80,
 ('P0C-TABLE-UserRole-DENY', 'denial.service_role.update'): 82,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.anon.delete'): 135,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.anon.insert'): 133,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.anon.select'): 132,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.anon.update'): 134,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.authenticated.delete'): 139,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.authenticated.insert'): 137,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.authenticated.select'): 136,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.authenticated.update'): 138,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.service_role.delete'): 143,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.service_role.insert'): 141,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.service_role.select'): 140,
 ('P0C-TABLE-UserSecurityProfile-DENY', 'denial.service_role.update'): 142}

NATIVE_DIGEST = 'a048478f5e834dc1686b558954ea9bdaeaba4278afcf63976510c114680f1fc6'
PACKET_PATH = 'review-output/native-table-denials-v2/packet.json'
MODEL_PATH = 'context/reconciliation/foundation-sql-draft-models.json'


class EvidenceFailure(Exception):
    """Fixed safe classification only; never arbitrary input or exceptions."""


def need(value, code):
    if not value:
        raise EvidenceFailure('NATIVE_COMPLETE_' + code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def same(actual, expected, code):
    need(canonical(actual) == canonical(expected), code)


def alltrue(value):
    return type(value) is dict and bool(value) and all(type(k) is str and v is True for k, v in value.items())


def zero(value):
    return type(value) is int and value == 0


def document(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON_DUPLICATE_KEY')
            result[key] = value
        return result
    def invalid(_):
        raise EvidenceFailure('NATIVE_COMPLETE_JSON_NONFINITE')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def read(root, relative, wanted):
    need(type(relative) is str and relative and ':' not in relative and '\\' not in relative
         and not any(ord(c) < 32 for c in relative)
         and all(part not in ('', '.', '..') for part in relative.split('/')), 'SAFE_PATH')
    need(type(wanted) is str and re.fullmatch('[0-9a-f]{64}', wanted) is not None, 'PIN_TYPE')
    path = root
    for part in relative.split('/'):
        path = path / part
        need(not path.is_symlink(), 'SYMLINK')
    need(path.resolve(strict=True).is_relative_to(root) and path.is_file(), 'SOURCE_PATH')
    metadata = path.stat()
    need(type(metadata.st_size) is int and 0 <= metadata.st_size <= 32 * 1024 * 1024, 'SOURCE_SIZE')
    with path.open('rb') as stream:
        raw = stream.read(32 * 1024 * 1024 + 1)
    need(type(raw) is bytes and len(raw) <= 32 * 1024 * 1024 and digest(raw) == wanted, 'PIN_DRIFT')
    return raw


def pointer(value, text):
    need(type(text) is str and text.startswith('/'), 'POINTER')
    for key in text[1:].split('/'):
        if type(value) is list:
            need(re.fullmatch('0|[1-9][0-9]*', key) is not None and int(key) < len(value), 'POINTER')
            value = value[int(key)]
        else:
            need(type(value) is dict and key in value, 'POINTER')
            value = value[key]
    return value


def identity(value, packet_key=None):
    same([value[k] for k in ('run_id', 'source_commit', 'source_tree')], [RUN, COMMIT, TREE], 'SOURCE_RUN')
    if packet_key:
        same(value[packet_key], OP, 'OPERATION_PACKET')


def validate_wrapper(record, wrapper, child, manifest, native, auth, provider, attestation, runplan, cleanup, oracle, catalog, ledger, contract, blobs):
    """Validate the closed original installation, source, authentication and cleanup."""
    identity(record, 'operation_packet_sha256')
    identity(manifest, 'packet_sha256')
    identity(child)
    same([wrapper[k] for k in ('run_id', 'approved_commit', 'approved_tree', 'approved_packet_sha256')], [RUN, COMMIT, TREE, OP], 'WRAPPER_IDENTITY')
    need(record['actual_result'] == wrapper['status'] == 'PASS_LOCAL_NATIVE_ACCESS_SUBSET_ONLY', 'COMPLETE_WRAPPER')
    need(wrapper['unexpected'] == [] and wrapper['persistence_failure'] is False
         and all(wrapper[k] is True for k in ('evidence_complete','output_complete','cleanup_actions_confirmed','packet_unchanged_after_run','tool_source_data_unchanged_after_run','external_input_archives_and_fresh_history_unchanged_after_run','external_sources_unchanged_after_run','all_source_and_external_inputs_preserved_after_run')), 'WRAPPER_PRESERVATION')
    need(all(type(v) is str and v.startswith('PASS') for v in wrapper['steps'].values()), 'WRAPPER_STEPS')
    pins = manifest['packet_files_sha256']
    need(len(pins) == 260 and digest(''.join(k + '\0' + pins[k] + '\n' for k in sorted(pins)).encode()) == OP, 'FULL260_PACKET')
    same(wrapper['source_verification']['files_sha256'], pins, 'VERIFIED_SOURCE_MAP')
    need(all(PINS.get(name) == wanted and digest(blobs[name]) == wanted for name, wanted in pins.items()), 'CURRENT_SOURCE')
    need(digest(blobs['scripts/sql-review/run-native-table-denials-v3.py']) == '6e74115cc7a77e626c4379c5a5744efdede1257d04b206fc339e62a23fd49cd3', 'EXACT_COORDINATOR')
    need(digest(canonical(native).encode()) == NATIVE_DIGEST, 'EXACT_NATIVE_SNAPSHOT')
    guards = [row for row in native['triggers'] if row['internal'] is False]
    need(len(guards) == 100 and all(row['enabled'] == 'O' for row in guards), 'FULL100_GUARDS')
    same(guards, contract['exact100_guard_identities'], 'GUARD_IDENTITIES')
    need(catalog['status'] == 'PASS' and catalog['findings'] == [] and type(catalog['check_counts']['PASS']) is int and catalog['check_counts'] == {'PASS':29089}
         and catalog['native_snapshot_sha256'] == NATIVE_DIGEST, 'NATIVE29089')
    same(wrapper['catalog_comparison'], catalog, 'CATALOG_COMPARISON')
    need(wrapper['ledger_comparison']['status'] == 'PASS' and len(wrapper['ledger_comparison']['checks']) == 22
         and len({row['field'] for row in wrapper['ledger_comparison']['checks']})==22
         and all(set(row)=={'field','status','expected_sha256','actual_sha256'} and type(row['field'])is str and row['status'] == 'PASS'
             and type(row['expected_sha256'])is str and re.fullmatch('[0-9a-f]{64}',row['expected_sha256'])is not None
             and row['expected_sha256'] == row['actual_sha256'] for row in wrapper['ledger_comparison']['checks']), 'LEDGER22')
    need(ledger['run_id'] == RUN and ledger['native_catalog_before_sha256'] == ledger['native_catalog_after_sha256'] == NATIVE_DIGEST, 'LEDGER_BINDING')
    history = ledger['observation']['history']
    need(len(history) == 1 and type(history[0]['steps']) is int and history[0]['steps'] == 1
         and all(history[0][k] is True for k in ('started','finished','id_is_uuid_v4','time_order_valid','checksum_format_valid'))
         and history[0]['rolled_back'] is False and history[0]['logs_state'] == 'NULL', 'GENUINE_LEDGER')
    need(history[0]['checksum_sha256']==digest(SQL_SHA.encode())and history[0]['name_sha256']==digest(b'20261117000100_f0_local_initial'),'LEDGER_CANONICAL_MIGRATION')
    need(oracle['connection_closed_before_observation'] is True and oracle['pre_oracle_catalog_sha256'] == oracle['post_rollback_catalog_sha256'] == NATIVE_DIGEST
         and alltrue(oracle['preflight']['outcomes']) and oracle['closure']['all_oracle_tables_absent'] is True
         and oracle['closure']['all_oracle_functions_absent'] is True, 'ORACLE_ROLLBACK_CLOSURE')
    expressions = oracle['results']['expressions']
    need(type(oracle['results']['expression_count']) is int and oracle['results']['expression_count'] == len(expressions) == 416, 'ORACLE416')
    same(expressions, contract['source_oracle416_expressions'], 'SOURCE_ORACLE416')
    target = wrapper['targets']['wa-p0c-4c894dba-native']
    need(len(wrapper['targets']) == 1 and target['container_id'] == child['resource']['container_id'] == CID
         and target['bootstrap'] == target['finalization'] == 'PASS' and target['network_mode'] == 'none' and target['published_ports'] is False, 'OWNED_CID')
    same(child['resource'],dict(container_id=CID,container_name='wa-p0c-4c894dba-native',volume_name='wa-p0c-4c894dba-native-data',image=manifest['image'],network='none',published_ports=False,labels={'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':RUN}),'EXACT_OWNED_RESOURCE')
    same(target['labels'],child['resource']['labels'],'TARGET_LABELS')
    same(wrapper['public_baseline_verification'],dict(predeclared_owner_and_three_acl_rows_match=True,learned_post_install_baseline=False),'PUBLIC_BASELINE')
    need(set(target['connections_before_finalization']) == {'migrator','other_client_backends'} and all(zero(v) for v in target['connections_before_finalization'].values()), 'FINALIZER_ABSENCE')
    same(target['finalization_observation'], dict(grantor='postgres',auth='scram-sha-256:postgres',remaining_memberships=0,active_install_connections=0,
         leaf_create=dict(wa_track_verifier=False,wa_customer_verifier=False,wa_private_helper_owner=False)), 'ORIGINAL_GRANTOR')
    need(len(wrapper['migration_operations']) == 1 and wrapper['migration_operations'][0]['operation'] == 'deploy'
         and zero(wrapper['migration_operations'][0]['exit_code']) and wrapper['migration_operations'][0]['source_sql_sha256'] == SQL_SHA
         and wrapper['migration_operations'][0]['container_id'] == CID, 'ONE_CANONICAL_INSTALL')
    need(len(wrapper['backend_closures']) == 14 and all(row['scope'] == 'ALL_DATABASES_ALL_ROLES_ALL_TAGS'
         and all(row[k] is True for k in ('observation_completed','counts_valid','migrator_zero','other_clients_zero','all_other_client_backends_absent')) for row in wrapper['backend_closures']), 'GLOBAL_CLOSURES')
    need({'BEFORE_NATIVE_DENIAL_COORDINATOR','AFTER_NATIVE_DENIAL_COORDINATOR'} <= {row['stage'] for row in wrapper['backend_closures']}, 'CHILD_BRACKETS')
    need(len(wrapper['catalog_operations']) == 11 and all(zero(row['exit_code']) and row['client_exited'] is True
         and row['unexpected_stderr'] is False and row['sqlstates'] == [] and row['raw_output_discarded'] is True for row in wrapper['catalog_operations']), 'CATALOG_CLIENTS')
    six = ['postgres','wa_migrator','wa_context_issuer','wa_identity_service_authority','wa_app_runtime','wa_worker']
    same(auth['authentication'], [dict(role=role,transport='TCP_127.0.0.1_5432',correct_password='PASS_SCRAM',wrong_password='PASS_REJECTED',wrong_password_exit_code=2) for role in six], 'FIRST_SIX_SCRAM')
    need(auth['scope'] == 'AUTH_PREFLIGHT_ONLY' and auth['status'] == 'PASS_PREFLIGHT_ONLY' and auth['current_stage'] == 'COMPLETE'
         and auth['failure'] is None and auth['subsequent_cases_stopped'] is False, 'AUTH_SCOPE')
    same(auth['effective_hba_selections'], [dict(role=role,address=address,rule_number=number,method='scram-sha-256') for address,number in [('127.0.0.1',2),('::1',3)] for role in six], 'HBA_SCRAM')
    auth_keys={'json_parsed','object','fields','string_fields','login','scram_identity','database','client_loopback','server_loopback'}
    same(auth['authentication_comparison'],{key:True for key in auth_keys},'FIRST_AUTH_COMPARISONS')
    same(child['authentication_comparisons'],{key:True for key in auth_keys},'CHILD_AUTH_COMPARISONS')
    provider_names = ['anon','authenticated','service_role']
    for entry, roles in ((child['authentication'], six+provider_names),(wrapper['provider_authentication'],provider_names)):
        same(entry, [dict(role=role,correct_password='PASS_SCRAM',wrong_password_rejected=True,wrong_password_exit_code=2) for role in roles], 'NINE_SCRAM')
    before, after = wrapper['provider_observations']
    need(type(before['explicit_usage']) is int and type(before['effective_usage']) is int and before['explicit_usage'] == before['effective_usage'] == 9
         and zero(after['explicit_usage']) and zero(after['effective_usage']), 'NINE_PROVIDER_REVOKES')
    roles = [dict(name=role,login=True,inherit=False,superuser=False,createdb=False,createrole=False,replication=False,
         bypassrls=role=='service_role',memberships=0,connect=True,create=False,temp=False) for role in provider_names]
    for value in (before['roles'],after['roles'],provider['roles'],child['provider_roles']):same(value,roles,'PROVIDER_FLAGS')
    for value in (provider,attestation,runplan):identity(value)
    need(provider['container_id'] == attestation['container_id'] == runplan['immutable_container_id'] == CID
         and provider['packet_sha256'] == attestation['deny_packet_sha256'] == runplan['packet_sha256'] == FINITE, 'ATTESTED_CID_PACKET')
    need(provider['application_sql_sha256'] == SQL_SHA and all(provider[k] is True for k in ('all_nine_schema_usage_sentinels_before_install','canonical_install_removed_all_nine','genuine_prisma_one_applied_migration','original_grantor_finalized','local_simulation_only'))
         and provider['hosted_parity_claimed'] is False, 'PROVIDER_ATTESTATION')
    need(attestation['operation_packet_sha256'] == OP and attestation['original_grantor_finalized'] is True
         and attestation['all_other_client_backends_absent'] is True and attestation['whole_case_promotion'] is False
         and attestation['coordinator_sha256'] == manifest['native_access']['coordinator_sha256'], 'NATIVE_ATTESTATION')
    need(attestation['native_snapshot_sha256'] == wrapper['qualified_native_snapshot_sha256'] == NATIVE_DIGEST
         and attestation['native_snapshot_file_sha256'] == digest(blobs[ASSET_BASE+'/evidence/native-before.json'])
         and attestation['comparison_file_sha256'] == digest(blobs[ASSET_BASE+'/evidence/catalog-comparison.json']), 'NATIVE_FILE_BINDING')
    need(child['run_plan_sha256'] == attestation['coordinator_plan_sha256'] == digest(blobs[ASSET_BASE+'/evidence/native-deny-run-plan.json'])
         and attestation['provider_proof_sha256'] == digest(blobs[ASSET_BASE+'/evidence/provider-preinstall-proof.json']), 'CLOSED_PLAN_BINDING')
    same(runplan['target_manifest'], document(blobs[ASSET_BASE+'/manifest/ok-migration-manifest.json']), 'TARGET_MANIFEST')
    need(all(pins.get(name) == wanted for name,wanted in runplan['source_modules_sha256'].items()), 'SOURCE_MODULES')
    need(cleanup['status'] == 'PASS_INDEPENDENT_PHYSICAL_CLEANUP' and cleanup['run_id'] == RUN
         and cleanup['run_evidence_sha256'] == PINS[ASSET_BASE+'/evidence/run-evidence.json']
         and cleanup['manifest_sha256'] == PINS[ASSET_BASE+'/manifest/operation-manifest.json']
         and cleanup['source_commit'] == COMMIT and cleanup['source_tree'] == TREE and cleanup['packet_sha256'] == OP
         and cleanup['private_directory_absent'] is True and cleanup['pinned_image_retained'] is True
         and all(row['absent_exact_known_diagnostic'] is True and row['raw_output_retained'] is False for row in cleanup['exact_name_observations'].values()), 'INDEPENDENT_CLEANUP')
    summary = wrapper['cleanup_summary']
    need(summary['resource_absence_observation_completed'] is True and summary['private_directory_absent'] is True
         and all(v is False for v in summary['resource_presence_after'].values()) and summary['image_removed'] is False, 'CLEANUP_ABSENCE')
    need(wrapper['sanitization']['actual_password_values_found'] is False and wrapper['sanitization']['unrestricted_subprocess_output_persisted'] is False
         and wrapper['sanitization']['raw_context_handles_persisted'] is False and wrapper['credential_handling']['real_credentials_in_argv_env_or_evidence'] is False, 'SECRET_EXCLUSION')


def validate_component(child, packet, native, models, contract, blobs):
    """All998 ordered operations and956 runnable probes are prerequisites only."""
    need(set(child)=={'schema','status','database_posture','current_stage','current_case','current_probe','current','operations','native_controls','facets','authentication','selected_cases','source_packet_sha256','cleanup_required','subsequent_cases_stopped','coverage_limit','run_id','source_commit','source_tree','run_plan_sha256','resource','current_auth_role','authentication_comparisons','provider_roles','fingerprint_order_comparisons','fingerprint_order_control','native_fact_projection'},'CHILD_FIELDS')
    need(child['status'] == 'COMPLETED_PREPARED_FACETS_ONLY_CASES_STILL_NOT_RUN' and child['current_stage'] == 'FINISHED'
         and child['database_posture'] == 'D' and child['subsequent_cases_stopped'] is False and child['source_packet_sha256'] == FINITE, 'COMPLETED_CHILD')
    same({k:child[k] for k in ('current_stage','current_case','current_probe')}, contract['closed_finished_context'], 'SOURCE_FINISHED_CONTEXT')
    same(child['current'], child['operations'][-1], 'LAST_SOURCE_OPERATION')
    need(len(child['selected_cases']) == 40 and all(row['status'] == row['source_vectors_status'] == row['allow_case_status'] == 'NOT_RUN' for row in child['selected_cases']), 'NO_CASE_PROMOTION')
    facts = child['native_fact_projection']
    need(len(facts) == 42 and len({row['object'] for row in facts}) == 42 and all(type(row['row_count']) is int and row['row_count'] > 0 for row in facts)
         and sum(row['row_count'] for row in facts) == 205, 'FULL42_205_DATA')
    same(facts, contract['native_fixture42_projection'], 'AUDITED42_FINGERPRINT')
    ops = child['operations']
    need(len(ops) == 998 and len({op['name'] for op in ops}) == 998, 'FULL998_OPERATIONS')
    same([dict(name=op['name'],role=op['role'],source_sql_sha256=op['source_sql_sha256']) for op in ops], contract['source_ordered_operation_statements'], 'SOURCE998_STATEMENTS_ROLES')
    for op in ops:
        need(set(op)<={'name','role','source_sql_sha256','closed_before_observers','evidence_complete','session_after_constructor','session_after_capture','actual_login_context_absent','exit_code','acknowledgement','session_after_finish','native_diagnostic','source_native_privilege_projection','exact_output_matches','session_before_close','session_after_close','all_100_trigger_functions_restored','fingerprint_checks','data_projection','all_native_facts_unchanged','native_catalog_unchanged','privilege_metadata_compared_to_source_native_pass'},'OPERATION_FIELDS')
        need(op['closed_before_observers'] is True and op['evidence_complete'] is True and op['actual_login_context_absent'] is True
             and op['all_100_trigger_functions_restored'] is True and alltrue(op['fingerprint_checks']), 'OPERATION_CLOSURE_GUARDS')
        same(op['fingerprint_checks'],{key:True for key in ('list','exact_row_count','objects','fields','known_name_set','source_name_order','typed_bounded_counts','digest_shape')},'EXACT_FINGERPRINT_FLAGS')
        same(op['data_projection'], facts, 'OPERATION_DATA_PRESERVED')
        need(type(op['exit_code']) is int and op['exit_code'] in (0,3) and type(op['acknowledgement']) is bool, 'TYPED_EXIT_ACK')
        closed = op['session_after_close']
        session_keys={'process_created','backend_tuple_present','capture_completed','finish_completed','process_exit_class','process_exit_confirmed','stdout_reader_finished','stderr_reader_finished','readers_finished','output_invalid','backend_absence_query_attempted','backend_absence_confirmed'}
        for phase in ('session_after_constructor','session_after_capture','session_after_finish','session_before_close','session_after_close'):
            value=op[phase];need(type(value)is dict and set(value)==session_keys and type(value['process_exit_class'])is str
                 and all(type(value[key])is bool for key in session_keys-{'process_exit_class'}),'CLOSED_SESSION_METADATA')
        need(all(closed[k] is True for k in ('process_created','backend_tuple_present','capture_completed','finish_completed','process_exit_confirmed','readers_finished','stdout_reader_finished','stderr_reader_finished','backend_absence_query_attempted','backend_absence_confirmed'))
             and closed['output_invalid'] is False and closed['process_exit_class'] == ('EXITED_ZERO' if op['exit_code']==0 else 'EXITED_NONZERO'), 'ACTUAL_SESSION_CLOSURE')
        same(op['session_after_finish'],op['session_before_close'],'FINISH_BEFORE_CLOSE')
        for phase in ('session_after_constructor','session_after_capture'):
            value=op[phase]
            need(value['process_created'] is True and value['finish_completed'] is False and value['process_exit_confirmed'] is False
                 and value['output_invalid'] is False and value['process_exit_class']=='RUNNING', 'SESSION_PROGRESSION')
        need(op['session_after_constructor']['backend_tuple_present'] is False and op['session_after_capture']['backend_tuple_present'] is True
             and op['session_after_capture']['capture_completed'] is True and op['session_before_close']['backend_absence_query_attempted'] is False
             and op['session_before_close']['backend_absence_confirmed'] is False, 'CAPTURE_CLOSE_ORDER')
        need(not any(k in op for k in ('failure','original_failure','unexpected_diagnostic')), 'NO_UNEXPECTED_OPERATION')
        need(op.get('all_native_facts_unchanged') is True or op['name']=='native-fact-setup', 'POSTSETUP_FACTS')
    setup=ops[0]
    need(setup['name']=='native-fact-setup' and setup['role']=='postgres' and setup['source_sql_sha256']==packet['files_sha256']['native-fact-setup.sql']
         and zero(setup['exit_code']) and setup['acknowledgement'] is True and setup['exact_output_matches'] is True, 'FIXTURE_SETUP')
    acls=native['nonowner_acl']
    def allowed(role,kind,obj,priv,col=None):
        return any(row['kind']==kind and row['object']==obj and row['privilege']==priv and row['grantee'] in (role,'PUBLIC')
             and (row.get('column') is None if col is None else row.get('column') in (None,col)) for row in acls)
    opmap={op['name']:op for op in ops};controls={row['case_id']:row for row in child['native_controls']}
    need(len(child['facets'])==960 and len(controls)==len(child['native_controls'])==40, 'FINITE_FACETS_CONTROLS')
    order=['native-fact-setup'];catalog_names={'native-fact-setup'};index=0;native_count=rls_count=blocked=0;gate_counts=Counter()
    for case in packet['cases']:
        name='native-control-'+case['model'];order.append(name);catalog_names.add(name);control=controls[case['id']];op=opmap[name]
        same(control,dict(case_id=case['id'],status='NATIVE_CONSTRAINT_FIXTURE_VALIDITY_ONLY',insert_one=True,update_controls_one=len(case['native_update_control_columns']),delete_one=True,rollback_and_restoration_proven=True), 'ROLLBACK_NATIVE_CONTROL')
        text=blobs['review-output/native-table-denials-v2/'+case['native_controls']].decode('utf8')
        need('ROLLBACK;' in text and 'COMMIT;' not in text and op['role']=='postgres' and op['source_sql_sha256']==packet['files_sha256'][case['native_controls']]
             and zero(op['exit_code']) and op['acknowledgement'] is True and op['exact_output_matches'] is True, 'ROLLBACK_ONLY_CONTROL_STATEMENT')
        if case['issuer_ownership_controls']:
            name='issuer-own-and-foreign';order.append(name);op=opmap[name]
            need(op['role']=='wa_context_issuer' and op['source_sql_sha256']==digest(case['issuer_ownership_controls']['sql_text'].encode())
                 and zero(op['exit_code']) and op['acknowledgement'] is True and op['exact_output_matches'] is True, 'ISSUER_OWN_FOREIGN')
        last=None
        for probe in case['probes']:
            facet=child['facets'][index];index+=1
            same([facet[k] for k in ('case_id','role','verb')],[case['id'],probe['role'],probe['verb']],'SOURCE_FACET_ORDER')
            if facet['status']=='NOT_RUN':
                need(set(facet)=={'case_id','role','verb','status','blocker'},'BLOCKED_FIELDS')
                blocked+=1;need(probe['preparation']=='BLOCKED' and probe['preparation_blocker'] is not None and facet['blocker']==probe['preparation_blocker'],'BLOCKED_REMAINS_NOT_RUN');continue
            need(digest(probe['sql_text'].encode())==probe['sql_sha256'],'ALL956_SQL_SOURCE_HASHES')
            name='deny-'+case['model']+'-'+probe['role']+'-'+probe['verb'];last=name;order.append(name);op=opmap[name]
            need(op['role']==probe['role'] and op['source_sql_sha256']==probe['sql_sha256'],'SOURCE_ROLE_STATEMENT')
            same(facet['post_probe_observers'],dict(operation_backend_absent=True,all_100_trigger_functions_restored=True,all_205_native_facts_unchanged=True),'POST_PROBE_OBSERVERS')
            need(facet['whole_case_promoted'] is False,'NO_FACET_PROMOTION')
            if facet['status']=='PASS_OBSERVED_NATIVE_GATE_ONLY':
                need(set(facet)=={'case_id','role','verb','status','facet','diagnostic','post_probe_observers','whole_case_promoted'}and facet['facet']=='NATIVE_SCHEMA_TABLE_OR_COLUMN_CEILING','NATIVE_FACET_FIELDS')
                native_count+=1;role=probe['role'];verb=probe['verb'];model=models[case['model']];schema=case['table'].split('.')[0]
                refs=[(model['fields'][pk],'SELECT') for pk in model['pk']] if verb in ('SELECT','UPDATE','DELETE')else[]
                if verb=='SELECT' and probe['native_forbidden_column']:refs.append((probe['native_forbidden_column'],'SELECT'))
                if verb=='INSERT':refs.extend((column,'INSERT')for column in model['fields'].values())
                if verb=='UPDATE':refs.append((probe['native_forbidden_column'],'UPDATE'))
                missing=sorted({column for column,permission in refs if not allowed(role,'TABLE',case['table'],permission,column)})
                projection=dict(schema_usage=allowed(role,'SCHEMA',schema,'USAGE'),required_permission_missing=bool(missing)or(verb=='DELETE'and not allowed(role,'TABLE',case['table'],'DELETE')),missing_referenced_columns=missing)
                same(op['source_native_privilege_projection'],projection,'INDEPENDENT_NATIVE_PRIVILEGES')
                gate='TABLE'if projection['schema_usage']else'SCHEMA';gate_counts[gate]+=1
                expected=dict(matched=True,sqlstate='42501',observed_gate=gate,native_location='aclcheck_error@aclchk.c',native_object=case['table']if gate=='TABLE'else schema,native_column=None,source_position_verified=gate=='SCHEMA',selected_column_isolation_claimed=False)
                same(facet['diagnostic'],expected,'EXACT_NATIVE_DIAGNOSTIC');same(op['native_diagnostic'],expected,'OPERATION_DIAGNOSTIC')
                need(projection['required_permission_missing'] is True and op['exit_code']==3 and op['acknowledgement'] is False,'NATIVE_DENIAL_EXIT')
            else:
                need(set(facet)=={'case_id','role','verb','status','facet','existing_row_count','restricted_count','post_probe_observers','whole_case_promoted'},'RLS_FIELDS')
                rls_count+=1
                need(facet['status']=='PASS_EXISTING_ROW_EMPTY_ONLY' and facet['facet'].startswith('RLS_') and type(facet['existing_row_count'])is int
                     and facet['existing_row_count']==1 and zero(facet['restricted_count']) and zero(op['exit_code']) and op['acknowledgement'] is True and op['exact_output_matches'] is True,'RLS_EMPTY_ONLY_UNQUALIFIED')
        catalog_names.add(last)
    need(index==960 and native_count==908 and rls_count==48 and blocked==4 and gate_counts=={'SCHEMA':480,'TABLE':428},'EXACT_FINITE_COUNTS')
    same(order,[op['name']for op in ops],'ALL998_SOURCE_ORDER')
    need({op['name']for op in ops if op.get('native_catalog_unchanged')is True}==catalog_names and len(catalog_names)==81,'ALL81_CATALOG_BOUNDARIES')
    same([row['id']for row in child['selected_cases']],packet['selected_case_ids'],'SELECTED40_SOURCE_CASES')


def validate_links(derived, proposal, inventory, child):
    need(len(derived['claims'])==len(proposal['rows'])==520,'CLOSED520')
    items={(case['id'],item['id']):item for case in inventory['cases']for item in case['assertions']}
    for index,(claim,row)in enumerate(zip(derived['claims'],proposal['rows'])):
        key=(claim['case_id'],claim['assertion_id']);need(CLOSED_CLAIMS.get(key)==index and claim['status']=='PASS','CLOSED_CLAIM')
        need('source_business_write'not in claim['assertion_id'] and claim['whole_case_promoted'] is False,'NO_AGGREGATE_OR_CASE_CLAIM')
        same(claim['independent_mapping'],dict(path=ARCHIVE+'/exact520-proposal.json',sha256=AUDIT_PINS[ARCHIVE+'/exact520-proposal.json'],json_pointer='/rows/'+str(index)),'AUDITED_MAPPING_POINTER')
        item=items[key]
        need(digest(item['expected_assertion'].encode())==claim['expected_assertion_sha256']==row['expected_assertion_sha256']
             and digest(canonical(item).encode())==claim['complete_source_assertion_sha256'],'COMPLETE_REQUIREMENT')
        facet=pointer(child,claim['component']['facet_json_pointer']);op=pointer(child,claim['component']['operation_json_pointer']);control=pointer(child,claim['component']['native_control_json_pointer'])
        need(facet['status']=='PASS_OBSERVED_NATIVE_GATE_ONLY' and facet['role']==item['role'] and facet['verb']==item['declared_operation']
             and item['availability']=='CANDIDATE_LOCAL_DENIAL' and item['dependency_ids']==[] and item['expected_outcome']=='DENY_OR_AUTHORIZED_NONENUMERATING_FILTER','ONLY_EXACT_NATIVE_REQUIREMENT')
        same([facet['case_id'],'denial.'+facet['role']+'.'+facet['verb'].lower()],list(key),'FACET_REQUIREMENT_IDENTITY')
        same(claim['component'],dict(path=ASSET_BASE+'/evidence/native-denials/native-denial-results.json',sha256=PINS[ASSET_BASE+'/evidence/native-denials/native-denial-results.json'],facet_json_pointer=row['facet_json_pointer'],operation_json_pointer=row['operation_json_pointer'],native_control_json_pointer=row['native_control_json_pointer']),'EXACT_COMPONENT_POINTERS')
        need(op['source_sql_sha256']==row['source_statement_sha256'] and digest(canonical(op['source_native_privilege_projection']).encode())==row['source_privilege_projection_sha256']
             and facet['diagnostic']['observed_gate']==claim['observed_gate']==row['observed_native_gate'] and control['case_id']==key[0],'CLAIM_OBSERVATION_BINDING')


def validate_bundle(blobs):
    cache={}
    def doc(name):
        if name not in cache:cache[name]=document(blobs[name])
        return cache[name]
    derived=doc(DERIVED);identity(derived,'packet_sha256')
    need(derived['actual_result']=='DERIVED_REVIEWED_NATIVE520_DENIAL_ASSERTIONS_ONLY'and derived['derivation']=='EXPLICIT_DERIVED_WRAPPER_NOT_RAW_RUNTIME_EVIDENCE','DERIVED_KIND')
    audit=doc(ARCHIVE+'/independent-audit.json');supplement=doc(ARCHIVE+'/binding-supplement.json')
    need(audit['decision']=='PASS_COMPLETED_FINITE_NATIVE_EVIDENCE_WITH_MAPPING_PROPOSALS_ONLY'
         and supplement['decision']=='PASS_ADDITIONAL_ATTESTATION_AND_CLOSURE_BINDINGS'and supplement['mapping_changes']is False,'INDEPENDENT_AUDITS')
    same(derived['independent_audit_files_sha256'],AUDIT_PINS,'AUDIT_PIN_SET')
    same(derived['limits'],dict(Posture='D',whole_case_promoted=False,RLS48_or_blocked4_qualified=False,source_business_write_qualified=False,owner_or_hosted_or_production_claim=False,old0a29_stop_cause='UNOBSERVED'),'FINITE_LIMITS')
    record=doc(RECORD);need(len(record['assets_sha256'])==33 and all(PINS.get(n)==h for n,h in record['assets_sha256'].items()),'IMMUTABLE33_ASSETS')
    need(derived['source_record']['path']==RECORD and derived['source_record']['sha256']==PINS[RECORD]and derived['source_record']['packet_alias_from']=='operation_packet_sha256','RAW_RECORD_ALIAS')
    packet=doc(PACKET_PATH);need(digest(blobs[PACKET_PATH])==FINITE and len(packet['cases'])==40,'FINITE_PACKET')
    for name,wanted in packet['source_inputs_sha256'].items():need(PINS.get(name)==wanted,'FINITE_SOURCE_INPUT')
    for name,wanted in packet['files_sha256'].items():need(PINS.get('review-output/native-table-denials-v2/'+name)==wanted,'FINITE_SQL_INPUT')
    child=doc(ASSET_BASE+'/evidence/native-denials/native-denial-results.json');native=doc(ASSET_BASE+'/evidence/native-before.json');contract=doc(CONTRACT)
    for suffix in ('native-after-oracle.json','native-after-ledger.json'):same(doc(ASSET_BASE+'/evidence/'+suffix),native,'FULL_NATIVE_PARITY')
    validate_wrapper(record,doc(ASSET_BASE+'/evidence/run-evidence.json'),child,doc(ASSET_BASE+'/manifest/operation-manifest.json'),native,
         doc(ASSET_BASE+'/evidence/authentication-ok/authentication-results-ok.json'),doc(ASSET_BASE+'/evidence/provider-preinstall-proof.json'),doc(ASSET_BASE+'/evidence/native-access-attestation.json'),doc(ASSET_BASE+'/evidence/native-deny-run-plan.json'),doc(ASSET_BASE+'/independent-cleanup.json'),doc(ASSET_BASE+'/evidence/oracle-evidence.json'),doc(ASSET_BASE+'/evidence/catalog-comparison.json'),doc(ASSET_BASE+'/evidence/ledger-evidence.json'),contract,blobs)
    validate_component(child,packet,native,{row['model']:row for row in doc(MODEL_PATH)},contract,blobs)
    validate_links(derived,doc(ARCHIVE+'/exact520-proposal.json'),doc(INVENTORY),child)
    proposal=doc(ARCHIVE+'/exact520-proposal.json')
    append_keys=frozenset((row['case_id'],row['assertion_id'])for row in proposal['rows']if row['proposed_action']=='PROPOSE_NEW_PASS_AFTER_REVIEWED_FAIL_CLOSED_PARSER')
    need(len(append_keys)==388,'EXACT388_APPEND_SET')
    return derived,append_keys


def _admit(root):
    return {name:read(root,name,wanted)for name,wanted in PINS.items()}


def _fingerprint(blobs):
    return digest(''.join(name+'\0'+digest(blobs[name])+'\n'for name in sorted(blobs)).encode())


class QualificationBatch:
    """Private closed-byte snapshot plus mandatory final full-byte barrier.

    No open readers or mutable proof dictionary leaves this object. Builder
    results remain provisional until verify_unchanged and require_finalized.
    """
    def __init__(self,root,all520=False,_single=None):
        self.__root=Path(root).resolve(strict=True)
        blobs=_admit(self.__root)
        derived,append_keys=validate_bundle(blobs)
        self.__execution=canonical(derived)
        self.__fingerprint=_fingerprint(blobs)
        self.__snapshot=MappingProxyType(blobs)
        self.__expected=frozenset(CLOSED_CLAIMS)if all520 else append_keys
        if _single is not None:
            need(_single in CLOSED_CLAIMS,'UNSUPPORTED_CLAIM');self.__expected=frozenset((_single,))
        self.__seen=set();self.__finalized=False;self.__failed=False

    def validate_claim(self,case_id,assertion_id,status,execution,root=None,json_pointer=None):
        try:
            need(not self.__failed and not self.__finalized,'BATCH_CLOSED')
            need(all(type(v)is str for v in(case_id,assertion_id,status))and status=='PASS','CLAIM_FIELDS')
            key=(case_id,assertion_id);index=CLOSED_CLAIMS.get(key);need(index is not None,'UNSUPPORTED_CLAIM')
            need(key in self.__expected,'BATCH_CLAIM_SCOPE')
            need(json_pointer=='/claims/'+str(index),'CLAIM_POINTER')
            if root is not None:need(Path(root).resolve(strict=True)==self.__root,'BATCH_ROOT')
            need(canonical(execution)==self.__execution,'EXACT_DERIVED_RECORD')
            self.__seen.add(key);return True
        except EvidenceFailure:
            self.__failed=True;raise
        except Exception:
            self.__failed=True;raise EvidenceFailure('NATIVE_COMPLETE_EVIDENCE_REJECTED')from None

    def verify_unchanged(self):
        try:
            need(not self.__failed and not self.__finalized,'BATCH_CLOSED')
            need(self.__seen==self.__expected,'INCOMPLETE_BATCH')
            again=_admit(self.__root)
            need(_fingerprint(again)==self.__fingerprint and all(again[name]==self.__snapshot[name]for name in PINS),'BATCH_DRIFT')
            self.__finalized=True;self.__snapshot=None
            return True
        except EvidenceFailure:
            self.__failed=True;raise
        except Exception:
            self.__failed=True;raise EvidenceFailure('NATIVE_COMPLETE_EVIDENCE_REJECTED')from None

    def require_finalized(self):
        need(not self.__failed and self.__finalized,'FINAL_BYTE_BARRIER_REQUIRED')
        return True


def prepare_batch(root,all520=False):
    try:
        need(type(all520)is bool,'BATCH_MODE')
        return QualificationBatch(root,all520=all520)
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('NATIVE_COMPLETE_EVIDENCE_REJECTED')from None


def validate_claim(case_id,assertion_id,status,execution,root,json_pointer=None):
    """Standalone calls always capture and finally recheck fresh whole evidence."""
    try:
        need(all(type(v)is str for v in(case_id,assertion_id,status))and status=='PASS','CLAIM_FIELDS')
        key=(case_id,assertion_id);need(key in CLOSED_CLAIMS,'UNSUPPORTED_CLAIM')
        need(json_pointer=='/claims/'+str(CLOSED_CLAIMS[key]),'CLAIM_POINTER')
        batch=QualificationBatch(root,_single=key)
        batch.validate_claim(case_id,assertion_id,status,execution,root,json_pointer=json_pointer)
        batch.verify_unchanged();return batch.require_finalized()
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('NATIVE_COMPLETE_EVIDENCE_REJECTED')from None
