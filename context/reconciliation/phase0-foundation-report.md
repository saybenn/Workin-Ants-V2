# Phase0 foundation checkpoint — Directives006/006-A

**P0-B functional acceptance passes; dependency security remains OPEN.** TECH-LOCK-001 and TECH-ROUTER-001 are resolved for the pinned Linux foundation. Clean installation, actual lint/route typegen/strict typecheck/production build and 41 real development/production HTTP checks pass. The new dependency audit reports15 affected packages including critical Next advisories; no version upgrade or production security clearance is claimed. Overall readiness remains NOT_READY;0 active parallel lanes and0 SH runtime-qualified/frozen operations.

## Workspace and legacy treatment

Original dedicated branch:codex/development-readiness-2026-09-29 at Checkpoint005 bbeb4c2a3a1ccd110273d7185f113db546549009, clean and preserved. New sequential branch:codex/phase0-clean-foundation-2026-10-19 in a separate Git worktree of the same repository. This is one bounded foundation workspace, not a parallel domain-agent lane. WA-R091 implements the explicit006-A amendment to R090's previous in-place normalization guidance.

The new app/ owns a minimal static shell, not-found handling, process-only health and development diagnostics. It has no forms, authentication, Prisma client, provider SDK, financial/queue/owner runtime or product feature. No old application behavior is silently imported. Thirteen original application/utility files and eight original configurations are preserved byte-for-byte under legacy/checkpoint-005/. The [inventory](legacy-application-inventory.json) pins21 archive files to the exact005 baseline; Git retains all earlier history. Archived pages/ is outside active router, strict compiler and ESLint inputs. Re-activation requires review and would restore known old debt.

The new health endpoint returns only fixed process-liveness data with no-store;it makes no database/provider readiness claim. Diagnostics use server NODE_ENV development mode. Public environment flags, query parameters and headers cannot enable them in production. The old arbitrary logger, raw-error handling, environment-presence utility and public-flag-based guard are preserved inactive. All methods of the debug API return404 in production. No secret value is displayed.

## Exact nine-role context mapping

| Foundational role | Actual file | Result |
|---|---|---|
| Product orientation | context/project-overview.md → project-overview-v3.md | Concise authoritative routing entry point added;V3 product truth retained |
| Architecture | context/architecture.md | Rich lower-level source/contract invariants retained;clean-foundation route added |
| Phased work/acceptance | context/build-plan.md | Mandatory Phase0, clean worktree and conditional later phases aligned |
| Code discipline | context/code-standards.md | Strict live-source boundaries, archive isolation, security and slice completion |
| Pinned usage | context/library-docs.md | Installed Next16.2.6 guidance, actual scripts and Prisma7 offline usage |
| Visual values | context/ui-tokens.md/json | Existing semantic values applied only to minimal shell |
| Interaction/safety | context/ui-rules.md | Owner/authority/privacy/accessibility rules retained |
| Reuse inventory | context/ui-registry.md/json | Actual shell, archived EnvironmentBanner and planned primitives/screens distinguished |
| Live state | context/progress-tracker.md | Current006 results, next actions and explicit limits precede history |

[context-foundation-review.md/json](context-foundation-review.md) records review of all nine upstream templates and README at jsmastery-pro/context-driven-dev commit cbd852b8ca3ff98b02329c4a2b98f91dbbf8ab47 via GitHub. Gaps resolved:missing unversioned overview, stale availability-only V3 text, explicit nine-file startup order, per-slice UI registry maintenance and amended clean-foundation guidance. Template UI-first sequencing, example model/provider/font choices, uniform API envelope and retrieval-method authority hierarchy were not adopted. Workin Ants concern authority and richer architecture remain.

AGENTS/CLAUDE load the nine roles first, then select actual owning/consuming Module/Cluster plans, connected journey and exact SH resources. They do not recursively load every historic report. UI registry updates after every slice must record actual paths, API/classes/token use, evidence and limits;ten planned primitive families and eight product screen patterns remain unimplemented. No direct shadcn/Radix/Zod dependency was added.

## Package/toolchain proof and actual failures

Available/proven environment:Linux, Node24.19.0/npm11.9.0, Next16.2.6, React/ReactDOM19.2.4, Prisma/client7.8.0 and all other original resolved package versions. Node/npm pins and packageManager/engines metadata are explicit. No existing dependency version, resolution URL or integrity changed;direct dependency declarations are unchanged.

Initial clean ci failed EUSAGE for missing @emnapi/core/runtime lock records. Registry-backed lock repair added eight missing records:top-level core/runtime1.10.0 and six bundled Tailwind wasm dependency records. This matches the pre-existing resolver's exact1.10.0 requirement and retains wasi-threads1.2.1. An initial broad resolver candidate selecting newer optional @emnapi/wasi entries was rejected before final installation. No force, legacy-peer, TLS bypass or ignored lifecycle failure was used. The final current lock installs453 applicable packages with lifecycle scripts enabled. See [reviewed package change](phase0-approved-file-changes.json).

The original Prisma config requires DATABASE_URL even while loading CLI help;an environment-free offline config now validates the schema without supplying a synthetic/real connection URL. This is source validation, not migration or live schema evidence. The old db:check executes SQL writes, so migrate/seed/check npm aliases now fail closed;three real denial checks confirm no database command is invoked. Direct CLI capabilities remain installed;the aliases are an accidental-execution guard, not a credential/security sandbox.

## Executed qualification

| Command | Actual result |
|---|---|
| npm ci --no-audit --no-fund --fetch-retries=0 --fetch-timeout=20000 | PASS, 453 applicable packages;current lock and lifecycle scripts enabled |
| npm run lint | PASS, ESLint9 over active source;archive excluded |
| npm run typecheck | PASS, next typegen then strict tsc --noEmit |
| npm run build | PASS, actual Next16.2.6 production Turbopack build and generated route/manifests |
| npm run test:foundation | PASS41 real loopback HTTP/client-asset/restart checks |
| npm run db:validate | PASS, Prisma7.8 source schema;no datasource/environment/DB contact |
| npm run db:migrate / db:seed / db:check | Expected exit1, all three write aliases deny |
| npm audit --omit=dev --json | Exit1, 15 affected packages;security gate OPEN |
| python scripts/check-context.py | PASS, all established structural/source/event/bridge/platform/root/foundation checks plus new Phase0 checks |
| Negative architecture/source checks |PASS:30 retained/new foundation package-guard mutations and13 Phase0 mutations rejected;results in linked evidence |
| git diff --check / staged diff check | Required PASS including newly added source/archive files |

[phase0-foundation-validation.json](phase0-foundation-validation.json) retains command output/exit codes, installed-guide hashes, source fingerprints and 41 HTTP results. The smoke proves root/health, unsupported health mutations, unknown/old filename routes, dev page, production404 denial across debug methods, misleading public flags/query/headers, trailing slash, secret-canary absence from responses/root client scripts and production restart denial. Tests bind127.0.0.1 and stop the servers. No actual provider/account/database input or credential is used. [phase0-preservation-validation.json](phase0-preservation-validation.json) confirms source/schema/history protection.

These tests qualify the bounded local Linux framework foundation. They do not qualify Windows, deployed hosting, security exploit resistance, rendered browser accessibility, source-owner adapters, Postgres/RLS/concurrent recovery, complete Privacy field/actions/providers or any of the 132 SH runtime implementation. The41 HTTP checks are real framework execution;the architectural mutation checks remain static evidence. Neither category substitutes for the other.

## New dependency security gate

[dependency-security-review.md/json](dependency-security-review.md) and the raw [audit](dependency-audit-2026-10-19.json) retain15 affected package classifications:1 critical, 10 high, 4 moderate. The number counts packages, not distinct advisories or proven reachable exploits. Peer-linked tools remain in the omit-dev graph and need scope review.

Three critical Next maintainer advisories were independently read:Windows-hosted filesystem RCE (patched16.3.3), AVIF/sharp/libheif optimization RCE (patched16.3.3), and next/og ImageResponse RCE (patched16.3.6). Current16.2.6 is in the reported affected ranges. Qualification ran on Linux and the clean app has no next/og/ImageResponse or image/upload integration;these are limited scope observations, not clearance. Other Next/transitive findings remain.

TECH-DEPENDENCY-SECURITY-001 remains open. npm suggests Next16.4.2 for the direct Next group;this is a proposal, not an adopted upgrade. The smallest next security task is an exact advisory/reachability review and bounded matched Next/eslint-config-next/transitive/Prisma7-compatible remediation diff, then new installed guidance and full requalification. Preserve this tested baseline for comparison. No bulk audit fix, Prisma major migration, production exposure or version change was performed under the no-unapproved-upgrade constraint.

## Greenfield database proposal and remaining evidence

A brand-new isolated development database is the preferred evaluation target. The old Supabase target has not been reused, reset, erased or contacted. Posture D persists. [database-provenance-requirements.json](database-provenance-requirements.json) assigns12 actual-evidence requirements;all are NOT_OBTAINED. The environment owner must identify/sanitize the isolated target, isolation/data-preservation obligations, actual migration ledger and full catalog/security comparison. No passwords, tokens, connection strings or personal rows are requested in repository evidence.

[greenfield-model-security-inventory.json](greenfield-model-security-inventory.json) routes177/177 current physical models and all 12 accepted compatibility cases:11 physical mirrors plus architecture-only Ops QueueJob. The latter is not fabricated as a physical table. Source owners, default browser denial and proposed reconciliation duties are explicit.53 historical creates/124 static gaps persist;Prisma validation does not approve these as a fresh baseline.

[greenfield-database-strategy.md](greenfield-database-strategy.md) specifies identity→owner/constraint reconciliation→candidate DDL/security review→single history routing→disposable replay/catalog comparison→actual allow/deny/concurrency/privacy tests→adoption. It covers managed Auth/schema boundaries, grants/default privileges/RLS, views, functions/search_path/triggers, BYPASSRLS, actual role/actor/currentness/security vectors and safe forward-repair/checksum stewardship. These are proposals/required future tests. No new baseline SQL or RLS migration was generated or applied. P0-D actual durable runtime remains gated on the relevant proven DB/security prerequisites.

The13 externally gated operations retain exact previous reasons:SH-017/SH-018 Trust, SH-019 financial readiness, SH-020 Healthcare, SH-065 AI provider, SH-067 Calendar, SH-068 Video, SH-069 geocoding, SH-070 provider deletion, SH-083 malware scanner, SH-106 optional fingerprint, SH-118 tax reporting, SH-130 Healthcare admin access. Provider/account/legal/retention/BAA/actual capability evidence is not fabricated. All132 architecture dispositions remain119 EVOLVABLE_COMPATIBLY/13 EXTERNALLY_GATED, zero UNSTABLE/frozen/runtime-qualified. P01–P19, R001–R090, 88 owner/Cluster architecture-plan files, 661 source/decision records, 563 raw bridge records/268 families and canonical identities remain preserved.

## Git and continuation

WA-R091 is the only new ruling. Exact final local HEAD/tree, clean-tree state, fresh remote comparison and independently cloned SHA-256 full-history bundle are pinned in the downloadable Checkpoint006 manifest. Original dedicated worktree/branch remains at005. Publication is separate:GitHub was independently read at f4e089902dcbcb303dc52976c4118f8903c135e5;new local commits are not reported published. No main merge, force push, deployment, DB migration/provisioning or broad product implementation occurred.

Next safe work is controlled dependency security remediation review and actual isolated database provenance. Context, source-only reconciliation and test design may continue while D remains;actual DB replay/runtime/RLS/provider qualification cannot be invented. No product-owner business decision is pending at this milestone.
