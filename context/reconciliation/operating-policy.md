# Development Readiness operating policy

Authority: product-owner instruction, 2026-10-12. Applies to the remainder of this sweep and supersedes earlier stop-on-product-question guidance. P01–P19 and other frozen decisions remain binding.

## Autonomous judgment

Use AI_RESOLVED_WITH_PRODUCT_JUDGMENT when product intent, architectural integrity, a conventional/simple MVP default, reversibility, configurable/versioned policy, or a strong recommendation supports a reasonable choice without materially changing the core business model. Two legitimate options alone do not require escalation. Record evidence, canonical owner, reasoning, meaningful rejected alternatives, downstream consequences, reversibility/configurability and affected artifacts. Apply the ruling to architecture, plans and consumers; validate and continue.

## Consequential choices only

Reserve PRODUCT_OWNER_CHOICE for material changes to core monetization/pricing, payer/payee, fee/commission, major refund/liability, marketplace/business structure, existence of major capability, materially different rights, significant privacy exposure, destructive/irreversible data behavior, major trust/safety posture, or substantial strategic/cost launch scope. First inspect existing rulings, authoritative owner, both bridge sides, comparable decisions, duplicates and versioned/configurable alternatives. Existing rulings may already determine the answer. Technical architecture is not a product escalation.

Queue genuinely consequential choices and continue independent work. Return one decision packet only at ten pending choices, when every remaining unresolved record depends on them, when the current gate cannot materially progress without them, or when the sweep is otherwise complete.

## External requirements

Legal/statutory/jurisdiction requirements, provider capabilities, vendor contracts and live database provenance are EXTERNAL_REQUIREMENT gates. Resolve surrounding architecture and unrelated work. Missing external evidence stops the sweep only when it prevents meaningful safe progress across all remaining work. Never invent approval or provider capability.

## Family workflow and evidence

Normalize records by underlying owner/contract decision before adjudication. Propagate one ruling to every legitimately settled duplicate, alias and consumer consequence; grouping alone is not closure. Track raw pending, unresolved canonical families, duplicates collapsed, existing-ruling closures, AI-resolved families, product-judgment families, external gates and genuinely unresolved owner choices. Canonical integration remains handoff-adjudication.json/md and platform-architecture-rulings.md.

Adjudicate → canonical ruling → owner architecture → affected plans/consumers → validate → continue. Commit logical batches. Continue Gates 2–10 without ordinary gate approval. Preserve source evidence, authority boundaries and one final cross-Cluster reconciliation before root synthesis.

## Exhaustive stopping rule

Return control only for (A) the batched consequential choices above, (B) an action literally requiring authorization, (C) an external blocker preventing meaningful remaining work, or (D) final readiness results. Status reports, ordinary questions and completed gates are not stop conditions. Existing restrictions on deployment, remote publication, destructive changes and feature implementation remain in effect.
