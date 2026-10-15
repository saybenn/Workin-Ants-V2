# Context-specific query contracts — WA-R074

Classification: AI_RESOLVED_WITH_TRADEOFF. Owners: Customer and Gig. Evidence: Customer architecture §11/14 permits authorized contextual display but disables a public profile; Professional's Gig-response dependency lacks an explicit query despite Gig retaining context truth. These definitions name those existing boundaries without adding discovery exposure or changing participation policy.

## Customer contextual display

Customer owns `getCustomerContextDisplay.v1`. Input: authenticated actor/service scope, typed source context ID and expected context revision, requested CustomerProfile ID, purpose `participant_display`. The source owner supplies current relationship/disclosure proof through its public facts port; Customer verifies the User-to-Customer relationship without disclosing User ID. Client IDs alone are not proof.

Return `available | denied | unavailable | conflict` with opaque CustomerProfile reference, current display revision, source-context revision, contextual display name and optional source-approved safe Media avatar rendition reference. Display fields must already be permitted for that context; unknown field policy denies rather than using a universal public name/avatar. No account ID, contact, exact/coarse location, lifecycle status, Track data, private evidence or raw asset/provider URL. Media enforces rendition safety/access. Missing profile or invalid relationship has a non-enumerating outward denial; a dependency failure is not permission to query private profile tables.

Messaging/Notification may request this query only for their authorized source relationship. Notification may omit display labels and render the already-approved generic template rather than widen disclosure. No public endpoint or Search projection follows. Revalidate current context rights and display policy before use; revoked relationship or changed source version invalidates cached display. Cache lifetime cannot outlive authorization evidence. Immutable past message attribution is retained under its owning history/privacy policy, not rewritten by this display query.

Alternative rejected: reusing self/support getCustomerProfile leaks a broader field surface; introducing public Customer search conflicts with the approved no-public-profile policy. The narrow DTO is versionable and reversible before consumers are frozen. It never authorizes public indexing.

## Gig participation requirements

Gig owns `getGigParticipationRequirements.v1`. Input: trusted actor/service scope, Gig ID, purpose/action `respond_to_gig`, optional expected Gig revision. Output is a versioned fact snapshot: Gig ID/revision/current participation state, owning source reference for internal relationship checks, accepted taxonomy IDs/versions, explicit participation requirement IDs/versions, regulated-context declaration and current response-window/capacity constraint facts. No competing response, private price, customer contact or restricted evidence is exposed.

Professional's action-specific eligibility decision consumes this owner snapshot together with its own current profile/Track/Healthcare/Trust facts. Gig does not call Professional to construct this query, preventing a recursive eligibility dependency. Gig response acceptance rechecks current Gig revision and its own capacity/state plus current Professional eligibility decision; a cached requirements snapshot alone cannot admit a response. Missing requirements required by policy, unsupported action, stale expected revision or unqueryable source returns denied/conflict/unavailable as appropriate; no empty permissive default.

Alternative rejected: Professional reading Gig repositories or reconstructing requirements from a public card breaks owner truth. Reusing a general Gig view without a closed field schema risks disclosure and underspecified rules. This is a versioned internal query, not a new requirement or paid benefit. Both query families require explicit allowed/denied, stale-source, dependency-unavailable and field-minimization contract fixtures before consumer freeze.
