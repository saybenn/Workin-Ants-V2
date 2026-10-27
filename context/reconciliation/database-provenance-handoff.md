# P0-C — reviewed candidate and evidence handoff

Updated 27 October 2026, Brain Directive P0-C-01. **Candidate ready for Brain review; posture D remains.** This assignment performed source review only. It contacted neither project and generated no DDL. Current checkpoint: [010](checkpoint-010.md); exact review artifacts: [candidate manifest](database-candidate-manifest.json).

The intended fresh project remains **lyalfdmfheevpahywuhv — Workin Ants MVP** ([endpoint](https://lyalfdmfheevpahywuhv.supabase.co)). Checkpoint 009 accepted its scoped identity/environment/version and empty application namespace. The older **sdceenkakajslwpctbgl** remains preserved and forbidden as a replay/shadow target. No new project, account or pasted credential is required for candidate review.

## Existing evidence and its limits

The [27 October observation](database-observations/2026-10-27/manifest.json) preserves provider identity, PostgreSQL 17.11, creator-specific defaults, public-only auto-RLS setup, two advisor warnings, empty app/public relations and absent migration histories. It does not prove managed Auth/Storage records empty, complete Data API exposure, effective least-privileged access, backup/restore coverage or safe adoption.

The [26 October observation](database-observations/2026-10-26/manifest.json) remains historical evidence only: the older target contains the June structure and matching historical Prisma ledger. Its objects/data are not disposable. Do not contact, reuse, reset or erase it under P0-C-01. Historical read-only probes are preserved; this directive requested no further live query.

## Candidate review now supplied

The canonical [model/security inventory](greenfield-model-security-inventory.json) is extended by physical_candidate_review, without rewriting its original 177 rows or 12 compatibility records. It now accounts for every original model/field and 37 justified additions: 214 models/219 enums in the staged candidate, 40 models in the proposed foundation FK closure. [Model ledger](database-candidate-model-ledger.md), [technical decisions](database-candidate-decisions.md), [SQL-only register](database-candidate-sql-objects.json), [object/access matrix](database-candidate-access-matrix.json), [JSON admission rules](database-candidate-json-boundaries.json) and [security analysis](database-candidate-security.md) form one package.

Both review schemas validate under pinned Prisma 7.10.1 with environment-free configs. Syntax and traceability do not establish installed SQL objects, RLS behavior, current actor/field authority, runtime atomicity or Privacy execution. The actual source schema, June migration, canonical shared contracts, P0-B source/dependencies and UI are preserved.

## Requirement states

| Requirement | Current state | Still required |
|---|---|---|
| DBP-01 identity | VERIFIED, scoped | Reconfirm exact identity before any later execution |
| DBP-02 environment | VERIFIED, scoped | Bind each later disposable/hosted action to its exact target |
| DBP-03 preservation | PARTIAL | Actual retained-data, backup and authorized disposal obligations |
| DBP-04 version/managed objects | VERIFIED, scoped | Later target versions/extensions and managed preservation comparison |
| DBP-05 namespace/ledger | VERIFIED, scoped | Actual installed history/catalog after approved execution |
| DBP-06 complete structure | PARTIAL | Full selected-cut catalog comparison including SQL-only objects |
| DBP-07 privileged objects | PARTIAL | Actual helper/default/trigger boundaries; exact public-function disposition tests |
| DBP-08 grants/API/RLS | PARTIAL | Positive/negative actual logins, pool isolation, field/source parity and provider exposure |
| DBP-09 physical candidate | PARTIAL; source review ready | Brain approval; actual approved SQL and physical qualification |
| DBP-10 replay | NOT_OBTAINED | Exact disposable identity/digest/tools, installation/redeployment/failure/recovery evidence |
| DBP-11 backup/access | PARTIAL | Actual backup/restore/retention/secret handover and privacy restore-marker coverage |
| DBP-12 adoption | NOT_OBTAINED | Evidence-supported exact schema/history/security adoption decision |

DBP-10's executable test specification is planning evidence, not an actual replay. DBP-12 cannot close because the candidate is syntactically valid. Four requirements retain scoped verification, six are partial and two remain pending.

## Next action boundary

Brain reviews the exact packet hashes and proposed ordinary technical choices. Approval precedes the [specified source-only SQL generation](database-candidate-migration-plan.md). Reviewed structural/security SQL and environment-role prerequisites then require authorization for an exact synthetic disposable identity/actions before execution. No DDL generation, provisioning, migration, seed, reset, provider setting or test table is authorized by P0-C-01.

The selected future executor is one pinned Prisma application migration/security history. Historical June SQL stays preserved/inactive; no db push/reset, fake applied ledger, competing Supabase application history or hosted shadow database. Managed Auth/Storage/Realtime/extensions retain ownership. Full catalog and actual allowed/denied tests, recovery and affected backup/preservation facts precede an adoption decision.

The [451-test plan](database-candidate-tests.json) marks every database, worker, adapter and executor test NOT_RUN and separates P0-C/D/E/F. The [first P0-D proposal](database-candidate-continuation.md) is Customer provisioning → durable default-Free Track enrollment, with current authority and minimal Privacy prerequisites. It is not implemented. U.S./18+ launch boundaries, excluded therapy/prescribing/child-directed/prize paths, external vendor/legal gates and separate UI work remain unchanged. No contract freezes, parallel lanes or Step 20 development follow from this checkpoint.
