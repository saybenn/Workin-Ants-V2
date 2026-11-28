# Held Track retained-selection business recipes

These recipes prepare two disjoint synthetic Customer cases for a separately reviewed Cloud owner on the exact held three-migration catalog. Each case creates its own genuine Customer intent and Work item. The retained worker transaction links its own command, effect, inbox, attempt and enrollment receipt to that Work. It reports `already_enrolled` while the existing Subscription and BaseSelection stay intact.

The Free case uses the reviewed provider-neutral plan shape. The paid-shaped case uses the existing `manual` enum with an in-range synthetic period and empty external provider identifiers. The nominal price distinguishes the synthetic subscription plan from Free and carries no billing or provider authority.

## Review sequence

1. Establish a fresh isolated three-migration target under its own reviewed owner. Verify the genuine ledger histories, native parity, migration status, repeated deploy no-op and original-grantor finalization before fixture setup.
2. Review `user-plan-fixtures.sql` as a separate fixture transaction by the exact `postgres` observer and setup role. It temporarily disables only `owner_commit` on `app.users`, `app.user_security_profiles` and `app.track_plans`, forces remaining constraints, and re-enables all three before commit. Confirm actual connection closure and full native parity. Bootstrap the one synthetic service identity under the separately scoped `wa_identity_service_authority` using the copied Worker source.
3. For each case, commit `source-customer.sql` under the declared restricted app grant and verify the original Customer observer. Commit `prior-selection-fixture.sql` separately after the Customer exists. This fixture inserts its matched Subscription and BaseSelection and applies only the two declared `owner_commit` exceptions. Keep physical, binding and enrollment triggers active. Verify the owner guards restored and native parity after closure. The worker must observe rows from the earlier fixture transaction.
4. Commit `schedule.sql` as the restricted app, then `claim.sql` as the restricted worker with fence zero and a fresh case-local lease secret supplied only in memory. Observe `before-retained-observe.sql` under the exact closed observer role and take the complete 42-table snapshot after both connections are closed.
5. Commit `retained-effect.sql` on a new `wa_worker` READ COMMITTED backend with its independently committed context grant, the same actual transaction tuple and the same lease secret at fence one. The exact markers require force-checking deferred constraints, a linked effect and Work still leased. Verify closure before `after-retained-observe.sql` and the second 42-table snapshot. Enforce the exact count deltas in `PROOF.json`, including one separate issuer grant and one each of the command, effect, inbox, attempt and enrollment receipt. The Work count stays fixed and its same-row projection must match before and after except for `effect_receipt_id` and `mutation_transaction_id`. Every other table keeps its full hash and count.

The fixture starts with empty entitlement grants, subscription history, and usage counters, events, and reservations. Their equality supports no new rows in those tables. The attempt reason `synthetic-worker-control-enrolled` is a retained fixture label. Outcome authority comes from the verified command body, effect and enrollment receipt.

The restore leaves enumerate only their corresponding fixture guards. Any use requires the same reviewed owner, exact native identity and observed client closure. Source8's competing app writer remains held because its TrackSubscription scope cannot read the linked CustomerProfile and TrackPlan from the invoker binding trigger. The packet makes no concurrent-writer, real paid billing, worker-loop, complete case or database qualification claim.

## Reproduction

The generator requires the pinned offline pglast package and the exact checkout inputs recorded in `PROOF.json`. Use a new scratch output directory.

```sh
PYTHONPATH=/workspace/scratch/workin-ants-f0-parser.P9ULJH/python python -B prepare.py \
  --checkout /workspace/Workin-Ants-Phase0-cloud --output /workspace/scratch/new-held-track-packet
```

`MANIFEST.json` closes every output file and the generator. This packet remains `HELD_SOURCE_ONLY`, with runtime `NOT_RUN` and posture D.

The offline regression replays the two previous source grant refusals and checks all eight corrected templates against the original context coordinator's grant validator. It also compares every capability membership and all other template fields to the preserved previous packet.

```sh
python -B test_grant_values.py --checkout /workspace/Workin-Ants-Phase0-cloud \
  --previous /workspace/scratch/wa-track-retained-base-recipes-v3.RXtGCj/packet/PROOF.json \
  --current /workspace/scratch/new-held-track-packet/PROOF.json
```
