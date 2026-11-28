# Track retained selection candidate

The current Track receipt verifier requires the selected subscription to come from the same transaction. A valid existing Free or paid selection must be preserved when default-Free work arrives. The candidate allows an `already_enrolled` receipt for the exact authorized existing selection while retaining the same work, effect, inbox, source and generation checks. The stored result and receipt bind to the original outbox fingerprint. Customer subscription updates and the retained receipt share the User/track transaction lock. [Approved Track rule](../../context/reconciliation/platform-architecture-rulings.md#wa-r078--default-free-enrollment-handoff-bf-035)

Reproduce the append and ordered catalog offline with the pinned Cloud parser.

```sh
bash scripts/setup-cloud-f0-parser-v1.sh
# Apply the PYTHONPATH printed by setup before running this command.
candidate_dir=$(mktemp -d /workspace/scratch/wa-track-retained-base.XXXXXX)
python -B scripts/sql-review/prepare-track-retained-base-candidate.py --output "$candidate_dir/reproduced"
cmp "$candidate_dir/reproduced/migration.sql" review-output/track-retained-base-candidate-v1/migration.sql
cmp "$candidate_dir/reproduced/expected-catalog.json" review-output/track-retained-base-candidate-v1/expected-catalog.json
```

The ordered source uses the original two migrations and this candidate append. The expected catalog records three changed function definitions and the reversible installation-time schema privilege. Runtime qualification requires an independently reviewed three-migration packet on a fresh disposable target. It must verify actual history, original-grantor finalization, full catalog and no-op redeploy. [Independent source review](independent-source-review.json)

Exercise genuine new Free enrollment, preserved existing Free and paid selections, mismatch and expiry rollbacks, and both orders of the competing subscription validity update. Inspect the persistent receipt, selection, subscription, typed entitlements, history, same-period usage, and exact cleanup independently. Runtime is `NOT_RUN` and database posture is D.
