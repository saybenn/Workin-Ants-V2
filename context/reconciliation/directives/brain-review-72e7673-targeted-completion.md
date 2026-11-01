WORKIN ANTS — BRAIN REVIEW OF 72e7673
Targeted completion of P0-C-02

Reviewed commit:
72e7673ff0970907d7c75e3993553fcf67000a3d

DECISION

B010-01's issuer-committed immutable transaction binding and
B010-02's exact consent representation are accepted at the
source-design level. Preserve them.

Database-script generation is NOT yet approved.

Complete the two narrow corrections below on the existing
correction branch. Do not restart architecture or restoration.

1. CORRECT TRACK WORKER PERMISSIONS

In scripts/database-candidate-correction-rules.py,
access_profile() currently assigns
INSERT_OR_UPDATE_DEFAULT_FREE_ONLY_WITH_CURRENT_CUSTOMER_FACT_AND_COMMAND_RECEIPT
to every Track-owned model.

This produces contradictory positive tests, including an
update-capable operation for immutable TrackUsageEvent records.
It also assigns the enrollment worker writes to plan-catalog
tables without distinguishing catalog administration.

Replace this owner-wide assignment with an explicit,
stage-appropriate model/handler/operation mapping derived from
the existing assignDefaultFreeTrack.v1 contract and continuation.

Required boundaries:

- The default-Free handler may read the existing approved plan
  and benefit definitions it needs. It must not create or alter
  the plan catalog as a side effect of enrollment.

- Permit only the enrollment/selection changes actually required
  by the existing contract. Preserve current valid Free or paid
  selection and the original semantic enrollment identity.

- TrackEnrollmentReceipt and TrackSubscriptionEvent may receive
  their required new evidence, but existing immutable semantic
  records cannot be updated or deleted by this worker.

- Default-Free enrollment must not consume, reset or rewrite
  existing usage events, counters or reservations. Grant reads
  only where the actual handler needs them.

- Review every affected F0 Track row. Do not replace the broad
  rule with another vague operation label.

- Keep fixture preparation separate from application-worker
  permissions. A test's need for prepared catalog data is not
  permission for an enrollment worker to administer that catalog.

Regenerate the existing access matrix and test definitions from
the corrected source. Preserve the schema and business decisions
unless a concrete inconsistency requires a documented change.

Add independent semantic checks and adversarial cases that reject:
- Worker UPDATE/DELETE of immutable Track evidence.
- Default-Free writes to plan/benefit definitions.
- Default-Free alteration of existing usage.
- The same forbidden operation inserted into BOTH the matrix and
  test definition, even though those two artifacts still agree.

Do not derive the expected security boundary exclusively from
the same generator being tested.

2. FIX P0C-CTX-02'S STALE SETUP

Update scripts/prepare-database-candidate-review-assets.py and
regenerate context/reconciliation/database-candidate-tests.json.

Replace "Valid grant issued before source transaction" with the
actual corrected sequence:

- Open the runtime/worker READ COMMITTED transaction.
- Capture its actual login/backend/transaction tuple before
  business reads or source locks.
- Have the separate issuer authorize and commit the bound grant.
- Bind through the permitted helper.
- Commit the tested revocation or generation change through its
  appropriate authorized path before the protected action.
- Verify the protected action is denied without the forbidden
  mutation or disclosure.

State which connection performs each action. Keep revocation
and generation-change scenarios distinguishable.

Add a source regression that rejects the superseded issuance
order in current test specifications. Do not rewrite historical
checkpoint evidence.

3. VALIDATE, COMMIT AND PUBLISH

Update affected generated artifacts, selection fingerprints and
current validation records consistently.

Run the applicable pinned offline schema/source/context and
adversarial checks. Keep every unexecuted database/runtime case
NOT_RUN. Do not manufacture a particular test count.

Use the existing working folder and branch:
C:\Users\elijr\source\WorkinAnts-Checkpoint010
codex/p0c-candidate-corrections-2026-10-31

Verify the actual current state first and preserve any later work.
Commit the narrow corrections and publish normally to the same
GitHub branch, retaining the existing deployment safeguards.
Verify the remote HEAD. No force-push or main merge.

Update the existing progress tracker and correction note.
Do not create a new bundle, ZIP or client questionnaire when
normal publication succeeds.

Return a short result:
- What changed.
- Which checks passed or were unavailable.
- Published commit and branch.
- Any remaining blocker.
- "Ready for Brain re-review; no human setup action needed"
  when applicable.

BOUNDARIES

Posture D remains.
No DDL/script generation, database connection, container run,
migration, seed/reset, hosted change or runtime implementation.

These corrections are source-only. Return the published commit
for the approval decision.