# Landing Showcase Publish Report v0.1

Статус: controlled showcase publish preparation report.
Дата: 2026-06-11.
Область: публичная витрина `showcase`, MVP entry, placeholder assets, build/static checks, visual smoke.

## 1. Executive Summary

Controlled showcase publish готов к текущему этапу при условии, что deploy/runtime предоставляет:

```text
NEXT_PUBLIC_MVP_ENTRY_URL=https://coocking-cart.speechbattle.com/
```

Это не полноценный public SaaS launch. Лендинг остается витриной Target Product с аккуратным входом в существующий MVP, закрытыми коммерческими действиями и registry-backed placeholder/scaffold assets.

Итог:

```text
controlled showcase publish: ready
MVP entry: env-configured icon-only service action
placeholder assets: accepted for showcase
production asset freeze: deferred
public SaaS launch: blocked by owner gates
```

## 2. Publish Mode

Проверенное состояние:

| Field | Value |
| --- | --- |
| `landingModeConfig.mode` | `showcase` |
| `ownerGates.landingMode` | `true` |
| `ownerGates.publicLaunch` | `false` |
| `ownerGates.mvpEntry` | `true` |
| Commercial gates | closed |
| Public launch | not ready |

Showcase publish читается как:

```text
Target Product storefront
+ placeholder/scaffold visuals
+ service entry into existing MVP
+ hidden/disabled commercial actions
```

## 3. Env / Config Used

Commands were run from `frontend/`.

PowerShell env syntax used:

```powershell
$env:NEXT_PUBLIC_MVP_ENTRY_URL='https://coocking-cart.speechbattle.com/'; npm run validate
$env:NEXT_PUBLIC_MVP_ENTRY_URL='https://coocking-cart.speechbattle.com/'; npm run lint
$env:NEXT_PUBLIC_MVP_ENTRY_URL='https://coocking-cart.speechbattle.com/'; npm run build
```

The MVP URL source remains:

```text
NEXT_PUBLIC_MVP_ENTRY_URL
```

The temporary domain was found only in allowed places:

- `frontend/.env.example`;
- `frontend/landing/config/landingMode.config.ts` as env source/read boundary;
- validation/resolver diagnostic strings;
- final build output generated from env.

No temporary domain hardcode was found in sections, components or Action Registry hrefs.

## 4. MVP Entry Behavior

With env:

| Check | Result |
| --- | --- |
| `nav.login` resolved state | `enabled`, `visible` |
| href | `https://coocking-cart.speechbattle.com/` |
| visible label | none |
| text content | empty |
| `aria-label` | `Вход в MVP` |
| role | service entry, not primary CTA |
| desktop visual smoke | visible in header right |
| mobile visual smoke | visible after compact menu open |

Without env:

| Check | Result |
| --- | --- |
| `npm run validate` | pass |
| resolved `nav.login` | hidden / owner-gated |
| rendered login hooks | `0` |
| broken link | absent |

With invalid env:

| Check | Result |
| --- | --- |
| `NEXT_PUBLIC_MVP_ENTRY_URL=not-a-valid-url npm run validate` | pass |
| resolved `nav.login` | hidden / owner-gated |

## 5. Commercial Action State

Resolver evidence with env:

| Action | State | Policy |
| --- | --- | --- |
| `demo.request` | enabled, visible | safe showcase scroll action |
| `sample.project.view` | enabled, visible | safe showcase scroll action |
| `signup.freeStart` | disabled | owner-gated, `decision_needed` |
| `pricing.view` | hidden | owner-gated, `decision_needed` |
| `docx.download` | disabled | roadmap action, not available-now |
| `nav.login` | enabled, visible | env-configured MVP service entry |

Commercial/future actions remain in the registry. They were not deleted, promoted to active links or reimplemented through section-local hacks.

## 6. Placeholder Asset State

Current `AssetRegistry` contains 6 records. All are `rightsStatus: "local-scaffold"`:

| Asset key | Kind | Background | Layer role | Status |
| --- | --- | --- | --- | --- |
| `brand.logoMark` | `brand` | `solid` | `brandMark` | `local-scaffold` |
| `hero.productUi` | `productUi` | `embedded` | `heroProductUi` | `local-scaffold` |
| `hero.dish` | `contentImage` | `embedded` | `heroForegroundObject` | `local-scaffold` |
| `documents.techCardPreview` | `documentPreview` | `embedded` | `documentContent` | `local-scaffold` |
| `documents.costCardPreview` | `documentPreview` | `embedded` | `documentContent` | `local-scaffold` |
| `cta.kitchenBoard` | `backdrop` | `embedded` | `finalCtaBrandBand` | `local-scaffold` |

Confirmed:

- placeholder assets do not claim production approval;
- no fake provenance/rights approval was added;
- no planned production keys were added without real files;
- `hero.chef`, hero backdrop, final CTA edge decor and production food cutouts remain planned future assets;
- sections were not rewritten around placeholder-specific assumptions.

## 7. Build / Validation Evidence

| Check | Result |
| --- | --- |
| `npm run validate` with env | pass |
| `npm run lint` with env | pass |
| `npm run build` with env | pass |
| `npm audit --omit=dev` | pass, `0 vulnerabilities` |
| `npm run validate` without env | pass, `MVP entry nav.login remains owner-gated` |
| `npm run validate` with invalid env | pass, `MVP entry nav.login remains owner-gated` |

Expected validation warnings remain:

- testimonials disabled because no approved real testimonials exist;
- pricing requires owner decision before public launch;
- onboarding requires owner decision before public launch;
- landing mode is `showcase`.

Static checks:

| Check | Result |
| --- | --- |
| temporary domain / env source search | pass |
| no direct colors in sections/components | pass |
| no direct image paths in sections | pass |
| no inline style/raw layout matches in sections | pass |
| no section-local analytics strings | pass |
| planned production keys absent from code registry/content/sections | pass |

## 8. Visual Smoke Evidence

Visual smoke was run with local Next production server and Playwright `1.60.0` from npx cache. No dependency was added to `package.json`.

Screenshots:

| Mode | Screenshot |
| --- | --- |
| with env, desktop | `frontend/.next-logs/publish-env-desktop.png` |
| with env, mobile | `frontend/.next-logs/publish-env-mobile.png` |
| without env, desktop | `frontend/.next-logs/publish-no-env-desktop.png` |
| without env, mobile | `frontend/.next-logs/publish-no-env-mobile.png` |

Results:

| Check | With env | Without env |
| --- | --- | --- |
| desktop rendered | pass | pass |
| mobile rendered | pass | pass |
| header present | pass | pass |
| hero present | pass | pass |
| documents block present | pass | pass |
| final CTA present | pass | pass |
| MVP entry | visible, icon-only | absent |
| horizontal overflow | false | false |
| disabled commercial CTAs | present as disabled buttons | present as disabled buttons |

With env smoke details:

```text
login hooks: 2
visible per viewport: 1
labels: "Вход в MVP"
hrefs: https://coocking-cart.speechbattle.com/
texts: empty
horizontalOverflow: false
```

Without env smoke details:

```text
login hooks: 0
horizontalOverflow: false
disabled CTAs: Скачать DOCX, Начать бесплатно
```

## 9. Remaining Blockers For Public SaaS Launch

Public launch remains blocked by:

- public signup/onboarding decision;
- pricing model decision;
- DOCX/PDF/Excel export status and wording;
- legal/copy approval;
- production asset candidates, provenance, rights review and freeze;
- analytics dispatch if launch metrics are required;
- automated accessibility audit;
- support/runbook/deployment ownership decisions.

These are not blockers for the current controlled showcase publish.

## 10. Next Steps

1. Configure `NEXT_PUBLIC_MVP_ENTRY_URL` in deploy env for the showcase environment.
2. Publish as controlled `showcase`, not as public SaaS launch.
3. Keep commercial actions hidden/disabled until owner gates close.
4. Keep placeholder assets marked as `local-scaffold`.
5. Run production asset workflow separately before any asset freeze.
6. Add analytics dispatch and accessibility automation before public launch freeze.

## 11. Acceptance Summary

| Criterion | Status |
| --- | --- |
| `landingMode = showcase` | pass |
| showcase publish status checked | pass |
| `NEXT_PUBLIC_MVP_ENTRY_URL` env/config source | pass |
| MVP entry visible with env | pass |
| MVP entry hidden without/invalid env | pass |
| MVP entry has no visible text | pass |
| MVP entry has `aria-label` | pass |
| commercial actions hidden/disabled | pass |
| placeholder assets remain scaffold | pass |
| no production asset keys without files/approval | pass |
| validate/lint/build/audit | pass |
| static checks | pass |
| visual smoke | pass |
| progress updated | pass |
| public launch not declared ready | pass |

Final verdict:

```text
controlled showcase publish ready
public launch still blocked
```
