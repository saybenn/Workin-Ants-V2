# Cloud Track retained-selection owned packet

This owner runs two synthetic retained-selection cases on a fresh target under Posture D. The three-history owner performs startup, Prisma deploy and no-op verification, original-grantor finalization, native parity and exact cleanup. The Track child runs after `track_terminal` on the same target. [Candidate](../../../review-output/track-retained-base-candidate-v1/README.md)

## Source preparation

Use the pinned Cloud parser and Prisma archive from the Cloud checklist. `python -B owned_operation.py prepare --draft --tool-archive <verified Cloud v2 tool archive>` prepares an offline draft. `verify --draft --packet <absolute operation.json>` rebuilds and rereads it. A draft carries `HELD_DRAFT_NO_EXECUTION_AUTHORITY`, source identity null and all cases `NOT_RUN`. [Cloud setup](../../../context/reconciliation/cloud-phase0-execution.md)

The committed `recipe-v4` capsule contains the generator, independent source review and exact packet. Committed prepare requires `--prior-acceptance <canonical absolute acceptance.json>` and `--prior-acceptance-sha256 <exact accepted digest>`. It validates the prior run and every source and recipe byte at the current Git commit and tree. It produces `HELD_COMMITTED_PENDING_EXACT_BUSINESS_REVIEW`. `verify --packet <absolute operation.json>` rebuilds that packet.

Each operation lives under `/workspace/scratch/wa-cloud-f0-track-retained-selection-owned-<run_id>/`. Its `operation.json` binds the new commit, tree, daemon and image, original prior acceptance, exact candidate catalog and history, nine Prisma archive files, the four native assets, and the 27-file business recipe capsule. The business SQL remains in `business-recipes/` with a closed copy of the source review. `run-manifest.json`, `source9.tar`, `source9/`, `native/` and the recipe capsule are independently reread by verification. Runtime work uses only checked source bytes and the accepted exact Cloud archive.

## Prior machinery acceptance contract

Provide `context/reconciliation/cloud-phase0-evidence/YYYY-MM-DD/track-<first eight run UUID characters>/acceptance.json` in the committed archive. Its exact top-level fields are as follows.

| Field | Required value or type |
| --- | --- |
| `schema` | `workinants.cloud-f0-track-retained-base-machinery-acceptance.v1` |
| `decision` | `ACCEPT_EXACT_TRACK_THREE_MIGRATION_MACHINERY` |
| `posture`, `business_cases` | `D`, `NOT_RUN` |
| `assertion_promotions`, `operator_exit_code` | Integer `0`, integer `0` |
| `run_id`, `container_id`, `volume_created_at` | Actual canonical UUID4, full lowercase hex CID, exact recorded volume birth |
| `source_commit`, `source_tree` | Actual operation commit plus tree, both lowercase 40 hex |
| `candidate_commit` | `d25792e0524a70af763c31cc0c64605d737cc915` |
| `candidate_catalog_sha256` | `59a6a99a96748b72d8d639977c457857058777bf99346afb59804df926c107a9` |
| `ordered_migration_sha256` | `[5ae39abf991f9c189e367eb6ab6968b0ad50836bf4220ac27ef8c18306ac26ad,49c3345c281d8ef62355d5392d02085d5fdfa71f7193e7e0bd4264562c33cfb7,ae7b94aae1689b54d6da0b9443b2512087018270774124f2b1d012f65f6ddcdb]` as JSON strings |
| `reviewer`, `source_author` | Distinct actual actor identifiers |
| `files_sha256` | Exact hash map of `operation.json`, `operation-exit.json`, `created-container.json`, `created-volume.json`, `evidence/run-evidence.json`, `evidence/noop-track-retained-base-results.json`, `independent-closure.json` |

The `operation-exit.json` must bind the actual observed process exit code zero, `PASS_TRACK_THREE_MIGRATION_MACHINERY_ONLY`, `evidence_complete: true`, exact packet and run-evidence bytes, and `method: ACTUAL_OPERATING_PROCESS_EXIT`. The actual outer run and result receipts must corroborate `29,089 / 416 / 22 / 3`, complete eight-column no-op preservation, pre-finalization and restored Track authority, real deploy/status/no-pending deploy, immutable sources and full-ID cleanup on the corrected operator. The independent closure needs `run_id`, `reviewer`, `decision: EXACT_TRACK_THREE_MIGRATION_MACHINERY_AND_CLEANUP_VERIFIED`, `created_container`, `created_volume`, `daemon`, `image`, `cleanup_verified` and `file_sha256`. Its cleanup map contains the same eight exact true absence/identity fields in `prior_machinery.CLEANUP`. Its file map covers the six actual siblings. An earlier stopped or ambiguous runtime never supplies this input.

## Fresh reviews and explicit execution

The current packet's `source-review.json` and `literal-review.json` use `P.read_review` with `schema`, `decision`, `reviewer`, `source_author`, `bindings` and `scopes`. Use the exact `SOURCE_REVIEW`, `LITERAL_REVIEW`, `SOURCE_SCOPES`, `LITERAL_SCOPES` and computed `bindings` in `owned_operation.py`. The literal binds the source receipt hash. Both bind the latest operation/source tree, prior accepted machinery hash, exact recipe review and archive, fresh target and reviewed eight grants. The earlier v4 recipe review establishes source provenance only.

A future admitted call uses `python -B owned_operation.py execute --execute-reviewed-cloud-f0-track-retained-selection-owned-v1 --packet <absolute operation.json>`. The entry requires the committed packet, typed approvals and exact fresh directory before the exclusive `attempt.json`. The inherited bounded Cloud owner reinspects the live daemon and resources before any SQL. The business driver preserves eight grants and the exact 42-table projection, prior selection and subscription, and distinct receipt scope. A new owner cannot reuse the old machine CID or run ID.

## Outcomes

The fresh business owner's machinery receipt is `evidence/track-retained-base-results.json`. Its Track section binds the business result's path and hash after success. The separate `evidence/track-retained-selection-business-results.json` uses `workinants.cloud-f0-track-retained-selection-business-result.v1` and `PASS_FINITE_TRACK_RETAINED_SELECTION_ONLY`. It binds exact current resource and packet identity, the two ordered case results with `already_enrolled`, v4 source hashes, eight grants and 26 closed observations with their hashes. It also carries 42-table comparisons and native, oracle and ledger parity. Current `evidence/run-evidence.json` uses `workinants.cloud-f0-track-retained-selection-owned-run-evidence.v1`. Acceptance requires the child result, outer status, independent closure and exact immutable readback. A stopped run preserves the first failure, suppresses later SQL when closure is uncertain and independently attempts exact resource cleanup. The synthetic paid-shaped case and the finite Free case contribute zero assertion promotions. Real billing evidence is separate.
