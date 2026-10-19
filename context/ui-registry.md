# UI component and screen registry

A registry is a reuse/ownership map, not a completion claim. Current application routing remains unqualified under WA-R090. The structured source is ui-registry.json. Only actual paths below exist; future paths are plans, not broken links or completed libraries.

| ID | Component | State | Actual / planned location | Boundary |
|---|---|---|---|---|
| UI-001 | EnvironmentBanner | EXISTS_UNQUALIFIED | components/EnvironmentBanner.tsx | Nonproduction environment context only; no secret/config value dump. Actual production hiding/build needs smoke proof. |
| UI-002 | Root shell and diagnostic routes | EXISTS_ROUTER_DEBT | pages/layout.tsx | Existing route bytes preserved in P0-B normalization; current folder convention conflicts with App Router intent. |
| UI-003 | Button / Link / Focus | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Semantic action/navigation, pending/disabled reason and visible focus; never authority. |
| UI-004 | Input / Select / FormField | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Visible labels and accessible errors; owner validation remains server-side. |
| UI-005 | Dialog / AlertDialog | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Keyboard focus containment/restoration and explicit consequences; no policy bypass. |
| UI-006 | Status / Result / AsyncProgress | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Distinct denied/stale/partial/unknown/accepted/completed states; no generic success coercion. |
| UI-007 | Table / List / Pagination | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Accessible header/empty/partial/cursor states; no total-count privacy leak. |
| UI-008 | ProtectedMediaView | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Exact owner permission/proof/expiry, protected credential handling and current generation. |
| UI-009 | ActorContextSelector | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Show selected permitted actor branch; switching context is not granting permission. |
| UI-010 | ConsentPresentation | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Exact immutable content/version and explicit affirmative action; presentation is not proof. |
| UI-011 | SourceActionForm | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Stable semantic intent, conflict/retry/reconcile, safe retained input; no double side effect. |
| UI-012 | AppShell / Navigation / Breadcrumbs | SPECIFIED_NOT_IMPLEMENTED | planned: components/ui/ | Role/current owner context drives available links; hidden navigation is not server access control. |

| Screen pattern | Workflow scope | State |
|---|---|---|
| Account, security and actor setup | WF-01, WF-02 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Professional readiness and Offering management | WF-03, WF-04 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Gig response and commercial transaction | WF-05, WF-06 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Schedule, purchased access and protected delivery | WF-07, WF-08 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Hiring, application, resume and Interview views | WF-09 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Conversations, notifications and discovery | WF-10 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Privacy, compliance and operator evidence | WF-11, WF-12 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |
| Reward and prize participation/fulfillment | WF-13 | PATTERN_SCOPE_ONLY_NOT_IMPLEMENTED |

React/Tailwind are declared; no installed dependency tree or completed build is claimed. shadcn/ui, Radix and Zod are overview intent, absent from package.json. Do not invent components/providers or add packages merely because the overview names them. Coordinate a justified dependency and reusable primitive once, then owner feature UI consumes it. Substantial UI requires actual pinned toolchain/router proof and appropriate owner/contract/security qualification.
