# UI and interaction rules

Read product overview, owner architecture, connected workflow and exact contract before designing a screen. UI presents owner facts and requests owner commands; it does not assign source status, grant eligibility, derive premium/blocked flags or interpret provider payloads. Customer, Professional, Candidate and Organization hiring contexts remain explicit; a User may act in several branches, and switching context never grants that branch's permission.

## Routing and rendering boundary

The framework foundation is a fresh Next App Router app/ under WA-R090/R091 and Directive006-A. The old pages/ application remains inactive under legacy/checkpoint-005/ with exact inventory/hashes; do not import it as a second architecture. Real framework/HTTP checks qualify the bounded shell separately from product UI. Development-only diagnostic access is denied in production by server execution mode,not public flags. Read installed pinned Next guidance and actual Phase0 evidence before changing this boundary.

Prefer server-owned data/permission boundaries and minimal client interaction islands. Thin route/handler validates input and delegates to owner application ports. Any framework caching, streaming, server action or client/server API must follow the actual installed version's guide and tests. Never put credentials, service-role database clients, provider SDKs or private repositories in browser imports. Client state is display/interaction state, not authority; protected refetch repeats current source checks.

## Required user-visible states

| State | Meaning and interaction |
|---|---|
| Initial/loading | Label the pending scope, preserve stable layout and accessible progress; no fabricated zero/empty state |
| Empty | Owner confirms empty permitted result; distinguish from incomplete/unavailable data |
| Partial/stale | Show bounded as-of/retry status and source links where allowed; do not present stale information as permission |
| Denied/revoked | Safe nonenumerating explanation and permitted recovery path; never expose private target existence/details |
| Needs verification/consent/setup | Link the actual owner workflow; do not precheck acceptance or infer completion from redirect |
| Submitted/pending | Command accepted or external effect unknown; show pending/reconciliation, not success or a new side-effecting attempt |
| Completed | Actual required source/effect receipt, with distinct retained/omitted disposition where relevant |
| Failed/unavailable | Stable safe explanation and bounded retry; preserve original semantic effect identity for unknown outcome |

Map owner result variants deliberately. Job Compliance warning/review, Healthcare redaction/block, Privacy retained/partial and provider unknown are distinct. A universal green success banner cannot collapse them. Notification sent is not legal service or business success; a signed URL/playback is not actual delivered bytes; Booking allegation is not Order completion.

## Interaction and safety

Use semantic headings, links and buttons; every input has a visible label, accessible description/error and correct keyboard focus. Dialog focus is trapped/restored, destructive actions have explicit target/consequence and server authorization, and recovery actions preserve keyboard access. Do not use color alone for validation/status. Reflow at 320px and zoom; tables need accessible headers and small-screen reading patterns, not hidden critical data. Respect reduced motion and do not autoplay nonessential content.

Forms retain safe input after validation failure, show field and summary errors, and protect against accidental duplicate submission while allowing reconciliation of uncertain results. A disabled button must expose its permitted reason; it never substitutes for server guards. No preselected legal consent, disguised fee/renewal, inferred opt-in discovery or client-only age gate. Consequential business behavior remains approved owner policy, not a design default.

Protected media/resume/location/Agreement/tax/healthcare/export views require current owner permission and mandatory durable proof before delivery. Keep signed credentials out of URLs/history/logs/analytics where the qualified delivery mechanism permits; do not persist them in shared browser state. Revoke removed audiences and refetch current context after stale generation/authority change. Search snippets/totals and Notification routes require the same current authorized field scope; never leak exact coordinates, resumes, private message bodies, raw reports or provider tokens through preview/error/loading content.

## Component and screen completion

Use ui-tokens.md and ui-registry.md before creating a shared component. Shared presentation primitives do not own domain policy. Place feature screens/components with their canonical owner; cross-owner facades compose actual public contracts. A new dependency requires a documented package/version/license/security/accessibility justification and integration-owner review; the product's shadcn/Radix/Zod intent is not proof they are installed.

Each substantial UI feature needs actual framework build checks, owner contract/schema fixtures, keyboard/focus/screen-reader/contrast/reflow/reduced-motion testing, currentness/denial/unknown/retry/privacy cases and visual review in supported layouts. A registry row marked specified or a screenshot is not completed behavior. Do not implement substantial UI until the routing/toolchain and required source contracts/adapters are qualified.


After every implementation slice update ui-registry.md/json with actual reusable component paths/API/classes/token usage and qualification limits; planned rows stay clearly unimplemented. Preserve source/contract/authority and accessibility obligations even when a foundation smoke check passes.
