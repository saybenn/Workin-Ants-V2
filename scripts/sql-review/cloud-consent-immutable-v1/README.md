# Held Cloud Consent empty-context proof

This source covers only `P0C-IMMUTABLE-01/control.empty_context`. The two cases pair SQL `NULL` with SQL `NULL` and the empty string with the empty string. The current global-context registry returns `false`. The initial and appended source8 migrations retain hashes `5ae39abf…` and `49c3345c…`. The source8 append replaces `runtime_transition()` and leaves the pinned Consent guard and registry intact. Runtime remains `NOT_RUN`, with zero assertion promotions and database posture D.

The procedure follows the [November 20 source plan](../../../context/reconciliation/local-f0-source-followups/0ff-read1161-install6850-reviewed-V6-V8-20261120/Remaining-immutable-CAS-source-facts-PLAN.json) and the checked-in [Consent scope](../../../context/reconciliation/foundation-sql-scope-policy.json). Generate the held source receipt with the pinned Cloud pglast 7.21 environment. The fixture UUID here is for offline reproduction.

```sh
python -B scripts/sql-review/cloud-consent-immutable-v1/prepare.py \
  --fixture-run-id 13572468-1246-4ad8-9c12-02468ace2468
python -B -m unittest discover -s scripts/sql-review/cloud-consent-immutable-v1 -v
```

`prepare.assemble()` returns the packet and 15 exact SQL assets in memory. The command writes the held receipt to standard output. It reads 14 pinned sources, including both migrations, the effective catalog, the two reviewed Identity setup exceptions, and the exact App pipe and grant helpers expected by a future owner.

## Required observations in an owning Cloud operation

1. Bind a fresh, verified source8 target to the live run, commit, tree, packet, immutable container ID and volume creation. Complete genuine exact two-row migration and repeated-deploy no-op proof, original-grantor finalization, current restricted authentication and full native and ledger comparisons. Establish all-client absence, the 100-trigger observation and a fresh fixture namespace.
2. Use the previously reviewed synthetic Identity setup within its own transaction. The setup momentarily disables `owner_commit` only on `app.users` and `app.user_security_profiles`, inserts exactly the new synthetic User and same-User security profile, and restores both triggers before commit. Check exact synthetic Identity presence, restored 100-trigger observation and full native parity. Capture the complete 42-table baseline with zero grant exclusions.
3. For each case open an actual `wa_app_runtime` transaction at READ COMMITTED and capture the login, backend and transaction tuple before protected work. Through separate authenticated `wa_context_issuer` connections, commit each of the exact publisher, presentation and SH-007 grants and close its backend before rebinding the original App tuple. Observe the same tuple at each bind. Grant templates derive every finite capability from named RLS field arrays and the registered related reads. Publisher and presentation inserts must each return the exact Boolean observation. Both writes stay in the App transaction.
4. Under the proof grant, observe one visible presentation/content pair, all other binding predicates exact, and an absent global registration. The proof SQL uses that presentation's `created_at` as the bounded synthetic acceptance timestamp and the exact PostgreSQL UTF-8 rendering hash. Require a before marker, no after marker or success acknowledgment, psql exit `3`, and SQLSTATE `P0001` with `exact consent binding required` at `platform_private.consent_guard()` body line 17. Its body SHA-256 is `61dc444ce22f462fbbfcfa706f0cfdce5a7e16a028592b51d1fec07fa219e7ae`. The payload can only roll back if the attempted insert unexpectedly returns. Expected terminal exit closes and rolls back the original transaction.
5. After each case independently verify exact App and issuer backend absence, all-client absence, the unchanged 100 triggers and full source8 native catalog. Check zero rows at all generated Consent IDs and semantic keys and exact 42-table equality with the post-Identity baseline. The equality excludes only the three or six newly issued grant UUIDs, which receive separate exact all-field retention checks under `wa_context_issuer`. Close and reread sanitized evidence, preserving the first failure and stopping further case dispatch on any mismatch or transport uncertainty. The owning operation also completes its independent ledger/native postcheck and exact cleanup.

The test ceiling is the single empty-context denial assertion after observing both variants. Legal applicability, rendered-user behavior, accepted or replayed consent, age evidence, and the remaining immutable assertions have separate requirements.

## Owning operation remains held for review

The owning composition binds the proven App `BoundedSession`, exact App context helpers, and the accepted TWO owner seam to this Consent recipe. Its distinct source and literal operational reviews bind a fresh target and preserve the scope above. [Owning operation](OWNING.md)
