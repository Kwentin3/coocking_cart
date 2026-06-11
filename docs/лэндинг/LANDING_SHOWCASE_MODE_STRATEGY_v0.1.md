# Landing Showcase Mode Strategy v0.1

<!-- STICKY-CONTEXT:
Этот лендинг сейчас работает как витрина Target Product. MVP - отдельный проверочный контур.
Не удаляй future CTA из модели. Управляй ими через landing mode, maturity и owner gates.
-->

Статус: стратегический refine режима витрины лендинга и контрактной управляемости CTA.
Дата: 2026-06-11.

Связанные документы:

- [Landing PRD](LANDING_PRD_v0.1.md)
- [Landing Implementation Handoff](LANDING_IMPLEMENTATION_HANDOFF_v0.1.md)
- [Landing Implementation Progress](LANDING_IMPLEMENTATION_PROGRESS.md)
- [Landing Implementation Audit](LANDING_IMPLEMENTATION_AUDIT_v0.1.md)
- [Landing Owner Gates](LANDING_OWNER_GATES_v0.1.md)
- [Product Vision](../product/PRODUCT_VISION_v0.1.md)
- [Product Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)
- [MVP / Target Product / Landing Traceability Matrix](mvp-landing-traceability-matrix.md)

## 1. Executive Summary

Текущий лендинг «ТехКухня» фиксируется как `showcase`: публичная витрина Target Product, а не полноценный SaaS launch и не MVP-only страница.

MVP остается отдельным проверочным контуром. Вход в него должен быть компактным служебным действием в header, предпочтительно в правом верхнем углу, и не должен конкурировать с маркетинговыми CTA.

Future/commercial actions не удаляются из документации, content modules или Action Registry. Они остаются контрактными объектами и переводятся между `visible`, `hidden`, `disabled`, `enabled`, `internal_only` и `owner_gated` через landing mode, claim maturity, owner gates и наличие реальной функции.

Текущая реализация содержит:

- `actionRegistry` с `demo.request`, `sample.project.view`, `signup.freeStart`, `pricing.view`, `docx.download`, `nav.login`;
- `landingModeConfig` с default mode `showcase`;
- owner-approved `showcase` storefront mode;
- owner-approved icon-only MVP entry, если `NEXT_PUBLIC_MVP_ENTRY_URL` задан;
- mode-aware Action Visibility Resolver;
- `header.json` с `loginActionId: "nav.login"`;
- section rendering через resolved `Button action={...}`, а не section-local labels/hrefs;
- claim maturity и resolved action validation;
- owner gates перед public launch.

`getLandingPageModel()` больше не передает raw `actionRegistry` в секции как render model. Секции получают resolved actions; raw actions остаются в модели отдельно как `rawActions` для аудита и validation context.

## 2. Storefront Analogy

Рабочая аналогия владельца продукта:

```text
Мы открываем большой продуктовый универмаг, но сейчас внутри ещё ремонт.
На фасаде уже есть баннеры, вывеска, описание будущего ассортимента и ценности.
Для участников теста есть аккуратный вход в уже существующий MVP.
```

Из этой аналогии следует:

- фасад может рассказывать о Target Product;
- нельзя обещать, что весь будущий ассортимент уже доступен;
- тестовый MVP вход должен быть отделен от публичной коммерческой воронки;
- коммерческие действия не вырезаются, а управляются как будущие capabilities;
- public showcase и SaaS launch имеют разные gates.

## 3. Current Landing Mode

Текущий режим: `showcase`.

Смысл режима:

- лендинг рассказывает о целевой продуктовой системе;
- MVP используется как рабочий проверочный контур;
- public launch не считается закрытым;
- коммерческие CTA остаются gated;
- roadmap/export/pricing/onboarding actions не выглядят как полностью доступные функции.

Текущие факты реализации:

| Area | Current state | Strategy reading |
| --- | --- | --- |
| Product framing | Target Product copy in docs/content | Correct for `showcase`. |
| MVP runtime | Existing Python/static runtime remains separate | Correct; do not merge into landing. |
| Header MVP entry | `header.json` references `nav.login`; resolver exposes it only when `NEXT_PUBLIC_MVP_ENTRY_URL` is configured | Icon-only service action approved; no visible label. |
| Primary safe action | `demo.request` enabled as scroll to final CTA | Acceptable scaffold action. |
| Example action | `sample.project.view` enabled as scroll to documents | Acceptable showcase action. |
| Signup/pricing | `decision_needed`; disabled/hidden | Correct for `showcase`. |
| DOCX export | `roadmap_claim`; disabled | Correct for `showcase`. |
| Testimonials | Section disabled | Correct until real approved quotes exist. |

## 4. Landing Modes

| Mode | Meaning | Public posture | MVP entry | Commercial CTA |
| --- | --- | --- | --- | --- |
| `showcase` | Target Product storefront without open commercial funnel | Can be published as a controlled product showcase if owner approves | Compact service entry, owner-gated | Mostly hidden/disabled unless safe and real |
| `beta` | Showcase plus limited intake | Public value story plus controlled applications/demo | Visible if test users need it | Demo/request actions may be enabled after owner decision |
| `launch` | Full public SaaS/commercial launch | Product is publicly available with conversion path | Secondary service action or account entry | Signup/pricing/onboarding/export can be enabled only if real |
| `internal` | Internal review/stage mode | Not a public promise | May be visible for team/testing | Can expose diagnostics or gated actions for review |
| `maintenance` | Temporary restricted mode | Minimal public surface | Optional | Commercial CTA hidden or disabled |

Minimum rule: a mode changes action state, not section code. Sections render the model they receive.

## 5. Action Visibility Policy

Action state must be resolved from these inputs:

- `landingMode`;
- action id;
- action maturity;
- `ownerApproved`;
- real function availability;
- target audience of the action: public, beta, MVP tester, internal;
- legal/copy status;
- fallback action.

Recommended output contract:

| State | Meaning | Rendering rule |
| --- | --- | --- |
| `enabled` | Real action is available and approved | Render active link/form/modal/scroll. |
| `visible` | Action may be shown but may not be active yet | Render normally only if also enabled; otherwise use disabled state. |
| `disabled` | Action is useful as a future/roadmap signal | Render disabled with reason or fallback. |
| `hidden` | Action should not appear in current mode | Render nothing. |
| `internal_only` | Action is for test/internal users | Render only in internal/beta context or behind explicit gate. |
| `owner_gated` | Action waits for owner decision | Hidden or disabled; never active. |

Policy rules:

1. Sections do not decide whether to show an action.
2. Sections do not remove actions from content.
3. `Button` and section components receive resolved action state.
4. `decision_needed` cannot become `enabled` without owner decision.
5. `roadmap_claim` cannot become an active available-now CTA.
6. `unsupported_claim` and `forbidden_claim` cannot render publicly.
7. MVP entry is not a marketing CTA; it is a service path.
8. Fallbacks point users to safe actions such as `demo.request` or `sample.project.view`.

## 6. MVP Entry Model

Target model:

- location: right side of header on desktop, compact menu placement on mobile;
- role: service entry into existing MVP/test contour;
- priority: lower than primary marketing CTA;
- label: no visible label; accessibility label `Вход в MVP`;
- icon: neutral login icon;
- URL/route: from `NEXT_PUBLIC_MVP_ENTRY_URL`, not section/component/registry hardcode;
- auth: explicit decision whether external users can access it;
- analytics: separate nav login event;
- maturity: `mvp_scope` because the current MVP/test contour exists.

Current state:

- `header.json` has `loginActionId: "nav.login"`;
- `HeaderSection` renders `loginActionId` through `Button` as icon-only;
- `nav.login` exists in Action Registry;
- `nav.login` is owner-approved as a service action;
- `landingModeConfig.mvpEntry.href` reads `NEXT_PUBLIC_MVP_ENTRY_URL`;
- resolver enables `nav.login` in `showcase` only when the URL is configured;
- if URL is missing, action remains hidden/owner_gated.

Audit result: MVP Entry Gate is partially closed for service entry visibility and presentation. Public SaaS registration remains closed.

## 7. CTA State Matrix

| Action id | Product role | Current maturity | Current scaffold state | `showcase` policy | Owner gate |
| --- | --- | --- | --- | --- | --- |
| `demo.request` | Safe discussion/pilot CTA | `mvp_scope` | enabled, visible, scroll | May remain visible/enabled if it does not imply open SaaS onboarding | Confirm target flow: form, mail, calendar, internal lead flow |
| `sample.project.view` | Safe sample/document preview | `mvp_scope` | enabled, visible, scroll | May remain visible/enabled as showcase evidence | Confirm sample scope and legal wording |
| `signup.freeStart` | Future onboarding/commercial CTA | `decision_needed` | disabled, visible | Keep disabled or hidden; do not delete | Decide whether free onboarding exists |
| `pricing.view` | Future pricing CTA | `decision_needed` | hidden | Keep hidden until pricing model is approved | Decide pricing model and visibility |
| `docx.download` | Future export action | `roadmap_claim` | disabled, visible | Keep disabled or hidden; do not imply active export | Decide export status and wording |
| `nav.login` | MVP/test contour entry | `mvp_scope` | env-configured icon-only service action | Visible/enabled only when `NEXT_PUBLIC_MVP_ENTRY_URL` is set | Keep service-only; auth handled by MVP |

Current action list is a contract asset. Removing future/commercial actions would erase governance information and make later mode transitions harder.

## 8. Claim Maturity Relation

| Claim maturity | Default action visibility | Notes |
| --- | --- | --- |
| `implemented_now` | `enabled` if owner/legal safe | May render as current capability. |
| `mvp_scope` | `enabled` or `internal_only` depending on audience | MVP entry may be service-only, not marketing primary. |
| `mvp_hypothesis` | `visible` with cautious wording, or `disabled` | Must not claim proven outcome. |
| `alpha_next` | `hidden`, `disabled`, or `owner_gated` | Can appear only with explicit owner-approved framing. |
| `roadmap_claim` | `disabled` or `hidden` | Never active available-now CTA. |
| `target_product_claim` | `visible` as storefront value | Action remains gated unless real function exists. |
| `vision_claim` | usually `hidden` or non-core `visible` | Avoid core CTA unless owner-approved. |
| `decision_needed` | `owner_gated`, then `hidden` or `disabled` | Cannot be enabled without owner decision. |
| `forbidden_claim` | `hidden`; validation error | Must not render. |
| `unsupported_claim` | `hidden`; validation error | Must not render until source/owner basis exists. |

This extends current claim maturity docs by tying maturity to action state. It does not replace Product Vision or Capability Roadmap.

## 9. Owner Gates Impact

Required gates:

| Gate | Decision needed | Blocks |
| --- | --- | --- |
| Landing Mode Gate | Choose `showcase`, `beta`, `launch`, `internal`, or `maintenance` for the next publish | Public status and action resolver config |
| MVP Entry Gate | Confirm URL/route, label, icon, visibility, external access, auth | Showing `nav.login` |
| CTA Visibility Gate | Decide state for signup, pricing, demo, export, sample actions per mode | CTA resolver/publish config |
| Public Launch Gate | Confirm SaaS launch readiness: onboarding, pricing, legal, analytics, support, export status | `launch` mode |
| Showcase Publish Gate | Confirm that showcase can be public without full SaaS launch | Public `showcase` publish |

Important distinction:

- `showcase` publish can be approved as a product storefront if owner accepts gated CTA and target-product framing.
- `launch` requires real commercial readiness and a stricter gate set.

## 10. Implementation Implications

Implemented engineering slice:

1. `landingModeConfig` defines default `showcase` and explicit owner/function gates.
2. Action Visibility Resolver takes raw `actionRegistry` and returns resolved actions.
3. Sections stay dumb: they receive resolved actions and render them.
4. Validation checks mode + maturity + owner gates before render.
5. MVP entry is icon-only and enabled only when `NEXT_PUBLIC_MVP_ENTRY_URL` is configured.
6. `LandingActionVisibility` remains render-level `visible | disabled | hidden`; richer states live in resolver metadata as `policyState`.

Remaining implementation implications:

1. Add analytics dispatch only after deciding which disabled/internal actions are actually clickable.
2. Keep deployment env `NEXT_PUBLIC_MVP_ENTRY_URL` updated until final domain is approved.
3. Add screenshot smoke for header state variants when non-showcase modes become active.

Verification surface:

- `npm run validate` must fail on unsafe mode/action combinations;
- `npm run lint` and `npm run build` must pass;
- static checks must still show no section-local CTA labels/hrefs;
- screenshot smoke should confirm header state per mode.

## 11. What Must Not Be Deleted

Do not delete:

- future/commercial actions from Action Registry;
- content action ids that point to gated actions;
- owner gates for pricing, onboarding, export, testimonials, legal wording;
- target-product claims that have Product Vision/Roadmap basis;
- disabled roadmap/export actions;
- `nav.login` contract hook;
- traceability and maturity documentation.

Deletion is only acceptable if the owner decides the capability is no longer part of Target Product or marks it `forbidden_claim`.

## 12. Follow-up Tasks

1. Keep MVP Entry URL in deploy/env config; replace temporary domain when final domain is approved.
2. Decide whether `demo.request` is a form, calendar link, email link, or internal lead flow.
3. Decide whether `signup.freeStart` remains disabled, hidden, or becomes beta/launch action.
4. Decide pricing visibility before exposing `pricing.view`.
5. Decide export wording before changing `docx.download` from disabled.
6. Add analytics dispatcher if action tracking is required before owner review.
7. Add visual/accessibility smoke for header state variants.
8. Add owner-approved non-showcase mode configs only after the corresponding gates are closed.

## 13. Sticky Comments Index

Sticky comments added by this refine:

| Location | Comment key | Purpose |
| --- | --- | --- |
| `LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md` | `STICKY-CONTEXT` | Anchor the storefront/showcase decision. |
| `LANDING_PRD_v0.1.md` | `STICKY-CONTEXT` | Prevent MVP-only rewrite and CTA deletion while reading PRD sections. |
| `LANDING_OWNER_GATES_v0.1.md` | `STICKY-ACTION-POLICY` | Keep signup/pricing/export/MVP entry gated, not removed. |
| `LANDING_IMPLEMENTATION_HANDOFF_v0.1.md` | `STICKY-ACTION-POLICY` | Tell implementers to route CTA state through resolver/config. |
| `frontend/landing/config/landingMode.config.ts` | `STICKY-ACTION-POLICY` | Keep mode changes out of sections. |
| `frontend/landing/registries/cta.registry.ts` | `STICKY-ACTION-POLICY` | Preserve future/commercial actions in registry. |
| `frontend/landing/lib/actionVisibilityResolver.ts` | `STICKY-ACTION-POLICY` | Mark resolver as boundary between registry and render. |
| `frontend/landing/sections/HeaderSection.tsx` | `STICKY-MVP-ENTRY` | Keep MVP entry separate from primary marketing CTA. |
| `frontend/landing/lib/validateLandingContent.ts` | `STICKY-ACTION-POLICY` | Validate resolved action state, not only raw registry state. |

Code sticky comments are intentionally limited to the resolver/config/registry/header/validation boundary points.

## 14. Owner Decision Addendum - Showcase Publish And MVP Entry

Дата: 2026-06-11.

Owner decision:

- `landingMode = showcase`;
- showcase publish allowed as Target Product storefront, not SaaS launch;
- MVP entry approved as icon-only service action in header;
- visible label: none;
- accessibility label: `Вход в MVP`;
- URL source: `NEXT_PUBLIC_MVP_ENTRY_URL`;
- temporary domain must not be hardcoded in sections, components or registry;
- commercial actions remain hidden/disabled.

Implementation reading:

- `landingModeConfig.ownerGates.landingMode = true`;
- `landingModeConfig.ownerGates.mvpEntry = true`;
- `landingModeConfig.functionAvailability.mvpEntry` depends on configured URL;
- `nav.login` remains a service action and is not promoted to a marketing CTA;
- public launch remains blocked by Public Launch Gate.
