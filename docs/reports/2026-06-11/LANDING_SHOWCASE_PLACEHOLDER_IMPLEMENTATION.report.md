# Landing Showcase Placeholder Implementation Report

Статус: implementation report.
Дата: 2026-06-11.
Область: showcase publish mode, MVP entry, placeholder/scaffold assets, landing contracts, validation evidence.

## 1. Summary

Выполнен связанный набор изменений для подготовки публичного showcase-лендинга «ТехКухня» без блокировки на production asset freeze.

Ключевой результат:

```text
showcase publish with placeholder assets: accepted for current stage
MVP entry: icon-only service action through env-configured URL
production asset freeze: deferred
public launch: still blocked by owner gates
```

Лендинг теперь может быть собран и проверен как controlled Target Product storefront. Он не объявляет полноценный SaaS launch, не открывает публичную регистрацию и не притворяется, что финальные production assets уже утверждены.

## 2. Related Artifacts

- [Landing Owner Gates](../../лэндинг/LANDING_OWNER_GATES_v0.1.md)
- [Landing Showcase Mode Strategy](../../лэндинг/LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md)
- [Landing Implementation Progress](../../лэндинг/LANDING_IMPLEMENTATION_PROGRESS.md)
- [Landing Implementation Audit](../../лэндинг/LANDING_IMPLEMENTATION_AUDIT_v0.1.md)
- [Visual Asset Layering Contract](../../лэндинг/LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md)
- [Production Asset Brief](../../лэндинг/LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md)
- [Asset & Icon Registry Contract](../../лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
- [Landing README](../../лэндинг/README.md)

Code/config entry points:

- [landingMode.config.ts](../../../frontend/landing/config/landingMode.config.ts)
- [actionVisibilityResolver.ts](../../../frontend/landing/lib/actionVisibilityResolver.ts)
- [cta.registry.ts](../../../frontend/landing/registries/cta.registry.ts)
- [asset.registry.ts](../../../frontend/landing/registries/asset.registry.ts)
- [HeaderSection.tsx](../../../frontend/landing/sections/HeaderSection.tsx)
- [Button.tsx](../../../frontend/landing/components/primitives/Button.tsx)
- [frontend/.env.example](../../../frontend/.env.example)

## 3. Owner Decisions Applied

Applied decisions:

- `landingMode = showcase`;
- showcase publish is allowed as Target Product storefront;
- showcase is not a full SaaS launch;
- MVP entry is allowed as a small icon-only service action;
- MVP entry URL must come from config/env;
- commercial actions remain hidden/disabled;
- current showcase may use placeholder/scaffold assets;
- production assets are not generated or approved in this stage.

Not changed:

- public launch remains blocked;
- `signup.freeStart` does not become active;
- `pricing.view` does not become active;
- `docx.download` does not become active available-now;
- planned production visual keys are not added to code registry without files.

## 4. Showcase Mode Implementation

`landingModeConfig` remains the single mode/config entrypoint for landing runtime decisions.

Implemented behavior:

- default mode is `showcase`;
- `ownerGates.landingMode = true`;
- `ownerGates.publicLaunch = false`;
- `ownerGates.mvpEntry = true`;
- commercial owner gates remain closed;
- `functionAvailability.mvpEntry` depends on a configured URL.

The MVP entry URL is read from:

```text
NEXT_PUBLIC_MVP_ENTRY_URL
```

The temporary deployment value is documented only in [frontend/.env.example](../../../frontend/.env.example), not hardcoded in sections/components/registries.

## 5. MVP Entry Implementation

MVP entry is implemented as a service action, not as a marketing CTA.

Behavior:

| Condition | `nav.login` result |
| --- | --- |
| `NEXT_PUBLIC_MVP_ENTRY_URL` is configured and valid | visible/enabled link |
| `NEXT_PUBLIC_MVP_ENTRY_URL` is missing or invalid | hidden/owner_gated |

UI contract:

- visible label: none;
- accessibility label: `Вход в MVP`;
- icon: neutral login icon;
- desktop placement: header right;
- mobile placement: mobile menu action;
- analytics event: `landing_nav_login_click`;
- auth is handled by the MVP itself.

Important boundary:

`HeaderSection` receives a resolved action. It does not decide locally whether MVP entry should be visible. The decision remains in config/resolver.

## 6. Action Resolver Policy

The resolver remains the boundary between raw registry actions and render-ready action state.

Current policy:

- public safe actions can remain enabled in `showcase`;
- MVP entry can be exposed in `showcase` only when owner-approved and URL-configured;
- commercial actions remain gated outside launch;
- roadmap actions remain disabled/hidden and cannot become available-now;
- forbidden/unsupported maturity remains blocked by validation.

Current key actions:

| Action | Current result |
| --- | --- |
| `demo.request` | enabled safe scroll action |
| `sample.project.view` | enabled safe scroll action |
| `nav.login` | env-configured icon-only service entry |
| `signup.freeStart` | disabled, owner-gated |
| `pricing.view` | hidden, owner-gated |
| `docx.download` | disabled roadmap action |

## 7. Placeholder Asset Policy

The current showcase uses placeholder/scaffold assets intentionally.

Policy:

- placeholder is a contract object, not a random picture;
- placeholder must be registered in `AssetRegistry`;
- placeholder must have asset metadata;
- placeholder must have explicit `rightsStatus: "local-scaffold"`;
- placeholder must not receive fake provenance/rights approval;
- placeholder must be replaceable later through registry/config;
- sections must not be rewritten for placeholder-specific hacks.

This policy is documented in:

- [Production Asset Brief](../../лэндинг/LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md)
- [Visual Asset Layering Contract](../../лэндинг/LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md)
- [Asset & Icon Registry Contract](../../лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
- [Landing Owner Gates](../../лэндинг/LANDING_OWNER_GATES_v0.1.md)
- [Landing README](../../лэндинг/README.md)
- [Landing Implementation Progress](../../лэндинг/LANDING_IMPLEMENTATION_PROGRESS.md)
- [Landing Implementation Audit](../../лэндинг/LANDING_IMPLEMENTATION_AUDIT_v0.1.md)

## 8. Current Asset Registry State

Current code registry contains 6 asset records.

| Asset key | Kind | Background | Layer role | Z-slot | Safe area | Rights status |
| --- | --- | --- | --- | --- | --- | --- |
| `brand.logoMark` | `brand` | `solid` | `brandMark` | `none` | `none` | `local-scaffold` |
| `hero.productUi` | `productUi` | `embedded` | `heroProductUi` | `base` | `preserveProductUiCore` | `local-scaffold` |
| `hero.dish` | `contentImage` | `embedded` | `heroForegroundObject` | `foreground` | `preserveCardContent` | `local-scaffold` |
| `documents.techCardPreview` | `documentPreview` | `embedded` | `documentContent` | `none` | `preserveCardContent` | `local-scaffold` |
| `documents.costCardPreview` | `documentPreview` | `embedded` | `documentContent` | `none` | `preserveCardContent` | `local-scaffold` |
| `cta.kitchenBoard` | `backdrop` | `embedded` | `finalCtaBrandBand` | `backdrop` | `preserveTextAndCta` | `local-scaffold` |

Important asset decisions:

- `hero.dish` remains `contentImage` with `embedded` background;
- `hero.dish` was not reclassified as `cutout`;
- current final CTA background remains `cta.kitchenBoard`;
- no `hero.chef` record was added;
- no hero backdrop production key was added;
- no final CTA edge decor production key was added.

## 9. Planned Production Assets

These remain future contract items, not current code registry entries:

| Planned asset | Status | Next required step |
| --- | --- | --- |
| `hero.chef` | planned | create/review candidate, rights review, approval |
| `hero.decor.backgroundKitchen` | planned | create/review backdrop, approve, add file and registry entry |
| `hero.dishCutout` or replacement `hero.dish` | planned | only after real transparent cutout exists |
| `finalCta.decor.*` | planned | create transparent edge decor assets |
| production replacement for `cta.kitchenBoard` | planned | approve final CTA band/backdrop |
| `documents.saladCaesar` or `documents.dishSample` | optional | add only with real file and registry metadata |

Production Asset Brief remains active as the future contract for those assets.

## 10. Documentation Changes

Updated docs:

| File | Change |
| --- | --- |
| `LANDING_OWNER_GATES_v0.1.md` | Recorded showcase/MVP entry decisions and placeholder asset exception for showcase. |
| `LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md` | Clarified icon-only MVP entry, env URL and gated commercial actions. |
| `LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md` | Added current showcase placeholder policy and current placeholder table. |
| `LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md` | Expanded current scaffold state and placeholder publishing rule. |
| `LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md` | Added placeholder asset policy and required current scaffold set. |
| `README.md` | Added consistency rule for placeholder/scaffold assets. |
| `LANDING_IMPLEMENTATION_PROGRESS.md` | Added Phase 14 and Phase 15 implementation records. |
| `LANDING_IMPLEMENTATION_AUDIT_v0.1.md` | Added Phase 14 and Phase 15 audit addenda with verification evidence. |

## 11. Code Changes

Showcase/MVP entry code changes:

| File | Change |
| --- | --- |
| `landingMode.config.ts` | Added MVP entry config, env URL read, owner gates, sticky comment. |
| `actionVisibilityResolver.ts` | Enabled MVP entry only when owner-approved and URL-configured. |
| `cta.registry.ts` | Updated `nav.login` as `mvp_entry`, `mvp_scope`, owner-approved service action. |
| `icon.registry.ts` | Added neutral login icon key. |
| `Button.tsx` | Added `iconOnly` and `ariaLabel` support while keeping shared action contract. |
| `HeaderSection.tsx` | Renders MVP entry as icon-only through `Button`; no local visibility policy. |
| `globals.css` | Added icon-only button sizing and mobile menu action placement. |
| `.env.example` | Added temporary `NEXT_PUBLIC_MVP_ENTRY_URL` example. |

Placeholder asset stage:

- no production asset files added;
- no new production asset keys added;
- no section rewrites for assets;
- existing registry metadata retained.

## 12. Validation Evidence

Commands run from `frontend/` with:

```text
NEXT_PUBLIC_MVP_ENTRY_URL=https://coocking-cart.speechbattle.com/
```

Results:

| Check | Result |
| --- | --- |
| `npm run validate` | pass |
| `npm run lint` | pass |
| `npm run build` | pass |
| `npm audit --omit=dev` | pass, `0 vulnerabilities` |

Expected validation warnings:

- testimonials section disabled;
- pricing claim requires owner decision before public launch;
- onboarding claim requires owner decision before public launch;
- landing mode is `showcase`.

Additional behavior check:

- without `NEXT_PUBLIC_MVP_ENTRY_URL`, `npm run validate` still passes and `nav.login` remains owner-gated.

## 13. Static Check Evidence

Static checks passed:

| Check | Result |
| --- | --- |
| `local-scaffold`, `rightsStatus`, `assetKind`, `backgroundMode`, `layerRole`, `zSlot`, `safeArea` search | pass; metadata present in registry/docs |
| no direct colors in sections/components | pass |
| no direct image paths in sections | pass |
| no inline style/magic layout in sections | pass |
| no section-local analytics strings | pass |
| planned production keys absent from code registry/content/sections | pass |
| TS registry export check | pass; 6 assets, all `local-scaffold` |
| Markdown links for changed docs | pass |
| UTF-8 BOM for changed Russian docs | pass |

## 14. Non-goals Confirmed

Not done intentionally:

- no production image generation;
- no production asset approval;
- no fake provenance metadata;
- no `hero.chef` code registry entry;
- no hero backdrop code registry entry;
- no final CTA edge decor code registry entries;
- no public launch declaration;
- no analytics dispatch implementation;
- no final legal/copy freeze.

## 15. Risks And Follow-ups

Remaining risks:

- placeholder visuals are acceptable for showcase, but not for production asset freeze;
- analytics is still scaffold-level unless dispatch is implemented;
- automated accessibility audit is not yet part of this slice;
- final copy/legal gates remain open for public launch;
- production asset replacement still needs visual smoke across desktop/mobile.

Recommended next steps:

1. Configure `NEXT_PUBLIC_MVP_ENTRY_URL` in deploy env for showcase.
2. Keep production asset generation as a separate reviewed workflow.
3. Add production asset provenance and approval only after real candidates exist.
4. Run visual smoke after replacing any placeholder assets.
5. Add analytics dispatch if click tracking is required for showcase metrics.
6. Keep public launch blocked until commercial/legal/asset gates are closed.

## 16. Readiness Verdict

```text
showcase publish with placeholder assets: yes
showcase publish requirement: deploy env must provide NEXT_PUBLIC_MVP_ENTRY_URL if MVP entry should be visible
production asset freeze: no, deferred
public launch: no, still blocked by owner gates
```

The implementation is ready for controlled showcase publishing with clearly marked placeholder/scaffold assets. It is not a full public SaaS launch and not a production asset freeze.
