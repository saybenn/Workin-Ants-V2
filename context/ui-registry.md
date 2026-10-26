# UI component and screen registry

Current slice:P0-B clean foundation. Update this file and ui-registry.json after every implementation slice with actual paths, API/classes/token usage, tests and limits; record no-component-change explicitly when applicable. Product primitives/screens remain unimplemented. The structured source retains their workflow and ownership boundaries.

| ID | Component/role | Actual state | Actual/planned path | Boundary |
|---|---|---|---|---|
| UI-001 | EnvironmentBanner | ARCHIVED_NOT_ACTIVE | legacy/checkpoint-005/application/components/EnvironmentBanner.tsx | Exact legacy artifact retained for comparison; not imported or reused by the clean app. |
| UI-002 | Root shell and diagnostic routes | FOUNDATION_FRAMEWORK_HTTP_QUALIFIED | app/layout.tsx | Minimal root html/body shell, static page and process-only diagnostics;41 real local dev/production HTTP checks pass. Product/UI accessibility remain unqualified;the subsequent Directive007 dependency audit is recorded below. |
| UI-003 | Button / Link / Focus | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Semantic action/navigation, pending/disabled reason and visible focus; never authority. |
| UI-004 | Input / Select / FormField | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Visible labels and accessible errors; owner validation remains server-side. |
| UI-005 | Dialog / AlertDialog | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Keyboard focus containment/restoration and explicit consequences; no policy bypass. |
| UI-006 | Status / Result / AsyncProgress | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Distinct denied/stale/partial/unknown/accepted/completed states; no generic success coercion. |
| UI-007 | Table / List / Pagination | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Accessible header/empty/partial/cursor states; no total-count privacy leak. |
| UI-008 | ProtectedMediaView | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Exact owner permission/proof/expiry, protected credential handling and current generation. |
| UI-009 | ActorContextSelector | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Show selected permitted actor branch; switching context is not granting permission. |
| UI-010 | ConsentPresentation | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Exact immutable content/version and explicit affirmative action; presentation is not proof. |
| UI-011 | SourceActionForm | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Stable semantic intent, conflict/retry/reconcile, safe retained input; no double side effect. |
| UI-012 | AppShell / Navigation / Breadcrumbs | SPECIFIED_NOT_IMPLEMENTED | planned:components/ui/ | Role/current owner context drives available links; hidden navigation is not server access control. |

The actual shell API is RootLayout({children:ReactNode}), HomePage() and NotFoundPage(); classes foundation-frame/foundation-label consume semantic CSS values from ui-tokens.json. No new reusable product primitive or business screen was implemented. The old EnvironmentBanner is an inactive archived file, not an active reusable component.

All eight screen-pattern rows in ui-registry.json remain PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED. React/Tailwind are actually installed at the lock versions and the shell passes local framework/HTTP checks. shadcn/Radix/Zod direct application dependencies are absent; a transitive zod package does not qualify an application parser/UI library. The original clean-shell dependency audit was open;the current Directive007 requalification passed. Actual product components still need owner/contract/security/currentness and rendered keyboard/focus/screen-reader/contrast/reflow/visual qualification. No substantial UI or parallel development is authorized.

Recovery-hygiene follow-up: no component/API/classes/token change. Only Python bytecode ignore rules and restore evidence changed; actual/planned component states remain as above.

## Directive007 dependency requalification —26 October2026

No component,API,class or token changed. The same bounded shell passes lint/typecheck/build and47 real HTTP/security/restart/instruction-preservation cases on Next16.4.3. Full/production audits have zero known vulnerabilities. UI-003–012 and all product screen patterns remain unimplemented;no rendered product/accessibility certification or new UI direction was adopted.
