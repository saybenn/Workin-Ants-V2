# UI tokens

Status: reversible foundation specification under WA-R089, not an applied brand redesign or completed UI. Preserved skeleton evidence is `legacy/checkpoint-005/application/pages/globals.css` (white/near-black, Arial and system dark preference) and EnvironmentBanner. The clean foundation app/globals.css consumes these token values; its shell checks do not certify product UI or accessibility.

The machine source is ui-tokens.json. Semantic tokens cover light/dark canvas/surface/text/muted text/border/action/on-action/focus and success/warning/danger surfaces. Neutral baseline is existing evidence; the restrained blue action/focus accent and 4px spacing rhythm are reversible defaults. Do not turn a status color into a domain meaning or use plan colors to infer entitlements.

Typography uses current system sans/monospace, 16px body with 1.5 line height and 14px readable labels. Spacing is 4/8/12/16/24/32/48/64px; control/card/dialog radii 4/8/12px. Use a 1200px maximum content frame and about 70ch reading width, with small screens reflowing to one column. Focus is visible with a 2px outline/offset; motion respects reduced-motion preference. These values may evolve compatibly without changing a source action, permission or public/private disclosure.

The offline token test checks specified text/background pairs at 4.5:1. That is evidence about these color values, not a WCAG certification of unimplemented components. Components also need keyboard, screen-reader, focus, touch/zoom/reflow, reduced-motion and non-color status tests. Form/interactive state contrasts must be checked on actual rendering before release; disabled status never hides the only explanation.

Use one semantic token source rather than hardcoded per-feature palettes. The archived globals remain comparison evidence; the clean shell applies the semantic values. Rendered product components still require actual visual/accessibility testing. No new logo, font service, third-party UI package or theme-persistence preference is assumed installed/approved by this specification.
