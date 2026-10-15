# Publication blocker and exact-history recovery

The authorized command `git push -u origin codex/development-readiness-2026-09-29` failed on 2026-10-15 with:

```
fatal: could not read Username for 'https://github.com': No such device or address
```

Read-only fetch and remote-head listing succeeded. The remote dedicated branch was not created by this push. This is missing Git transport authentication, not a refusal of user authorization. No force-push or main merge was attempted. The GitHub connector offers object/file creation but cannot reproduce these exact local commit objects (including original author/time metadata) through its exposed commit schema; reconstructing a replacement history is not the authorized transfer.

The delivered `Workin_Ants_Account_Transfer.zip` contains:

- `workin-ants-readiness.bundle`: complete dedicated-branch reachable history, with no prerequisite commit requirement.
- The operational handoff and bootstrap prompt as standalone files.
- `RECOVERY.md`: exact final local commit and verified recovery commands.
- `SHA256SUMS.txt`: checksums for bundle and included documents.

The ZIP is outside the repository to avoid recursive inclusion of its own commit. A clean clone from the bundle was checked against the final source HEAD and tree and the repository validators were run in that clone. See the package verification report.

## Recover in the new Work environment

Extract the ZIP, then execute from its directory (choose a fresh destination):

```bash
git clone --branch codex/development-readiness-2026-09-29 workin-ants-readiness.bundle workin-ants
cd workin-ants
git remote set-url origin https://github.com/saybenn/Workin-Ants-V2.git
git status --short
git rev-parse HEAD
```

Compare HEAD to the exact SHA in the package's RECOVERY.md and the sender's final response. Read the handoff/bootstrap immediately; do not start a new reconciliation audit.

To publish from an environment with authorized GitHub Git authentication:

```bash
git fetch origin
git ls-remote --heads origin refs/heads/codex/development-readiness-2026-09-29
git push -u origin codex/development-readiness-2026-09-29
git ls-remote --heads origin refs/heads/codex/development-readiness-2026-09-29
```

If the remote branch now exists, compare its history first. Push only when it is absent or a fast-forward from the inspected remote head. If it diverged, preserve both histories and reconcile deliberately; never force-push or reset away another developer's work. Publication is verified only when remote HEAD equals intended local HEAD. If the receiving environment also lacks Git credentials, use this bundle with an authorized local Git client to publish, then connect the Pro account to the published branch. Do not paste tokens into a chat or commit them.
