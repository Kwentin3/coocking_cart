# Landing Implementation Progress

## Phase 0 — Repo audit и техническое решение

Status: done

Done:
- Проверен текущий frontend/runtime: Python `ThreadingHTTPServer` + static HTML/CSS/JS.
- Не найден существующий Vite/Next/React stack.
- Зафиксирован путь: отдельный Next.js app в `frontend/`.
- Создан `LANDING_IMPLEMENTATION_PLAN_v0.1.md`.

Validation:
- `node --version` -> `v22.19.0`.
- `npm --version` -> `11.6.2`.
- `rg --files` не нашел `package.json`, `vite.config.*`, `next.config.*`, `tsconfig.json`.

Deviations:
- Нет.

Next:
- Phase 1: создать минимальный Next.js frontend-контур.

## Phase 1 — Next.js scaffold

Status: done

Done:
- Создан standalone Next.js frontend в `frontend/`.
- Добавлены `app/page.tsx`, `app/layout.tsx`, `app/globals.css`, `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`.
- Добавлены команды `dev`, `build`, `start`, `lint`, `validate`.
- Текущий Python/static MVP runtime в `app/` не менялся.

Validation:
- `npm install` прошёл.
- `npm run build` проходит.
- `frontend/package-lock.json` зафиксировал закрытый набор npm-зависимостей.

Deviations:
- Next.js 16 не поддерживает прежний `next lint`; lint script использует `eslint .`.

Next:
- Phase 2: contracts, tokens, registries.

## Phase 2 — Contracts, tokens, registries

Status: done

Done:
- Созданы theme/layout/typography/motion contracts.
- Созданы `asset.registry.ts`, `icon.registry.ts`, `cta.registry.ts`, `analytics.registry.ts`, `section.registry.ts`.
- Создан `claimMaturity.ts` с maturity enum, claim refs и render/public policy.
- `docx.download`, `signup.freeStart`, `pricing.view`, `nav.login` не доступны как active available-now actions.

Validation:
- `npm run validate` проверяет action analytics coverage, asset paths, decorative alt, claim maturity и disabled decision actions.
- `npm audit --omit=dev` проходит после `postcss` override.

Deviations:
- Для Next.js 16.2.9 добавлен npm `overrides.postcss = 8.5.10`, чтобы закрыть транзитивный audit issue без breaking downgrade.

Next:
- Phase 3: content modules and schemas.

## Phase 3 — Content modules и schemas

Status: done

Done:
- Созданы русские JSON content modules в `frontend/landing/content/ru/`.
- Созданы Zod schemas для header, hero, audience, benefits, workflow, documents, standards, testimonials, final CTA, SEO.
- Контент лендинга опирается на Target Product framing и не сжимается до MVP-only copy.
- Testimonials имеют `mode: hidden` и не выводят fake quotes.

Validation:
- `npm run validate` проходит.
- Max length rules есть для hero/title/CTA/cards через Zod schemas.
- Стабильные ids есть у секций и content items.

Deviations:
- Финальный public copy не заморожен; спорные claims и CTA оставлены gated/configurable.

Next:
- Phase 4: primitives.

## Phase 4 — Primitives

Status: done

Done:
- Реализованы `Container`, `SectionShell`, `ResponsiveGrid`, `Stack`, `Cluster`, `Split`, `AspectFrame`, `FloatingPanel`, `Button`, `Card`, `Icon`, `AssetImage`, `Badge`.
- `Button` принимает `LandingAction`, а не raw href/label.
- `AssetImage` работает через `LandingAssetKey` и `AssetRegistry`.
- `Icon` работает через `IconKey` и `IconRegistry`.
- Disabled state и focus state предусмотрены.

Validation:
- `npm run lint` проходит.
- Static checks не нашли прямые цвета, image paths, inline styles или section-local analytics strings в sections/components.

Deviations:
- `Split` добавлен как primitive для контракта, но текущие секции используют `ResponsiveGrid` для основной композиции.

Next:
- Phase 5: section scaffolds.

## Phase 5 — Section scaffolds

Status: done

Done:
- Реализованы Header, Hero, Audience, Benefits, Workflow, Documents Demo, Standards, Testimonials, Final CTA.
- `LandingPage` рендерит секции через `sectionRegistry`, с сортировкой по `order` и фильтрацией `enabled`.
- Header находится вне `main`; остальные секции внутри `main`.
- Testimonials не рендерится публично, пока нет approved real testimonials.

Validation:
- `npm run build` проходит.
- `npm run validate` проходит.

Deviations:
- Активная форма заявки не реализована; primary CTA ведёт к final CTA секции как безопасный scroll action.

Next:
- Phase 6: visual implementation.

## Phase 6 — Visual implementation

Status: done

Done:
- Собрана визуальная композиция hero с named layers, tokenized offsets, aspect frame и registry-backed assets.
- Добавлены local scaffold SVG assets в `frontend/public/landing/assets/`.
- Documents demo использует registry-backed document preview assets.
- Mobile compact mode скрывает сложный hero visual, чтобы не ломать первый экран.

Validation:
- `npm run build` проходит.
- В секциях нет прямых imports PNG/SVG/WebP и прямых `/images/...`.
- В sections/components не найдены direct hex/rgb/hsl.

Deviations:
- Ассеты имеют `rightsStatus: local-scaffold`; production assets требуют отдельного approval/publishing flow.

Next:
- Phase 7: responsive pass.

## Phase 7 — Responsive pass

Status: done

Done:
- Проверены compact, comfortable, expanded, wide modes.
- Сняты Playwright screenshots для 360, 390, 768, 1024, 1280, 1440 px.
- После первого mobile screenshot исправлен overflow длинного H1 через mobile token, `overflow-wrap` и hyphenation.
- Compact mode показывает начало следующей секции в первом viewport.

Validation:
- Screenshots сохранены локально в `frontend/.next-logs/final-*.png`.
- HTTP smoke `http://localhost:3000` вернул 200.
- Internal anchors resolve: `audience`, `documents`, `final-cta`, `hero`, `standards`, `workflow`.

Deviations:
- Playwright используется через `npx --yes playwright@latest`, не добавлен в проектные зависимости.

Next:
- Phase 8: validation, lint, static checks.

## Phase 8 — Validation, lint, static checks

Status: done

Done:
- Выполнены content/schema validation, lint, production build, production audit, static hardcode checks, HTTP smoke и anchor check.
- Проверены section-level запреты: direct colors, direct assets, inline style/magic layout matches, analytics event strings.
- Проверены closed-world guards: нет parent-directory imports, runtime path hacks или secret/config path literals в frontend source.

Validation:
- `npm run validate` — pass с ожидаемыми warnings по disabled testimonials и owner decision claims.
- `npm run lint` — pass.
- `npm run build` — pass.
- `npm audit --omit=dev` — pass, 0 vulnerabilities.
- `rg` static checks — pass.

Deviations:
- Accessibility проверена структурно и через semantic implementation; отдельный axe-run не добавлен в этом проходе.

Next:
- Phase 9: owner gates перед public freeze.

## Phase 9 — Owner gates перед public freeze

Status: done

Done:
- Owner gates вынесены в `LANDING_OWNER_GATES_v0.1.md`.
- Спорные actions остаются hidden/disabled/configurable.
- Final CTA явно показывает, что public freeze требует owner decisions.

Validation:
- `decision_needed` actions не enabled.
- `roadmap_claim` export action disabled.
- `forbidden_claim` и `unsupported_claim` не используются в content/render path.

Deviations:
- Engineering scaffold ready; public launch blocked by owner gates.

Next:
- Owner review для CTA, pricing, exports, legal wording, roadmap mockups и testimonials.

## Phase 10 — Showcase mode и action visibility governance

Status: done

Done:
- Создан `LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md`.
- Зафиксировано: текущий режим лендинга — `showcase`, то есть витрина Target Product без открытой SaaS-воронки.
- Зафиксировано: MVP остаётся отдельным проверочным контуром, а вход в него должен быть служебным header action, не primary marketing CTA.
- Зафиксировано: future/commercial actions не удаляются из registry/content; они управляются через landing mode, claim maturity и owner gates.
- Owner gates расширены Landing Mode Gate, MVP Entry Gate, CTA Visibility Gate и Public Launch Gate.
- Implementation Handoff расширен разделом `Showcase Mode And Action Visibility`.

Validation:
- Это документационный refine; UI и кодовая логика не менялись.
- Текущий scaffold остаётся готовым как engineering scaffold.

Deviations:
- Mode-aware Action Resolver пока не реализован; это follow-up engineering slice.

Next:
- Owner decision по Landing Mode Gate и MVP Entry Gate.
- Реализация action visibility resolver после отдельного подтверждения.

## Phase 11 — Landing Mode и Action Visibility Resolver

Status: done

Done:
- Добавлен `frontend/landing/config/landingMode.config.ts` с default mode `showcase`, owner gates и function availability.
- Добавлен `frontend/landing/lib/actionVisibilityResolver.ts`.
- `actionRegistry` расширен role/requiredFunction metadata без удаления future/commercial actions.
- `getLandingPageModel()` теперь передаёт секциям resolved actions, а raw registry сохраняет как `rawActions`.
- `Button` и CTA-секции типизированы на `ResolvedLandingAction`.
- `nav.login` сохранён как MVP entry action, но остаётся hidden/owner-gated без MVP Entry Gate.
- Validation проверяет resolved action states, а не только raw registry.
- Добавлены точечные sticky comments в config, Action Registry, resolver, Header/MVP entry binding и validation policy.

Validation:
- `npm run validate` проходит.
- Ожидаемые warnings: testimonials disabled, pricing/onboarding owner decisions, `Landing mode: showcase`, `MVP entry nav.login remains owner-gated`.
- `npm run lint` проходит.
- `npm run build` проходит.
- `npm audit --omit=dev` проходит, 0 vulnerabilities.
- Static checks по direct colors/assets/inline layout/section-local analytics проходят.
- Closed-world quick check не нашёл parent imports, runtime path hacks или env assumptions в frontend source.

Deviations:
- Никакие non-showcase modes не включены публично.
- Public launch не объявлен готовым.
- Analytics dispatch не реализован; это отдельный follow-up.

Next:
- Закрыть Landing Mode Gate и MVP Entry Gate перед показом MVP entry.
- Реализовать analytics dispatch только после решения по clickable disabled/internal actions.

## Phase 12 — Visual asset taxonomy и layered composition contracts

Status: done

Done:
- Создан `LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md`.
- Зафиксированы asset kinds: `cutout`, `contentImage`, `backdrop`, `productUi`, `edgeDecor`, `documentPreview`, `brand`, `avatar`.
- Зафиксировано: прозрачный фон обязателен для `cutout`/`edgeDecor`, но не нужен для `contentImage` внутри карточек.
- Hero описан как layered product scene: backdrop, product UI, human cutout, foreground object, metric card, decor.
- Final CTA описан как high-contrast brand band with inverse text and protected text/CTA safe area.
- `asset.registry.ts` расширен metadata: background mode, transparent flag, layer role, z-slot, overlap policy, safe area, crop policy, shadow policy.
- `AssetImage` прокидывает `data-asset-kind`, `data-background-mode`, `data-layer-role`, `data-z-slot`.
- Validation проверяет transparent/background/safe-area rules.
- AI Asset Generation Pipeline уточнён под asset-kind prompt/output requirements.

Validation:
- `npm run validate` проходит.
- `npm run lint` проходит.
- `npm run build` проходит.
- `npm audit --omit=dev` проходит, 0 vulnerabilities.
- Static checks по direct colors/assets/inline layout/section-local analytics проходят.
- Closed-world quick check не нашёл parent imports, runtime path hacks или env assumptions в frontend source.

Deviations:
- Новые production assets не добавлялись: текущие SVG остаются local scaffold.
- `hero.chef`, hero backdrop и final CTA edge decor пока описаны как будущие registry additions, не как существующие файлы.

Next:
- Подготовить production asset brief для hero cutouts, backdrop and final CTA edge decor.
- После появления файлов добавить registry entries and provenance/rights metadata.

## Phase 13 — Production asset brief

Status: done

Done:
- Создан `LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md`.
- Зафиксирован первый production-пакет ассетов: hero backdrop, `hero.chef` cutout, hero food cutout, final CTA brand band, final CTA edge decor и optional content image для карточек.
- Разделены правила для transparent cutout/edge decor и embedded content images.
- Зафиксированы target registry metadata для каждого planned asset kind.
- Подтверждено: новые registry entries не добавляются до появления реальных файлов, provenance/rights metadata and manual approval.
- README, Visual Asset Layering Contract and AI Asset Generation Pipeline связаны с production brief.

Validation:
- Документационная фаза; код лендинга не менялся.
- Требуется локальная проверка Markdown links and UTF-8 BOM after edit.

Deviations:
- Production images не создавались и не публиковались.
- `hero.chef`, hero backdrop and final CTA edge decor остаются planned assets.

Next:
- Generate/review candidates по production brief.
- После approval добавить файлы, provenance/rights records, registry entries and visual smoke.

## Phase 14 — Showcase publish config и MVP entry

Status: done

Done:
- Owner decision применён: `landingMode = showcase`.
- Showcase publish зафиксирован как controlled Target Product storefront, не как полноценный SaaS launch.
- `landingModeConfig.ownerGates.landingMode` закрыт.
- MVP Entry Gate частично закрыт: `nav.login` стал owner-approved service action.
- MVP entry рендерится как icon-only action без видимого label; accessibility label: `Вход в MVP`.
- URL берётся из `NEXT_PUBLIC_MVP_ENTRY_URL` через config/resolver, не из секций, компонентов или registry.
- Если URL не задан, resolver оставляет `nav.login` hidden/owner_gated.
- Коммерческие/lead actions `demo.request`, `signup.freeStart`, `pricing.view`, `docx.download` не удалены и не стали active available-now.
- В `showcase` `demo.request` и `signup.freeStart` скрыты; безопасным публичным действием остаётся `sample.project.view`.
- Добавлен `frontend/.env.example` с временным MVP URL как deployment example.
- Sticky comments уточнены в config, resolver and header.

Validation:
- `npm run validate` проходит с `NEXT_PUBLIC_MVP_ENTRY_URL`.
- `npm run lint` проходит.
- `npm run build` проходит с `NEXT_PUBLIC_MVP_ENTRY_URL`.
- `npm audit --omit=dev` проходит, `0 vulnerabilities`.
- Static check подтвердил: временный домен встречается в `frontend/.env.example`, но не в sections/components/registries.
- Static checks по direct colors/assets/inline layout/section-local analytics проходят.
- Closed-world quick check: env читается только в `frontend/landing/config/landingMode.config.ts`; workspace imports/runtime path hacks не найдены.
- Rendered HTML содержит icon-only `nav.login` links с `aria-label="Вход в MVP"` и без видимого текстового label.

Deviations:
- Public launch не объявлен готовым.
- Временный домен остаётся deployment/env значением и должен быть заменён после решения по финальному домену.

Next:
- Настроить `NEXT_PUBLIC_MVP_ENTRY_URL` в deploy env для showcase publish.
- Добавить analytics dispatch, если метрики кликов нужны до публичного showcase.

## Phase 15 — Placeholder asset policy для showcase

Status: done

Done:
- Owner decision применён: текущая showcase-публикация использует placeholder/scaffold assets.
- Production assets не генерировались и не утверждались.
- Новые production keys (`hero.chef`, hero backdrop, final CTA edge decor) не добавлялись в code registry.
- Проверено: текущий `AssetRegistry` содержит только существующие scaffold files and keys.
- Все текущие assets имеют `rightsStatus: "local-scaffold"` and layered metadata.
- `hero.dish` оставлен `contentImage` with `embedded` background, не переведён в `cutout`.
- Production Asset Brief сохранён как future contract для candidates, review, provenance/rights approval and replacement.
- Placeholder policy добавлена в Owner Gates, Production Asset Brief, Visual Asset Layering Contract, Asset & Icon Registry Contract and README.
- Секции не переписывались под плейсхолдеры.

Validation:
- `npm run validate` проходит с `NEXT_PUBLIC_MVP_ENTRY_URL`.
- `npm run lint` проходит.
- `npm run build` проходит с `NEXT_PUBLIC_MVP_ENTRY_URL`.
- `npm audit --omit=dev` проходит, `0 vulnerabilities`.
- TypeScript registry check подтвердил: 6 current asset records, все `rightsStatus: "local-scaffold"`.
- Static check подтвердил: planned production keys отсутствуют в code registry/content/sections.
- Static checks по direct colors/assets/inline layout/section-local analytics проходят.

Deviations:
- Public launch не объявлен готовым.
- Production asset freeze перенесён на будущий этап.

Next:
- После production asset approval заменить placeholder assets через `AssetRegistry`.
- После замены выполнить visual smoke across desktop/mobile.

## Phase 16 — Controlled showcase publish preparation

Status: done

Done:
- Проверена текущая controlled showcase configuration: `landingMode = showcase`, `ownerGates.landingMode = true`, `ownerGates.publicLaunch = false`.
- Проверено, что `NEXT_PUBLIC_MVP_ENTRY_URL` управляет `nav.login` через config/resolver, а не через section/component/registry hardcode.
- С env `NEXT_PUBLIC_MVP_ENTRY_URL=https://coocking-cart.speechbattle.com/` MVP entry рендерится как icon-only service action: без visible text, с `aria-label="Вход в MVP"` and href из env.
- Без env и с невалидным env validation проходит, а `nav.login` остается hidden/owner_gated.
- Проверено, что commercial/lead actions остаются gated: `demo.request` hidden, `signup.freeStart` hidden, `pricing.view` hidden, `docx.download` disabled roadmap action.
- Проверено, что current asset registry содержит 6 scaffold records, все с `rightsStatus: "local-scaffold"`.
- Проверено, что planned production keys (`hero.chef`, hero backdrop, final CTA edge decor, dish cutout/content image additions) не добавлены без файлов and approval.
- Выполнен visual smoke desktop/mobile с env и без env; screenshots сохранены в `frontend/.next-logs/publish-*.png`.
- Создан `LANDING_SHOWCASE_PUBLISH_REPORT_v0.1.md`.

Validation:
- PowerShell env syntax used: `$env:NEXT_PUBLIC_MVP_ENTRY_URL='https://coocking-cart.speechbattle.com/'; npm ...`.
- `npm run validate` with env — pass; expected warnings only.
- `npm run lint` — pass.
- `npm run build` with env — pass; final build artifact собран с MVP entry URL.
- `npm audit --omit=dev` — pass, `0 vulnerabilities`.
- `npm run validate` without env — pass with `MVP entry nav.login remains owner-gated`.
- `npm run validate` with invalid env — pass with `MVP entry nav.login remains owner-gated`.
- Static checks по temporary domain, direct colors, direct section assets, inline section layout, section-local analytics and planned production keys — pass.
- Playwright visual smoke via cached `playwright@1.60.0` — pass: desktop/mobile, no horizontal overflow, hero/documents/final CTA present, MVP entry visible only with env.

Deviations:
- Production deploy itself was not executed in this phase.
- Production assets were not generated or approved.
- Analytics dispatch and automated accessibility audit remain follow-up tasks.
- Public SaaS launch не объявлен готовым.

Next:
- Configure `NEXT_PUBLIC_MVP_ENTRY_URL` in deploy runtime for controlled showcase publish.
- Add analytics dispatch if click metrics are required for showcase.
- Run production asset workflow separately before asset freeze.
- Keep public launch blocked until commercial/legal/accessibility/asset gates are closed.

## Phase 17 — Responsive final CTA brand band assets

Status: done

Done:
- Final CTA single-backdrop contract replaced with explicit desktop/mobile backdrop keys.
- Generated two bitmap derivatives with built-in image generation, not project OpenAI/Gemini API:
  - `cta.kitchenBoard.desktop` -> `frontend/public/landing/assets/cta-kitchen-board-desktop.webp`;
  - `cta.kitchenBoard.mobile` -> `frontend/public/landing/assets/cta-kitchen-board-mobile.webp`.
- `FinalCtaSection` now renders the brand band through a registry-backed responsive `<picture>` primitive.
- Validation now fails if final CTA uses the same backdrop key for desktop/mobile or if the variant visibility does not match `desktop-only` / `mobile-only`.
- Visual contracts updated in Production Asset Brief, Visual Asset Layering Contract and Asset/Icon Registry Contract.
- Overlay adjusted so desktop edge decor remains visible while preserving the text-safe area.

Validation:
- `npm run validate` — pass; expected showcase/owner warnings only.
- `npm run lint` — pass.
- `npm run build` — pass.
- `git diff --check` — pass.
- Browser smoke:
  - desktop viewport uses `cta-kitchen-board-desktop.webp`;
  - mobile viewport uses `cta-kitchen-board-mobile.webp`;
  - final CTA remains full-width in both viewports;
  - showcase commercial CTA text and owner-gate text remain absent.

Deviations:
- Full production visual freeze is still not declared.
- Future final CTA edge decor cutouts remain separate planned assets.
