# Cloud Customer stale-predecessor fixture packet v2

The full-table observer now requests bytewise table-name ordering with `COLLATE "C"` in the outer aggregate. The validator still requires all 42 projections in exact order with their original row shapes. At a fixed fixture ID, the ten other SQL leaves match the published v1 packet byte for byte. The generator orders the baseline grant's same 179 capabilities after substituting fresh UUIDs so that the inherited issuer accepts the fixture.

Use the repository's pinned PostgreSQL 17 parser, `pglast==7.21`, in an isolated Python path. Run these commands from the repository root.

```sh
python -B -m unittest discover -s scripts/sql-review/cloud-customer-stale-predecessor-v2 -v
output=$(mktemp -d)
python -B scripts/sql-review/cloud-customer-stale-predecessor-v2/prepare.py \
  --fixture-run-id d71b17d0-8156-416b-aadb-d2abc2c3ef21 --output "$output/source-only"
```

The offline reproduction emits 12 files. The fixture hash is `87f85b0db37da7b62a0be3bf11912e3ee071218491ef24d22fba660222d98e20`. The observer hash is `a27a308bca693b77badea835b32000e35dbb47b4a8b6d606fc69b64b0af3f8eb`. The fixture content hash is `f9c77a74132cbb76551855b49f2355b85fe87164dbad35ab350cdc27abd6bf27`. Reserve that fixture ID for offline reproduction and choose a fresh UUID4 when preparing an operational packet.

Seven focused offline tests passed. The ordering mock reads the generated SQL projections and aggregate order, then drives the unchanged coordinator. Under a modeled default sort that gives punctuation lower priority, the original SQL fails the strict shape check and the corrected SQL meets it. A separate run of the model with the Cloud host's `en_US.UTF-8` collation differed from the strict order at 11 positions before the correction and matched all 42 afterward. The parser verifies the exact outer aggregate ordering expression. Replaying the exact Cloud `549e90b7` fixture reproduced the issuer's capability-order refusal before INSERT. The regression reaches the same issuer's modeled INSERT, returned timestamp verification and closure after the ordering fix.

The Windows attempt `73292a8f` remains recorded as a stop at the first complete snapshot after its one-history observation. The rejected response and target collation were unretained. The model demonstrates a source ordering defect, and the full cause of the historical stop remains unknown.

The corrected Cloud fixture requires fresh source and literal reviews, resource preflight, execution, and evidence admission. The prospective ceiling remains the selected `P0C-CAS-01/control.stale_predecessor` assertion after observed restricted-role controls, post-state proof, and verified cleanup. Posture D and the historical qualification counts still apply.
