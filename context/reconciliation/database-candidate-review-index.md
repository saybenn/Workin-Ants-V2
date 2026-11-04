# P0-C-03 foundation SQL draft — current review entry

Brain approved `671ef58383580687ecf728036bf32c302aeb026c` for **source-only F0 SQL drafting** under [P0-C-03](directives/brain-directive-p0-c-03.md). This draft is generated, **not execution-approved or adopted**. Posture D and all database/container/provider/runtime execution stops remain. The historical source packet below retains its recorded pre-generation flags; those are not the current drafting stage.

| Review need | Artifact |
|---|---|
| Current stage, exact reviewed inputs and draft hashes | [SQL drafting manifest](foundation-sql-draft-manifest.json) |
| Actual environment bootstrap SQL | [Role/namespace draft](../../review-output/foundation-bootstrap.review.sql) |
| Untouched Prisma source-only output | [Raw 40-model structure](../../review-output/foundation-structure.sql), [generation evidence/workaround](foundation-sql-generation.json) |
| Complete assembled application SQL review artifact | [Integrated structure/security draft](../../review-output/foundation-application.review.sql) |
| Installation/order/security decisions and exact open conflicts | [Technical review](foundation-sql-draft-review.md) |
| All 18 requirements and explicit F0/deferred/owner dependencies | [Control map](foundation-sql-draft-controls.json) |
| Exact SQL role/column maximums and physical model map | [ACL evidence](foundation-sql-draft-access.json), [40-model metadata](foundation-sql-draft-models.json) |
| Original proposed 94 tests mapped to controls, all NOT_RUN | [Replay map](foundation-sql-draft-replay-map.json) |
| Fresh offline checks and limits | [Draft validation](foundation-sql-draft-validation.json) |
| Normal Git publication and independent remote file/history verification | [Source publication proof](foundation-sql-draft-publication-verification.json) |

Review bootstrap separately from application ownership. The raw structural artifact is retained evidence; the integrated application draft includes its tables and is not an additional file to apply after the raw draft. The future single Prisma history remains inactive. The three named source conflicts are denied explicitly until reviewed; broad worker/helper access is not a remedy. Next action belongs to Brain, not another client setup questionnaire. Current project status stays in [the existing progress tracker](../progress-tracker.md).

## Historical P0-C-02 source packet

Start with the owner-authorized [B010-01/02/03 corrections](database-candidate-corrections.md), then the historical [Checkpoint 010](checkpoint-010.md). This packet is ready for Brain review, **not approved or adopted**. It performed source work only: no target contact, DDL generation, migrations, seeds, resets, provider changes or runtime implementation. Posture D remains.

| Review need | Authoritative artifact |
|---|---|
| Exact governing assignment | [Retained directive](directives/brain-directive-p0-c-01.md) |
| File hashes and execution boundary | [Candidate manifest](database-candidate-manifest.json) |
| Every model, field, compatibility case and staged change | [Existing inventory, extended physical_candidate_review](greenfield-model-security-inventory.json) |
| Human model/owner/stage summary | [Model ledger](database-candidate-model-ledger.md) |
| Ordinary technical choices and rationale | [Decision register](database-candidate-decisions.md) |
| Full staged physical representation | [214-model schema](../../prisma/review/physical-candidate.prisma) |
| Proposed first migration cut | [40-model foundation schema](../../prisma/review/foundation-candidate.prisma) |
| Objects/invariants Prisma cannot represent | [18 SQL-only specifications](database-candidate-sql-objects.json) |
| Object ownership, roles, access and exceptions | [Access matrix](database-candidate-access-matrix.json), [security analysis](database-candidate-security.md) |
| Exact JSON admission and staged restrictions | [JSON boundary register](database-candidate-json-boundaries.json), [review-only schemas](../../contracts/database-review/) |
| Single history, disposable identity, comparison and recovery | [Migration/replay plan](database-candidate-migration-plan.md) |
| Actual logins, fixtures, actions and expected outcomes | [451 planned tests, all NOT_RUN](database-candidate-tests.json), [synthetic fixture specification](../../tests/database/candidate-fixtures.json) |
| First P0-D owner/contracts/files and prerequisites | [Continuation plan](database-candidate-continuation.md) |
| Remaining DBP evidence | [Live provenance handoff](database-provenance-handoff.md), [requirements](database-provenance-requirements.json) |
| Actual offline schema validation and CLI behavior | [Current correction native proof](database-candidate-corrections-native-validation.json); [historical native proof](database-candidate-native-validation.json) |
| Exact checks, negative cases, preservation and limits | [Checkpoint validation](checkpoint-010-validation.json) |
| Reviewed source versions | [Source-input hashes](database-candidate-source-review.json) |

Reproduce the review representation with the three prepare-database-candidate*.py scripts, in schema → security → assets order. They read/write source only. Run check-database-candidate.py and check-database-candidate-negative.py for source/evidence consistency; those commands cannot establish database behavior. Native validation needs the pinned dependencies and environment-free review configs. The validation report preserves exact commands and the independent reproduction comparison.

The downloaded review archive includes these files at their repository-relative paths. The separate full-history Git bundle is the complete recoverable repository. The external recovery manifest pins its final HEAD/tree/checksum and gives restore instructions; no public remote publication is implied.
