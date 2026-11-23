"""Pure, one-assertion INSTALL6850 evidence reader. No project code execution.

This new reader never changes an older reader, report or scoreboard. Fixed
hash-bound data and a final fresh closed-byte barrier support one prior PARTIAL
replacement only. No business-row, whole-case or production claim is inferred.
"""
import hashlib,json,math,os,re,stat
from pathlib import Path
from types import MappingProxyType

B='context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c'
REC='context/reconciliation/local-f0-install-0ff2a91-6850ee4c-execution.json'
ARCHIVE='context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1'
DERIVED='context/reconciliation/local-f0-install-0ff2a91-6850ee4c-precleanup-qualified-evidence.json'
RUN='6850ee4c-154b-4834-9ed0-c3612db77724'
COMMIT='0ff2a910ce081a0c6e0c6a268d6f876b8e061a45'
TREE='886f85d4a919a8a04f85c8fe45a01e0a8801ba1c'
PACKET='1ec1f730e6023d22c52e93b750c91f96ea07b2337fe793dd3d1477cd383c4fc2'
CLAIM=('P0C-INSTALL-02', 'vector.FUNCTION-ACL-FAILURE-CLEANUP.adversarial')
ASSERTION_SHA='34db5106a123525087e33083c3917fb0cf0065d6c20f3d2060b2e8de5e8c60e9'
KIND='DERIVED_REVIEWED_INSTALL6850_PRECLEANUP_ONE_ASSERTION_ONLY'
PINS={'context/reconciliation/database-candidate-tests.json': 'bba9bef6b94e9f4974f2a3a0b19a3277df54ac04aa77ceaa6b70ffcf75d988b8',
 'context/reconciliation/foundation-sql-draft-access.json': 'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea',
 'context/reconciliation/foundation-sql-draft-models.json': 'd04bf44bd67dceda35199fd1ff1e494eed3016e80d180144018e879f5aee778d',
 'context/reconciliation/foundation-sql-verifier-access.json': 'f84421c4957fcb4cf7fa5b04d3b5f804f8810ee58da2c1529e98daba8ab36bde',
 'context/reconciliation/local-f0-assertions.json': '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558',
 'context/reconciliation/local-f0-catalog-eb2aae6-2e4f5d40-execution.json': '76923eea9f3a68cb6157a0ed23432662492d79c068a7b58be507309edbe3e452',
 'context/reconciliation/local-f0-cli-diagnostics-validation.json': '8bf070ea0473fa41cd815737de96920f70ecf6896bf9188c52d90dbd42ed6e7b',
 'context/reconciliation/local-f0-install-0ff2a91-6850ee4c-execution.json': 'fe69a4b0dc9c973e4aee851b8bebdda4f9b5346c5d7a95164215cf4c65e4bc74',
 'context/reconciliation/local-f0-install-0ff2a91-6850ee4c-precleanup-qualified-evidence.json': '912b8ed02988b58e5df0268b5c0038b987f265e658c730d6895ca8d947d45f76',
 'context/reconciliation/local-f0-install-controls-owned-source-phase-v5-source-validation.json': '5a24c1d3d648e263f7278b452efe4752982a9cc3e135cba351aafacfe3b5c52f',
 'context/reconciliation/local-f0-migration-tooling-validation.json': '83d079ae068a04aee70c2d307ba7352a58a20409aef47df4f6a8866c25c2ce33',
 'context/reconciliation/local-f0-native-catalog-acl-correction.json': '017c9ee8c46de01c8a70ffbd68c0c80c27a1508cf4f1887fffaafcdba8d54f85',
 'context/reconciliation/local-f0-native-catalog-metadata-diagnostics.json': '5acadf4bbcc01b6133ebc0c81cb72e806a2c3d6f3840fd8f752353bde9c1735d',
 'context/reconciliation/local-f0-native-catalog-text-correction.json': '83766af0fc699b88a56081ccebd59eff59b6c850678506f6ffe67c3d04b38565',
 'context/reconciliation/local-f0-native-catalog-validation.json': 'cbc26b6d1935ced05a03b3d186658864cb687de6b49af888c92c551976279d75',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/Catalog-explicit-recovery-decision-receipt.json': '59c9494895fe53a082bc5fa2800bd9e5c543a507305faacd6e8ca1ec35672aac',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/exact-one-claim-admission-plan.json': 'fe0d8719f0b3fa90ef758a4072e098ea5f1cbb0defb33da5fda62301daca3b4e',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/independent-final-actual-audit.json': 'e5dcfe07e8bfab6fe31cbe3ed31b5c6598014df32dee9d87234a3d7c3a0b3f01',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/normalized-record-inventory111.json': '5bf4b879b0bbdfaa685765e6b4b925a0d4bc7bc09f7e7de99d2c0e8528247fcd',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/prior638-status.json': '5ab0d974a02f7a99bbb92b30d8f55c5b9c50d1bd962dd0654467243f3b3f2e07',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/prior671-ledger.json': '8b7cd04a5681dc7d2b2996c20b896dc352af67e88f968f1ccc9250f9bdda0d64',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-final.log': 'c6302130b0caf02c6a22bf75b7c98e50f5d21df41ef0bd19cd79992c5b06b09a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-first.log': 'e6c9905279f7d2ef32f17d281c2dfeb522d71c17dc9b392e93829ae4b28601da',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/affected-legacy14-first.log': 'efea1ed51eeb5a6c8099bd040ef95bb699aee51bf37c2be0fe66addc9682160b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/author-review.json': 'b5e2289bbafd39517a384e4dd0ed050bcc4993f218a548ff04f0434231d785e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/before-preservation.json': 'c0bd370703855009125bb301433ea956b98e952d3fc3567bbc9e1ad686b34340',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/build_install_failed_precleanup_v5_source_draft_20261120.py.txt': 'ebf4c405492032d81160f35a48c6bd3c66b9a28b5966f72663352ec8d2ecb7f1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/check_install_failed_precleanup_v5_admission_20261120.py.txt': '348841a64c838bad1cd331ac9cea83f785b3d500813a505c4f898912db0d149a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-affected-checks.json': '6c348402be42cd85fde33cc07c609b9ec8476c2c1e9a51a089dbcd2fc1fd9bbf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-preservation-freeze.json': 'c868f89f7d8fa6b8a2c9269abc29357f25203384acd1df897a95c3e19c2c0bdb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-scope-and-preservation.json': 'c04cec00bad304399261afeb543499b3667de6e7831b1d1d8bf2380bcaa66d5c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-first.log': 'be08f5d5b3b929d9b15e09bc5f387132d19084db90b54410d608aa8e75ee9d9d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-second.log': '799815fa13fdb74a5e62102f1344a2d83ad02f2e3bd87a3f57881f0f2b01f617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused10-first.log': 'dcf5cb63afc26fc1d8c80da2ade2bf2a2c24dd55d3ecd04947dc6212dd48da7d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-focused-failure.json': '548b44c6e96525ea61ca246c691d625c2d362a9a5f45ca5b932a82ce86ea7193',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-process-mock-stage-bytes.py.txt': '1a04be27cc6f8acc36bf1f238f679bb519b2d7c28b81d53292d417049687c42b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'c146b8848116faf10de41d1a9d83e532e7d789d40083eabd41b400dff535a11d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': 'c1e7053ab9f4a65d4b4d33bbb21c25c3d6297d830227806c1c60c7eb273e8777',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': 'fc6bb6d6cdfdb484cb794801d64f112600323e1e389b77404538349bd9d18054',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer8-failure.json': '0bf0a8354db65bdd78c2bb5ccb70a96d7dabf7db93eaf17628a72c33c41074b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/reason.json': 'd33c07be2e74a0af8650d4f81790af26fabce8c2eaf2ca5451a5785acdec892c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/run-install-control-rehearsal-v5.py.txt': 'cd25fc81e171e76a52ad9f1967feff096829bd6e9c2d6037279b1179241c364f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/test_watch_install_independent_review_source_phase_v5.py.txt': '475f420e671b51a9dc9ee05131b257310a28834b77851feb91815a90d98c22f9',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_install_independent_review_protocol_source_phase_v5.py.txt': '394714a90b6ec2a94d2dc1d39e67fc35b258758a60e1cab2a283a51176c89d55',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_watch_install_independent_review_source_phase_v5.py.txt': '5b31fbfd089ce058a1dba8e9883e2e7bc5961343a5ca1d2eb067b9a5cb997434',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/watch-install-independent-review-source-phase-v5.py.txt': '40d1d706ae6011afe8fcd07c4817fb85beff28e229072a621241778952931a04',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/outcome.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/test-source.py.txt': '976434174edbb2d73783ea12846bf6c3980796a2887a229149ef8688274bdc62',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/namespace-and-snapshot-scope-supplements.json': 'e4891be9c3b07857258e3560967caa4b659fd5ff1b45fdad8514a220e59e13ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.json': 'cbc3a3d1f1a423b131d991b2c52b1899f8231b39b4e17dc5818e749a0344eaee',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.log': '035a516b234adb0e7eb9129bbcf01772d2569d4e371ecf73fe6199bec41d41c2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.json': '1e8db3d81aea01b6090aff4c97cf5418cbe1c30cedfb09a52c255b861486893f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.log': '6a574c18fe85772d26e868a5f4a527806d06d9228cea6a989795998c15fb0f22',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/owning8-final.log': '1b79ca2830a8cf940b7c381b700ae880c426702bee30baf1af07b0d2c4212324',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/pending-validation-before-final-evidence.json': '5ed7ac2dcc1df4360b247f1b366ca07e0d7d05b8e12b67dd78bdb7bf7859aa92',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/phase10-final.log': '3b118da9fb2286b6754d4b3604bedd278ffc6b955e56c7f0fece46b7d0337147',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/refresh_install_failed_precleanup_v5_draft_20261120.py.txt': '0418ed674f667061ac1e200257a7261ec1b4462bc4449339fe37fcc704df65a3',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/run_install_failed_precleanup_v5_final_affected_20261120.py.txt': '4979b9506867ed32cf4690bef7b9e8c5f57e1525f918ce8599814b036e0e4ac7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport-namespace-map.json': 'bb512a7b83b29fd93e485abe257470d4250919306f73ae6bbbcfe75a373883e2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.json': 'df07d84b0aac6dcff929df19c00c7eadb53bd390a7f54bd24e6722f7bbe7d6db',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.log': '4a1e4f76123e4cfaf64b8b057db9104b3dcf7a2c281d02fbbd3c07ab019473eb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.log': '3ef2f686aeafe33579bc208abc6bd610cf64cf81f0aea1d2aec98334523cc1e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport26-final.log': 'fa1609ab2dcc4bfd8b6f82797cbc0e97a2f76112f46cea4e0a9866f24324f112',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_Root_bounded_implementation_ACK_20261120.json': '966733cac75e8235cd0c0e53593cf0169181f2ec4f7912e9d4677b5f0067976c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_bounded_source_proposal_20261120.json': '337b34cdf5eddec2160d9cb5056bf13005b3064243bd95fc2075c1c431b876b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_independent_plan_review_20261120.json': '9e40127580ef6271c9947867b918fda1fffde0fd6e5a3496e1956cfcb83879ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'd4195896856ace2cae521245c59eb8c8eb361fe43faed7c7727fcfc19d9f76f7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-control-rehearsal-v5.py.txt': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-failed-precleanup-phase-v5.py.txt': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install-controls-coordinator-v5.md.txt': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_failed_precleanup_activation_v5.py.txt': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_independent_review_protocol_source_phase_v5.py.txt': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/prepare-install-control-rehearsal-v5.py.txt': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/run-install-control-rehearsal-v5.py.txt': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_install_independent_review_protocol_source_phase_v5.py.txt': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_run_install_control_rehearsal_v5.py.txt': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_watch_install_independent_review_source_phase_v5.py.txt': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/watch-install-independent-review-source-phase-v5.py.txt': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/execute_local_f0_install_controls_20261120_source_phase_v5.py.txt': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-install-controls-owned-source-phase-v5-source-validation.json': '2c93f4ed8a95440a925e7bce642f5079c5e9a822ac2443ed30f8532d15bfb5f6',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-final.log': 'c6302130b0caf02c6a22bf75b7c98e50f5d21df41ef0bd19cd79992c5b06b09a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-first.log': 'e6c9905279f7d2ef32f17d281c2dfeb522d71c17dc9b392e93829ae4b28601da',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/affected-legacy14-first.log': 'efea1ed51eeb5a6c8099bd040ef95bb699aee51bf37c2be0fe66addc9682160b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/author-review.json': 'b5e2289bbafd39517a384e4dd0ed050bcc4993f218a548ff04f0434231d785e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/before-preservation.json': 'c0bd370703855009125bb301433ea956b98e952d3fc3567bbc9e1ad686b34340',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/build_install_failed_precleanup_v5_source_draft_20261120.py.txt': 'ebf4c405492032d81160f35a48c6bd3c66b9a28b5966f72663352ec8d2ecb7f1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/check_install_failed_precleanup_v5_admission_20261120.py.txt': '348841a64c838bad1cd331ac9cea83f785b3d500813a505c4f898912db0d149a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-affected-checks.json': '6c348402be42cd85fde33cc07c609b9ec8476c2c1e9a51a089dbcd2fc1fd9bbf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-preservation-freeze.json': 'c868f89f7d8fa6b8a2c9269abc29357f25203384acd1df897a95c3e19c2c0bdb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-scope-and-preservation.json': 'c04cec00bad304399261afeb543499b3667de6e7831b1d1d8bf2380bcaa66d5c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-first.log': 'be08f5d5b3b929d9b15e09bc5f387132d19084db90b54410d608aa8e75ee9d9d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-second.log': '799815fa13fdb74a5e62102f1344a2d83ad02f2e3bd87a3f57881f0f2b01f617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused10-first.log': 'dcf5cb63afc26fc1d8c80da2ade2bf2a2c24dd55d3ecd04947dc6212dd48da7d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-focused-failure.json': '548b44c6e96525ea61ca246c691d625c2d362a9a5f45ca5b932a82ce86ea7193',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-process-mock-stage-bytes.py.txt': '1a04be27cc6f8acc36bf1f238f679bb519b2d7c28b81d53292d417049687c42b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'c146b8848116faf10de41d1a9d83e532e7d789d40083eabd41b400dff535a11d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': 'c1e7053ab9f4a65d4b4d33bbb21c25c3d6297d830227806c1c60c7eb273e8777',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': 'fc6bb6d6cdfdb484cb794801d64f112600323e1e389b77404538349bd9d18054',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer8-failure.json': '0bf0a8354db65bdd78c2bb5ccb70a96d7dabf7db93eaf17628a72c33c41074b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/reason.json': 'd33c07be2e74a0af8650d4f81790af26fabce8c2eaf2ca5451a5785acdec892c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/run-install-control-rehearsal-v5.py.txt': 'cd25fc81e171e76a52ad9f1967feff096829bd6e9c2d6037279b1179241c364f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/test_watch_install_independent_review_source_phase_v5.py.txt': '475f420e671b51a9dc9ee05131b257310a28834b77851feb91815a90d98c22f9',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_install_independent_review_protocol_source_phase_v5.py.txt': '394714a90b6ec2a94d2dc1d39e67fc35b258758a60e1cab2a283a51176c89d55',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_watch_install_independent_review_source_phase_v5.py.txt': '5b31fbfd089ce058a1dba8e9883e2e7bc5961343a5ca1d2eb067b9a5cb997434',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/watch-install-independent-review-source-phase-v5.py.txt': '40d1d706ae6011afe8fcd07c4817fb85beff28e229072a621241778952931a04',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/outcome.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/test-source.py.txt': '976434174edbb2d73783ea12846bf6c3980796a2887a229149ef8688274bdc62',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/namespace-and-snapshot-scope-supplements.json': 'e4891be9c3b07857258e3560967caa4b659fd5ff1b45fdad8514a220e59e13ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.json': 'cbc3a3d1f1a423b131d991b2c52b1899f8231b39b4e17dc5818e749a0344eaee',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.log': '035a516b234adb0e7eb9129bbcf01772d2569d4e371ecf73fe6199bec41d41c2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.json': '1e8db3d81aea01b6090aff4c97cf5418cbe1c30cedfb09a52c255b861486893f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.log': '6a574c18fe85772d26e868a5f4a527806d06d9228cea6a989795998c15fb0f22',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/owning8-final.log': '1b79ca2830a8cf940b7c381b700ae880c426702bee30baf1af07b0d2c4212324',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/pending-validation-before-final-evidence.json': '5ed7ac2dcc1df4360b247f1b366ca07e0d7d05b8e12b67dd78bdb7bf7859aa92',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/phase10-final.log': '3b118da9fb2286b6754d4b3604bedd278ffc6b955e56c7f0fece46b7d0337147',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/refresh_install_failed_precleanup_v5_draft_20261120.py.txt': '0418ed674f667061ac1e200257a7261ec1b4462bc4449339fe37fcc704df65a3',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/run_install_failed_precleanup_v5_final_affected_20261120.py.txt': '4979b9506867ed32cf4690bef7b9e8c5f57e1525f918ce8599814b036e0e4ac7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport-namespace-map.json': 'bb512a7b83b29fd93e485abe257470d4250919306f73ae6bbbcfe75a373883e2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.json': 'df07d84b0aac6dcff929df19c00c7eadb53bd390a7f54bd24e6722f7bbe7d6db',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.log': '4a1e4f76123e4cfaf64b8b057db9104b3dcf7a2c281d02fbbd3c07ab019473eb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.log': '3ef2f686aeafe33579bc208abc6bd610cf64cf81f0aea1d2aec98334523cc1e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport26-final.log': 'fa1609ab2dcc4bfd8b6f82797cbc0e97a2f76112f46cea4e0a9866f24324f112',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_Root_bounded_implementation_ACK_20261120.json': '966733cac75e8235cd0c0e53593cf0169181f2ec4f7912e9d4677b5f0067976c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_bounded_source_proposal_20261120.json': '337b34cdf5eddec2160d9cb5056bf13005b3064243bd95fc2075c1c431b876b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_independent_plan_review_20261120.json': '9e40127580ef6271c9947867b918fda1fffde0fd6e5a3496e1956cfcb83879ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'd55eb0ce64b514832625b008b172ce87998829848f31b416d3e4bc6607b09c5e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-control-rehearsal-v5.py.txt': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-failed-precleanup-phase-v5.py.txt': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install-controls-coordinator-v5.md.txt': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_failed_precleanup_activation_v5.py.txt': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_independent_review_protocol_source_phase_v5.py.txt': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/prepare-install-control-rehearsal-v5.py.txt': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/run-install-control-rehearsal-v5.py.txt': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_install_independent_review_protocol_source_phase_v5.py.txt': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_run_install_control_rehearsal_v5.py.txt': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_watch_install_independent_review_source_phase_v5.py.txt': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/watch-install-independent-review-source-phase-v5.py.txt': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/execute_local_f0_install_controls_20261120_source_phase_v5.py.txt': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': 'ed6be9d0d62890ef25782bf6e566395d08b8572e1e0dbe76d4ebde181e22121e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/pin_local_f0_install_controls_plan_20261120_source_phase_v5.py.txt': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/README.md': 'bfd38911a7aa54e36f21ae4f48601758ab7df2228815e873264ced3ac54af366',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/authority-observe.sql': 'b5791265492feb42a4e68b5538d41f33c1b3a77518e8b62f48ce3852b7f4b3e5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/bootstrap.sql': '05c7d98aac1a13158ac2e6a28dcf7b377de8e1c881f347155421e5dd24e39893',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/canonical/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/division_failure/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/finalize.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/fixtures.json': '3992a73c920a510f18ee903e15d74f98c42720266eb4ff26abd61478e6c398e5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/fresh-observe.sql': '674f92c95bbb627ba74abbc91dea0067ffd7cb25a01f1537487a21f354c09138',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/inactive-observe.sql': '3c81794dce2ef746695500f7539313f27fefd0590f12275deb8f471aef8bb92f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/inventory.sql': '4364890304d7c112b69c1e25d20a6ccbbf99bf7b32c44183403bb216a5c7f453',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/late_function_grant/20261117000100_f0_local_initial/migration.sql': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/ledger-observe.sql': '42ac58118727dbdc03c54e5ad6fb3cbedb3187f2ff2063eac4258336f0dfbb3c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/rearm.sql': '40a2f1a0b2472a16af7b6b5544e330486b296c2265dba726c6264fd190f6b94b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/check-install-control-rehearsal-v5.py': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/check-install-failed-precleanup-phase-v5.py': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/install_failed_precleanup_activation_v5.py': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/install_independent_review_protocol_source_phase_v5.py': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/prepare-install-control-rehearsal-v5.py': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/install-controls-coordinator-v5.md': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/run-install-control-rehearsal-v5.py': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/test_run_install_control_rehearsal_v5.py': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/test_watch_install_independent_review_source_phase_v5.py': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/watch-install-independent-review-source-phase-v5.py': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/test_install_independent_review_protocol_source_phase_v5.py': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/check_local_f0_install_controls_operation_source_phase_v5.py': 'd55eb0ce64b514832625b008b172ce87998829848f31b416d3e4bc6607b09c5e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/execute_local_f0_install_controls_20261120_source_phase_v5.py': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/local_f0_install_controls_operation_steps_source_phase_v5.py': 'ed6be9d0d62890ef25782bf6e566395d08b8572e1e0dbe76d4ebde181e22121e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/pin_local_f0_install_controls_plan_20261120_source_phase_v5.py': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/prepare_local_f0_install_controls_plan_source_phase_v5.py': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_independent_catalog_focused_20261120.json': '93f9ed3ba3a02cbd644efabe575e62b097b775d8e07c097f1ed8fbd80cece152',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_independent_catalog_inventory_20261120.json': '6d3b008d8c23da635d4b54ed31af5b794576d985d43937635ca4c8f32a2c7a71',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_independent_source_review_catalog_HOLD_20261120.json': '2354c454e49d243d8e7e0620a5cecee5dd65505ca5da8971ebdf996c70d9534d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_parent_final_reference_Root_bounded_fix_ACK_20261120.json': '83361cadbe7a8585b03a79cc6203362f6814716c2aa0c082288c917a21dd5727',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_parent_reference_order_independent_probe_20261120.json': '0aacfabe7617d75acd4ed4430cba52a836abc5d13d80ac0ad0800bd5ffb4c1bf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/original-freeze-manifest.json': '6113911c34ba2b6265d35ecb2e8fb4217277ab18fb13b1de91a778bfe10fda0c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/preservation.json': '09b016ee5323f9bc5f76206c86130c3d6a5b1035ab9d3bdc7628f4e7b76eb65a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/probe_install_v5_parent_reference_order_catalog_20261120.py': 'bc2b0450a7dada113299a34a1adb2c3c2ce1782f1086b44ffd4abf580a978822',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': '5dd5ece0f0ff86ce59411f4a4587100a743df05e82a807cdf6ce73765532e08b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/check_install_v5_parent_final_reference_fix1_20261120.py.txt': 'fccb54ee7bc10a1a3ceb3d3df7333d302e8a105bf12d2f6df60380744a449e9d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-affected16-first.json': '5da6bb60bf720927256548dfb3e7746c937d1a63c86de7c7917a6fd9df543819',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-affected16-first.log': 'cd74c062bdeaf894001a1ef4c13b6c157b4b3fbafdb589450bca7ae71038b1af',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-author-review.json': '43ded06f472e76aa9a8f1d723510ee9947e41955fe17f7a72f5f5b9e916adc66',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-final.json': '4b9756047f1ec9d43500e2009c7375355078ae6d159e974cc7158a1e488de76e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-final.log': 'b0a111c1f35c46c67a145f184c4e81594292bf1c1bee171f3ab418bb72d7c5b4',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-first.json': 'edb81386fb2835a45508d7f385e0dd6da8d3d1173b07c97b2cf91966fa4da49a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-first.log': '1d5fe0b255b287a9ff63921972198fea07c5b5a0313dc008f5de9f10e09de238',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-static-AST-scope.json': '004bfe44b2a09caacdccef8a65a382764d725e986282f030f74118f5c62dac29',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-static-progress.json': '725816c4ea5b196a36d2fdbea0264a53f320685f435f1cf15c1b3f7ef7eecb4e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/pending-validation-before-final-fix-evidence.json': 'a9fa60bbf535ee5d0706f7e316d792ddc1c219eedbe2186c7c7f882b3ab29662',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/run_install_v5_parent_final_reference_fix1_affected_20261120.py.txt': 'd6828a55522f56c6fc851e23ff52d1661d171a52814370a641775f71c9e6493a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/pin_local_f0_install_controls_plan_20261120_source_phase_v5.py.txt': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/Root-source-admission-helper.py.txt': 'c63963861987fff84e0aa8cd5183b0cacdaab6d2268d90e64b29eed6ff46febf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/Root-source-closure-fix1.json': '287800f0c6dfb9f9eb37f9e7c98512dafc8bf5caa834072f2bde1ccfc7ce913e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/frozen-reviewed-delivery-fix1.json': 'cde49587d2aa856c93efad9e8b8e6ebbd7812f7dcf8753ea5a5bc3330843964e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/independent-Catalog-source-closure-fix1.json': '5b82e9585e8e29ec8b48d0a470e222915424cfa78ec2898f5213b83f22d8de1b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/validation-before-Root-closure-fix1.json': '95eefcacb8805d1bd345be33b77af2e67f0b6d098b8393721a22863aa2256b92',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-actual-launch-environment.json': '0509256b0cc0ed525348013f155a0cc5e5a56e62811571592d57d73d92ba9485',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-exact-literal-preflight.json': '795f720fa10dfd21c476192b39698d68cd8f2a942ef76e42fdf6b77fcad08a55',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-independent-cleanup-helper.py.txt': '83dac1721f53069b51c2a769bb0dc076fd02039fd0d9dd887ba01d0616844894',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-launcher.py.txt': '7ac775f5011feb86ebef1f3de780da68c160796d5e655691a8c5f0c653837d02',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-preflight-helper.py.txt': 'c7aa3a5f4bb1b9a856ae69ea58728311d35be5b3db8e37b51a13d6e77d1e3853',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-preservation-helper.py.txt': '99f312fa9162ee50eb615e1ac026d62d4a983abc769f2db6b0add69883d582ab',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/Root-helper-before-cleanup-schema-correction.py.txt': '135a54878c76dbf55249dc47647ea5b6d782810becb9e495d24957593b81e791',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/first-helper.py.txt': '542ca8738681b2d6076b0bec9140f60a2e8d946a2bcedf2d5259e38ef72a75a7',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/first-interface-failure.log.txt': 'ac43527f0d2ef1311d6deec12e16466d921294bdee86a14db90e5cd29a4ebc17',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/independent-closed-audit-helper.py.txt': 'c256d02b482b8e2bebc206b5f8bed6b397f5a4115c95ac5297a8620d86a7995a',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/independent-live-sealed-audit-helper.py.txt': 'f49113f648623140ecb1965a95c8baed18b037713c59aa42556da99f07bb54b7',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/second-helper.py.txt': '761a8854870fbcf03f36436900f25a4dadb2eac57d2a445a64490c508e0095df',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/second-interface-failure.log.txt': '2e8fba421097fe1271c031e438df1fca12c169938fbbec39073651206c87975e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/third-completed-audit.log.txt': '2b89e902c6febbba1e2ffeeac01305875a2b80a858e8f72a7bd5a7ff5f5ef7c0',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/bounded-single-claim-admission-plan.json': 'fe0d8719f0b3fa90ef758a4072e098ea5f1cbb0defb33da5fda62301daca3b4e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-comparison.json': '58bef4aeb4cbd592d5df85397d29d066acd3cdb63b4b4e78c69c669a7cd8516e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-evidence.json': '6aec870993b1c94e941d91f0028e707013adf58c4602fd342baa955814ab54ee',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-registration.json': '9df79c1de87f730f03368ee6be53015d2c73363db7edc87e30882b770ffd0209',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-native-after-ledger.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-native-after-oracle.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/independent-review-outer-identity.json': '480ed34e69e867469ed80933562bf7e3cd2f0b64fc3e5df2cf4a6e9245f191aa',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-recovery-approval.json': 'c294fa71aa9d491ab696e7221854d07b4d70fa928bb420f3f0f374e87073d4ec',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-review-child-snapshot.json': 'f60859c7c105de763b0fc85a8a00b4c143c0754f4b5ed88c213c6e0efe101056',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-review-child-v2-evidence.json': 'c0eab0c1ccd1342a49eea49577a89d02e8ea80970119595f1fcb584101ee5c2d',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-review-ready.json': 'ff4b4ee79d29c3c937bb8eb1615d6af6a7d68169de4b13c379b7fce92e83613d',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/rollback-proof-for-review.json': 'f0eefef1c583485d0c3624b064ba1f04dc133d7258e5e0cd4c6782b848742924',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-coordinator-run-plan.json': '591bb587546afcd5e4d2772919b9299f9540e163357f1e80748554951d93ed9a',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-native-summary.json': '8ae2bf24ac65f1a7977baaa5e508f20da8c4f9663965afd08c8d31fad73d6a04',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-semantic-parity.json': '79736c166f527a15931a19de28a6c87b005e878adbae01448fab5d7e45eb39d8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-catalog-comparison.json': 'f7daa67ff3ec72667dd2b6073d66a6541b9c5231796807c1a2d8e5663217611c',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-install-failure-proof.json': 'db4a8c65a567987bf6f278f4ab9e6e977d248949a3f0c0518304ceecd88c8c56',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-comparison.json': '3253528643b4b2297520dc6c2c4b2fce15bec905b4eff7fd41d62fee44dd5094',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-evidence.json': 'fb5458d4dff72a1156ddbc3ec7013192d45b3fb9ed8440db820434cea1e16ce5',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-observation.json': '2652266dfce9e40c1ac0ebd135b28d2dbdf26b7d3395c7556b64b19f85287301',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-registration.json': 'e562cb0c0ef54632ecf79c9457d64d6eb5e64ac234a86541c0c375fbb1780dc8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-native-after-ledger.json': '24c5d8392ab622e1a0f27c5bca84c8dfa8c64fd9f372d8125ee37616a3178a72',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-native-after-oracle.json': '24c5d8392ab622e1a0f27c5bca84c8dfa8c64fd9f372d8125ee37616a3178a72',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-native-before.json': '24c5d8392ab622e1a0f27c5bca84c8dfa8c64fd9f372d8125ee37616a3178a72',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-evidence.json': 'a37b829fd6b917c983fc90692c41c0bd31d4c62b388fac265ac7f23e006ecd76',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/run-evidence.json': 'eada43073ac1d0496ee922230ca05cc49cca8f0777a87ce5725689d47599f096',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/set-private-acl.ps1.txt': 'd5ef58e51c12b4371601557f027a44e9ca206b81444724f8aab65365bf9c057f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/historical-first-admission-plan.json': 'e7fd7fcb49d4de42897e7e3d1b1951f15d9dd1af0e7d65f118b215ecf0a4cc1c',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/historical-first-audit.json': '919f1b73eb656e54211047d1c1701db4f2c07358bc8bb2c8f2650e51d50c2ada',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-cleanup.json': 'd8880f065a01842960c85b1654110dc4bcc26f3ebfe312583c9083decf5072bc',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-closed-final-audit.json': 'e5dcfe07e8bfab6fe31cbe3ed31b5c6598014df32dee9d87234a3d7c3a0b3f01',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-exact-literal-review.json': '284a95d991f3a0ea82171725d67c9b5ccd9092e3b1f4f61a42dac606466654fa',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-explicit-seven-field-decision-receipt.json': '59c9494895fe53a082bc5fa2800bd9e5c543a507305faacd6e8ca1ec35672aac',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-final-audit-receipt.json': '27f5576b4a92aeb9015830ad7fe273b6099bfb0eebb00168ae188125236862f0',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-live-sealed-evidence-review.json': '4dce88c29abf7d4b8b2eee5e53a1ca086963bfd47920b91ff8c36b88cbe3a92e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-original-READY-receipt.json': '60e831b7ff28d73d0cca698819e1433160227f42d2e04aca267427349e47261f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-watch-ARMACK.json': 'f034d7c7b7cdb71321f3d0ee0a3cb18b7f911409c00cb19ce0840d01d4906b0e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-watch-arming.json': '643dac5f5717b5ad1fadbb5900fea26c709a60e5542d31dc354f0a781fb96091',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/canonical-migration-manifest.json': '6deae8fc47520614a11fbd2fee39003edded0b4ed9f32ad5d28c7122e33d27b6',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/division_failure-migration-manifest.json': 'fe3bd79ae3d330c7c0c5b035a37ddfc64a01587b4e307912fffd415484ee04c2',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/division_recovery-migration-manifest.json': '1ebf7aa1cf103fe2ac993177a3978446dd396acd6ce6f6abe1402a199e44bb22',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/late_function_grant-migration-manifest.json': '0163daf39eabbc932d04db15b14807854f1ec01da1dba923a9bd0e6cc2298a10',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/operation-manifest-before-operational-review.json': '86e9c2fd07b553a563b69f6c6962d354ad8c43717abca9e95333ddf1a69d3d08',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/operation-manifest-before-source-pin.json': '6cf1a7771cc80535201d48f8507736eebd7aae7f26c014d5df5d77129190d928',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/operation-manifest.json': '98a2f53b88af97f308c2005d82708f1e0e624bc8546d705b64894e33efd320b9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/migration-manifest.json': '6deae8fc47520614a11fbd2fee39003edded0b4ed9f32ad5d28c7122e33d27b6',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-code-only.tar.gz': '1c110be54a815364ace687a95d27ee7cef9c360ea662768e54783508371ebcad',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/foundation/history-manifest.json': '6216d17b7cf9cf1835fe08c8db2427981fdf429d339a242736d566bf373ff64e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/migration-manifest.json': 'fe3bd79ae3d330c7c0c5b035a37ddfc64a01587b4e307912fffd415484ee04c2',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-code-only.tar.gz': '04ca98ac20727fd306631916c8b8a7983ed4637a4c71994655b411babe7e576f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/foundation/history-manifest.json': 'e5534a21c8a86b26662e30fef1292d76acc12f77aea66a14defc6c5e128e283a',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/migration-manifest.json': '1ebf7aa1cf103fe2ac993177a3978446dd396acd6ce6f6abe1402a199e44bb22',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-code-only.tar.gz': '75e9d9a734f508fe7a059a6d5ef949a30ac44f6f3a5616135be7f1ead00237b9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/foundation/history-manifest.json': '07edbd157c3cfbceb05803d20c1590a9ddd3a9800983b1f77cdecd93ed1502a3',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/migration-manifest.json': '0163daf39eabbc932d04db15b14807854f1ec01da1dba923a9bd0e6cc2298a10',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-code-only.tar.gz': 'e91ea4d8215875b1772eca0830b7c03267c15578e9ca1f25fe353ae46e09d7b9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/foundation/history-manifest.json': 'eca5e28cb0424df08bf0377821107004a6bf22f3b4a4bfee7bd9ac3667b559f7',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/eb2aae6-native-catalog-2e4f5d40/source-prefix-analysis.json': 'b3931b71fe3d0560d6864ce20aa64cc88086563c4399a34e4b442ed108c4fc4d',
 'context/reconciliation/local-f0-server-diagnostics-validation.json': '560504eea761a06864edea01fba42e2e2a9a086ecfaab583309868f8f2f9c027',
 'context/reconciliation/local-f0-tooling/linux-tooling-manifest.json': 'e8fcce8f3ed4eaad0f7834e908166a0947b997e75513d589078f0d79c9a940d0',
 'context/reconciliation/local-f0-tooling/prisma-tools-closure.json': '610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b',
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
 'review-output/install-control-rehearsal-v3/division_failure/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'review-output/install-control-rehearsal-v5/README.md': 'bfd38911a7aa54e36f21ae4f48601758ab7df2228815e873264ced3ac54af366',
 'review-output/install-control-rehearsal-v5/authority-observe.sql': 'b5791265492feb42a4e68b5538d41f33c1b3a77518e8b62f48ce3852b7f4b3e5',
 'review-output/install-control-rehearsal-v5/bootstrap.sql': '05c7d98aac1a13158ac2e6a28dcf7b377de8e1c881f347155421e5dd24e39893',
 'review-output/install-control-rehearsal-v5/canonical/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'review-output/install-control-rehearsal-v5/division_failure/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'review-output/install-control-rehearsal-v5/finalize.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'review-output/install-control-rehearsal-v5/fixtures.json': '3992a73c920a510f18ee903e15d74f98c42720266eb4ff26abd61478e6c398e5',
 'review-output/install-control-rehearsal-v5/fresh-observe.sql': '674f92c95bbb627ba74abbc91dea0067ffd7cb25a01f1537487a21f354c09138',
 'review-output/install-control-rehearsal-v5/inactive-observe.sql': '3c81794dce2ef746695500f7539313f27fefd0590f12275deb8f471aef8bb92f',
 'review-output/install-control-rehearsal-v5/inventory.sql': '4364890304d7c112b69c1e25d20a6ccbbf99bf7b32c44183403bb216a5c7f453',
 'review-output/install-control-rehearsal-v5/late_function_grant/20261117000100_f0_local_initial/migration.sql': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f',
 'review-output/install-control-rehearsal-v5/ledger-observe.sql': '42ac58118727dbdc03c54e5ad6fb3cbedb3187f2ff2063eac4258336f0dfbb3c',
 'review-output/install-control-rehearsal-v5/rearm.sql': '40a2f1a0b2472a16af7b6b5544e330486b296c2265dba726c6264fd190f6b94b',
 'review-output/native-catalog/README.md': '89e82bb70f53d6e959109c1e249bb4dda0101d22470d68211715baf5b1c74388',
 'review-output/native-catalog/expected.json': '9ad2129c9b7b7b5fd99f2088ae94215326f6ccbf40550945694c44538d8d0976',
 'review-output/native-catalog/expression-oracle-plan.json': 'cce4b19c1931472841de2fec2662fa4b002278b275341815782078689a1af36f',
 'review-output/native-catalog/expression-oracle.sql': '74d585741e1e097ac0614621b86c7ec97673697eb7dde344023e1dbe0ca613d2',
 'review-output/native-catalog/public-schema-registration.json': 'f0a46eef94da5f4836f46e64fe3a1c11a700fc158d40e36381e30bbdc0ec28d3',
 'review-output/native-catalog/source-pins.json': 'a0e9c36eecf61b1d4ce717744c29f4b72424ecd8d9db5ce0519b6bdaf9f58d00',
 'scripts/assemble-foundation-sql-review.py': '136489b5fb966085020128bfbd7140dad5e0b340a2312319d346305311fc212f',
 'scripts/check-first-rehearsal-mocks.py': '777d9d74788c37c9b20891196180708400e4f58991026075e60bb6bc74a96adf',
 'scripts/check-install-control-rehearsal-v5.py': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'scripts/check-install-failed-precleanup-phase-v5.py': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'scripts/check-local-f0-migrate.py': '59d890c145e1f14a62e296fba0139eaa22ab728b70fa76a7dbd7dc3883222a14',
 'scripts/check-migration-server-diagnostics.py': 'cb3ded2eaf6c1532691a41af241897b11072907c37aaeb2d3f2f1478da157163',
 'scripts/check-native-catalog-review.py': '05d39953bd26c61ef7d414a53bb5c0bc65cb2e59ec8513e17230ad5f7e4ef859',
 'scripts/check-trigger-row-shapes.py': '7e6c851630a65c9e07685138e03eca5d4fd5404e8a4bb2b36895e34069d52ce9',
 'scripts/database-candidate-correction-rules.py': '6b79a14ffa77c450c3864ba5e2d930d61d5a427a6b0c11545e1afdd37ccaabb3',
 'scripts/install_control_protocol_v2.py': '6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f',
 'scripts/install_failed_precleanup_activation_v5.py': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'scripts/install_independent_review_protocol_source_phase_v5.py': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'scripts/prepare-database-candidate-review-assets.py': 'dcb1544afc39cffbd9a8b052749f544c7531ff3dee2ff9cc738fd38d8d3bc9ed',
 'scripts/prepare-first-rehearsal.py': 'b03f4b7fda4e60ff7bafc2b6a7463d7bb9a3ee7bffc9f4e6c8f840f99b4116ce',
 'scripts/prepare-install-control-rehearsal-v5.py': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'scripts/prepare-local-f0-history.py': '33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8',
 'scripts/prepare-native-catalog-review.py': 'cef4f4f191e478593a679e9b86c7eee410531b01501a896c0b6f0e1bc1ac4fa2',
 'scripts/prepare-rehearsal-diagnostics.py': '598bc556999a16f303171003324be8763cb00a0fff2bb54de8a1195e1e7c852b',
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
 'scripts/sql-review/install-controls-coordinator-v5.md': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'scripts/sql-review/install_ledger_proof_v3.py': '44211b9a783271dd336c03df9104686980e528575181365583aca214ca44dc05',
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
 'scripts/sql-review/run-install-control-rehearsal-v5.py': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'scripts/sql-review/run-local-f0-migrate.py': '4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f',
 'scripts/sql-review/test_catalog_collector_acl.py': 'd9ac90cb8c335bd70b04056e422692c55bf73569ef109d3f8fb2bd73e9e1b57b',
 'scripts/sql-review/test_catalog_collector_text.py': 'fe7a29132b7d69b69213f61ccfda3e14a7339735c202f3cae1334c92dc6e24a7',
 'scripts/sql-review/test_catalog_expression_oracle.py': 'a758a17b8cd92922e7a599dc06679e6309dc107028c151387e533dcf8a5f5c85',
 'scripts/sql-review/test_catalog_manifest.py': '633e4f8c8f3b93d7e44d7c8abff7aa5ca1f3caa063cc354d592d1913d4ba9750',
 'scripts/sql-review/test_compare_native_catalog.py': '38d0e26ac030a1024c739c8ea79e0c653b3f0bf9aee54e9815bf314b8887ce37',
 'scripts/sql-review/test_install_ledger_proof_v3.py': 'bd34a3fa2c724988661e8cddccf1f9272ad53035d98fe5e02fee3a7407fcff8a',
 'scripts/sql-review/test_local_image_identity.py': '0edae319a544aaaa8ed112e2ec477fe7ac428b58a7970ca8cd0e33ff006abe93',
 'scripts/sql-review/test_pg17_catalog_rules.py': 'c6879cd715df8bb45b26bbeec90352189e339d87be2f37c869cf471e42cfbb4a',
 'scripts/sql-review/test_prisma_ledger_proof.py': '62685fbff83d42cad600de2d1f387647737a42bd5cffc50c2240eb1c66006095',
 'scripts/sql-review/test_run_install_control_rehearsal_v5.py': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'scripts/sql-review/test_watch_install_independent_review_source_phase_v5.py': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'scripts/sql-review/watch-install-independent-review-source-phase-v5.py': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'scripts/test_install_independent_review_protocol_source_phase_v5.py': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc'}
AUDIT_PINS={'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/Catalog-explicit-recovery-decision-receipt.json': '59c9494895fe53a082bc5fa2800bd9e5c543a507305faacd6e8ca1ec35672aac',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/exact-one-claim-admission-plan.json': 'fe0d8719f0b3fa90ef758a4072e098ea5f1cbb0defb33da5fda62301daca3b4e',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/independent-final-actual-audit.json': 'e5dcfe07e8bfab6fe31cbe3ed31b5c6598014df32dee9d87234a3d7c3a0b3f01',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/normalized-record-inventory111.json': '5bf4b879b0bbdfaa685765e6b4b925a0d4bc7bc09f7e7de99d2c0e8528247fcd',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/prior638-status.json': '5ab0d974a02f7a99bbb92b30d8f55c5b9c50d1bd962dd0654467243f3b3f2e07',
 'context/reconciliation/local-f0-operation-sources/install-6850-precleanup-evidence-v1/prior671-ledger.json': '8b7cd04a5681dc7d2b2996c20b896dc352af67e88f968f1ccc9250f9bdda0d64'}
ASSET_PINS={'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-actual-launch-environment.json': '0509256b0cc0ed525348013f155a0cc5e5a56e62811571592d57d73d92ba9485',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-exact-literal-preflight.json': '795f720fa10dfd21c476192b39698d68cd8f2a942ef76e42fdf6b77fcad08a55',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-independent-cleanup-helper.py.txt': '83dac1721f53069b51c2a769bb0dc076fd02039fd0d9dd887ba01d0616844894',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-launcher.py.txt': '7ac775f5011feb86ebef1f3de780da68c160796d5e655691a8c5f0c653837d02',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-preflight-helper.py.txt': 'c7aa3a5f4bb1b9a856ae69ea58728311d35be5b3db8e37b51a13d6e77d1e3853',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/Root-preservation-helper.py.txt': '99f312fa9162ee50eb615e1ac026d62d4a983abc769f2db6b0add69883d582ab',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/Root-helper-before-cleanup-schema-correction.py.txt': '135a54878c76dbf55249dc47647ea5b6d782810becb9e495d24957593b81e791',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/first-helper.py.txt': '542ca8738681b2d6076b0bec9140f60a2e8d946a2bcedf2d5259e38ef72a75a7',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/first-interface-failure.log.txt': 'ac43527f0d2ef1311d6deec12e16466d921294bdee86a14db90e5cd29a4ebc17',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/independent-closed-audit-helper.py.txt': 'c256d02b482b8e2bebc206b5f8bed6b397f5a4115c95ac5297a8620d86a7995a',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/independent-live-sealed-audit-helper.py.txt': 'f49113f648623140ecb1965a95c8baed18b037713c59aa42556da99f07bb54b7',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/second-helper.py.txt': '761a8854870fbcf03f36436900f25a4dadb2eac57d2a445a64490c508e0095df',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/second-interface-failure.log.txt': '2e8fba421097fe1271c031e438df1fca12c169938fbbec39073651206c87975e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/audit-history/third-completed-audit.log.txt': '2b89e902c6febbba1e2ffeeac01305875a2b80a858e8f72a7bd5a7ff5f5ef7c0',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/bounded-single-claim-admission-plan.json': 'fe0d8719f0b3fa90ef758a4072e098ea5f1cbb0defb33da5fda62301daca3b4e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-catalog-comparison.json': '34d94ba869e1dc969bec09d70d2c74430e9d3af5f9d93bc39dcff67e9a983c0e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-comparison.json': '58bef4aeb4cbd592d5df85397d29d066acd3cdb63b4b4e78c69c669a7cd8516e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-evidence.json': '6aec870993b1c94e941d91f0028e707013adf58c4602fd342baa955814ab54ee',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-observation.json': '5a3d33491366fb9587bcc4a167efa4e38bda170b7b3291c022f28676dbdd94b3',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-ledger-registration.json': '9df79c1de87f730f03368ee6be53015d2c73363db7edc87e30882b770ffd0209',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-native-after-ledger.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-native-after-oracle.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-native-before.json': 'e2bc04014b3f3d57ac6669d3364cc15162d923f1fd29ccb782bdc809f7a861f8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-evidence.json': 'c3e91a70099256f5edbce4678193c7d228bdcbbc7cd60c2c711887b773011bc3',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/canonical-text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/independent-review-outer-identity.json': '480ed34e69e867469ed80933562bf7e3cd2f0b64fc3e5df2cf4a6e9245f191aa',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-recovery-approval.json': 'c294fa71aa9d491ab696e7221854d07b4d70fa928bb420f3f0f374e87073d4ec',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-review-child-snapshot.json': 'f60859c7c105de763b0fc85a8a00b4c143c0754f4b5ed88c213c6e0efe101056',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-review-child-v2-evidence.json': 'c0eab0c1ccd1342a49eea49577a89d02e8ea80970119595f1fcb584101ee5c2d',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/independent-review-ready.json': 'ff4b4ee79d29c3c937bb8eb1615d6af6a7d68169de4b13c379b7fce92e83613d',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/rollback-proof-for-review.json': 'f0eefef1c583485d0c3624b064ba1f04dc133d7258e5e0cd4c6782b848742924',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-coordinator-run-plan.json': '591bb587546afcd5e4d2772919b9299f9540e163357f1e80748554951d93ed9a',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-native-summary.json': '8ae2bf24ac65f1a7977baaa5e508f20da8c4f9663965afd08c8d31fad73d6a04',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-semantic-parity.json': '79736c166f527a15931a19de28a6c87b005e878adbae01448fab5d7e45eb39d8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-acl-preflight.json': 'b1dffe67c99d83c46073c8db1f5e14bbda1b5dc0ed053be56d56a67a6018f3c8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-catalog-comparison.json': 'f7daa67ff3ec72667dd2b6073d66a6541b9c5231796807c1a2d8e5663217611c',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-install-failure-proof.json': 'db4a8c65a567987bf6f278f4ab9e6e977d248949a3f0c0518304ceecd88c8c56',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-comparison.json': '3253528643b4b2297520dc6c2c4b2fce15bec905b4eff7fd41d62fee44dd5094',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-evidence.json': 'fb5458d4dff72a1156ddbc3ec7013192d45b3fb9ed8440db820434cea1e16ce5',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-observation.json': '2652266dfce9e40c1ac0ebd135b28d2dbdf26b7d3395c7556b64b19f85287301',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-ledger-registration.json': 'e562cb0c0ef54632ecf79c9457d64d6eb5e64ac234a86541c0c375fbb1780dc8',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-native-after-ledger.json': '24c5d8392ab622e1a0f27c5bca84c8dfa8c64fd9f372d8125ee37616a3178a72',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-native-after-oracle.json': '24c5d8392ab622e1a0f27c5bca84c8dfa8c64fd9f372d8125ee37616a3178a72',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-native-before.json': '24c5d8392ab622e1a0f27c5bca84c8dfa8c64fd9f372d8125ee37616a3178a72',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-closure.json': '89067a06862e197fd49f3aed1e3f18bfc93d6a6c2035f9cdfc85a57036257ab9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-evidence.json': 'a37b829fd6b917c983fc90692c41c0bd31d4c62b388fac265ac7f23e006ecd76',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-preflight.json': 'e64b96e2f73e7a6d369d61c09301dc7c986c08bcd1cf95af06c6ab9756bcbe66',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-oracle-results.json': 'd7f91fb358b73d3f36acde73ec730c41259009c1e0f06931ded2a7d44510f995',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/recovered-text-preflight.json': '176676da1274c55ec6f8800089b61d1c5249c44ed52b3ecfbcf2c8edf6a3cda1',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/run-evidence.json': 'eada43073ac1d0496ee922230ca05cc49cca8f0777a87ce5725689d47599f096',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/set-private-acl.ps1.txt': 'd5ef58e51c12b4371601557f027a44e9ca206b81444724f8aab65365bf9c057f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/historical-first-admission-plan.json': 'e7fd7fcb49d4de42897e7e3d1b1951f15d9dd1af0e7d65f118b215ecf0a4cc1c',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/historical-first-audit.json': '919f1b73eb656e54211047d1c1701db4f2c07358bc8bb2c8f2650e51d50c2ada',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-cleanup.json': 'd8880f065a01842960c85b1654110dc4bcc26f3ebfe312583c9083decf5072bc',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-closed-final-audit.json': 'e5dcfe07e8bfab6fe31cbe3ed31b5c6598014df32dee9d87234a3d7c3a0b3f01',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-exact-literal-review.json': '284a95d991f3a0ea82171725d67c9b5ccd9092e3b1f4f61a42dac606466654fa',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-explicit-seven-field-decision-receipt.json': '59c9494895fe53a082bc5fa2800bd9e5c543a507305faacd6e8ca1ec35672aac',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-final-audit-receipt.json': '27f5576b4a92aeb9015830ad7fe273b6099bfb0eebb00168ae188125236862f0',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-live-sealed-evidence-review.json': '4dce88c29abf7d4b8b2eee5e53a1ca086963bfd47920b91ff8c36b88cbe3a92e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-original-READY-receipt.json': '60e831b7ff28d73d0cca698819e1433160227f42d2e04aca267427349e47261f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-watch-ARMACK.json': 'f034d7c7b7cdb71321f3d0ee0a3cb18b7f911409c00cb19ce0840d01d4906b0e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-watch-arming.json': '643dac5f5717b5ad1fadbb5900fea26c709a60e5542d31dc354f0a781fb96091',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/canonical-migration-manifest.json': '6deae8fc47520614a11fbd2fee39003edded0b4ed9f32ad5d28c7122e33d27b6',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/division_failure-migration-manifest.json': 'fe3bd79ae3d330c7c0c5b035a37ddfc64a01587b4e307912fffd415484ee04c2',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/division_recovery-migration-manifest.json': '1ebf7aa1cf103fe2ac993177a3978446dd396acd6ce6f6abe1402a199e44bb22',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/late_function_grant-migration-manifest.json': '0163daf39eabbc932d04db15b14807854f1ec01da1dba923a9bd0e6cc2298a10',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/operation-manifest-before-operational-review.json': '86e9c2fd07b553a563b69f6c6962d354ad8c43717abca9e95333ddf1a69d3d08',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/operation-manifest-before-source-pin.json': '6cf1a7771cc80535201d48f8507736eebd7aae7f26c014d5df5d77129190d928',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/manifest/operation-manifest.json': '98a2f53b88af97f308c2005d82708f1e0e624bc8546d705b64894e33efd320b9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/migration-manifest.json': '6deae8fc47520614a11fbd2fee39003edded0b4ed9f32ad5d28c7122e33d27b6',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-code-only.tar.gz': '1c110be54a815364ace687a95d27ee7cef9c360ea662768e54783508371ebcad',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/foundation/history-manifest.json': '6216d17b7cf9cf1835fe08c8db2427981fdf429d339a242736d566bf373ff64e',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/canonical/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/migration-manifest.json': 'fe3bd79ae3d330c7c0c5b035a37ddfc64a01587b4e307912fffd415484ee04c2',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-code-only.tar.gz': '04ca98ac20727fd306631916c8b8a7983ed4637a4c71994655b411babe7e576f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/foundation/history-manifest.json': 'e5534a21c8a86b26662e30fef1292d76acc12f77aea66a14defc6c5e128e283a',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_failure/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/migration-manifest.json': '1ebf7aa1cf103fe2ac993177a3978446dd396acd6ce6f6abe1402a199e44bb22',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-code-only.tar.gz': '75e9d9a734f508fe7a059a6d5ef949a30ac44f6f3a5616135be7f1ead00237b9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/foundation/history-manifest.json': '07edbd157c3cfbceb05803d20c1590a9ddd3a9800983b1f77cdecd93ed1502a3',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/division_recovery/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/migration-manifest.json': '0163daf39eabbc932d04db15b14807854f1ec01da1dba923a9bd0e6cc2298a10',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-code-only.tar.gz': 'e91ea4d8215875b1772eca0830b7c03267c15578e9ca1f25fe353ae46e09d7b9',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma.local-f0.config.mjs': 'ca19d1de07215b7f3304f8693745a446f051b4e46f833db1479d125dbdf46684',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/foundation/history-manifest.json': 'eca5e28cb0424df08bf0377821107004a6bf22f3b4a4bfee7bd9ac3667b559f7',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/foundation/migrations/20261117000100_f0_local_initial/migration.sql': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/foundation/migrations/migration_lock.toml': '1db17a8d051aa136110736752c5e1f8b7ed92b6ea8e803112fbbe2497047c210',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/prisma/review/foundation-candidate.prisma': 'de069b3beae07ab7f29167203efae11937f6a29c470cb1c95c2c143fdb623723',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/scripts/sql-review/local-f0-migrate-guard.mjs': '7c78a4238e0df137f6f97e1b651a856506d86ec27a1e73b9318fcac093de227b',
 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/source/late_function_grant/source-files/scripts/sql-review/local-f0-migrate-runner.mjs': '7b3c705b2cc29149e9d9e644803d6ea8a968dd9eea8e045caa6c74a3487f52fd'}
SOURCE_PINS={'context/reconciliation/database-candidate-tests.json': 'bba9bef6b94e9f4974f2a3a0b19a3277df54ac04aa77ceaa6b70ffcf75d988b8',
 'context/reconciliation/foundation-sql-draft-access.json': 'f9d529a7fc481beea3fcb0b2307fce47c44d7168380a7e2dfab6b9be44831eea',
 'context/reconciliation/foundation-sql-draft-models.json': 'd04bf44bd67dceda35199fd1ff1e494eed3016e80d180144018e879f5aee778d',
 'context/reconciliation/foundation-sql-verifier-access.json': 'f84421c4957fcb4cf7fa5b04d3b5f804f8810ee58da2c1529e98daba8ab36bde',
 'context/reconciliation/local-f0-assertions.json': '7fff51fc849cb37464b3df47d157fda73f1888f4909901c11ff44b5c5d388558',
 'context/reconciliation/local-f0-catalog-eb2aae6-2e4f5d40-execution.json': '76923eea9f3a68cb6157a0ed23432662492d79c068a7b58be507309edbe3e452',
 'context/reconciliation/local-f0-cli-diagnostics-validation.json': '8bf070ea0473fa41cd815737de96920f70ecf6896bf9188c52d90dbd42ed6e7b',
 'context/reconciliation/local-f0-install-controls-owned-source-phase-v5-source-validation.json': '5a24c1d3d648e263f7278b452efe4752982a9cc3e135cba351aafacfe3b5c52f',
 'context/reconciliation/local-f0-migration-tooling-validation.json': '83d079ae068a04aee70c2d307ba7352a58a20409aef47df4f6a8866c25c2ce33',
 'context/reconciliation/local-f0-native-catalog-acl-correction.json': '017c9ee8c46de01c8a70ffbd68c0c80c27a1508cf4f1887fffaafcdba8d54f85',
 'context/reconciliation/local-f0-native-catalog-metadata-diagnostics.json': '5acadf4bbcc01b6133ebc0c81cb72e806a2c3d6f3840fd8f752353bde9c1735d',
 'context/reconciliation/local-f0-native-catalog-text-correction.json': '83766af0fc699b88a56081ccebd59eff59b6c850678506f6ffe67c3d04b38565',
 'context/reconciliation/local-f0-native-catalog-validation.json': 'cbc26b6d1935ced05a03b3d186658864cb687de6b49af888c92c551976279d75',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-final.log': 'c6302130b0caf02c6a22bf75b7c98e50f5d21df41ef0bd19cd79992c5b06b09a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-first.log': 'e6c9905279f7d2ef32f17d281c2dfeb522d71c17dc9b392e93829ae4b28601da',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/affected-legacy14-first.log': 'efea1ed51eeb5a6c8099bd040ef95bb699aee51bf37c2be0fe66addc9682160b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/author-review.json': 'b5e2289bbafd39517a384e4dd0ed050bcc4993f218a548ff04f0434231d785e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/before-preservation.json': 'c0bd370703855009125bb301433ea956b98e952d3fc3567bbc9e1ad686b34340',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/build_install_failed_precleanup_v5_source_draft_20261120.py.txt': 'ebf4c405492032d81160f35a48c6bd3c66b9a28b5966f72663352ec8d2ecb7f1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/check_install_failed_precleanup_v5_admission_20261120.py.txt': '348841a64c838bad1cd331ac9cea83f785b3d500813a505c4f898912db0d149a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-affected-checks.json': '6c348402be42cd85fde33cc07c609b9ec8476c2c1e9a51a089dbcd2fc1fd9bbf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-preservation-freeze.json': 'c868f89f7d8fa6b8a2c9269abc29357f25203384acd1df897a95c3e19c2c0bdb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-scope-and-preservation.json': 'c04cec00bad304399261afeb543499b3667de6e7831b1d1d8bf2380bcaa66d5c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-first.log': 'be08f5d5b3b929d9b15e09bc5f387132d19084db90b54410d608aa8e75ee9d9d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-second.log': '799815fa13fdb74a5e62102f1344a2d83ad02f2e3bd87a3f57881f0f2b01f617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused10-first.log': 'dcf5cb63afc26fc1d8c80da2ade2bf2a2c24dd55d3ecd04947dc6212dd48da7d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-focused-failure.json': '548b44c6e96525ea61ca246c691d625c2d362a9a5f45ca5b932a82ce86ea7193',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-process-mock-stage-bytes.py.txt': '1a04be27cc6f8acc36bf1f238f679bb519b2d7c28b81d53292d417049687c42b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'c146b8848116faf10de41d1a9d83e532e7d789d40083eabd41b400dff535a11d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': 'c1e7053ab9f4a65d4b4d33bbb21c25c3d6297d830227806c1c60c7eb273e8777',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': 'fc6bb6d6cdfdb484cb794801d64f112600323e1e389b77404538349bd9d18054',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer8-failure.json': '0bf0a8354db65bdd78c2bb5ccb70a96d7dabf7db93eaf17628a72c33c41074b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/reason.json': 'd33c07be2e74a0af8650d4f81790af26fabce8c2eaf2ca5451a5785acdec892c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/run-install-control-rehearsal-v5.py.txt': 'cd25fc81e171e76a52ad9f1967feff096829bd6e9c2d6037279b1179241c364f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/test_watch_install_independent_review_source_phase_v5.py.txt': '475f420e671b51a9dc9ee05131b257310a28834b77851feb91815a90d98c22f9',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_install_independent_review_protocol_source_phase_v5.py.txt': '394714a90b6ec2a94d2dc1d39e67fc35b258758a60e1cab2a283a51176c89d55',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_watch_install_independent_review_source_phase_v5.py.txt': '5b31fbfd089ce058a1dba8e9883e2e7bc5961343a5ca1d2eb067b9a5cb997434',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/watch-install-independent-review-source-phase-v5.py.txt': '40d1d706ae6011afe8fcd07c4817fb85beff28e229072a621241778952931a04',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/outcome.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/test-source.py.txt': '976434174edbb2d73783ea12846bf6c3980796a2887a229149ef8688274bdc62',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/namespace-and-snapshot-scope-supplements.json': 'e4891be9c3b07857258e3560967caa4b659fd5ff1b45fdad8514a220e59e13ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.json': 'cbc3a3d1f1a423b131d991b2c52b1899f8231b39b4e17dc5818e749a0344eaee',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.log': '035a516b234adb0e7eb9129bbcf01772d2569d4e371ecf73fe6199bec41d41c2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.json': '1e8db3d81aea01b6090aff4c97cf5418cbe1c30cedfb09a52c255b861486893f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.log': '6a574c18fe85772d26e868a5f4a527806d06d9228cea6a989795998c15fb0f22',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/owning8-final.log': '1b79ca2830a8cf940b7c381b700ae880c426702bee30baf1af07b0d2c4212324',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/pending-validation-before-final-evidence.json': '5ed7ac2dcc1df4360b247f1b366ca07e0d7d05b8e12b67dd78bdb7bf7859aa92',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/phase10-final.log': '3b118da9fb2286b6754d4b3604bedd278ffc6b955e56c7f0fece46b7d0337147',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/refresh_install_failed_precleanup_v5_draft_20261120.py.txt': '0418ed674f667061ac1e200257a7261ec1b4462bc4449339fe37fcc704df65a3',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/run_install_failed_precleanup_v5_final_affected_20261120.py.txt': '4979b9506867ed32cf4690bef7b9e8c5f57e1525f918ce8599814b036e0e4ac7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport-namespace-map.json': 'bb512a7b83b29fd93e485abe257470d4250919306f73ae6bbbcfe75a373883e2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.json': 'df07d84b0aac6dcff929df19c00c7eadb53bd390a7f54bd24e6722f7bbe7d6db',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.log': '4a1e4f76123e4cfaf64b8b057db9104b3dcf7a2c281d02fbbd3c07ab019473eb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.log': '3ef2f686aeafe33579bc208abc6bd610cf64cf81f0aea1d2aec98334523cc1e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport26-final.log': 'fa1609ab2dcc4bfd8b6f82797cbc0e97a2f76112f46cea4e0a9866f24324f112',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_Root_bounded_implementation_ACK_20261120.json': '966733cac75e8235cd0c0e53593cf0169181f2ec4f7912e9d4677b5f0067976c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_bounded_source_proposal_20261120.json': '337b34cdf5eddec2160d9cb5056bf13005b3064243bd95fc2075c1c431b876b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_independent_plan_review_20261120.json': '9e40127580ef6271c9947867b918fda1fffde0fd6e5a3496e1956cfcb83879ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'd4195896856ace2cae521245c59eb8c8eb361fe43faed7c7727fcfc19d9f76f7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-control-rehearsal-v5.py.txt': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-failed-precleanup-phase-v5.py.txt': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install-controls-coordinator-v5.md.txt': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_failed_precleanup_activation_v5.py.txt': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_independent_review_protocol_source_phase_v5.py.txt': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/prepare-install-control-rehearsal-v5.py.txt': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/run-install-control-rehearsal-v5.py.txt': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_install_independent_review_protocol_source_phase_v5.py.txt': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_run_install_control_rehearsal_v5.py.txt': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_watch_install_independent_review_source_phase_v5.py.txt': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/watch-install-independent-review-source-phase-v5.py.txt': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/execute_local_f0_install_controls_20261120_source_phase_v5.py.txt': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-install-controls-owned-source-phase-v5-source-validation.json': '2c93f4ed8a95440a925e7bce642f5079c5e9a822ac2443ed30f8532d15bfb5f6',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-final.log': 'c6302130b0caf02c6a22bf75b7c98e50f5d21df41ef0bd19cd79992c5b06b09a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/admission4-first.log': 'e6c9905279f7d2ef32f17d281c2dfeb522d71c17dc9b392e93829ae4b28601da',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/affected-legacy14-first.log': 'efea1ed51eeb5a6c8099bd040ef95bb699aee51bf37c2be0fe66addc9682160b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/author-review.json': 'b5e2289bbafd39517a384e4dd0ed050bcc4993f218a548ff04f0434231d785e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/before-preservation.json': 'c0bd370703855009125bb301433ea956b98e952d3fc3567bbc9e1ad686b34340',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/build_install_failed_precleanup_v5_source_draft_20261120.py.txt': 'ebf4c405492032d81160f35a48c6bd3c66b9a28b5966f72663352ec8d2ecb7f1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/check_install_failed_precleanup_v5_admission_20261120.py.txt': '348841a64c838bad1cd331ac9cea83f785b3d500813a505c4f898912db0d149a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-affected-checks.json': '6c348402be42cd85fde33cc07c609b9ec8476c2c1e9a51a089dbcd2fc1fd9bbf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-preservation-freeze.json': 'c868f89f7d8fa6b8a2c9269abc29357f25203384acd1df897a95c3e19c2c0bdb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/final-source-scope-and-preservation.json': 'c04cec00bad304399261afeb543499b3667de6e7831b1d1d8bf2380bcaa66d5c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-first.log': 'be08f5d5b3b929d9b15e09bc5f387132d19084db90b54410d608aa8e75ee9d9d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused01-second.log': '799815fa13fdb74a5e62102f1344a2d83ad02f2e3bd87a3f57881f0f2b01f617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/focused10-first.log': 'dcf5cb63afc26fc1d8c80da2ade2bf2a2c24dd55d3ecd04947dc6212dd48da7d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-focused-failure.json': '548b44c6e96525ea61ca246c691d625c2d362a9a5f45ca5b932a82ce86ea7193',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/initial-process-mock-stage-bytes.py.txt': '1a04be27cc6f8acc36bf1f238f679bb519b2d7c28b81d53292d417049687c42b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'c146b8848116faf10de41d1a9d83e532e7d789d40083eabd41b400dff535a11d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': 'c1e7053ab9f4a65d4b4d33bbb21c25c3d6297d830227806c1c60c7eb273e8777',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer-admission-before-namespace-fix/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': 'fc6bb6d6cdfdb484cb794801d64f112600323e1e389b77404538349bd9d18054',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/outer8-failure.json': '0bf0a8354db65bdd78c2bb5ccb70a96d7dabf7db93eaf17628a72c33c41074b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/reason.json': 'd33c07be2e74a0af8650d4f81790af26fabce8c2eaf2ca5451a5785acdec892c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/run-install-control-rehearsal-v5.py.txt': 'cd25fc81e171e76a52ad9f1967feff096829bd6e9c2d6037279b1179241c364f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-sealed-snapshot-projection/test_watch_install_independent_review_source_phase_v5.py.txt': '475f420e671b51a9dc9ee05131b257310a28834b77851feb91815a90d98c22f9',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_install_independent_review_protocol_source_phase_v5.py.txt': '394714a90b6ec2a94d2dc1d39e67fc35b258758a60e1cab2a283a51176c89d55',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/test_watch_install_independent_review_source_phase_v5.py.txt': '5b31fbfd089ce058a1dba8e9883e2e7bc5961343a5ca1d2eb067b9a5cb997434',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/pre-watcher-v2-binding-verification/watch-install-independent-review-source-phase-v5.py.txt': '40d1d706ae6011afe8fcd07c4817fb85beff28e229072a621241778952931a04',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/outcome.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/history/transport25-initial-exception-type-fixture/test-source.py.txt': '976434174edbb2d73783ea12846bf6c3980796a2887a229149ef8688274bdc62',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/namespace-and-snapshot-scope-supplements.json': 'e4891be9c3b07857258e3560967caa4b659fd5ff1b45fdad8514a220e59e13ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.json': 'cbc3a3d1f1a423b131d991b2c52b1899f8231b39b4e17dc5818e749a0344eaee',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-first.log': '035a516b234adb0e7eb9129bbcf01772d2569d4e371ecf73fe6199bec41d41c2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.json': '1e8db3d81aea01b6090aff4c97cf5418cbe1c30cedfb09a52c255b861486893f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/outer8-second.log': '6a574c18fe85772d26e868a5f4a527806d06d9228cea6a989795998c15fb0f22',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/owning8-final.log': '1b79ca2830a8cf940b7c381b700ae880c426702bee30baf1af07b0d2c4212324',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/pending-validation-before-final-evidence.json': '5ed7ac2dcc1df4360b247f1b366ca07e0d7d05b8e12b67dd78bdb7bf7859aa92',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/phase10-final.log': '3b118da9fb2286b6754d4b3604bedd278ffc6b955e56c7f0fece46b7d0337147',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/refresh_install_failed_precleanup_v5_draft_20261120.py.txt': '0418ed674f667061ac1e200257a7261ec1b4462bc4449339fe37fcc704df65a3',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/run_install_failed_precleanup_v5_final_affected_20261120.py.txt': '4979b9506867ed32cf4690bef7b9e8c5f57e1525f918ce8599814b036e0e4ac7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport-namespace-map.json': 'bb512a7b83b29fd93e485abe257470d4250919306f73ae6bbbcfe75a373883e2',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.json': 'df07d84b0aac6dcff929df19c00c7eadb53bd390a7f54bd24e6722f7bbe7d6db',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport23-first.log': '4a1e4f76123e4cfaf64b8b057db9104b3dcf7a2c281d02fbbd3c07ab019473eb',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.json': '6b358691ffe49d2300a26e259a694046b9d85c30d33fdaaab2460790a69bec0d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport25-first.log': '3ef2f686aeafe33579bc208abc6bd610cf64cf81f0aea1d2aec98334523cc1e1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-evidence/transport26-final.log': 'fa1609ab2dcc4bfd8b6f82797cbc0e97a2f76112f46cea4e0a9866f24324f112',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_Root_bounded_implementation_ACK_20261120.json': '966733cac75e8235cd0c0e53593cf0169181f2ec4f7912e9d4677b5f0067976c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_bounded_source_proposal_20261120.json': '337b34cdf5eddec2160d9cb5056bf13005b3064243bd95fc2075c1c431b876b5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/author-plan/install_failed_precleanup_activation_independent_plan_review_20261120.json': '9e40127580ef6271c9947867b918fda1fffde0fd6e5a3496e1956cfcb83879ed',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/check_local_f0_install_controls_operation_source_phase_v5.py.txt': 'd55eb0ce64b514832625b008b172ce87998829848f31b416d3e4bc6607b09c5e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-control-rehearsal-v5.py.txt': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/check-install-failed-precleanup-phase-v5.py.txt': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install-controls-coordinator-v5.md.txt': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_failed_precleanup_activation_v5.py.txt': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/install_independent_review_protocol_source_phase_v5.py.txt': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/prepare-install-control-rehearsal-v5.py.txt': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/run-install-control-rehearsal-v5.py.txt': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_install_independent_review_protocol_source_phase_v5.py.txt': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_run_install_control_rehearsal_v5.py.txt': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/test_watch_install_independent_review_source_phase_v5.py.txt': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/child-source/watch-install-independent-review-source-phase-v5.py.txt': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/execute_local_f0_install_controls_20261120_source_phase_v5.py.txt': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': 'ed6be9d0d62890ef25782bf6e566395d08b8572e1e0dbe76d4ebde181e22121e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/pin_local_f0_install_controls_plan_20261120_source_phase_v5.py.txt': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/README.md': 'bfd38911a7aa54e36f21ae4f48601758ab7df2228815e873264ced3ac54af366',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/authority-observe.sql': 'b5791265492feb42a4e68b5538d41f33c1b3a77518e8b62f48ce3852b7f4b3e5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/bootstrap.sql': '05c7d98aac1a13158ac2e6a28dcf7b377de8e1c881f347155421e5dd24e39893',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/canonical/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/division_failure/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/finalize.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/fixtures.json': '3992a73c920a510f18ee903e15d74f98c42720266eb4ff26abd61478e6c398e5',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/fresh-observe.sql': '674f92c95bbb627ba74abbc91dea0067ffd7cb25a01f1537487a21f354c09138',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/inactive-observe.sql': '3c81794dce2ef746695500f7539313f27fefd0590f12275deb8f471aef8bb92f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/inventory.sql': '4364890304d7c112b69c1e25d20a6ccbbf99bf7b32c44183403bb216a5c7f453',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/late_function_grant/20261117000100_f0_local_initial/migration.sql': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/ledger-observe.sql': '42ac58118727dbdc03c54e5ad6fb3cbedb3187f2ff2063eac4258336f0dfbb3c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/review-output/install-control-rehearsal-v5/rearm.sql': '40a2f1a0b2472a16af7b6b5544e330486b296c2265dba726c6264fd190f6b94b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/check-install-control-rehearsal-v5.py': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/check-install-failed-precleanup-phase-v5.py': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/install_failed_precleanup_activation_v5.py': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/install_independent_review_protocol_source_phase_v5.py': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/prepare-install-control-rehearsal-v5.py': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/install-controls-coordinator-v5.md': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/run-install-control-rehearsal-v5.py': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/test_run_install_control_rehearsal_v5.py': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/test_watch_install_independent_review_source_phase_v5.py': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/sql-review/watch-install-independent-review-source-phase-v5.py': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/ROOT/scripts/test_install_independent_review_protocol_source_phase_v5.py': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/check_local_f0_install_controls_operation_source_phase_v5.py': 'd55eb0ce64b514832625b008b172ce87998829848f31b416d3e4bc6607b09c5e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/execute_local_f0_install_controls_20261120_source_phase_v5.py': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/local_f0_install_controls_operation_steps_source_phase_v5.py': 'ed6be9d0d62890ef25782bf6e566395d08b8572e1e0dbe76d4ebde181e22121e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/pin_local_f0_install_controls_plan_20261120_source_phase_v5.py': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/TASK/prepare_local_f0_install_controls_plan_source_phase_v5.py': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_independent_catalog_focused_20261120.json': '93f9ed3ba3a02cbd644efabe575e62b097b775d8e07c097f1ed8fbd80cece152',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_independent_catalog_inventory_20261120.json': '6d3b008d8c23da635d4b54ed31af5b794576d985d43937635ca4c8f32a2c7a71',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_independent_source_review_catalog_HOLD_20261120.json': '2354c454e49d243d8e7e0620a5cecee5dd65505ca5da8971ebdf996c70d9534d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_parent_final_reference_Root_bounded_fix_ACK_20261120.json': '83361cadbe7a8585b03a79cc6203362f6814716c2aa0c082288c917a21dd5727',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/install_v5_parent_reference_order_independent_probe_20261120.json': '0aacfabe7617d75acd4ed4430cba52a836abc5d13d80ac0ad0800bd5ffb4c1bf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/original-freeze-manifest.json': '6113911c34ba2b6265d35ecb2e8fb4217277ab18fb13b1de91a778bfe10fda0c',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/preservation.json': '09b016ee5323f9bc5f76206c86130c3d6a5b1035ab9d3bdc7628f4e7b76eb65a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/held-before-parent-final-reference-fix1/probe_install_v5_parent_reference_order_catalog_20261120.py': 'bc2b0450a7dada113299a34a1adb2c3c2ce1782f1086b44ffd4abf580a978822',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/local_f0_install_controls_operation_steps_source_phase_v5.py.txt': '5dd5ece0f0ff86ce59411f4a4587100a743df05e82a807cdf6ce73765532e08b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/check_install_v5_parent_final_reference_fix1_20261120.py.txt': 'fccb54ee7bc10a1a3ceb3d3df7333d302e8a105bf12d2f6df60380744a449e9d',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-affected16-first.json': '5da6bb60bf720927256548dfb3e7746c937d1a63c86de7c7917a6fd9df543819',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-affected16-first.log': 'cd74c062bdeaf894001a1ef4c13b6c157b4b3fbafdb589450bca7ae71038b1af',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-author-review.json': '43ded06f472e76aa9a8f1d723510ee9947e41955fe17f7a72f5f5b9e916adc66',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-final.json': '4b9756047f1ec9d43500e2009c7375355078ae6d159e974cc7158a1e488de76e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-final.log': 'b0a111c1f35c46c67a145f184c4e81594292bf1c1bee171f3ab418bb72d7c5b4',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-first.json': 'edb81386fb2835a45508d7f385e0dd6da8d3d1173b07c97b2cf91966fa4da49a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-focused8-first.log': '1d5fe0b255b287a9ff63921972198fea07c5b5a0313dc008f5de9f10e09de238',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-static-AST-scope.json': '004bfe44b2a09caacdccef8a65a382764d725e986282f030f74118f5c62dac29',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/parent-reference-fix1-static-progress.json': '725816c4ea5b196a36d2fdbea0264a53f320685f435f1cf15c1b3f7ef7eecb4e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/pending-validation-before-final-fix-evidence.json': 'a9fa60bbf535ee5d0706f7e316d792ddc1c219eedbe2186c7c7f882b3ab29662',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/parent-final-reference-fix1-evidence/run_install_v5_parent_final_reference_fix1_affected_20261120.py.txt': 'd6828a55522f56c6fc851e23ff52d1661d171a52814370a641775f71c9e6493a',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/pin_local_f0_install_controls_plan_20261120_source_phase_v5.py.txt': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/prepare_local_f0_install_controls_plan_source_phase_v5.py.txt': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/Root-source-admission-helper.py.txt': 'c63963861987fff84e0aa8cd5183b0cacdaab6d2268d90e64b29eed6ff46febf',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/Root-source-closure-fix1.json': '287800f0c6dfb9f9eb37f9e7c98512dafc8bf5caa834072f2bde1ccfc7ce913e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/frozen-reviewed-delivery-fix1.json': 'cde49587d2aa856c93efad9e8b8e6ebbd7812f7dcf8753ea5a5bc3330843964e',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/independent-Catalog-source-closure-fix1.json': '5b82e9585e8e29ec8b48d0a470e222915424cfa78ec2898f5213b83f22d8de1b',
 'context/reconciliation/local-f0-operation-sources/install-controls-owned-source-phase-v5/reviews/validation-before-Root-closure-fix1.json': '95eefcacb8805d1bd345be33b77af2e67f0b6d098b8393721a22863aa2256b92',
 'context/reconciliation/local-f0-run-assets/eb2aae6-native-catalog-2e4f5d40/source-prefix-analysis.json': 'b3931b71fe3d0560d6864ce20aa64cc88086563c4399a34e4b442ed108c4fc4d',
 'context/reconciliation/local-f0-server-diagnostics-validation.json': '560504eea761a06864edea01fba42e2e2a9a086ecfaab583309868f8f2f9c027',
 'context/reconciliation/local-f0-tooling/linux-tooling-manifest.json': 'e8fcce8f3ed4eaad0f7834e908166a0947b997e75513d589078f0d79c9a940d0',
 'context/reconciliation/local-f0-tooling/prisma-tools-closure.json': '610e36e4006e9680d0e6a036486f302a18ecce9593699125b4173f5914acb88b',
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
 'review-output/install-control-rehearsal-v3/division_failure/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'review-output/install-control-rehearsal-v5/README.md': 'bfd38911a7aa54e36f21ae4f48601758ab7df2228815e873264ced3ac54af366',
 'review-output/install-control-rehearsal-v5/authority-observe.sql': 'b5791265492feb42a4e68b5538d41f33c1b3a77518e8b62f48ce3852b7f4b3e5',
 'review-output/install-control-rehearsal-v5/bootstrap.sql': '05c7d98aac1a13158ac2e6a28dcf7b377de8e1c881f347155421e5dd24e39893',
 'review-output/install-control-rehearsal-v5/canonical/20261117000100_f0_local_initial/migration.sql': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'review-output/install-control-rehearsal-v5/division_failure/20261117000100_f0_local_initial/migration.sql': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'review-output/install-control-rehearsal-v5/finalize.sql': 'afd6d11cb19d8e1cc0c5996221935877fe9b93a0672b25d2718343813c9c6e98',
 'review-output/install-control-rehearsal-v5/fixtures.json': '3992a73c920a510f18ee903e15d74f98c42720266eb4ff26abd61478e6c398e5',
 'review-output/install-control-rehearsal-v5/fresh-observe.sql': '674f92c95bbb627ba74abbc91dea0067ffd7cb25a01f1537487a21f354c09138',
 'review-output/install-control-rehearsal-v5/inactive-observe.sql': '3c81794dce2ef746695500f7539313f27fefd0590f12275deb8f471aef8bb92f',
 'review-output/install-control-rehearsal-v5/inventory.sql': '4364890304d7c112b69c1e25d20a6ccbbf99bf7b32c44183403bb216a5c7f453',
 'review-output/install-control-rehearsal-v5/late_function_grant/20261117000100_f0_local_initial/migration.sql': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f',
 'review-output/install-control-rehearsal-v5/ledger-observe.sql': '42ac58118727dbdc03c54e5ad6fb3cbedb3187f2ff2063eac4258336f0dfbb3c',
 'review-output/install-control-rehearsal-v5/rearm.sql': '40a2f1a0b2472a16af7b6b5544e330486b296c2265dba726c6264fd190f6b94b',
 'review-output/native-catalog/README.md': '89e82bb70f53d6e959109c1e249bb4dda0101d22470d68211715baf5b1c74388',
 'review-output/native-catalog/expected.json': '9ad2129c9b7b7b5fd99f2088ae94215326f6ccbf40550945694c44538d8d0976',
 'review-output/native-catalog/expression-oracle-plan.json': 'cce4b19c1931472841de2fec2662fa4b002278b275341815782078689a1af36f',
 'review-output/native-catalog/expression-oracle.sql': '74d585741e1e097ac0614621b86c7ec97673697eb7dde344023e1dbe0ca613d2',
 'review-output/native-catalog/public-schema-registration.json': 'f0a46eef94da5f4836f46e64fe3a1c11a700fc158d40e36381e30bbdc0ec28d3',
 'review-output/native-catalog/source-pins.json': 'a0e9c36eecf61b1d4ce717744c29f4b72424ecd8d9db5ce0519b6bdaf9f58d00',
 'scripts/assemble-foundation-sql-review.py': '136489b5fb966085020128bfbd7140dad5e0b340a2312319d346305311fc212f',
 'scripts/check-first-rehearsal-mocks.py': '777d9d74788c37c9b20891196180708400e4f58991026075e60bb6bc74a96adf',
 'scripts/check-install-control-rehearsal-v5.py': '23e2d7f13499b63b27eef16d7337ad7e74cdcef069ff7a4874152f396b11b8d1',
 'scripts/check-install-failed-precleanup-phase-v5.py': '0e8fae619db3130d0464e185efcdc6ba6e5a12a217c4ff16a5837eeec0699690',
 'scripts/check-local-f0-migrate.py': '59d890c145e1f14a62e296fba0139eaa22ab728b70fa76a7dbd7dc3883222a14',
 'scripts/check-migration-server-diagnostics.py': 'cb3ded2eaf6c1532691a41af241897b11072907c37aaeb2d3f2f1478da157163',
 'scripts/check-native-catalog-review.py': '05d39953bd26c61ef7d414a53bb5c0bc65cb2e59ec8513e17230ad5f7e4ef859',
 'scripts/check-trigger-row-shapes.py': '7e6c851630a65c9e07685138e03eca5d4fd5404e8a4bb2b36895e34069d52ce9',
 'scripts/database-candidate-correction-rules.py': '6b79a14ffa77c450c3864ba5e2d930d61d5a427a6b0c11545e1afdd37ccaabb3',
 'scripts/install_control_protocol_v2.py': '6c1474dc12a603b07346fff014c8ab8bd15dec5be0b972ec1d504342115ba48f',
 'scripts/install_failed_precleanup_activation_v5.py': '4d3235b174fb184509e993ed2548f89ba62805f01947ade613f884df31451018',
 'scripts/install_independent_review_protocol_source_phase_v5.py': '973ebe07aa52152fee99cded1b0add6d93c753f2818078592f890aeff305ff38',
 'scripts/prepare-database-candidate-review-assets.py': 'dcb1544afc39cffbd9a8b052749f544c7531ff3dee2ff9cc738fd38d8d3bc9ed',
 'scripts/prepare-first-rehearsal.py': 'b03f4b7fda4e60ff7bafc2b6a7463d7bb9a3ee7bffc9f4e6c8f840f99b4116ce',
 'scripts/prepare-install-control-rehearsal-v5.py': '99fc6b2b779f1f747362964a507875e864ad9372cda12de72453da44f6eeb1d7',
 'scripts/prepare-local-f0-history.py': '33fe46e1b50c8d808ffb95b60cc42750e795582e6a1b15fb82f4fe93321281f8',
 'scripts/prepare-native-catalog-review.py': 'cef4f4f191e478593a679e9b86c7eee410531b01501a896c0b6f0e1bc1ac4fa2',
 'scripts/prepare-rehearsal-diagnostics.py': '598bc556999a16f303171003324be8763cb00a0fff2bb54de8a1195e1e7c852b',
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
 'scripts/sql-review/install-controls-coordinator-v5.md': 'a884cc27485cc34b9ca926948101197df936add274a918b8be59783bf6e0a880',
 'scripts/sql-review/install_ledger_proof_v3.py': '44211b9a783271dd336c03df9104686980e528575181365583aca214ca44dc05',
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
 'scripts/sql-review/run-install-control-rehearsal-v5.py': '2216187773803e940961b745585e553ee85d4b2a3bc874baa36367b78524c90c',
 'scripts/sql-review/run-local-f0-migrate.py': '4b929dd8c46fea0fa0e09f92cf54e8bb37db194a9ce5c6fd02c0e91542d7909f',
 'scripts/sql-review/test_catalog_collector_acl.py': 'd9ac90cb8c335bd70b04056e422692c55bf73569ef109d3f8fb2bd73e9e1b57b',
 'scripts/sql-review/test_catalog_collector_text.py': 'fe7a29132b7d69b69213f61ccfda3e14a7339735c202f3cae1334c92dc6e24a7',
 'scripts/sql-review/test_catalog_expression_oracle.py': 'a758a17b8cd92922e7a599dc06679e6309dc107028c151387e533dcf8a5f5c85',
 'scripts/sql-review/test_catalog_manifest.py': '633e4f8c8f3b93d7e44d7c8abff7aa5ca1f3caa063cc354d592d1913d4ba9750',
 'scripts/sql-review/test_compare_native_catalog.py': '38d0e26ac030a1024c739c8ea79e0c653b3f0bf9aee54e9815bf314b8887ce37',
 'scripts/sql-review/test_install_ledger_proof_v3.py': 'bd34a3fa2c724988661e8cddccf1f9272ad53035d98fe5e02fee3a7407fcff8a',
 'scripts/sql-review/test_local_image_identity.py': '0edae319a544aaaa8ed112e2ec477fe7ac428b58a7970ca8cd0e33ff006abe93',
 'scripts/sql-review/test_pg17_catalog_rules.py': 'c6879cd715df8bb45b26bbeec90352189e339d87be2f37c869cf471e42cfbb4a',
 'scripts/sql-review/test_prisma_ledger_proof.py': '62685fbff83d42cad600de2d1f387647737a42bd5cffc50c2240eb1c66006095',
 'scripts/sql-review/test_run_install_control_rehearsal_v5.py': 'f3df0f5d547cca1de5ebc13d86c3d1117edc5341d0a528a3c9d9784fd5abb617',
 'scripts/sql-review/test_watch_install_independent_review_source_phase_v5.py': '3b1361ef4a38675d31e6fabfdd5e650f9996c86a8c7a973efcd4fe4a83940751',
 'scripts/sql-review/watch-install-independent-review-source-phase-v5.py': '5fb09251e7bf7d70b8935f5bfb93dc7413bdb98c5cc864bce976bb57fa62db3a',
 'scripts/test_install_independent_review_protocol_source_phase_v5.py': 'c0ca118830a128d6daf02863b21da62c49f95d4ece60aaf759bcf1b2329313cc'}
FIVE={'check_local_f0_install_controls_operation_source_phase_v5.py': 'd4195896856ace2cae521245c59eb8c8eb361fe43faed7c7727fcfc19d9f76f7',
 'execute_local_f0_install_controls_20261120_source_phase_v5.py': 'bd50b44a48b5cdbf37736fa90b758419a0e44dbb76d9b3989c235f096a79593e',
 'local_f0_install_controls_operation_steps_source_phase_v5.py': '5dd5ece0f0ff86ce59411f4a4587100a743df05e82a807cdf6ce73765532e08b',
 'pin_local_f0_install_controls_plan_20261120_source_phase_v5.py': '29737e9cafaced66ac0449885f2c29cfd8b5cbd532f0c3c8876ab4c3d2347db0',
 'prepare_local_f0_install_controls_plan_source_phase_v5.py': '97da728d4caf50bf6933d8a5167736f327a541c514a7299ae833c62504159004'}
IDENTITY={'packet_sha256': '1ec1f730e6023d22c52e93b750c91f96ea07b2337fe793dd3d1477cd383c4fc2',
 'run_id': '6850ee4c-154b-4834-9ed0-c3612db77724',
 'source_commit': '0ff2a910ce081a0c6e0c6a268d6f876b8e061a45',
 'source_tree': '886f85d4a919a8a04f85c8fe45a01e0a8801ba1c'}
SQL={'canonical': '5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad',
 'division_failure': 'dd088298a5ffc9b42543c249fd433d7de1d22cabcc9ec108f928737c346b8c5c',
 'late_function_grant': 'bb41107428c6a2868abe402c28d14554cfb073113f5687f806b395366189a61f'}
CIDS={'canonical': 'cf9dcd38c7bca7b01f6bb040d65cd71d0f543ae7bc4fe35850d86ad604bb3c4d',
 'division_failure': 'cd4fb26d0aa8d91c3ac84f2366299fe0695439d5387b13df9f897243dab241e4',
 'late_function_grant': 'e5c27c97a94df0144f8971fdf5744605365f85bcae92258b8efe866b44d53fe4'}
VARIANTS=('canonical', 'division_failure', 'late_function_grant')
RUNTIME=('wa_context_issuer', 'wa_identity_service_authority', 'wa_app_runtime', 'wa_worker')
PHASE='POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION'
MIGRATION='20261117000100_f0_local_initial'
COUNT_FIELDS=('registered',
 'division_22012',
 'function_42501',
 'secondary_25p02',
 'other_migrator_error',
 'malformed',
 'forbidden_body')
FALSE_GATE={'activated': False, 'install_closed_success': False, 'original_cleanup_verified': False}
INACTIVE={'all_null_verifiers': True, 'flags_exact': True, 'runtime_roles': 4}
AUTHORITY3={'exact_temporary_options': True,
 'leaf_create': False,
 'permanent_migrator_edge': True,
 'temporary_memberships': 3}
AUTHORITY0={'exact_temporary_options': True,
 'leaf_create': False,
 'permanent_migrator_edge': True,
 'temporary_memberships': 0}
CLEANUP={'leaf_create': False, 'original_grantor': 'postgres', 'other_clients': 0, 'temporary_memberships': 0}
CLOSED={'all_other_clients_absent': True,
 'observation_completed': True,
 'scope': 'ALL_DATABASES_ALL_ROLES_ALL_APPLICATION_NAMES'}
CLI_FIELDS={'attestation_sha256',
 'container_id',
 'database_qualification_claimed',
 'diagnostic_format',
 'exit_code',
 'no_pending_message_observed',
 'operation',
 'prisma_codes',
 'raw_output_discarded',
 'run_id',
 'schema',
 'source_sql_sha256',
 'sqlstates',
 'status'}
PARENT_FIELDS={'acl_compatibility_preflight',
 'all_source_and_external_inputs_preserved_after_run',
 'approved_commit',
 'approved_packet_sha256',
 'approved_tree',
 'authorization',
 'backend_closures',
 'catalog_comparison',
 'catalog_operations',
 'catalog_preparation',
 'cleanup',
 'cleanup_summary',
 'credential_handling',
 'events',
 'evidence_complete',
 'external_input_archives_and_fresh_history_unchanged_after_run',
 'external_sources_unchanged_after_run',
 'finished_at',
 'host_secret_cleanup',
 'image',
 'install',
 'ledger_comparison',
 'ledger_observation_sha256',
 'ledger_registration_sha256',
 'limits',
 'local_preflight',
 'native_snapshots',
 'oracle_records',
 'packet_unchanged_after_run',
 'persistence_failure',
 'public_baseline_verification',
 'run_id',
 'run_manifest',
 'run_manifest_sha256',
 'sanitization',
 'source_verification',
 'stage',
 'started_at',
 'status',
 'steps',
 'targets',
 'text_compatibility_preflight',
 'tool_source_data_unchanged_after_run',
 'unexpected'}
CHILD_FIELDS={'current_stage',
 'evidence_complete',
 'first_failure',
 'limits',
 'packet_sha256',
 'persistence_failure',
 'reviewed_plan_sha256',
 'run_id',
 'schema',
 'source_commit',
 'source_tree',
 'status',
 'subsequent_cases_stopped',
 'targets'}
RECORD_FIELDS={'671_ledger_rows_preserved',
 'Posture',
 'accepted_counts_unchanged',
 'actual_wrapper_status',
 'assertion_links_changed',
 'assets_sha256',
 'authoritative_later_native_proofs',
 'business_row_fingerprints',
 'canonical_and_recovered_catalog_relations',
 'continue_standing_assignment',
 'coordinator_reference',
 'external_trigger_guards',
 'finished_at_utc',
 'independent_cleanup_sha256',
 'independent_closed_audit_sha256',
 'independent_recovery',
 'known_executor_exit',
 'new_phase_scope',
 'operation_manifest_sha256',
 'operation_packet_sha256',
 'proposed_only_claim',
 'qualification',
 'raw41_asset_locations',
 'raw_actual_step_flags_preserved',
 'raw_aggregate_reconciliation',
 'raw_child_sha256',
 'raw_evidence_sha256',
 'raw_reports_unchanged',
 'recorded_at_utc',
 'run_id',
 'schema',
 'single_claim_plan_sha256',
 'source_commit',
 'source_preservation',
 'source_tree',
 'started_at_utc'}
TARGET_FIELDS={'canonical': {'AFTER_VERIFIED_CLEANUP_STILL_INACTIVE',
               'BEFORE_INSTALL_RUNTIME_INACTIVE',
               'activation_gate_allowed',
               'activation_gate_held',
               'auth_postgres',
               'auth_wa_app_runtime',
               'auth_wa_context_issuer',
               'auth_wa_identity_service_authority',
               'auth_wa_migrator',
               'auth_wa_worker',
               'authority',
               'cli_canonical_deploy',
               'closure_ACTIVATE_FOUR_AFTER_VERIFIED_SUCCESS_CLEANUP',
               'closure_ACTIVATE_ONLY_MIGRATOR',
               'closure_AFTER_VERIFIED_CLEANUP_STILL_INACTIVE',
               'closure_AUTHORITY_OBSERVE',
               'closure_AUTH_postgres',
               'closure_AUTH_wa_app_runtime',
               'closure_AUTH_wa_context_issuer',
               'closure_AUTH_wa_identity_service_authority',
               'closure_AUTH_wa_migrator',
               'closure_AUTH_wa_worker',
               'closure_BEFORE_INSTALL_RUNTIME_INACTIVE',
               'closure_CLI_deploy',
               'closure_COMPLETE_APPLICATION_INVENTORY',
               'closure_EMPTY_TARGET_PRE_BOOTSTRAP',
               'closure_FINAL_GLOBAL',
               'closure_GUARDED_PRIVATE_LEDGER',
               'closure_ORIGINAL_GRANTOR_FINALIZATION',
               'closure_PRE_FINALIZATION',
               'closure_SCHEMA_FINGERPRINT',
               'closure_SEPARATE_ORIGINAL_BOOTSTRAP',
               'closure_SETTINGS',
               'closure_STAGE_canonical',
               'closure_WRONG_AUTH_postgres',
               'closure_WRONG_AUTH_wa_app_runtime',
               'closure_WRONG_AUTH_wa_context_issuer',
               'closure_WRONG_AUTH_wa_identity_service_authority',
               'closure_WRONG_AUTH_wa_migrator',
               'closure_WRONG_AUTH_wa_worker',
               'closure_WRONG_FINALIZER',
               'finite_result',
               'inventory',
               'ledger',
               'original_cleanup',
               'schema_fingerprint',
               'settings',
               'wrong_grantor'},
 'division_failure': {'AFTER_VERIFIED_CLEANUP_STILL_INACTIVE',
                      'BEFORE_INSTALL_RUNTIME_INACTIVE',
                      'FAILED_INSTALL_REMAINS_INACTIVE',
                      'activation_gate_allowed',
                      'activation_gate_held',
                      'auth_postgres',
                      'auth_wa_app_runtime',
                      'auth_wa_context_issuer',
                      'auth_wa_identity_service_authority',
                      'auth_wa_migrator',
                      'auth_wa_worker',
                      'authority',
                      'cli_division_failure_deploy',
                      'cli_division_failure_resolve-rolled-back',
                      'cli_division_recovery_deploy',
                      'closure_ACTIVATE_FOUR_AFTER_VERIFIED_SUCCESS_CLEANUP',
                      'closure_ACTIVATE_ONLY_MIGRATOR',
                      'closure_AFTER_VERIFIED_CLEANUP_STILL_INACTIVE',
                      'closure_AUTHORITY_OBSERVE',
                      'closure_AUTH_postgres',
                      'closure_AUTH_wa_app_runtime',
                      'closure_AUTH_wa_context_issuer',
                      'closure_AUTH_wa_identity_service_authority',
                      'closure_AUTH_wa_migrator',
                      'closure_AUTH_wa_worker',
                      'closure_BEFORE_INSTALL_RUNTIME_INACTIVE',
                      'closure_CLI_deploy',
                      'closure_CLI_resolve-rolled-back',
                      'closure_COMPLETE_APPLICATION_INVENTORY',
                      'closure_EMPTY_TARGET_PRE_BOOTSTRAP',
                      'closure_FAILED_INSTALL_REMAINS_INACTIVE',
                      'closure_FINAL_GLOBAL',
                      'closure_GUARDED_PRIVATE_LEDGER',
                      'closure_ORIGINAL_GRANTOR_FINALIZATION',
                      'closure_ORIGINAL_GRANTOR_THREE_EXACT_MEMBERSHIPS',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__FAILED_DEPLOY_RETURNED',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_AUTHORITY',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_DIAGNOSTIC',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_NULL_VERIFIERS',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_app_runtime',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_context_issuer',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_identity_service_authority',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_worker',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_AUTHORITY',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_DIAGNOSTIC',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_NULL_VERIFIERS',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_app_runtime',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_context_issuer',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_identity_service_authority',
                      'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_worker',
                      'closure_PRE_FINALIZATION',
                      'closure_SCHEMA_FINGERPRINT',
                      'closure_SEPARATE_ORIGINAL_BOOTSTRAP',
                      'closure_SETTINGS',
                      'closure_STAGE_division_failure',
                      'closure_STAGE_division_recovery',
                      'closure_WRONG_AUTH_postgres',
                      'closure_WRONG_AUTH_wa_app_runtime',
                      'closure_WRONG_AUTH_wa_context_issuer',
                      'closure_WRONG_AUTH_wa_identity_service_authority',
                      'closure_WRONG_AUTH_wa_migrator',
                      'closure_WRONG_AUTH_wa_worker',
                      'failed_precleanup_activation',
                      'failed_precleanup_closures',
                      'failure_verdict',
                      'independent_recovery_review',
                      'inventory',
                      'ledger',
                      'original_cleanup',
                      'recovery_result',
                      'review_hold',
                      'schema_fingerprint',
                      'server_after',
                      'server_before',
                      'settings'},
 'late_function_grant': {'BEFORE_INSTALL_RUNTIME_INACTIVE',
                         'FAILED_INSTALL_REMAINS_INACTIVE',
                         'activation_gate_held',
                         'auth_postgres',
                         'auth_wa_app_runtime',
                         'auth_wa_context_issuer',
                         'auth_wa_identity_service_authority',
                         'auth_wa_migrator',
                         'auth_wa_worker',
                         'authority',
                         'cli_late_function_grant_deploy',
                         'closure_ACTIVATE_ONLY_MIGRATOR',
                         'closure_AUTHORITY_OBSERVE',
                         'closure_AUTH_postgres',
                         'closure_AUTH_wa_app_runtime',
                         'closure_AUTH_wa_context_issuer',
                         'closure_AUTH_wa_identity_service_authority',
                         'closure_AUTH_wa_migrator',
                         'closure_AUTH_wa_worker',
                         'closure_BEFORE_INSTALL_RUNTIME_INACTIVE',
                         'closure_CLI_deploy',
                         'closure_COMPLETE_APPLICATION_INVENTORY',
                         'closure_EMPTY_TARGET_PRE_BOOTSTRAP',
                         'closure_FAILED_INSTALL_REMAINS_INACTIVE',
                         'closure_FINAL_GLOBAL',
                         'closure_GUARDED_PRIVATE_LEDGER',
                         'closure_ORIGINAL_GRANTOR_FINALIZATION',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__FAILED_DEPLOY_RETURNED',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_AUTHORITY',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_DIAGNOSTIC',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_NULL_VERIFIERS',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_app_runtime',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_context_issuer',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_identity_service_authority',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__POST_STARTUP_wa_worker',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_AUTHORITY',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_DIAGNOSTIC',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_NULL_VERIFIERS',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_app_runtime',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_context_issuer',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_identity_service_authority',
                         'closure_POST_FAILED_DEPLOY_PRE_ORIGINAL_GRANTOR_FINALIZATION__PRE_STARTUP_wa_worker',
                         'closure_PRE_FINALIZATION',
                         'closure_SEPARATE_ORIGINAL_BOOTSTRAP',
                         'closure_SETTINGS',
                         'closure_STAGE_late_function_grant',
                         'closure_WRONG_AUTH_postgres',
                         'closure_WRONG_AUTH_wa_migrator',
                         'failed_precleanup_activation',
                         'failed_precleanup_closures',
                         'failure_verdict',
                         'inventory',
                         'ledger',
                         'original_cleanup',
                         'server_after',
                         'server_before',
                         'settings'}}
DERIVED_FIELDS={'actual_result',
 'claims',
 'derivation',
 'independent_audit_files_sha256',
 'limits',
 'packet_sha256',
 'preserved_prior_ledger',
 'run_id',
 'schema',
 'source_commit',
 'source_record',
 'source_tree'}
EVIDENCE_PIECES=[{'json_pointer': '/targets/division_failure/failed_precleanup_activation',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual division_failure failed_precleanup_activation; precleanup10/closure15 then '
                    'original grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/division_failure/failed_precleanup_closures',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual division_failure failed_precleanup_closures; precleanup10/closure15 then '
                    'original grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/division_failure/failure_verdict',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual division_failure failure_verdict; precleanup10/closure15 then original '
                    'grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/division_failure/original_cleanup',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual division_failure original_cleanup; precleanup10/closure15 then original '
                    'grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/division_failure/authority',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual division_failure authority; precleanup10/closure15 then original '
                    'grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/late_function_grant/failed_precleanup_activation',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual late_function_grant failed_precleanup_activation; precleanup10/closure15 '
                    'then original grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/late_function_grant/failed_precleanup_closures',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual late_function_grant failed_precleanup_closures; precleanup10/closure15 '
                    'then original grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/late_function_grant/failure_verdict',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual late_function_grant failure_verdict; precleanup10/closure15 then original '
                    'grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/late_function_grant/original_cleanup',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual late_function_grant original_cleanup; precleanup10/closure15 then original '
                    'grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/targets/late_function_grant/authority',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Exact actual late_function_grant authority; precleanup10/closure15 then original '
                    'grantor0/noCREATE.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/application_inventory',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/rollback-proof-for-review.json',
  'required_piece': 'Division failure complete zero-object inventory before reviewed recovery.',
  'sha256': 'f0eefef1c583485d0c3624b064ba1f04dc133d7258e5e0cd4c6782b848742924'},
 {'json_pointer': '/targets/late_function_grant/inventory',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/install-controls/install-controls-results.json',
  'required_piece': 'Late function-permission failure complete zero-object rollback.',
  'sha256': '24d007393874a91f239ec3ab5fe29353c14bad0d54124ea401ec68d8fc99c257'},
 {'json_pointer': '/exact_name_observations',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/independent-cleanup.json',
  'required_piece': 'Independent exact six resources absent; private credentials deleted.',
  'sha256': 'd8880f065a01842960c85b1654110dc4bcc26f3ebfe312583c9083decf5072bc'},
 {'json_pointer': '/install/coordinator_reference',
  'path': 'context/reconciliation/local-f0-run-assets/0ff2a91-install-6850ee4c/evidence/run-evidence.json',
  'required_piece': 'Original raw child hash/length before native and after all postchecks.',
  'sha256': 'eada43073ac1d0496ee922230ca05cc49cca8f0777a87ce5725689d47599f096'}]
SCOPE=('Exact observed INSTALL failed-after-function-setup/precleanup activation refusal and rollback/authority '
 'cleanup only. No full case,42-row business data,owner/API,worker,hosted or production readiness claim.')
LIMITS={'Posture': 'D',
 'business_COMPLETE42_claimed': False,
 'current_rows_added': 0,
 'full_prior_PARTIAL_preserved': True,
 'maximum_claims': 1,
 'only_existing_PARTIAL_replaced': True,
 'other_links_rerecorded': False,
 'owner_API_claimed': False,
 'whole_case_promoted': False,
 'worker_loop_claimed': False}

class EvidenceFailure(Exception):
    """Only fixed safe rejection codes escape the public API."""

def need(value,code):
    if not value:raise EvidenceFailure(code)
def sh(raw):return hashlib.sha256(raw).hexdigest()
sha=sh
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def same(actual,expected,code):need(canonical(actual)==canonical(expected),code)

# Static copies of reviewed pure helpers; old module remains byte-identical.
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

def pointer(value,text):
 need(type(text)is str and text.startswith('/'),'POINTER')
 for part in text[1:].split('/'):
  part=part.replace('~1','/').replace('~0','~')
  if type(value)is list:need(part.isdigit()and str(int(part))==part,'POINTER_INDEX');value=value[int(part)]
  else:value=value[part]
 return value

def semantic_view(native,expected):
 """Independently derive this exact source's 78 RESTRICT FK x four triggers."""
 wanted={};empty=sha(b'');fk_count=0
 for table,info in expected['tables'].items():
  for source in info['constraints']:
   if source['kind']!='FOREIGN':
    need(not(source['kind']in('PRIMARY','UNIQUE')and source['deferrable']),'NO_OTHER_INTERNAL_TRIGGER_SOURCE');continue
   fk_count+=1;need(source['delete_action']==source['update_action']=='r'and source['deferrable']is False and source['initially_deferred']is False,'EXACT_RESTRICT_FK_SOURCE')
   candidates=[x for x in native['constraints']if x['table_name']==table and x['kind']=='f'and x['columns']==source['columns']and x['references']==source['references']and x['referenced_columns']==source['referenced_columns']and (source['name']is None or x['name']==source['name'])]
   need(len(candidates)==1,'SOURCE_FK_IDENTITY');actual=candidates[0]
   for field in('delete_action','update_action','deferrable','initially_deferred','match'):same(actual[field],source[field],'SOURCE_FK_PROPERTY')
   need(type(actual['name'])is str and actual['name'].endswith('_fkey')and len(actual['name'].encode())<=63,'SOURCE_GENERATED_CONSTRAINT_NAME')
   reference=source['references'];index=actual['referenced_unique_index'];ref_info=expected['tables'][reference]
   source_indexes=[x for x in ref_info['constraint_indexes']if x['unique']is True and x['columns']==source['referenced_columns']]
   native_indexes=[x for x in native['indexes']if x['object']==index and x['table_name']==reference and x['unique']is True and [k['column']for k in x['keys']]==source['referenced_columns']]
   explicit=expected['explicit_indexes'].get(index)
   source_index_match=any(x['constraint_name']is None or index==reference.split('.')[0]+'.'+x['constraint_name']for x in source_indexes)or(type(explicit)is dict and explicit['table']==reference and explicit['unique']is True and [x['IndexElem']['name']for x in explicit['keys_ast']]==source['referenced_columns'])
   need(len(native_indexes)==1 and source_index_match,'SOURCE_REFERENCED_INDEX')
   for target,other,function,bits,prefix in [(table,reference,'RI_FKey_check_ins',5,'c'),(table,reference,'RI_FKey_check_upd',17,'c'),(reference,table,'RI_FKey_restrict_del',9,'a'),(reference,table,'RI_FKey_restrict_upd',17,'a')]:
    row={'table_name':target,'constraint_table':table,'constraint_name':actual['name'],'function':'pg_catalog.'+function,'function_identity':'pg_catalog.'+function+'()','function_release_builtin':True,'type_bits':bits,'enabled':'O','constraint':True,'deferrable':False,'initially_deferred':False,'argument_count':0,'arguments_sha256':empty,'when_sha256':None,'has_constraint_relation':True,'referenced_table':other,'has_constraint_index':True,'constraint_index':index,'dependencies':[{'class':'constraint','object':table+'/'+actual['name'],'direction':'trigger_to','object_subid':0,'dependency_type':'i','referenced_subid':0}],'internal':True}
    key=(table,actual['name'],target,'pg_catalog.'+function,bits);need(key not in wanted,'UNIQUE_SOURCE_TRIGGER');wanted[key]=(row,prefix)
 need(fk_count==78 and len(wanted)==312,'SOURCE312_INTERNAL_IDENTITIES')
 internal={};external={};names={};seen=set()
 for row in native['triggers']:
  need(type(row)is dict and len(row)==21 and type(row['internal'])is bool,'TRIGGER21_FIELDS');keyname=(row['table_name'],row['name']);need(keyname not in seen,'UNIQUE_TRIGGER_NAME');seen.add(keyname)
  if row['internal']is False:
   key=row['table_name']+'/'+row['name'];need(key in expected['triggers']and key not in external,'SOURCE100_EXTERNAL_IDENTITIES');need(row['enabled']=='O','EXTERNAL_RESTORED');external[key]=row;continue
  key=(row['constraint_table'],row['constraint_name'],row['table_name'],row['function'],row['type_bits']);need(key in wanted and key not in internal,'EXACT_SOURCE_INTERNAL_IDENTITY');source,prefix=wanted[key]
  need(re.fullmatch('RI_ConstraintTrigger_'+prefix+'_[0-9]+',row['name'])is not None,'ONLY_GENERATED_INTERNAL_NAME')
  clean={k:v for k,v in row.items()if k!='name'};same(clean,source,'ALL20_INTERNAL_NONNAME_FIELDS');internal[key]=clean;names[key]=row['name']
 need(set(internal)==set(wanted)and set(external)==set(expected['triggers'])and len(external)==100 and len(native['triggers'])==412,'COMPLETE312_100_TRIGGER_SET')
 view={'format':'workinants.install-source-semantic-native-view.v1','nontrigger_sections':{k:v for k,v in native.items()if k!='triggers'},'external_triggers':external,'internal_triggers':[[list(k),internal[k]]for k in sorted(internal)]}
 need(len(view['nontrigger_sections'])==26,'OTHER26_NATIVE_SECTIONS');return view,names

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
    need(sum(map(len,blobs.values()))<=80*1024*1024,'BUNDLE_SIZE')
    return blobs

def _doc(raw):
    need(type(raw)is bytes and len(raw)<=8*1024*1024,'JSON_BYTES_LIMIT')
    def pairs(items):
        value={}
        for key,item in items:need(key not in value,'DUPLICATE_JSON');value[key]=item
        return value
    try:value=json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in()).throw(EvidenceFailure('NONFINITE_JSON')))
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('JSON_REJECTED')from None
    _typed_json(value);return value

def _identity(value,packet='packet_sha256'):
    same([value[k]for k in('run_id','source_commit','source_tree',packet)],[RUN,COMMIT,TREE,PACKET],'RUN_SOURCE_TREE_PACKET')

def _phase(rows,closures,variant,cid,cli):
    expected={**IDENTITY,'variant':variant,'container_id':cid,'source_sql_sha256':SQL[variant]}
    need(type(rows)is list and len(rows)==10 and type(closures)is list and len(closures)==15,'EXACT_PHASE_COUNTS')
    kinds=['CLOSED_FAILED_DEPLOY_VERIFIED','GATE_PREREQUISITES','GATE_REFUSED','NULL_VERIFIERS',*['STARTUP_REJECTED_'+r for r in RUNTIME],'TEMPORARY_AUTHORITY','COMPLETE']
    for index,row in enumerate(rows):
        need(type(row)is dict and set(row)=={'phase','sequence','identity','kind','facts'}and row['phase']==PHASE and type(row['sequence'])is int and row['sequence']==index and row['kind']==kinds[index],'PHASE_ORDER')
        same(row['identity'],expected,'PHASE_IDENTITY');facts=row['facts']
        if index==0:
            need(type(facts)is dict and set(facts)=={'cli_attestation_sha256','cli_exit_code','cli_status','intended_primary_sqlstate','diagnostic_delta','all_operation_backends_absent','closed_process_result_observed'},'PHASE_CLOSED_FAILURE_FIELDS')
            need(facts['cli_attestation_sha256']==cli['attestation_sha256']and type(facts['cli_exit_code'])is int and facts['cli_exit_code']==cli['exit_code']and facts['cli_status']==cli['status']and facts['intended_primary_sqlstate']==('22012'if variant=='division_failure'else'42501')and facts['all_operation_backends_absent']is True and facts['closed_process_result_observed']is True,'PHASE_GENUINE_FAILURE')
            change=facts['diagnostic_delta'];need(type(change)is dict and set(change)==set(COUNT_FIELDS)and all(type(v)is int and 0<=v<=65536 for v in change.values()),'PHASE_DIAGNOSTIC_TYPES')
            field='division_22012'if variant=='division_failure'else'function_42501';foreign='function_42501'if variant=='division_failure'else'division_22012'
            need(change[field]==1 and change[foreign]==change['other_migrator_error']==change['malformed']==change['forbidden_body']==0 and change['secondary_25p02']==1 and change['registered']==2,'PHASE_EXACT_PRIMARY')
        elif index==1:same(facts,FALSE_GATE,'PHASE_GATE_FALSE')
        elif index==2:same(facts,{'outcome':'REFUSED','refusal_code':'INSTALL_RUNTIME_ACTIVATION_HELD','database_password_sql_executed':False},'PHASE_GATE_REFUSAL')
        elif index==3:same(facts,INACTIVE,'PHASE_NULL_VERIFIERS')
        elif 4<=index<=7:same(facts,{'role':RUNTIME[index-4],'candidate_startup':'PASS_REJECTED_INACTIVE','exit_code':2,'operation_connection_closed':True},'PHASE_ACTUAL_STARTUP_REFUSAL')
        elif index==8:same(facts,AUTHORITY3,'PHASE_THREE_MEMBERSHIPS')
        else:same(facts,{'observations_complete':True,'original_finalization_not_yet_run':True,'database_password_sql_executed':False,'gate_state':FALSE_GATE},'PHASE_BEFORE_FINALIZATION')
    tokens=['FAILED_DEPLOY_RETURNED','PRE_DIAGNOSTIC','POST_DIAGNOSTIC','PRE_NULL_VERIFIERS','POST_NULL_VERIFIERS',*[x+'_'+r for r in RUNTIME for x in('PRE_STARTUP','POST_STARTUP')],'PRE_AUTHORITY','POST_AUTHORITY']
    for index,row in enumerate(closures):
        need(type(row)is dict and set(row)=={'phase','sequence','stage','proof'}and row['phase']==PHASE and type(row['sequence'])is int and row['sequence']==index and row['stage']==tokens[index],'PHASE_CLOSURE_ORDER');same(row['proof'],CLOSED,'PHASE_CLOSURE_PROOF')

def _cli(value,cid,sql,operation='deploy',success=False):
    need(type(value)is dict and set(value)==CLI_FIELDS and value['schema']=='workinants.local-f0-migrate-result.v2'and value['operation']==operation,'CLI_FIELDS')
    need(value['run_id']==RUN and value['container_id']==cid and value['source_sql_sha256']==sql and type(value['attestation_sha256'])is str and re.fullmatch('[0-9a-f]{64}',value['attestation_sha256']),'CLI_IDENTITY')
    need(type(value['exit_code'])is int and value['raw_output_discarded']is True and value['database_qualification_claimed']is False,'CLI_SAFE_CLOSED_RESULT')
    diagnostic=value['diagnostic_format'];need(type(diagnostic)is dict and set(diagnostic)=={'text_valid','sgr_stripped','headers_valid','prisma_header_present','prisma_header_unique','database_header_present','database_header_unique'}and all(type(v)is bool for v in diagnostic.values())and diagnostic['text_valid']is True and value['prisma_codes']==[]and value['sqlstates']==[]and type(value['no_pending_message_observed'])is bool,'CLI_FIXED_DIAGNOSTIC_FIELDS')
    if success:need(value['status']=='CLI_COMPLETED_REQUIRES_INDEPENDENT_LEDGER_CATALOG_CHECKS'and value['exit_code']==0,'CLI_COMPLETION')
    else:need(value['status']in('CLI_FAILED_STOP_AND_INSPECT','CLI_OUTPUT_REJECTED_STOP_AND_INSPECT')and 1<=value['exit_code']<=255,'CLI_GENUINE_FAILED_DEPLOY')

def _server(value):
    need(type(value)is dict and set(value)=={'schema','counts','raw_output_discarded'}and value['schema']=='workinants.install-server-counts.v1'and value['raw_output_discarded']is True,'SERVER_COUNTS_SCHEMA')
    row=value['counts'];need(type(row)is dict and set(row)==set(COUNT_FIELDS)and all(type(v)is int and 0<=v<=65536 for v in row.values())and sum(v for k,v in row.items()if k!='registered')<=row['registered'],'SERVER_COUNTS_TYPES');return row

def _ledger(value):
    need(type(value)is dict and set(value)=={'rows','ids_unique'}and value['ids_unique']is True and type(value['rows'])is list and 1<=len(value['rows'])<=2,'LEDGER_FIELDS')
    for row in value['rows']:
        need(type(row)is dict and set(row)=={'name_sha256','checksum_sha256','finished','rolled_back','steps','logs_state','immutable_sha256'}and all(type(row[k])is str and re.fullmatch('[0-9a-f]{64}',row[k])for k in('name_sha256','checksum_sha256','immutable_sha256'))and row['name_sha256']==sh(MIGRATION.encode())and type(row['steps'])is int and row['steps']in(0,1)and type(row['finished'])is bool and type(row['rolled_back'])is bool and row['logs_state']=='NULL','LEDGER_ROW')
    return value['rows']

def _failure(variant,target,failed_row,zero):
    _cli(target['cli_'+variant+'_deploy'],CIDS[variant],SQL[variant]);same(zero,dict.fromkeys(('relations','functions','types','enums','other_clients'),0),'ALL_OBJECT_ROLLBACK')
    old,new=_server(target['server_before']),_server(target['server_after']);need(old['registered']>0 and all(new[k]>=old[k]for k in COUNT_FIELDS)and old['malformed']==old['forbidden_body']==new['malformed']==new['forbidden_body']==0,'SERVER_DELTA_CURRENT')
    change={k:new[k]-old[k]for k in COUNT_FIELDS};field='division_22012'if variant=='division_failure'else'function_42501';foreign='function_42501'if variant=='division_failure'else'division_22012'
    need(change[field]==1 and change[foreign]==change['other_migrator_error']==change['malformed']==change['forbidden_body']==0 and change['secondary_25p02']==1,'SOURCE_PRIMARY_AND_SECONDARY')
    _ledger({'rows':[failed_row],'ids_unique':True});need(failed_row['checksum_sha256']==sh(SQL[variant].encode())and failed_row['finished']is False and failed_row['rolled_back']is False and failed_row['steps']==0,'EXACT_FAILED_IMMUTABLE_ROW')
    expected={'variant':variant,'primary_sqlstate':'22012'if variant=='division_failure'else'42501','classification':'SERVER_PRIMARY_WITH_SECONDARY_25P02_NULL_LOGS','delta':change,'failed_row_immutable_sha256':failed_row['immutable_sha256'],'P3018_claimed':False,'actual_database_failure_observed':True,'rollback_observed':True,'recovery_approved':False}
    same(target['failure_verdict'],expected,'ACTUAL_FAILURE_VERDICT')

def _resources(r,plan,outer):
    manifest=r['run_manifest'];_identity(manifest);same(manifest['operator_sources_sha256'],FIVE,'MANIFEST_FIVE_BINDING')
    cfg=manifest['install'];need(cfg['scope']=='FINITE_THREE_TARGET_INSTALL_ONLY'and type(cfg['independent_review_transport']['timeout_seconds'])is int and cfg['independent_review_transport']['timeout_seconds']==240,'INSTALL_SCOPE_AND_TIMEOUT')
    need(all(SOURCE_PINS.get(n)==h for n,h in cfg['independent_review_transport']['source_modules_sha256'].items())and set(cfg['independent_review_transport']['source_modules_sha256'])=={'scripts/install_control_protocol_v2.py','scripts/install_failed_precleanup_activation_v5.py','scripts/install_independent_review_protocol_source_phase_v5.py','scripts/sql-review/watch-install-independent-review-source-phase-v5.py'},'SOURCE_PHASE_FOUR_BINDING')
    targets=manifest['targets'];need(type(targets)is list and len(targets)==3 and {x['kind']for x in targets}==set(VARIANTS)and set(r['targets'])=={x['name']for x in targets},'EXACT_THREE_RESOURCES')
    for target in targets:
        variant=target['kind'];value=r['targets'][target['name']]
        need(value['container_id']==CIDS[variant]==plan['targets'][variant]['container_id']==outer['targets'][variant]['container_id']and value['volume']==target['volume']==target['name']+'-data'and value['network_mode']=='none'and value['published_ports']is False,'RESOURCE_ISOLATION')
        same(value['labels'],{'workinants.rehearsal':'p0c-local-f0','workinants.rehearsal.run':RUN},'RESOURCE_RUN_LABELS');same(value['tmpfs'],{'/run/wa-secrets':'rw,nosuid,noexec,nodev,mode=0700'},'ROOT0700_SECRET_TMPFS')
        same(sorted(value['mounts'],key=lambda x:x['type']),[{'type':'bind','destination':'/run/bootstrap-password','rw':False},{'type':'volume','destination':'/var/lib/postgresql/data','rw':True,'volume':target['volume']}],'EXACT_REVIEWED_MOUNTS')
        need(value['finalization']=='PASS_INDEPENDENT_OBSERVED_COORDINATOR_FINALIZATION'and value['pre_bootstrap_public_baseline']['public_owner']=='pg_database_owner'and type(value['pre_bootstrap_public_baseline']['application_roles'])is int and value['pre_bootstrap_public_baseline']['application_roles']==0 and type(value['pre_bootstrap_public_baseline']['event_triggers'])is int and value['pre_bootstrap_public_baseline']['event_triggers']==0 and value['linux_tool_compatibility']['preexec_hashes_verified']is True,'FRESH_SOURCE_AND_TOOL_BASELINE')
    image=r['image'];need(image['reference']==manifest['image']=='docker.io/library/postgres:17.11@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'and image['image_id']=='sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1'and image['config_digest']=='sha256:eb0fb2377534e65aad04f37838956b3dfb888e1a3dd3c1acf957bc6557eb6c7d'and image['manifest_content_hash_verified']is True and image['pinned_repo_digest_verified']is True and image['os']=='linux'and image['architecture']=='amd64'and image['removed']is False,'PINNED_IMAGE_IDENTITIES')
    cred=r['credential_handling'];need(cred['host_private_directory_owner_only_acl_verified']is True and cred['real_credentials_in_argv_env_or_evidence']is False and cred['container_pgpass']=='root_owned_0600_tmpfs'and cred['independent_per_role_per_target']is True and type(cred['independent_correct_candidates'])is int and cred['independent_correct_candidates']==18 and type(cred['independent_wrong_candidates'])is int and cred['independent_wrong_candidates']==18 and cred['application_credentials_activated_by_outer']is False,'REVIEWED_CREDENTIAL_BOUNDARIES')
    for row in r['backend_closures']:
        need(set(row)=={'stage','scope','observation_completed','counts_valid','migrator_zero','other_clients_zero','all_other_client_backends_absent'}and row['scope']=='ALL_DATABASES_ALL_ROLES_ALL_TAGS'and all(row[k]is True for k in('observation_completed','counts_valid','migrator_zero','other_clients_zero','all_other_client_backends_absent')),'PARENT_GLOBAL_CLOSURES')

def _check_bundle(blobs):
    cache={}
    def j(path):
        if path not in cache:cache[path]=_doc(blobs[path])
        return cache[path]
    def a(path):return j(B+'/evidence/'+path)
    record=j(REC);_identity(record,'operation_packet_sha256');need(set(record)==RECORD_FIELDS and record['schema']=='workinants.local-f0-INSTALL6850-audited-success-execution.v1'and record['actual_wrapper_status']=='PASS_FINITE_INSTALL_PROTOCOLS_AND_NATIVE_SUBSET_ONLY'and record['raw_reports_unchanged']is True,'EXECUTION_RESULT_KIND');same(record['known_executor_exit'],{'session':40813,'exit_code':0},'KNOWN_EXECUTOR_EXIT')
    r=a('run-evidence.json');c=a('install-controls/install-controls-results.json');plan=a('install-coordinator-run-plan.json');proof=a('install-controls/rollback-proof-for-review.json');approval=a('install-controls/independent-recovery-approval.json');outer=a('independent-review-outer-identity.json')
    need(record['raw_evidence_sha256']==PINS[B+'/evidence/run-evidence.json']and record['raw_child_sha256']==PINS[B+'/evidence/install-controls/install-controls-results.json'],'NORMALIZED_RAW_REPORT_UNCHANGED');same(record['assets_sha256'],ASSET_PINS,'COMPLETE_PRESERVED_ASSET_GRAPH');need(all(PINS.get(path)==wanted for path,wanted in ASSET_PINS.items()),'EXACT_ASSET_PIN_LINKAGE');_identity(c);_identity(plan);_identity(proof);_identity(outer)
    need(set(r)==PARENT_FIELDS and set(c)==CHILD_FIELDS and c['schema']=='workinants.install-controls-results.v2'and c['status']=='PASS_FINITE_INSTALL_PROTOCOLS_PENDING_FULL_NATIVE_COMPARISON'and c['current_stage']=='AUTH_WA_WORKER'and c['evidence_complete']is True and c['persistence_failure']is False and c['first_failure']is None and c['subsequent_cases_stopped']is False,'CHILD_CLEAN_COMPLETION')
    same([r['run_id'],r['approved_commit'],r['approved_tree'],r['approved_packet_sha256']],[RUN,COMMIT,TREE,PACKET],'PARENT_SOURCE_IDENTITY')
    need(r['status']=='PASS_FINITE_INSTALL_PROTOCOLS_AND_NATIVE_SUBSET_ONLY'and r['evidence_complete']is True and r['persistence_failure']is False and r['unexpected']==[],'PARENT_CLEAN_COMPLETION')
    need(r['source_verification']['files_sha256']==SOURCE_PINS and type(r['source_verification']['file_count'])is int and r['source_verification']['file_count']==291,'EXACT291_SOURCE_VERIFICATION')
    need(all(PINS.get(path)==wanted for path,wanted in SOURCE_PINS.items()),'EXACT_SOURCE_PIN_LINKAGE')
    same(r['run_manifest']['packet_files_sha256'],SOURCE_PINS,'SOURCE_MANIFEST_MAP');need(sh(''.join(p+'\0'+SOURCE_PINS[p]+'\n'for p in sorted(SOURCE_PINS)).encode())==PACKET,'SOURCE_PACKET_AGGREGATE')
    same(outer['operator_sources_sha256'],FIVE,'EXACT_FIVE_SNAPSHOTS')
    _resources(r,plan,outer)
    need(proof['source_sql_sha256']==SQL['division_failure']and proof['container_id']==CIDS['division_failure']and proof['original_grantor_finalized']is True,'ORIGINAL_PROOF_IDENTITY')
    for variant,target in c['targets'].items():
        need(variant in VARIANTS and set(target)==TARGET_FIELDS[variant],'TARGET_CLOSED_FIELDS')
        same(target['original_cleanup'],CLEANUP,'SEPARATE_ORIGINAL_GRANTOR');same(target['authority'],AUTHORITY0,'ZERO_MEMBERSHIP_AND_CREATE_AFTER')
        same(target['settings'],dict.fromkeys(('prefix','terse','no_statements','no_error_statements','locale','passwords','version'),True),'LOGGING_SETTINGS')
        for role in ('postgres','wa_migrator',*RUNTIME):
            active=variant!='late_function_grant'or role in('postgres','wa_migrator')
            same(target['auth_'+role],{'role':role,'correct_password':'PASS_SCRAM'if active else'PASS_REJECTED_INACTIVE','wrong_password':'PASS_REJECTED'if active else'NOT_RUN','actual_connection_closed':True},'FULL_ACTUAL_AUTH_CONTROLS')
        need(plan['targets'][variant]['container_id']==outer['targets'][variant]['container_id']==CIDS[variant],'SAME_ACTUAL_CID')
        for key,value in target.items():
            if key.startswith('closure_'):same(value,CLOSED,'ALL_CHILD_GLOBAL_CLOSURES')
        if variant=='canonical':continue
        _phase(target['failed_precleanup_activation'],target['failed_precleanup_closures'],variant,CIDS[variant],target['cli_'+variant+'_deploy'])
        same(target['FAILED_INSTALL_REMAINS_INACTIVE'],INACTIVE,'POST_FAILURE_INACTIVE');same(target['activation_gate_held'],{'permit':False,'database_password_sql_executed':False},'POST_FAILURE_GATE_HELD')
        _failure(variant,target,proof['failed_ledger']if variant=='division_failure'else _ledger(target['ledger'])[0],proof['application_inventory']if variant=='division_failure'else target['inventory'])
    need(set(c['targets'])==set(VARIANTS),'EXACT_THREE_TARGETS')
    div=c['targets']['division_failure'];same(proof['failure'],div['failure_verdict'],'PROOF_ACTUAL_FAILURE')
    same(approval,{'schema':'workinants.install-independent-rollback-review.v1','decision':'APPROVED_STANDARD_RESOLVE_ROLLED_BACK','run_id':RUN,'container_id':CIDS['division_failure'],'source_sql_sha256':SQL['division_failure'],'proof_sha256':sh((canonical(proof)+'\n').encode()),'reviewer':'/root/catalog_v4_review'},'SEVEN_FIELD_EXPLICIT_APPROVAL')
    receipt=j(ARCHIVE+'/Catalog-explicit-recovery-decision-receipt.json');same(receipt['decision'],approval,'EXPLICIT_REVIEW_DECISION');need(type(receipt['original_review_deadline_monotonic'])is float and receipt['original_review_deadline_monotonic']==213727.921 and type(receipt['remaining_seconds_after_publication'])in(int,float)and math.isfinite(receipt['remaining_seconds_after_publication'])and 0<receipt['remaining_seconds_after_publication']<=220 and receipt['all_read_handles_closed']is True,'ORIGINAL_UNEXTENDED_DEADLINE')
    rows=_ledger(div['ledger']);same(rows[0],{**proof['failed_ledger'],'rolled_back':True},'ONLY_STANDARD_ROLLED_BACK_CHANGE');need(len(rows)==2 and rows[1]['checksum_sha256']==sh(SQL['canonical'].encode())and rows[1]['finished']is True and rows[1]['rolled_back']is False and rows[1]['steps']==1,'RETAINED_FAILED_AND_NEW_CANONICAL_HISTORY')
    _cli(div['cli_division_failure_resolve-rolled-back'],CIDS['division_failure'],SQL['division_failure'],'resolve-rolled-back',True)
    for variant,key in [('canonical','canonical'),('division_failure','division_recovery')]:
        target=c['targets'][variant];_cli(target['cli_'+key+'_deploy'],CIDS[variant],SQL['canonical'],success=True);need(target['cli_'+key+'_deploy']['no_pending_message_observed']is True,'GENUINE_SECOND_NOOP')
        same(target['inventory'],{'relations':188,'functions':147,'types':142,'enums':29,'other_clients':0},'FULL_CANONICAL_OBJECTS')
    ref=r['install']['coordinator_reference'];need(ref['sha256']==PINS[B+'/evidence/install-controls/install-controls-results.json']and type(ref['bytes'])is int and ref['bytes']==len(blobs[B+'/evidence/install-controls/install-controls-results.json'])and ref['reference_qualified']is True,'CLOSED_REFERENCE_ORIGINAL_BYTES')
    same([x['phase']for x in ref['integrity_checks']],['BEFORE_CANONICAL_NATIVE','BEFORE_RECOVERED_NATIVE','AFTER_ALL_POSTCHECKS'],'REFERENCE_EARLY_FINAL_STAGES');need(all(x['matched_original']is True and x['all_read_handles_closed']is True for x in ref['integrity_checks']),'REFERENCE_EARLY_FINAL_MATCH')
    expected=j('review-output/native-catalog/expected.json')['expected'];views={};names={}
    for variant,prefix,count,ledger_count in [('canonical','canonical-',29089,22),('division_failure','recovered-',29090,23)]:
        native=a(prefix+'native-before.json');same(a(prefix+'native-after-oracle.json'),native,'ORACLE_ROLLBACK_PARITY');same(a(prefix+'native-after-ledger.json'),native,'LEDGER_NATIVE_PARITY');native_hash=sh(canonical(native).encode())
        comparison=a(prefix+'catalog-comparison.json');need(comparison['status']=='PASS'and comparison['findings']==[]and comparison['check_counts']=={'PASS':count}and type(comparison['check_counts']['PASS'])is int and comparison['native_snapshot_sha256']==native_hash and comparison['source_expected_sha256']==sh(canonical(expected).encode()),'FULL_NATIVE_SOURCE_COMPARISON')
        oracle=a(prefix+'oracle-results.json');need(type(oracle['expression_count'])is int and oracle['expression_count']==len(oracle['expressions'])==416 and oracle['source_expected_sha256']==comparison['source_expected_sha256'],'EXACT416_ORACLE')
        ledger=a(prefix+'ledger-comparison.json');need(ledger['status']=='PASS'and type(ledger['checks'])is list and len(ledger['checks'])==ledger_count and all(set(x)=={'field','status','expected_sha256','actual_sha256'}and x['status']=='PASS'and x['expected_sha256']==x['actual_sha256']for x in ledger['checks']),'FULL_LEDGER_SOURCE_COMPARISON')
        same(r['install']['native'][variant]['catalog_check_counts'],comparison['check_counts'],'PARENT_NATIVE_BINDING');same(r['install']['native'][variant]['ledger_checks'],ledger['checks'],'PARENT_LEDGER_BINDING')
        views[variant],names[variant]=semantic_view(native,expected)
    same(views['canonical'],views['division_failure'],'ONLY_SOURCE_DERIVED_SEMANTIC_NORMALIZATION');parity=a('install-semantic-parity.json');need(parity['only_validated_internal_name_equality_omitted']is True and parity['raw_snapshots_rewritten']is False and sum(names['canonical'][k]!=names['division_failure'][k]for k in names['canonical'])==312,'ONLY312_INTERNAL_NAMES');same(parity['semantic_view_sha256'],{k:sh(canonical(v).encode())for k,v in views.items()},'SOURCE_SEMANTIC_DIGESTS')
    cleanup=j(B+'/independent-cleanup.json');_identity(cleanup);need(cleanup['status']=='PASS_INDEPENDENT_PHYSICAL_CLEANUP'and cleanup['known_executor_exit']==0 and cleanup['private_directory_absent']is True and len(cleanup['exact_name_observations'])==6 and all(x['absent_exact_known_diagnostic']is True for x in cleanup['exact_name_observations'].values()),'INDEPENDENT_EXACT_CLEANUP')
    for flag in('packet_unchanged_after_run','tool_source_data_unchanged_after_run','external_input_archives_and_fresh_history_unchanged_after_run','external_sources_unchanged_after_run','all_source_and_external_inputs_preserved_after_run'):need(r[flag]is True,'SOURCE_POSTCHECKS')
    need(r['sanitization']['actual_password_values_found']is False and r['sanitization']['unrestricted_subprocess_output_persisted']is False and r['sanitization']['raw_context_handles_persisted']is False and r['sanitization']['coordinator_evidence_uses_reviewed_allowlist']is True,'SAFE_RETAINED_EVIDENCE')
    derived=j(DERIVED);_identity(derived);need(set(derived)==DERIVED_FIELDS and derived['schema']=='workinants.install6850-precleanup-derived-evidence.v1'and derived['derivation']=='EXPLICIT_DERIVED_WRAPPER_NOT_RAW_RUNTIME_EVIDENCE'and derived['actual_result']==KIND,'DERIVED_FIELDS')
    same(derived['source_record'],{'path':REC,'sha256':PINS[REC],'packet_alias_from':'operation_packet_sha256'},'RECORD_BINDING');same(derived['independent_audit_files_sha256'],AUDIT_PINS,'AUDIT_GRAPH')
    audit=j(ARCHIVE+'/independent-final-actual-audit.json');need(audit['decision']=='PASS_ACTUAL_FINITE_INSTALL_EVIDENCE_NEW_PRECLEANUP_PHASE_SUPPORTED','INDEPENDENT_ACTUAL_AUDIT')
    old=j(ARCHIVE+'/prior671-ledger.json');need(len(old['assertions'])==671,'PRESERVED_PRIOR671');previous=next(x for x in old['assertions']if(x['case_id'],x['assertion_id'])==CLAIM);need(previous['status']=='PARTIAL','PRIOR_PARTIAL_NOT_REWRITTEN')
    inventory=j('context/reconciliation/local-f0-assertions.json');item=next(x for x in next(x for x in inventory['cases']if x['id']==CLAIM[0])['assertions']if x['id']==CLAIM[1]);need(item['mandatory_for_case']is True and item['availability']=='CANDIDATE_LOCAL_SQL_PATH'and sh(item['expected_assertion'].encode())==ASSERTION_SHA,'EXACT_SOURCE_ASSERTION')
    same(derived['preserved_prior_ledger'],{'path':ARCHIVE+'/prior671-ledger.json','sha256':PINS[ARCHIVE+'/prior671-ledger.json'],'rows':671},'PRIOR_LEDGER_BINDING')
    need(type(derived['claims'])is list and len(derived['claims'])==1,'EXACT_ONE_CLAIM')
    expected_claim={'case_id':CLAIM[0],'assertion_id':CLAIM[1],'status':'PASS','expected_assertion_sha256':ASSERTION_SHA,'complete_source_assertion_sha256':sh(canonical(item).encode()),'action':'REPLACE_ONLY_EXISTING_PARTIAL_KEEP_PRIOR_HISTORY','prior_evidence':previous,'prior_evidence_sha256':sh(canonical(previous).encode()),'evidence_pieces':EVIDENCE_PIECES,'scope_ceiling':SCOPE}
    same(derived['claims'][0],expected_claim,'EXACT_ONE_CLAIM_AND_HISTORY');same(derived['limits'],LIMITS,'ONE_CLAIM_LIMITS')
    for piece in EVIDENCE_PIECES:
        need(piece['path']in PINS and piece['sha256']==PINS[piece['path']],'EXACT_EVIDENCE_REFERENCE');pointer(j(piece['path']),piece['json_pointer'])
    return canonical(derived)

def _validate_bundle(blobs):
    need(type(blobs)is dict and set(blobs)==set(PINS),'EXACT_CLOSED_GRAPH');need(all(type(v)is bytes and sh(v)==PINS[n]for n,v in blobs.items()),'CAPTURED_HASHES');return _check_bundle(blobs)

class QualificationBatch:
    def __init__(self,root):
        path=Path(root);need(not path.is_symlink(),'ROOT_SYMLINK');self.__root=path.resolve(strict=True);blobs=_capture(self.__root);self.__execution=_validate_bundle(blobs);self.__snapshot=MappingProxyType(blobs);self.__seen=False;self.__failed=False;self.__finalized=False
    def validate_claim(self,case_id,assertion_id,status,execution,root=None,json_pointer=None):
        try:
            need(not self.__failed and not self.__finalized,'BATCH_CLOSED');need(all(type(x)is str for x in(case_id,assertion_id,status,json_pointer)),'CLAIM_FIELDS');need((case_id,assertion_id)==CLAIM and status=='PASS'and json_pointer=='/claims/0','EXACT_ONE_ALLOWED_CLAIM');need(not self.__seen,'DUPLICATE_CLAIM')
            if root is not None:need(Path(root).resolve(strict=True)==self.__root,'BATCH_ROOT')
            need(type(execution)is dict,'EXACT_DERIVED_RECORD');_typed_json(execution);same(canonical(execution),self.__execution,'EXACT_DERIVED_RECORD');self.__seen=True;return True
        except EvidenceFailure:self.__failed=True;raise
        except Exception:self.__failed=True;raise EvidenceFailure('INSTALL_PRECLEANUP_EVIDENCE_REJECTED')from None
    def verify_unchanged(self):
        try:
            need(not self.__failed and not self.__finalized and self.__seen,'BATCH_CLOSED_OR_INCOMPLETE');again=_capture(self.__root);need(all(again[n]==self.__snapshot[n]for n in PINS),'FINAL_BYTE_DRIFT');self.__snapshot=None;self.__finalized=True;return True
        except EvidenceFailure:self.__failed=True;raise
        except Exception:self.__failed=True;raise EvidenceFailure('INSTALL_PRECLEANUP_EVIDENCE_REJECTED')from None
    def require_finalized(self):
        if self.__failed or not self.__finalized:self.__failed=True;raise EvidenceFailure('FINAL_BYTE_BARRIER_REQUIRED')
        return True

def prepare_batch(root):
    try:return QualificationBatch(root)
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('INSTALL_PRECLEANUP_EVIDENCE_REJECTED')from None

def validate_claim(case_id,assertion_id,status,execution,root,json_pointer=None):
    try:
        need((case_id,assertion_id)==CLAIM and status=='PASS'and json_pointer=='/claims/0','EXACT_ONE_ALLOWED_CLAIM');batch=prepare_batch(root);batch.validate_claim(case_id,assertion_id,status,execution,root,json_pointer);batch.verify_unchanged();return batch.require_finalized()
    except EvidenceFailure:raise
    except Exception:raise EvidenceFailure('INSTALL_PRECLEANUP_EVIDENCE_REJECTED')from None
