# R068/R069 source verification — 2026-10-15

Baseline: `d672ea2f609d64762685e847f1e3d2da2a046421`. Priority 0 independently verified by Git fetch and GitHub comparison; see publication-verification-2026-10-15.json.

All 34 owner action/fact/assurance rows match R068. All 26 coordinated architecture/plan appendices remain present exactly once. The older integration status is now APPLIED_AND_SOURCE_VERIFIED. Original pending-appendix text remains immutable provenance; the applied files include the corrections below.

R069 producer payloads and recipient effects were compared against the named owner appendices. Corrected five missing consumer registrations across Search, Messaging, Media, Video and Candidate. Notification's Messaging/Privacy/Ops routes are separate semantic intents; Role reads current Identity assignments. Gig/Order readiness and Order checkout checks are current-owner query obligations, not event-derived authorization. Candidate stage handling remains optional and disabled until qualified. Named Location consumers act only for registered disclosure scopes.

`authority-event-review.json` records the exact owner/plan paths, reviewed producer/subscriber sets and routes that are not subscriptions. `scripts/check-authority-events.py` checks those registrations, all R068 row fields, source-revision/replay/privacy obligations, and appendix uniqueness. It fails if the canonical event registry changes without review.

The incorporated producer/consumer protocol binds immutable event identity, source revisions, atomic outbox intent, subscriber deduplication, effect-specific idempotency, correction lineage, tombstones, gap recovery and minimized recipient payloads. Events never become current authority or substitute for Privacy/Moderation effect commands. R031, approved Privacy verification-generation policy and the absence of generic Professional moderation permissions are preserved.

This is source-level contract consistency evidence. Runtime replay, DTO compatibility, RLS parity, actual provider behavior, template qualification, and legal/program values remain unverified activation gates. Broader Cluster/bridge convergence and stale historical wording remain subject to Gate 4/5.

## Subsequent source review — WA-R080

Taxonomy bridge review adds four explicitly scoped recipients of the existing taxonomy.policy_changed.v1 event: Candidate and Gig contextual assignment owners, plus Job Compliance and Location only for registered requirement mappings. The canonical recipient row, producer/consumer appendices and reviewed machine snapshot were updated together. The namespace remains 46 events; no interface is frozen. These are distinct from the five initial propagation omissions described above.

## Gate 4 continuation — WA-R082

Media now produces `media.availability_changed.v1` for Customer avatar and Candidate attachment/parse invalidation. Current Media queries and Candidate source projection checks remain mandatory; no direct Media-to-Search stream is added. Registry, producer, two subscribers and review snapshot changed together: **47 events / 34 owner pairs / 26 preserved coordinated appendices**. This closes BF-036/179 architecture, not runtime event delivery.

## Gate 5 opening correction — WA-R084

Payment's existing financial-source-effect consumer was absent from the R069 Order outcome row. Added Payment to that row and synchronized Order/Payment appendices and plans. The existing event remains non-authorizing and requires source-bound settlement queries; **47 events remain**. This specific finding demonstrates why Checkpoint 001 registration consistency was not final platform semantic certification.
