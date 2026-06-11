# Agent-Native CSM / Landing Control Plane Blueprint

Статус: архитектурный blueprint без реализации кода.
Версия: 0.1
Область: управляемый публичный лендинг «ТехКухня».

Связанные документы:

* [Пакет документов публичного лендинга](лэндинг/README.md)
* [PRD лендинга](лэндинг/LANDING_PRD_v0.1.md)
* [Визуальный и технический контракт](лэндинг/LANDING_VISUAL_TECH_CONTRACT_v0.1.md)
* [Asset & Icon Registry Contract](лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
* [Product Vision](product/PRODUCT_VISION_v0.1.md)
* [Capability Roadmap](product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)

## 1. Executive Summary

Landing Control Plane — это не классическая CMS и не свободное редактирование JSX агентом. Это контрактный слой управления лендингом, где агент работает с адресуемыми модулями, схемами, реестрами и проверками.

Рекомендация для v1:

* Git-backed content в JSON как основной источник данных.
* Zod-схемы в TypeScript как runtime validation и источник JSON Schema для агента.
* Отдельные реестры секций, ассетов, иконок, тем и аналитики.
* Манифест на каждый модуль как Agent Context Capsule.
* CLI `landingctl` как основной управляющий интерфейс для агента.
* Preview, diff, validation и Git rollback как обязательный контур перед публикацией.
* Headless CMS и визуальную админку отложить до v2, не делая их владельцами архитектуры.
* AI-generated assets подключать только через отдельный pipeline: candidate -> preview -> manual approval -> Asset Registry -> section patch.

Главное упрощение: не строить полноценную CMS на старте. Для v1 достаточно файлового content layer, строгих контрактов и хорошего agent tooling. Это закрывает основную боль: тексты, ассеты, иконки, CTA, порядок секций и тема меняются управляемо, без хардкода в верстке.

## 2. Current Repo Audit

Короткий аудит текущего репозитория:

* Существующий runtime — Python-приложение с HTML-шаблоном и vanilla frontend: `app/templates/index.html`, `app/static/app.js`, `app/static/styles.css`.
* Отдельного production-лендинга в коде пока нет.
* Текущий frontend demo содержит тексты прямо в HTML/JS и CSS tokens в `:root`; это допустимо для Demo MVP, но не является целевой моделью лендинга.
* Уже есть документационный пакет лендинга в `docs/лэндинг/`: PRD, визуально-технический контракт, asset/icon contract и эскизы.
* Значит Landing Control Plane нужно проектировать как future architecture для нового landing frontend, а не как немедленный refactor текущего demo chat UI.

Практический вывод: Phase 0 реализации должна подтвердить выбранный frontend stack. Blueprint ниже предполагает React/Next-style структуру как целевую, но сами контракты не завязаны жестко на Next.js.

## 3. Problem Statement

Лендинг с маркетинговой подачей быстро деградирует, если тексты, изображения, иконки, цвета, CTA и порядок секций живут прямо в компонентах. Любая правка превращается в инженерное изменение, а агенту приходится открывать большие файлы с версткой, стилями и бизнес-текстами одновременно.

Целевая проблема:

* агент должен менять конкретный модуль лендинга без загрузки всей страницы в контекст;
* правки должны быть ограничены схемами и реестрами;
* пользователь должен видеть diff и preview до фиксации;
* контентные изменения должны быть отделены от инженерных изменений;
* откат должен работать на уровне отдельных content modules, а не только всего приложения.

## 4. Goals / Non-Goals

Goals:

* вынести контент из JSX/TSX в управляемые content modules;
* сделать каждый модуль лендинга адресуемым и валидируемым;
* централизовать темы, ассеты, иконки, секции и analytics events;
* дать агенту inspect/read/patch/validate/preview/diff/rollback операции;
* обеспечить Git-based versioning;
* сохранить возможность подключить CMS позже без переписывания секций.

Non-goals для v1:

* не строить полноценную визуальную CMS;
* не давать агенту произвольное редактирование всей верстки;
* не делать универсальный page builder;
* не поддерживать произвольные layout-блоки от пользователя;
* не автоматизировать юридическую экспертизу нормативных утверждений;
* не смешивать реализацию лендинга с Demo MVP chat workspace.

## 5. Target Architecture

Целевая схема:

```text
User chat window
  -> Agent
    -> landingctl CLI / Landing Control API
      -> Module manifest registry
      -> Content registry
      -> Schema registry
      -> Section registry
      -> Asset registry
      -> Icon registry
      -> Theme registry
      -> Analytics registry
      -> Validation layer
      -> Diff layer
      -> Preview builder
      -> Git versioning
        -> Rendered landing
```

Ответственность слоев:

| Слой | Ответственность |
| --- | --- |
| User chat window | Пользователь ставит задачу агенту и подтверждает рискованные изменения. |
| Agent | Выбирает модуль, читает manifest/context capsule, готовит patch, запускает validation/preview/diff. |
| CLI/API | Узкая поверхность управления. Не дает агенту обходить контракты. |
| Content registry | Хранит адресуемые content keys и пути к content files. |
| Schema registry | Связывает content key со схемой и validation rules. |
| Section registry | Определяет порядок, включенность, variant и binding секций. |
| Asset registry | Управляет изображениями, decorative assets, previews и loading strategy. |
| Icon registry | Управляет пиктограммами и их theme variants. |
| Theme registry | Управляет semantic tokens и доступными темами. |
| Analytics registry | Фиксирует допустимые events и обязательные CTA bindings. |
| Validation layer | Проверяет схему, ссылки, длины, юридически чувствительные фразы, analytics coverage. |
| Preview layer | Собирает локальный/preview render для проверки. |
| Git/versioning | Хранит историю изменений и обеспечивает rollback. |
| Rendered landing | Только читает контракты и данные. Не является источником данных. |

Ключевой принцип границ: компоненты рендера не знают физические пути ассетов, конкретные hex-цвета и бизнес-тексты. Они получают content DTO, asset resolver, icon resolver, theme tokens и analytics handler.

## 6. Domain and Ownership Map

| Домен | Владелец решения | Что хранит | Что не должен делать |
| --- | --- | --- | --- |
| Content | Product/marketing через agent workflow | Тексты, CTA labels, списки карточек, SEO metadata | Не хранит JSX, CSS, пути файлов |
| Schema | Engineering | Zod/JSON Schema, length limits, enum keys, legal guardrails | Не хранит маркетинговый текст |
| Rendering | Frontend | Секции, компоненты, layout primitives | Не владеет текстами и ассетами |
| Visual system | Design/frontend | Theme tokens, component variants, section variants | Не решает product messaging |
| Assets | Design/content ops | Asset keys, alt, roles, loading, visibility | Не импортируется секциями напрямую |
| Icons | Design/frontend | IconKey, source, role, variants | Не задает локальные цвета |
| Analytics | Product/analytics | Event names, required CTA bindings | Не встраивает events в контент без registry |
| Governance | Engineering/product | Risk gates, preview, diff, rollback | Не подменяет schema validation |

## 7. Module Model

Каждая секция лендинга — самостоятельный управляемый модуль. Минимальная единица работы агента: `moduleId`, например `hero`, `audience`, `documents`.

Общие поля модуля:

```ts
type LandingModuleContent = {
  id: string;
  locale: "ru";
  version: number;
  updatedAt?: string;
  title?: string;
  enabled?: boolean;
};
```

Общие правила:

* content file содержит только данные;
* модуль имеет schema, manifest и preview route;
* module patch не может менять чужой модуль без отдельной операции;
* все asset/icon ссылки валидируются по registry;
* все CTA валидируются по action contract и analytics registry.

### 7.1. Module Contract Matrix

| Модуль | Назначение | Обязательные данные | Опциональные данные | Ограничения | Допустимые ассеты/иконки | Analytics | Риск |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Header | Навигация, login/register CTA, brand signal | logo asset key, nav items, primary CTA, login link | dropdown groups, mobile label | nav label до 24 символов, CTA label до 28 | `brand.logo`, `brand.logoMark`, `nav.chevronDown` | nav click, login click, primary CTA | Средний для nav, низкий для labels |
| Hero | Первый экран, позиционирование, primary conversion | title, description, primary/secondary CTA, trust items, visual keys | eyebrow, metric card, secondary visual | title 45-90 символов, description 120-220 | `hero.*`, `feature.*`, `action.*` | hero primary/secondary CTA | Средний; высокий при layout/visual variant |
| Audience | Сегменты пользователей | title, 3-6 audience items | href per item, badges | item title до 40, description до 140 | `audience.*`, `audience.*` icons | audience card click | Низкий для текста, средний для item count |
| Benefits | Практическая ценность | title, 3-5 benefit items | section intro | item description до 160 | `benefit.*` icons | benefit view/click optional | Низкий |
| Workflow | Процесс работы | title, 4-6 ordered steps | step captions, secondary link | step title до 48, description до 140 | `workflow.*` icons | workflow step interaction optional | Средний при reorder |
| Documents Demo | Демонстрация результата | document types, dish card, calculation sample, output doc CTA | download sample link, filters | document label до 42, table rows 2-6 | `documents.*`, `document.*`, `status.*` | document type click, sample download | Средний |
| Standards | Нормативное доверие | title, cautious copy, standard list | footnote, links | запрещены абсолютные legal claims | `standard.*`, `standards.decor.*` | standard info click optional | Средний из-за legal sensitivity |
| Testimonials | Social proof | testimonials or placeholder mode | avatars, company, role | запрещены fake testimonials как реальные | `testimonials.avatar.*`, `testimonial.quote` | testimonial carousel/click optional | Средний |
| Final CTA | Повторная конверсия | title, description, primary/secondary CTA | terms list, decor keys | title до 80, CTA label до 28 | `finalCta.decor.*`, `action.*` | final CTA, demo request | Средний |

## 8. Content Contract

Рассмотренные варианты:

| Вариант | Плюсы | Минусы | Решение |
| --- | --- | --- | --- |
| JSON | Машинно-патчится, строгий diff, нет выполнения кода, удобно валидировать | Менее удобен человеку, нет комментариев | Рекомендован для v1 |
| YAML | Удобнее читать, можно комментировать | Риск неоднозначных типов, сложнее безопасный patch | Можно позже для редакторских черновиков |
| TypeScript modules | Типы рядом, удобно разработчику | Контент становится кодом, сложнее агентный patch, выше риск | Не для v1 content source |
| Headless CMS | UI, роли, publish workflow | Интеграционная сложность, vendor lock-in, рано для текущей стадии | v2 |
| Git-backed content | Простой audit trail, PR/diff/rollback, не нужен сервер CMS | Требует CLI tooling и дисциплины | Базовая модель v1 |

Рекомендация: Git-backed JSON content + Zod validation + generated JSON Schema для агента.

Пример структуры content entity:

```json
{
  "id": "landing.hero",
  "locale": "ru",
  "version": 1,
  "title": "Технологические карты и расчеты для кухни без хаоса в таблицах",
  "description": "ТехКухня помогает быстро готовить технологические карты, расчеты и документы для общепита.",
  "primaryAction": {
    "label": "Начать бесплатно",
    "href": "/signup",
    "event": "landing_hero_primary_cta_click"
  },
  "secondaryAction": {
    "label": "Как это работает",
    "href": "#workflow",
    "event": "landing_hero_secondary_cta_click"
  },
  "visual": {
    "productUiAssetKey": "hero.productUi",
    "chefAssetKey": "hero.chef",
    "dishAssetKey": "hero.dish"
  }
}
```

Content namespaces:

* `landing.header`
* `landing.hero`
* `landing.audience`
* `landing.benefits`
* `landing.workflow`
* `landing.documents`
* `landing.standards`
* `landing.testimonials`
* `landing.finalCta`
* `seo.metadata`
* `navigation.header`
* `navigation.footer`

## 9. Schema / Validation Strategy

Рекомендованная модель: Zod as source of truth, TypeScript types inferred from Zod, JSON Schema generated for agent-readable contracts.

Почему не только TypeScript:

* TS не валидирует runtime JSON;
* агенту нужен машиночитаемый contract;
* build-time типы не ловят broken asset/icon references.

Почему не только JSON Schema:

* Zod проще в TypeScript-коде;
* удобно писать custom refinements для legal guardrails, analytics coverage и registry checks.

Где живут схемы:

```text
landing/schemas/
  common/action.schema.ts
  common/legal.schema.ts
  header.schema.ts
  hero.schema.ts
  audience.schema.ts
  benefits.schema.ts
  workflow.schema.ts
  documents.schema.ts
  standards.schema.ts
  testimonials.schema.ts
  finalCta.schema.ts
```

Validation pipeline:

1. Parse JSON.
2. Validate module schema.
3. Validate text length and required fields.
4. Validate `assetKey` against asset registry.
5. Validate `icon` against icon registry.
6. Validate CTA shape, href/action type and analytics event.
7. Validate legal-sensitive copy through denylist/allowlist rules.
8. Validate required analytics events.
9. Validate section registry references.
10. Produce structured validation report.

Legal-sensitive validation для v1 должна быть conservative lint, а не юридическая экспертиза. Запрещенные паттерны:

* «гарантируем соответствие»;
* «полная юридическая защита»;
* «автоматически соответствует всем требованиям»;
* любые абсолютные обещания без оговорки.

Разрешенная рамка:

* «помогает готовить документы с учетом требований»;
* «поддерживает работу с шаблонами»;
* «помогает контролировать внутренние стандарты».

## 10. Module Manifests / Agent Context Capsule

Manifest — основной файл, который агент читает перед правкой модуля. Он должен быть коротким, машинно читаемым и достаточным для работы без загрузки всего лендинга.

Рекомендуемый формат:

```ts
export type LandingModuleManifest = {
  id: LandingModuleId;
  name: string;
  purpose: string;
  riskLevel: "low" | "medium" | "high";
  editableByAgent: boolean;
  contentFile: string;
  schemaFile: string;
  previewRoute: string;
  owner: "product" | "design" | "engineering";
  allowedAssetKeys: LandingAssetKey[];
  allowedIconKeys: IconKey[];
  allowedVariants: string[];
  requiredAnalyticsEvents: string[];
  validationRules: Array<{
    id: string;
    severity: "error" | "warning";
    description: string;
  }>;
  dependencies: Array<{
    type: "asset" | "icon" | "theme" | "analytics" | "section" | "schema";
    key: string;
  }>;
  editableFields: string[];
  blockedFields: string[];
  notesForAgent: string[];
};
```

Agent Context Capsule для команды `landingctl inspect hero` должен возвращать:

* manifest;
* current content;
* JSON Schema;
* allowed assets/icons subset;
* required analytics events;
* validation summary;
* preview route;
* risk level and required gate.

Это решает вопрос контекста: агент работает не со всей страницей, а с капсулой конкретного модуля.

## 11. Asset Registry

Asset registry уже описан в отдельном документе пакета лендинга. Для Control Plane он становится runtime contract.

Минимальная структура:

```ts
export type LandingAsset = {
  key: LandingAssetKey;
  kind: "brand" | "photo" | "product-ui" | "decor" | "avatar" | "document-preview" | "composed";
  role: "content" | "decorative" | "ui" | "brand";
  section: LandingSectionId | "global";
  src?: string;
  component?: string;
  alt: string;
  loading: "eager" | "lazy";
  priority: boolean;
  visibility: "always" | "desktop-only" | "tablet-up" | "mobile-only" | "optional" | "theme-dependent";
  themeBehavior: "theme-neutral" | "theme-mapped" | "uses-semantic-colors";
  fallbackKey?: LandingAssetKey;
};
```

Правила:

* секции не импортируют PNG/SVG/WebP напрямую;
* content хранит только `assetKey`;
* `AssetImage` или `AssetSlot` разрешает key через registry;
* декоративные assets имеют пустой `alt`;
* hero priority assets проходят отдельный LCP check;
* missing asset key — validation error.

Generated assets:

* generated asset не публикуется напрямую в section content;
* сначала создается `GeneratedAssetCandidate`;
* после preview и manual approval ассет получает stable `assetKey`;
* registry stores `source`, `generatedCandidateId`, `provider`, `model`, `promptHash`, `provenance`, `rightsStatus`, `approvalStatus`, `storagePath`, `cdnUrl`, `rollbackAssetKey`;
* подробный pipeline описан в [AI Asset Generation Pipeline](ai-asset-generation-pipeline.md).

## 12. Icon Registry

Иконки отделены от assets. Это снижает шум в asset registry и запрещает локальные SVG-импорты внутри секций.

```ts
export type LandingIconDefinition = {
  key: IconKey;
  source: "lucide" | "custom-svg" | "inline-component";
  importName?: string;
  role: "decorative" | "semantic" | "action" | "status";
  allowedVariants: Array<"brand" | "neutral" | "success" | "warning" | "muted" | "inverse">;
  defaultVariant: "brand" | "neutral" | "success" | "warning" | "muted" | "inverse";
  themeBehavior: "uses-current-color" | "uses-semantic-colors";
  fallbackKey?: IconKey;
};
```

Правила:

* секция передает `icon: "workflow.export"` и `variant: "brand"`;
* компонент `Icon` выбирает source и применяет theme token;
* `color="#..."` и Tailwind direct color classes запрещены;
* missing icon key — validation error;
* missing optional icon with fallback — warning.

## 13. Theme Registry / Design Tokens

Theme contract должен быть отдельным boundary contract, а не набором CSS-переменных без структуры.

Минимальные группы tokens:

* `color.page`
* `color.surface`
* `color.text`
* `color.border`
* `color.brand`
* `color.action`
* `color.status`
* `color.icon`
* `gradient`
* `shadow`
* `radius`
* `spacing`
* `typography`
* `motion`
* `component.button`
* `component.card`
* `component.badge`
* `section.hero`
* `section.cta`

Темы v1:

1. `warmKitchen` — основная теплая ресторанная тема.
2. `neutralBusiness` — строгая B2B-тема для проверки отделения смысла от визуала.
3. `accessible` — повышенный контраст и более спокойные декоративные элементы.

Запреты:

* прямые hex/rgb/hsl в секциях;
* локальные градиенты в секциях;
* локальные тени вне theme contract;
* Tailwind classes прямого цвета, если они не aliases tokens;
* theme values в content files.

## 14. Section Registry

Section registry определяет страницу как композицию модулей.

```ts
export type LandingSectionRegistryItem = {
  id: LandingSectionId;
  enabled: boolean;
  order: number;
  component: string;
  contentKey: string;
  manifestKey: string;
  variant: string;
  layout: {
    desktop: string;
    tablet: string;
    mobile: string;
  };
  previewMode: "full" | "isolated" | "minimal";
  requiredAssetKeys: LandingAssetKey[];
  requiredIconKeys: IconKey[];
  requiredAnalyticsEvents: string[];
};
```

Правила:

* изменение порядка секций — medium risk;
* отключение секции — medium risk, а для `hero` и `finalCta` high risk;
* добавление новой секции требует engineering flow: schema, manifest, component, registry entry, tests;
* section registry не хранит бизнес-тексты.

## 15. Agent Operations

CLI/API surface должен быть малым и стабильным.

Основные команды:

```bash
landingctl list sections
landingctl inspect hero
landingctl read hero
landingctl patch hero --file patch.json
landingctl validate hero
landingctl validate all
landingctl preview hero
landingctl preview all
landingctl diff
landingctl rollback --module hero --to <ref>
landingctl list assets --section hero
landingctl list icons --section workflow
landingctl switch theme warmKitchen
landingctl section disable testimonials
landingctl section move workflow --after benefits
landingctl check references
landingctl assets generate --asset-key hero.chef --template hero.chef.visual --count 4
landingctl assets candidates preview <candidateId>
landingctl assets approve <candidateId> --asset-key hero.chef.v2
landingctl assets publish <candidateId>
landingctl assets replace hero.chef --with hero.chef.v2
landingctl assets provenance hero.chef.v2
```

API equivalents:

* `GET /landing/modules`
* `GET /landing/modules/{id}/context`
* `GET /landing/modules/{id}/content`
* `PATCH /landing/modules/{id}/content`
* `POST /landing/validate`
* `POST /landing/preview`
* `GET /landing/diff`
* `POST /landing/rollback`
* `GET /landing/assets?section=hero`
* `GET /landing/icons?section=workflow`

Для v1 достаточно CLI. API нужен, если появится UI/control panel.

## 16. CLI/API Proposal

Patch format должен быть JSON Patch или ограниченный merge patch. Рекомендация: JSON Patch для точного diff.

```json
[
  {
    "op": "replace",
    "path": "/title",
    "value": "Технологические карты без хаоса в таблицах"
  }
]
```

Команда:

```bash
landingctl patch hero --file hero.patch.json --validate --preview
```

Выход validation report:

```json
{
  "ok": false,
  "module": "hero",
  "errors": [
    {
      "rule": "cta.analytics.required",
      "path": "/primaryAction/event",
      "message": "CTA must use a registered analytics event."
    }
  ],
  "warnings": []
}
```

Ограничение: CLI не должен иметь команду `edit raw file` как штатный путь. Raw edits остаются engineering escape hatch.

## 17. Claim Maturity Model

Landing Control Plane должен валидировать не только форму content modules, но и зрелость сильных продуктовых claims. Лендинг может описывать Target Product, но не должен выдавать roadmap/vision capability за уже доступную функцию.

Источник maturity:

* [Product Vision](product/PRODUCT_VISION_v0.1.md)
* [Capability Roadmap](product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)
* [Product Scope Alignment Audit](лэндинг/product-consistency-audit.md)
* [MVP / Target Product / Landing Traceability Matrix](лэндинг/mvp-landing-traceability-matrix.md)

Базовый тип:

```ts
type ClaimMaturity =
  | "implemented_now"
  | "mvp_scope"
  | "mvp_hypothesis"
  | "alpha_next"
  | "roadmap_claim"
  | "target_product_claim"
  | "vision_claim"
  | "decision_needed"
  | "forbidden_claim"
  | "unsupported_claim";
```

Рекомендуемый content contract fragment:

```ts
type LandingClaim = {
  id: string;
  text: string;
  maturity: ClaimMaturity;
  sourceRefs: string[];
  requiresDisclaimer?: boolean;
  ownerApproved?: boolean;
};
```

Validation rules:

* `implemented_now` допустим как current feature.
* `mvp_scope` допустим как MVP/current capability.
* `mvp_hypothesis` допустим как проверяемая MVP-гипотеза, но не как доказанный production-result.
* `alpha_next` не должен попадать в hero без owner approval.
* `roadmap_claim` требует явной future/roadmap маркировки.
* `target_product_claim` допустим как продуктовая перспектива, но не должен звучать как current availability.
* `vision_claim` обычно запрещен для core landing без отдельного owner approval.
* `decision_needed` блокирует публикацию до решения владельца продукта.
* `forbidden_claim` всегда validation error.
* `unsupported_claim` блокирует публикацию до фиксации основания в Product Vision, Capability Roadmap или owner decision.

Governance rule for over-MVP claims:

1. Если claim не входит в MVP, validate сначала проверяет Product Vision and Capability Roadmap.
2. Если claim закреплен как `roadmap_claim`, `target_product_claim` или `vision_claim`, он может оставаться в лендинге при корректной формулировке.
3. Если claim не закреплен нигде, он получает `unsupported_claim`.
4. Если claim относится к forbidden-zone, он блокируется всегда, даже если похож на target-product value proposition.

True drift после refine:

* claim отсутствует в MVP, Product Vision, Roadmap and owner decisions и получает `unsupported_claim`;
* claim противоречит human-review boundary;
* claim обещает legal/compliance guarantee;
* claim выдает roadmap/vision за current feature;
* claim не имеет maturity status.

## 18. Risk Model

| Риск | Операции | Gate |
| --- | --- | --- |
| Low | title, description, CTA label, alt text, SEO description, порядок карточек внутри секции | schema validation + diff; preview optional, но рекомендован |
| Medium | asset key, icon key, section variant, section enable/disable, section order, theme switch, document types | validation + reference check + preview + user confirmation |
| High | JSX/TSX, base components, theme contract, asset contract, schema contract, layout primitives, new section type | engineering task + tests/build + visual review + explicit approval |

AI asset generation additions:

* Low: inspect providers/templates, draft prompt, generate candidate without publishing, reject candidate.
* Medium: approve candidate, publish approved asset, replace asset key, edit prompt template, switch provider for an asset kind.
* High: enable auto-publish, change provider credentials, change safety policy, publish assets with people/logos/brands/reference images, change storage/CDN policy.

Особые правила:

* `standards` всегда минимум medium risk из-за юридически чувствительного текста.
* `hero` title/CTA labels low risk, но visual composition и layout variant medium/high.
* Отключение `hero`, `header`, `finalCta` — high risk.
* Fake testimonials in production — validation error.

## 19. Preview / Diff / Rollback Workflow

Рабочий контур:

1. Агент получает задачу.
2. Агент определяет `moduleId`.
3. Агент вызывает `landingctl inspect <moduleId>`.
4. CLI возвращает context capsule.
5. Агент готовит JSON Patch.
6. CLI применяет patch во временную рабочую область.
7. CLI запускает schema validation и reference validation.
8. CLI показывает structured diff.
9. CLI собирает isolated preview для модуля и full-page preview при medium/high risk.
10. Пользователь подтверждает.
11. Изменение фиксируется в Git.
12. Rollback выполняется по модулю или всему landing content set.

For generated assets:

* preview must include candidate gallery;
* medium/high changes must show old asset vs candidate;
* registry metadata diff and section content diff are separate;
* old asset is archived, not deleted immediately;
* rejected candidates are cleaned up only by retention policy.

Хранение версий:

* Git commit на каждую подтвержденную группу изменений;
* commit message содержит module id и risk level;
* content version внутри JSON увеличивается при успешном patch;
* rollback модуля можно делать через `git checkout <ref> -- landing/content/ru/hero.json`, но штатно через `landingctl rollback`.

Rollback уровни:

* module rollback — вернуть один content file;
* registry rollback — только high-risk engineering flow;
* full landing rollback — revert commit или revert range.

## 20. Recommended File Structure

Рекомендуемая структура для будущей реализации:

```text
landing/
  page.tsx
  landing.config.ts

  content/
    ru/
      header.json
      hero.json
      audience.json
      benefits.json
      workflow.json
      documents.json
      standards.json
      testimonials.json
      finalCta.json
      seo.json
      navigation.json

  schemas/
    common/
      action.schema.ts
      legal.schema.ts
      seo.schema.ts
    header.schema.ts
    hero.schema.ts
    audience.schema.ts
    benefits.schema.ts
    workflow.schema.ts
    documents.schema.ts
    standards.schema.ts
    testimonials.schema.ts
    finalCta.schema.ts

  manifests/
    header.manifest.ts
    hero.manifest.ts
    audience.manifest.ts
    benefits.manifest.ts
    workflow.manifest.ts
    documents.manifest.ts
    standards.manifest.ts
    testimonials.manifest.ts
    finalCta.manifest.ts

  registries/
    content.registry.ts
    schema.registry.ts
    section.registry.ts
    asset.registry.ts
    icon.registry.ts
    theme.registry.ts
    analytics.registry.ts

  sections/
    HeaderSection/
    HeroSection/
    AudienceSection/
    BenefitsSection/
    WorkflowSection/
    DocumentsSection/
    StandardsSection/
    TestimonialsSection/
    FinalCtaSection/

  components/
    Button/
    Card/
    Icon/
    AssetImage/
    SectionShell/
    MetricCard/
    DocumentCard/
    StepCard/

  theme/
    theme.contract.ts
    themes/
      warmKitchen.theme.ts
      neutralBusiness.theme.ts
      accessible.theme.ts

  tools/
    landingctl/
      index.ts
      commands/
      validators/
      preview/
```

Если проект останется на vanilla frontend, структура меняется технически, но границы сохраняются:

* `content/*.json`;
* `schemas/*.js`;
* `registries/*.js`;
* `sections/*.js`;
* `landingctl` как Node/Python CLI.

## 21. Implementation Phases

### Phase 0 — Audit

Цель: подтвердить фактический stack и scope.

Deliverables:

* audit текущих frontend файлов;
* решение: отдельный landing app или расширение текущего app;
* список существующих hardcoded texts/styles/assets;
* список рисков миграции.

Gate: без реализации лендинга до принятия frontend stack decision.

### Phase 1 — Contracts

Сделать минимальный contract layer:

* `LandingAction`;
* content schemas;
* theme contract;
* asset registry;
* icon registry;
* section registry;
* analytics registry;
* module manifests.

Gate: `landingctl validate all` может проверить content/registries без UI.

### Phase 2 — Data-Driven Landing

Собрать лендинг из секций:

* компоненты читают content DTO;
* секции не содержат бизнес-тексты;
* assets/icons идут только через resolvers;
* цвета идут через theme tokens.

Gate: visual smoke + validation + no direct asset imports in sections.

### Phase 3 — Agent Tooling

Добавить CLI:

* inspect;
* read;
* patch;
* validate;
* diff;
* preview;
* rollback;
* list assets/icons.

Gate: агент может поменять hero title через JSON Patch и получить validation/diff.

### Phase 4 — Preview and Governance

Добавить:

* isolated module preview;
* full-page preview;
* risk gates;
* required user confirmation for medium/high risk;
* Git commit conventions.

Gate: medium-risk change cannot be finalized without preview and confirmation.

### Phase 5 — Optional CMS / Admin UI

Добавлять только если Git-backed flow станет узким местом.

Требование: CMS должна быть source adapter, а не владельцем архитектуры. Секции продолжают читать DTO одного формата.

### Phase 6 — AI Asset Generation Pipeline

Добавлять после базового Asset Registry:

* provider research and ADR;
* `GenerationProviderRegistry`;
* `PromptTemplateRegistry`;
* `GeneratedAssetCandidate` schema;
* candidate storage and approved asset storage;
* approval workflow;
* `landingctl assets generate/list/preview/approve/reject/publish/replace/provenance`;
* provenance and rights gates;
* billing/rate-limit guardrails;
* rollback and rejected-candidate cleanup.

## 22. Acceptance Criteria

Blueprint и будущая реализация считаются достаточными, если:

1. Агент определяет модуль через section/content registry.
2. Агент получает контракт модуля через manifest/context capsule.
3. Агент читает только нужный content, schema и allowed keys.
4. Тексты не живут в JSX/TSX секций.
5. Цвета не хардкодятся в секциях.
6. Ассеты не импортируются напрямую в секциях.
7. Asset keys и icon keys валидируются по registry.
8. CTA валидируются по action schema и analytics registry.
9. Content changes и engineering changes имеют разные risk gates.
10. Пользователь видит diff перед фиксацией.
11. Preview собирается для medium/high risk изменений.
12. Rollback работает на уровне модуля.
13. Новая секция требует manifest, schema, content, registry entry и component.
14. Новая тема добавляется через theme registry без изменения секций.
15. Новая аудитория или document type добавляется через content + registry keys без layout rewrite.
16. CMS можно подключить позже как source adapter.
17. Legal-sensitive copy не проходит без cautious wording.
18. Missing analytics event для CTA является validation error.
19. Generated assets never bypass candidate preview and manual approval.
20. Published generated assets have provenance, rights status and rollback asset key.

## 23. Open Questions

1. Будущий landing frontend должен быть отдельным Next/React app или частью текущего Python-приложения?
2. Нужна ли мультиязычность сразу или только `ru`?
3. Какие CTA реально существуют в продукте на старте: signup, demo request, sample download, pricing?
4. Будут ли реальные отзывы к запуску или нужен production-safe placeholder режим без fake social proof?
5. Где будут физически храниться optimized images: repo, object storage, CDN?
6. Нужен ли preview на отдельном домене или достаточно локального/branch preview?
7. Кто утверждает medium/high risk изменения?
8. Требуется ли audit log поверх Git history?
9. Нужно ли агенту менять copy только через JSON Patch или можно разрешить structured natural-language operations?
10. Какие analytics provider и naming convention будут финальными?
11. Какой image generation provider выбрать для v1?
12. Где хранить generated asset candidates и approved assets?
13. Разрешить ли people/reference images в v1?
14. Кто имеет право approve and publish generated assets?

## 24. Agent Recommendations

Что избыточно для v1:

* полноценная CMS;
* визуальный page builder;
* произвольные layout-конструкторы;
* API server для control plane до появления admin UI;
* сложная ролевая модель внутри landing tooling.

Что стоит упростить:

* начать с JSON content, а не YAML/TS content modules;
* сделать один CLI вместо CLI + API + admin UI;
* начать с isolated preview и full-page preview, без сложного publish workflow;
* legal validation сделать rule-based lint, а не пытаться автоматизировать экспертизу.

Что принять сразу:

* content не живет в JSX/TSX;
* Zod + generated JSON Schema;
* asset/icon/section/theme/analytics registries;
* module manifest как Agent Context Capsule;
* risk gates;
* Git-backed rollback.

Что отложить:

* headless CMS;
* visual admin panel;
* A/B testing registry;
* personalization;
* multi-tenant content workflow;
* external asset DAM integration.

Главный архитектурный риск: построить слишком гибкую CMS вместо управляемого landing control plane. Для текущей стадии правильнее сделать узкую контрактную систему, которая закрывает реальные изменения лендинга и не дает агенту обходить границы.
