# Landing Implementation Audit v0.1

Статус: независимый аудит фактической реализации управляемого публичного лендинга «ТехКухня».
Дата: 2026-06-11.
Область: `frontend/`, landing docs, build/lint/validate, registries, content, schemas, sections, responsive evidence, claim maturity, owner gates.

Связанные документы:

- [Landing Implementation Plan](LANDING_IMPLEMENTATION_PLAN_v0.1.md)
- [Landing Implementation Progress](LANDING_IMPLEMENTATION_PROGRESS.md)
- [Landing Implementation Handoff](LANDING_IMPLEMENTATION_HANDOFF_v0.1.md)
- [Landing Owner Gates](LANDING_OWNER_GATES_v0.1.md)
- [Landing PRD](LANDING_PRD_v0.1.md)
- [Visual Tech Contract](LANDING_VISUAL_TECH_CONTRACT_v0.1.md)
- [Production Asset Brief](LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md)
- [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)

## 1. Executive Summary

Verdict: `accepted_with_minor_findings`.

```text
engineering scaffold ready: yes
public launch ready: no
independent code audit completed: yes
readiness verdict: engineering_scaffold_verified_with_minor_findings
public launch verdict: public_launch_blocked_by_owner_gates
```

Фактическая реализация в целом соответствует заявленной архитектуре: отдельный Next.js frontend в `frontend/`, content modules, Zod schemas, registries, primitives, isolated sections, claim maturity validation и owner gates присутствуют и проверяются. Текущий Python/static MVP runtime в `app/` не изменён.

Scaffold можно считать проверенным для следующей engineering-фазы. Public launch остаётся заблокирован owner gates и несколькими follow-up задачами: analytics dispatch, automated accessibility audit, production asset approval, final copy/CTA/legal freeze.

## 2. Scope

Проверялось:

- документы: `LANDING_IMPLEMENTATION_HANDOFF_v0.1.md`, `LANDING_IMPLEMENTATION_PLAN_v0.1.md`, `LANDING_IMPLEMENTATION_PROGRESS.md`, `LANDING_OWNER_GATES_v0.1.md`, landing README;
- frontend code: `frontend/app`, `frontend/landing`, `frontend/public/landing/assets`;
- package/config: `package.json`, `package-lock.json`, `tsconfig.json`, `next.config.ts`, `eslint.config.mjs`;
- content modules, schemas, registries, sections, primitives, tokens;
- build/lint/validate/audit commands;
- responsive screenshots in `.next-logs`;
- claim maturity and owner gates;
- отсутствие изменений в текущем `app/` runtime.

Не проверялось:

- production deployment;
- real analytics delivery to an external provider;
- final legal approval;
- automated axe report;
- owner decisions по CTA/pricing/export/legal/testimonials.

## 3. Evidence

| Check | Command | Result | Notes |
| --- | --- | --- | --- |
| Git status | `git status --short` | pass | `frontend/` and `docs/лэндинг/` are untracked additions; unrelated dirty files already exist elsewhere. |
| Tracked app diff | `git diff --name-only -- app app/templates app/static app/main.py` | pass | No tracked diff under `app/`; Python/static MVP runtime not changed. |
| Stack files | `rg --files -g 'package.json' -g 'vite.config.*' -g 'next.config.*' -g 'tsconfig.json' -g 'package-lock.json'` | pass | Found only `frontend/package.json`, `frontend/package-lock.json`, `frontend/next.config.ts`, `frontend/tsconfig.json`; no Vite stack. |
| Node/npm | `node --version; npm --version` | pass | Node `v22.19.0`, npm `11.6.2`. |
| Validation | `npm run validate` | pass with warnings | Expected warnings: testimonials disabled; pricing/onboarding owner decisions. |
| Lint | `npm run lint` | pass | `eslint .` exits 0. |
| Build | `npm run build` | pass | Next.js `16.2.9`; route `/` prerendered static. |
| Production audit | `npm audit --omit=dev` | pass | `0 vulnerabilities`; `postcss` override exists. |
| Content files | `rg --files frontend/landing/content` | pass | 10 Russian JSON modules exist. |
| Schemas | `rg --files frontend/landing/schemas` | pass | Zod schemas exist for all modules plus common schemas. |
| No direct section colors | `rg -n "#[0-9a-fA-F]{3,8}|rgb\(|hsl\(" frontend/landing/sections frontend/landing/components` | pass | No matches in sections/components. |
| No direct section assets | `rg -n "/images/|\.png|\.webp|\.svg" frontend/landing/sections` | pass | No matches in sections. |
| No section-local analytics strings | `rg -n "landing_.*_click|gtag|dataLayer" frontend/landing/sections` | pass | No matches in sections. |
| Section layout literals | `rg -n "style=|top:|left:|z-index:|width: [0-9]|height: [0-9]|margin|padding|gap" frontend/landing/sections` | pass with expected matches | Only primitive variant props like `gap="lg"` found. |
| HTTP smoke | `Invoke-WebRequest http://localhost:3000` | pass | Status 200; hero content present. |
| Anchor smoke | internal anchor check over rendered HTML | pass | `audience`, `documents`, `final-cta`, `hero`, `standards`, `workflow` resolve. |
| Responsive screenshots | `Get-ChildItem frontend/.next-logs/final-*.png` | pass | Files exist for 360, 390, 768, 1024, 1280, 1440 px. |
| Markdown links | local docs link checker | pass | Audited docs links resolve. |
| Closed-world imports | `rg -n "\.\./" frontend/app frontend/landing frontend/next.config.ts` | pass | No parent-directory imports. |
| Runtime path hacks | `rg -n "process\.cwd\(|path\.resolve\(|secrets/.*\.json|\.\./\.\./config|process\.env" ...` | pass | No runtime path hacks/env assumptions found. |
| Build artifact | `Get-ChildItem frontend/.next/server/app` | pass | `.next/server/app/index.html`, `index.rsc`, `page.js` and manifests exist. |

## 4. Phase-by-phase Audit

| Phase | Claimed status | Evidence | Audit status | Notes |
| --- | --- | --- | --- | --- |
| Phase 0 - Repo audit | done | `LANDING_IMPLEMENTATION_PLAN_v0.1.md`; no Vite files; current `app/` unchanged | verified | Decision for standalone Next.js is justified by repo state. |
| Phase 1 - Next.js scaffold | done | `frontend/package.json`, `app/page.tsx`, `layout.tsx`, configs, README | verified | `npm run build` passes. |
| Phase 2 - Contracts/tokens/registries | done | `theme/*`, `registries/*`, `claimMaturity.ts` | partially_verified | Core contracts exist; no separate `theme.registry.ts`, but single theme is exported via theme index. |
| Phase 3 - Content/schemas | done | `content/ru/*.json`, `schemas/*.ts`, `safeParse` in `landingContent.ts` | verified | Runtime validation covers all modules. |
| Phase 4 - Primitives | done | `components/primitives/*` | verified | `Button`, `AssetImage`, `Icon` use registry-backed contracts. |
| Phase 5 - Sections | done | `sections/*.tsx`, `LandingPage.tsx` registry render | verified | Sections receive DTOs/actions and do not import physical assets. |
| Phase 6 - Visual implementation | done | `globals.css`, `HeroVisual`, local SVG scaffold assets | partially_verified | Visual exists; production assets remain scaffold and require approval. |
| Phase 7 - Responsive pass | done | `.next-logs/final-*.png`, HTTP/anchor smoke | verified | Screenshots exist for required widths. |
| Phase 8 - Validation/static checks | done | validate/lint/build/audit/static rg checks | verified | Commands pass. |
| Phase 9 - Owner gates | done | `LANDING_OWNER_GATES_v0.1.md`, disabled/hidden actions | verified | Public launch correctly blocked. |

## 5. Documentation Compliance Matrix

| Requirement | Source doc | Evidence in code/docs | Status | Notes |
| --- | --- | --- | --- | --- |
| Standalone Next.js app | Implementation Plan | `frontend/package.json`, `frontend/next.config.ts` | pass | No Vite stack found. |
| Do not change MVP runtime | Implementation Plan / Handoff | Empty tracked diff under `app/` | pass | Existing dirty files elsewhere are unrelated to landing scaffold. |
| Content modules | Handoff sections 12-13 | `frontend/landing/content/ru/*.json`; `landingContent.ts` | pass | Main product copy is in JSON. |
| Runtime schemas | Handoff sections 11, 13, 20 | Zod schemas and `safeParse` | pass | Max length rules present via `limitedTextSchema`. |
| Asset Registry | Asset contract / Handoff | `asset.registry.ts`; `AssetImage` | pass | Assets have key/src/alt/width/height/role/loading/visibility/rights. |
| Icon Registry | Asset/Icon contract | `icon.registry.ts`; no `lucide-react` imports in sections/components | pass | `lucide-react` isolated to registry. |
| Action Registry | Handoff CTA contract | `cta.registry.ts`; resolver; `Button` consumes resolved actions | pass | `decision_needed` and `roadmap_claim` actions disabled/hidden through policy. |
| Analytics Registry | Handoff analytics contract | `analytics.registry.ts`; `data-analytics-event` bindings | partial | Event names are registered, but no dispatch adapter yet. |
| Section Registry | Handoff section contract | `section.registry.ts`, `LandingPage.tsx:39-40` | pass | Section order/enabled state config-driven. |
| Claim Maturity | Roadmap / Handoff | `claimMaturity.ts`, `validateLandingContent.ts:57-61` | pass | Forbidden/unsupported blocked by validation policy. |
| No direct section colors/assets | Handoff hard bans | rg checks | pass | No direct colors/assets in sections/components. |
| No section-local analytics strings | Handoff analytics contract | rg checks | pass | Header receives event from model; Button from action. |
| Owner gates | Owner Gates doc | `LANDING_OWNER_GATES_v0.1.md`; `cta.registry.ts` | pass | Public freeze remains blocked. |

## 6. Architecture Compliance

### Next.js Isolation

Pass. `frontend/` is a standalone npm package with its own `package.json` and `package-lock.json`. No root package or Vite stack was introduced. Tracked diff under `app/` is empty, so current Python/static MVP runtime remains untouched.

### Domain Boundaries

Pass with minor caveats. Content, schemas, registries, theme contracts, primitives and sections are separate directories. `LandingPage` composes sections from `sectionRegistry` and validated model. UI code does not call backend/storage/env APIs.

### Content-driven Sections

Pass. Primary visible product copy is in `frontend/landing/content/ru/*.json`. Sections receive typed content DTOs. The audit found a small amount of hardcoded technical/accessibility Russian text in sections and root metadata; see findings.

### Registries

Pass. Asset, icon, CTA, analytics and section registries exist. Assets carry metadata and `rightsStatus: "local-scaffold"`. Icons are resolved through `IconRegistry`; actions through `ActionRegistry`.

### Tokens

Partial. Colors and spacing are centralized in `app/globals.css` CSS variables, with TS theme/layout contracts. Sections do not contain magic numbers. However several layout variant values live directly in `app/globals.css` rather than a dedicated generated token/contract file.

### Primitives

Pass. `Button` accepts resolved action state; `AssetImage` accepts `LandingAssetKey`; `Icon` accepts `IconKey`; layout primitives expose variants, not raw styles.

### Claim Maturity

Pass. `decision_needed` and `roadmap_claim` actions are not enabled. Validation errors on enabled `decision_needed`, enabled `roadmap_claim`, decorative asset alt mismatch, and forbidden/unsupported maturity.

### Owner Gates

Pass. CTA, pricing, export/download, cost, legal wording, product UI mockups and testimonials are explicitly gated in docs and reflected in registries/content.

## 7. Hardcode / Magic Findings

| Finding | Severity | File | Line | Why it matters | Recommended fix |
| --- | --- | --- | --- | --- | --- |
| Product metadata is hardcoded in root layout, while page metadata is content-driven. | low | `frontend/app/layout.tsx` | 5-6 | Strict reading says public text should come from content modules. `page.tsx` already overrides metadata from `seo.json`, so runtime impact is low. | Remove layout metadata or make it generic/non-product; keep SEO in `content/ru/seo.json`. |
| Accessibility/UI labels are hardcoded in sections. | low | `HeaderSection.tsx`, `HeroSection.tsx`, `DocumentsSection.tsx` | Header 16/33, Hero 26, Documents 32 | These are technical labels, not marketing copy, but they are still Russian strings outside content/i18n modules. | Move reusable labels to content/common UI labels or a small locale module. |
| Analytics events are registered and bound as data attributes, but no dispatcher exists. | medium | `analytics.registry.ts`, `Button.tsx`, `HeaderSection.tsx` | Button 45/57, Header 17/26/36 | Contract validates event existence, not actual event delivery. Disabled buttons also cannot emit `landing_disabled_cta_click` because native disabled buttons do not fire click events. | Add a tiny analytics adapter/client boundary, or document scaffold-only analytics and implement dispatch before owner/public review. |
| Some layout variant values live in `app/globals.css` outside TS layout contract. | medium | `frontend/app/globals.css` | 260, 265, 273, 777 | Sections are clean, but strict "numeric values only in token/contract files" is not fully met if global CSS is not treated as the CSS token implementation. | Either promote these values into named CSS variables/contract comments, or document `globals.css` token/variant section as the implementation contract. |

No findings for direct colors/assets in sections, direct image imports in sections, section-local CTA labels/hrefs, or section-local analytics event strings.

## 8. Responsive / Accessibility / Performance Findings

Responsive:

- Screenshots exist for 360, 390, 768, 1024, 1280, 1440 px.
- HTTP smoke passes on `http://localhost:3000`.
- Internal anchors resolve.
- Playwright was used through `npx --yes playwright@latest`; this is acceptable for manual audit, but CI needs an explicit decision.

Accessibility:

- Rendered HTML has `h1=1`, `main=1`, `header=1`, `sections=7`.
- Semantic `header`, `main`, `section`, `nav`, anchors and buttons are present.
- Focus state exists in `app/globals.css:82-84`.
- Reduced motion exists in `app/globals.css:93`.
- `AssetImage` takes alt from registry and marks decorative assets hidden at `AssetImage.tsx:26-34`.
- Axe or equivalent automated accessibility check was not run.

Performance:

- No `use client`, `useEffect`, viewport resize loops, `innerWidth`, `getBoundingClientRect`, or `ResizeObserver` were found.
- `AssetImage` wraps `next/image`, supplies intrinsic width/height and `sizes`.
- Hero/product UI and logo are priority; below-fold/document/decorative assets are lazy in registry.
- SVG assets are unoptimized via `unoptimized={asset.src.endsWith(".svg")}`, acceptable for scaffold SVGs but production raster assets need optimization policy.

## 9. Claim Maturity / Owner Gates

| Area | Audit result |
| --- | --- |
| `forbidden_claim` | Present in enum and docs; not used in content render path. |
| `unsupported_claim` | Present in enum and docs; not used in content render path. |
| `decision_needed` | `signup.freeStart`, `pricing.view`, `nav.login` are disabled/hidden and not enabled. |
| `roadmap_claim` | `docx.download` is disabled; cost/export claims are cautious. |
| Target Product | Hero and copy are target-product framed without claiming all capabilities are available now. |
| CTA | `demo.request` and `sample.project.view` enabled as safe scroll actions. |
| Export | DOCX export disabled, not active download. |
| Cost | Cost wording is cautious and tied to `claim.roadmap.costControl`. |
| Legal/standards | Standards copy is cautious and gated. |
| Testimonials | Section disabled; `testimonials.json` mode hidden; no fake quotes rendered. |
| Public launch | Explicitly blocked by owner gates. |

## 10. Risks

| Risk | Severity | Evidence | Recommended action |
| --- | --- | --- | --- |
| Analytics is scaffold-level only. | medium | `data-analytics-event` attributes exist, but no dispatcher; disabled buttons cannot click. | Add analytics adapter before owner/public review, or explicitly mark analytics as non-functional scaffold. |
| Token discipline is centralized but not perfectly contract-driven. | medium | Layout numeric values exist in `app/globals.css` class implementations. | Promote layout variant values to named CSS variables/contract layer. |
| No automated axe/accessibility CI. | medium | Structural accessibility checked; axe not run. | Add Playwright + axe or equivalent before public freeze. |
| Assets are local scaffold SVGs. | medium | `rightsStatus: "local-scaffold"` in Asset Registry. | Run production asset approval/provenance flow before public launch. |
| Hardcoded technical labels outside content/i18n. | low | Cyrillic strings in section aria labels and menu summary. | Move to locale/common labels if strict localization is required. |
| Playwright screenshots are local artifacts only. | low | `.next-logs/final-*.png`; Playwright via `npx`. | Decide whether screenshots become CI artifacts. |

## 11. Required Fixes

Must fix before next engineering phase:

- none blocking scaffold acceptance.

Must fix before owner review:

- clarify analytics status: scaffold-only or functional tracking;
- prepare owner review checklist from `LANDING_OWNER_GATES_v0.1.md`;
- decide whether root metadata and accessibility labels must move to locale/content.

Must fix before visual review:

- review production visual direction against references;
- replace or approve local scaffold assets;
- decide whether CSS layout variant values should become explicit token variables.

Must fix before public launch:

- close owner gates for CTA, pricing, exports, cost wording, legal wording, roadmap mockups and testimonials;
- add automated accessibility audit;
- add production analytics dispatch if metrics are required;
- approve assets/provenance and final copy;
- run deployment planning for serving `frontend/`.

Optional cleanup:

- add `theme.registry.ts` if multiple themes become real;
- move technical labels into `content/ru/ui.json` or similar locale module;
- add CI scripts for Playwright screenshots.

## 12. Readiness Verdict

```text
engineering_scaffold_verified_with_minor_findings
public_launch_blocked_by_owner_gates
```

The implementation is suitable as an engineering scaffold for the controlled landing. It is not production/public-launch ready.

## 13. Recommended Next Task

Recommended next task:

```text
Prepare owner review and visual review package for the landing:
- keep current code unchanged except approved fixes;
- review CTA/pricing/export/legal/testimonials gates;
- decide production asset direction and provenance;
- decide whether analytics dispatch is required before owner review;
- add automated accessibility/visual smoke if moving toward public freeze.
```

## 14. Phase 11 Addendum - Landing Mode And Action Visibility Resolver

Дата: 2026-06-11.

Изменение:

- добавлен `frontend/landing/config/landingMode.config.ts`;
- default landing mode зафиксирован как `showcase`;
- добавлен `frontend/landing/lib/actionVisibilityResolver.ts`;
- `actionRegistry` расширен metadata `role` и `requiredFunction`;
- `getLandingPageModel()` теперь отдаёт секциям resolved actions и сохраняет raw actions как `rawActions`;
- CTA-секции и `Button` типизированы на resolved action state;
- validation проверяет небезопасные resolved action states.

Текущий resolved state:

| Action | Result |
| --- | --- |
| `demo.request` | enabled in `showcase` as safe scroll action. |
| `sample.project.view` | enabled in `showcase` as safe sample/document preview action. |
| `signup.freeStart` | disabled, owner-gated, not active available-now. |
| `pricing.view` | hidden, owner-gated, not active available-now. |
| `docx.download` | disabled, roadmap, not active available-now. |
| `nav.login` | hidden, owner-gated; MVP Entry Gate not closed. |

Verification:

| Check | Result |
| --- | --- |
| `npm run validate` | pass; expected warnings include `Landing mode: showcase` and `MVP entry nav.login remains owner-gated`. |
| `npm run lint` | pass. |
| `npm run build` | pass; route `/` prerendered static. |
| `npm audit --omit=dev` | pass, `0 vulnerabilities`. |
| Section color static check | pass; no direct colors in sections/components. |
| Section asset static check | pass; no direct image paths in sections. |
| Section layout static check | pass; no inline style/magic layout matches in sections. |
| Section analytics static check | pass; no section-local analytics event strings. |
| Closed-world quick check | pass; no parent imports/runtime path hacks/env assumptions in frontend source. |

Readiness after Phase 11:

```text
engineering slice accepted
current mode: showcase
public launch: still blocked by owner gates
showcase publish: still requires Landing Mode Gate
MVP entry: still requires MVP Entry Gate
```

## 15. Phase 12 Addendum - Visual Asset Layering Contracts

Дата: 2026-06-11.

Изменение:

- создан `LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md`;
- `LANDING_VISUAL_TECH_CONTRACT_v0.1.md` дополнен layered hero scene и final CTA brand band rules;
- `LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md` расширен asset taxonomy and metadata;
- `asset.registry.ts` расширен `assetKind`, `backgroundMode`, `transparentBackground`, `layerRole`, `zSlot`, `overlapPolicy`, `safeArea`, `cropPolicy`, `shadowPolicy`;
- `AssetImage` прокидывает стабильные data hooks: `data-asset-kind`, `data-background-mode`, `data-layer-role`, `data-z-slot`;
- `validateLandingContent.ts` проверяет transparent/background/safe-area rules;
- `HeroVisual` и `FinalCtaSection` получили точечные sticky comments;
- AI Asset Generation Pipeline and Asset Provenance docs уточнены для cutout/content/backdrop/edgeDecor assets.

Ключевая фиксация:

| Pattern | Rule |
| --- | --- |
| Hero Layered Scene | Hero is a layered scene, not a single right-column image. Cutouts may overlap product UI only through registry/layer metadata. |
| Cutout Assets | Require transparent background metadata and clean alpha. |
| Content Images | Use embedded background; example: dish/card image inside calculation/document card. |
| Product UI | Must preserve product UI core safe area. |
| Final CTA Brand Band | High-contrast brand band with inverse text and protected text/CTA safe area. |
| Edge Decor | Transparent assets at edges; cannot cover heading, terms or buttons. |

Current scaffold note:

```text
No new production visual files were added.
Current SVGs remain local scaffold assets.
Future hero.chef, hero backdrop and final CTA edge decor require actual files, registry entries and provenance/rights metadata.
```

Verification:

| Check | Result |
| --- | --- |
| `npm run validate` | pass; asset layering validation accepts current scaffold. |
| `npm run lint` | pass. |
| `npm run build` | pass. |
| `npm audit --omit=dev` | pass, `0 vulnerabilities`. |
| Section color static check | pass. |
| Section asset static check | pass. |
| Section layout static check | pass. |
| Section analytics static check | pass. |
| Closed-world quick check | pass; no parent imports/runtime path hacks/env assumptions in frontend source. |

## 16. Phase 13 Addendum - Production Asset Brief

Дата: 2026-06-11.

Изменение:

- создан `LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md`;
- зафиксированы briefs для hero backdrop, `hero.chef` cutout, hero food cutout, final CTA brand band, final CTA edge decor and optional content image;
- target registry metadata описана заранее, но без создания несуществующих keys;
- reference composition связана с правилами transparent cutout, embedded content image, backdrop and edge decor.

Ключевая фиксация:

```text
Production brief is a generation/review contract, not a publish action.
No new production files, registry entries or provenance records were added in Phase 13.
```

Verification:

| Check | Result |
| --- | --- |
| Code changes | none; docs-only phase. |
| Registry changes | none; planned keys remain unregistered until files and approval exist. |
| Required next check | Markdown links and UTF-8 BOM after doc edit. |

## 17. Phase 14 Addendum - Showcase Publish Config And MVP Entry

Дата: 2026-06-11.

Изменение:

- owner decision по `landingMode = showcase` применён в `landingModeConfig`;
- `landingModeConfig.ownerGates.landingMode` закрыт;
- MVP entry включён как icon-only service action, не primary CTA;
- `nav.login` остаётся отдельным `mvp_entry` action;
- URL берётся из `NEXT_PUBLIC_MVP_ENTRY_URL` через config/resolver;
- временный домен не добавлен в sections/components/registry;
- commercial actions остаются hidden/disabled.

Текущий resolved behavior:

| Condition | `nav.login` result |
| --- | --- |
| `NEXT_PUBLIC_MVP_ENTRY_URL` задан и валиден | visible/enabled link, icon-only, aria-label `Вход в MVP`. |
| `NEXT_PUBLIC_MVP_ENTRY_URL` отсутствует или невалиден | hidden/owner_gated. |

Readiness after Phase 14:

```text
showcase publish: ready when deploy env provides NEXT_PUBLIC_MVP_ENTRY_URL
public launch: still blocked by owner gates
```

Verification:

| Check | Result |
| --- | --- |
| `npm run validate` with `NEXT_PUBLIC_MVP_ENTRY_URL` | pass; expected owner/public-launch warnings only. |
| `npm run lint` | pass. |
| `npm run build` with `NEXT_PUBLIC_MVP_ENTRY_URL` | pass; route `/` prerendered static. |
| `npm audit --omit=dev` | pass, `0 vulnerabilities`. |
| Temporary domain static check | pass; domain only in `frontend/.env.example` and build output generated from env, not source sections/components/registries. |
| Header render evidence | pass; prerendered HTML contains icon-only login links with `aria-label="Вход в MVP"` and no visible label span. |
| Closed-world quick check | pass; env read is isolated to landing config entrypoint, no workspace imports/runtime path hacks. |

## 18. Phase 15 Addendum - Showcase Placeholder Asset Policy

Дата: 2026-06-11.

Изменение:

- owner decision применён: текущий showcase может публиковаться с placeholder/scaffold assets;
- production asset generation/freeze не выполнялись;
- current code registry остается на существующих scaffold keys;
- planned production keys не добавлены без файлов;
- placeholder policy закреплена в docs/contracts;
- sections не менялись ради placeholder assets.

Current scaffold assets:

| Asset key | Kind | Background | Layer role | Rights status |
| --- | --- | --- | --- | --- |
| `brand.logoMark` | `brand` | `solid` | `brandMark` | `local-scaffold` |
| `hero.productUi` | `productUi` | `embedded` | `heroProductUi` | `local-scaffold` |
| `hero.dish` | `contentImage` | `embedded` | `heroForegroundObject` | `local-scaffold` |
| `documents.techCardPreview` | `documentPreview` | `embedded` | `documentContent` | `local-scaffold` |
| `documents.costCardPreview` | `documentPreview` | `embedded` | `documentContent` | `local-scaffold` |
| `cta.kitchenBoard` | `backdrop` | `embedded` | `finalCtaBrandBand` | `local-scaffold` |

Readiness after Phase 15:

```text
showcase publish with placeholder assets: accepted for current stage
production asset freeze: deferred
public launch: still blocked by owner gates
```

Verification:

| Check | Result |
| --- | --- |
| `npm run validate` with `NEXT_PUBLIC_MVP_ENTRY_URL` | pass; expected showcase/owner warnings only. |
| `npm run lint` | pass. |
| `npm run build` with `NEXT_PUBLIC_MVP_ENTRY_URL` | pass; route `/` prerendered static. |
| `npm audit --omit=dev` | pass, `0 vulnerabilities`. |
| TypeScript registry check | pass; 6 current asset records, all `rightsStatus: "local-scaffold"`. |
| Planned key static check | pass; `hero.chef`, `hero.decor.backgroundKitchen`, `finalCta.decor.*` absent from code registry/content/sections. |
| Section hardcode static checks | pass; no direct colors, direct image paths, inline style/magic layout, or section-local analytics strings. |
