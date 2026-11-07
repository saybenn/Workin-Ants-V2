# Brain directive P0-C-03A — retained correction scope

Source: user-forwarded Brain decision, page context 7b2e9222-2a72-4cbb-b2b2-ec6433e4ad41. Reviewed commit: [8917e2035622017eccd14c99ad7fd2b55740163f](https://github.com/saybenn/Workin-Ants-V2/commit/8917e2035622017eccd14c99ad7fd2b55740163f). Existing branch: codex/p0c-candidate-corrections-2026-10-31. This retained transcription captures the governing correction instructions; original commit and prior review evidence remain in Git history.

> Brain decision: return `8917e20` to Work for source corrections. Hold the disposable database test.

> Continue from `8917e20` on the existing correction branch. The following decisions authorize **source changes and revised SQL drafts only**.

| Reported gap | Brain decision |
|---|---|
| DRAFT-01 · Current service authorization | Approve the proposed private, Identity-owned record for each service's current authorization generation and revocation state. Bind it to an Identity receipt. The grant issuer cannot create its own proof of current authority. Specify rotation, revocation and recovery before opening the service path. |
| DRAFT-02 · Worker verification | Approve narrowly scoped, read-only functions that answer fixed yes/no questions. Enumerate the columns each needs, including the link from the Customer message to the Track worker's effect. Preserve the worker's existing direct permissions. Test the wrong customer, job, plan revision and lease. |
| DRAFT-03 · Missing revisions | Make AgeGateAttempt and AgeGateBlock append-only. Add an owner revision to TrackUsageReservation and PrivacyRestoreMarker, with each update proving the prior revision and advancing it by exactly one. Update both candidate schemas and their evidence definitions together. |

> These decisions adopt the bounded remedies Work documented. Keep each affected path blocked until its replacement checks are present.

| Additional finding | Required correction before execution review |
|---|---|
| First-write evidence | Use one rule throughout the schema, generator and triggers. Creation has no predecessor and commits revision zero. An update must identify the exact predecessor. Add a valid create-then-update case and a wrong-predecessor denial. |
| Installation authority | Bootstrap gives the schema owner ADMIN FALSE, yet the application script expects that owner to revoke the temporary helper membership. Put cleanup under the authorized grantor or eliminate the temporary grant. Specify how to verify its removal after both success and failure. |
| Authorization and consent scope | The helper that checks action, purpose and root target has no policy or trigger caller. Enforce that scope at protected operations and test a wrong-purpose grant with otherwise matching row permissions. For consent, two matching empty context IDs are valid only for an explicitly registered global context. |
| Customer messages and result versions | A customer change requires matching messages, but an extra message can pass its own guard with only a committed command from the same transaction. Require every emitted message to match the exact source change, history and allowed message count. Test an extra Free-enrollment command beside a legitimate event. Also enforce the registered schema version on command results. |
| Worker completion and lease ownership | A queued item cannot attach its first effect receipt because its initially empty link is immutable. Permit one protected link to the exact matching effect. Verify the worker holds the current lease using a secret or trusted holder binding. A worker allowed to read the stored hash can copy it. Cover renewal, expiry, concurrent reclaim and an unrelated effect with the same fence number. |
| Reservation release | The guard checks proof on unknown → released, but unknown → active → released sidesteps it. Define permitted transitions explicitly. Release after an uncertain outcome must require durable proof tied to that exact reservation, command and effect. Test the two-step bypass and a receipt from a different operation. |

> **Return one corrected commit on the same GitHub branch.** Update the existing tracker and replay map, add independent positive and adversarial checks for these findings, and publish the verified commit for Brain re-review. Database execution, containers, hosted changes and migration adoption still require a separate decision.

Brain independently matched the original three SQL hashes, 18 requirement mappings and 94 selected replay IDs within the 451-case register. All 451 remain NOT_RUN. Brain inspected earlier offline results without rerunning or executing SQL. P0-C remains posture D. Work owns edits, checks and publication; no client decision or setup task is requested.
