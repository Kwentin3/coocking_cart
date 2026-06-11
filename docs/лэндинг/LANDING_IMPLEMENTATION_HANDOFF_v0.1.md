# Landing Implementation Handoff v0.1

Статус: инженерный handoff для будущей верстки публичного лендинга «ТехКухня».
Дата: 2026-06-11.
Область: архитектура реализации, layout system, responsive strategy, design tokens, section/component/content contracts, asset/icon/CTA contracts, claim maturity guardrails, validation and acceptance.

Связанные документы:

* [PRD лендинга](LANDING_PRD_v0.1.md)
* [Визуальный и технический контракт](LANDING_VISUAL_TECH_CONTRACT_v0.1.md)
* [Visual Asset Layering Contract](LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md)
* [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
* [Product Vision](../product/PRODUCT_VISION_v0.1.md)
* [Capability Roadmap](../product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)
* [MVP / Target Product / Landing Traceability Matrix](mvp-landing-traceability-matrix.md)
* [Landing Showcase Mode Strategy](LANDING_SHOWCASE_MODE_STRATEGY_v0.1.md)
* [Product Scope Alignment Audit](product-consistency-audit.md)
* [Landing Control Plane Blueprint](../landing-control-plane-blueprint.md)
* [AI Asset Generation Pipeline](../ai-asset-generation-pipeline.md)
* [Refine Analysis Report](refine-analysis-report.md)

## 1. Executive Summary

Реализуем публичный лендинг «ТехКухня» как витрину Target Product, а не MVP-only страницу. MVP остается проверочным срезом; лендинг может показывать целевой продукт, если claims закреплены в Product Vision / Capability Roadmap and не звучат как already available без подтверждения.

Архитектурный стиль: контрактная композиция управляемых модулей.

Главные запреты:

* не хардкодить тексты, цвета, ассеты, иконки, CTA, analytics events, breakpoints and layout sizes внутри секций;
* не использовать прямые hex/rgb/hsl, прямые пути `/images/...`, прямые импорты PNG/SVG/WebP в секциях;
* не использовать локальные magic numbers для `gap`, `padding`, `width`, `height`, `top`, `left`, `z-index`, `radius`, `shadow`;
* не превращать лендинг в MVP-safe copy;
* не публиковать `forbidden_claim` or `unsupported_claim`;
* не начинать CMS, `landingctl`, AI Asset Generation Pipeline or backend product implementation in this slice.

После этого документа можно начинать engineering scaffold лендинга: contracts, tokens, registries, schemas, primitives and section skeletons. Production-copy, final CTA, legal wording, export/download claims and roadmap UI mockups требуют owner decision before public launch.

## 2. Implementation Goals

Цели реализации:

1. Data-driven landing: секции читают content DTO, а не хранят бизнес-тексты.
2. Theme-driven visual system: цвета, тени, радиусы, типографика, spacing and motion идут через semantic tokens.
3. Registry-driven assets/icons: изображения and иконки доступны только через keys and resolvers.
4. Modular isolated sections: секция не зависит от соседних секций and может быть выключена, переставлена or заменена через config.
5. Responsive layout: mobile-first, CSS-native, с container queries, `clamp()`, `minmax()`, aspect-ratio and layout variants.
6. Agent-friendly content management: у каждого модуля есть manifest, schema, allowed assets/icons/actions and validation surface.
7. Future Landing Control Plane compatibility: структура готова к `landingctl inspect/read/patch/validate/preview/diff/rollback`.
8. Claim Maturity safety: спорные product claims не решаются в UI, но UI умеет hidden/disabled/roadmap presentation.

## 3. Non-Goals

В этом handoff не проектируется:

* полноценная CMS;
* AI Asset Generation Pipeline implementation;
* `landingctl` implementation;
* production-copy freeze;
* юридическая экспертиза claims;
* MVP-only лендинг;
* backend продукта;
* изменение текущего Demo MVP chat workspace;
* миграция существующего `app/static/app.js` на framework только ради лендинга.

## 4. Current Repo Assumptions

Фактический runtime на момент handoff:

* текущий frontend demo: `app/templates/index.html`, `app/static/app.js`, `app/static/styles.css`;
* static serving and HTTP entrypoint: `app/main.py`;
* отдельного production landing frontend в коде пока нет;
* package/bundler files вроде `package.json`, `vite.config.*`, `next.config.*`, `tsconfig.json` не обнаружены;
* в документации уже есть target architecture для будущего Landing Control Plane.

Практический вывод: первая реализация лендинга должна выбрать один из двух путей:

1. отдельный landing frontend/app, если принимается framework/build pipeline;
2. contract-driven static implementation, если проект остается на текущем Python/static runtime.

Оба пути обязаны сохранить границы: content, schemas, registries, theme/layout tokens, sections and primitives отделены друг от друга.

## 5. Target Architecture

Целевая структура для framework-oriented implementation:

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

  schemas/
    common/
      action.schema.ts
      claim.schema.ts
      asset.schema.ts
      icon.schema.ts
      richText.schema.ts
    header.schema.ts
    hero.schema.ts
    audience.schema.ts
    benefits.schema.ts
    workflow.schema.ts
    documents.schema.ts
    standards.schema.ts
    testimonials.schema.ts
    finalCta.schema.ts
    seo.schema.ts

  registries/
    section.registry.ts
    asset.registry.ts
    icon.registry.ts
    theme.registry.ts
    analytics.registry.ts
    cta.registry.ts

  theme/
    theme.contract.ts
    layout.contract.ts
    typography.contract.ts
    motion.contract.ts
    themes/
      warmKitchen.theme.ts
      neutralBusiness.theme.ts
      accessible.theme.ts

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
    primitives/
      Button/
      Card/
      Icon/
      AssetImage/
      SectionShell/
      Container/
      ResponsiveGrid/
      Stack/
      Cluster/
      Split/
      Layer/
      FloatingPanel/
      AspectFrame/
      Badge/
    landing/
      HeroVisual/
      MetricCard/
      StepCard/
      DocumentCard/
      AudienceCard/
      BenefitCard/
      StandardsBadge/
      TestimonialCard/

  manifests/
    header.manifest.json
    hero.manifest.json
    audience.manifest.json
    benefits.manifest.json
    workflow.manifest.json
    documents.manifest.json
    standards.manifest.json
    testimonials.manifest.json
    finalCta.manifest.json

  lib/
    resolveTheme.ts
    resolveAsset.ts
    resolveIcon.ts
    validateLandingContent.ts
    resolveCta.ts
    claimMaturity.ts
```

Static-runtime adaptation, если framework не вводится:

```text
app/
  landing/
    content/ru/*.json
    schemas/*.js
    registries/*.js
    theme/*.css
    theme/*.js
    sections/*.js
    components/*.js
    manifests/*.json
  templates/
    landing.html
  static/
    landing/
      landing.css
      landing.js
      assets/
```

В static-варианте `landing.js` не должен стать новым монолитом. Он должен только bootstrap resolved config, mount sections and wire events.

## 6. Domain Boundaries

| Domain | Owns | Files | May depend on | Must not depend on |
| --- | --- | --- | --- | --- |
| Product/content | Texts, lists, labels, SEO fields, section data | `content/ru/*.json` | schemas, action ids, asset/icon keys, claim maturity ids | JSX/TSX, CSS selectors, physical asset paths |
| Visual/theme | Color, typography, radius, shadow, motion semantic tokens | `theme/*.contract.ts`, `themes/*.theme.ts` | design decisions, accessibility constraints | section content, business claims |
| Layout | Container widths, grid tracks, spacing, ratios, z-index scale, responsive variants | `theme/layout.contract.ts`, layout primitives | theme tokens | product copy, physical image paths |
| Asset | Asset metadata, alt, roles, loading, visibility, rights state | `asset.registry.ts` | asset files, generated asset metadata | section implementation details |
| Icon | Icon keys, sources, roles, variants | `icon.registry.ts`, `Icon` primitive | icon library/custom icon definitions | local colors, section-specific SVG imports |
| CTA/action | Action ids, labels, href/modal/form/scroll/disabled, analytics event, maturity | `cta.registry.ts`, content action refs | analytics registry, claim maturity | section-local href/text |
| Analytics | Event names and required bindings | `analytics.registry.ts` | CTA ids, section ids | arbitrary section event strings |
| Claim maturity | Claim enum, source refs, render policy | `claimMaturity.ts`, content claim fields | Product Vision, Capability Roadmap, traceability docs | visual styling decisions |
| Section composition | Section order, enabled flags, variants, content keys | `section.registry.ts`, `landing.config.ts` | content ids, section components | business copy values |
| Runtime rendering | Pure render from DTOs and resolvers | `sections/*`, `components/*` | resolved DTOs, tokens, resolvers | domain rules, API calls, storage mutation |

Rule: UI components receive data and emit user intent events. They do not decide product maturity, pricing, legal wording, or business availability.

## 7. Layout System

Layout primitives:

* `Container`: page width and inline padding.
* `SectionShell`: vertical rhythm, background variant, section landmark.
* `ResponsiveGrid`: tokenized grid variants.
* `Stack`: vertical spacing between children.
* `Cluster`: wrapping inline groups for nav, CTA rows, badges.
* `Split`: two-zone composition for hero and document demo.
* `Layer`: named layer inside visual compositions.
* `FloatingPanel`: tokenized floating card placement.
* `AspectFrame`: stable ratio wrapper for images, previews and UI mockups.

Minimal contract:

```ts
type LayoutTokens = {
  viewport: {
    min: string;
    mobile: string;
    tablet: string;
    laptop: string;
    desktop: string;
    wide: string;
  };
  container: {
    maxWidth: string;
    paddingInline: string;
    narrowMaxWidth: string;
    wideMaxWidth: string;
  };
  grid: {
    columns: number;
    gap: string;
    denseGap: string;
    relaxedGap: string;
  };
  section: {
    paddingBlock: string;
    paddingBlockCompact: string;
    paddingBlockHero: string;
  };
  ratio: {
    heroVisual: string;
    cardImage: string;
    documentPreview: string;
    avatar: string;
  };
  zIndex: {
    base: number;
    raised: number;
    overlay: number;
    header: number;
    modal: number;
  };
};
```

Implementation rule: numeric values are allowed only in token/contract files. Sections use variants and token names.

Example:

```tsx
<SectionShell spacing="hero" background="hero">
  <Container width="wide">
    <ResponsiveGrid variant="heroSplit">
      ...
    </ResponsiveGrid>
  </Container>
</SectionShell>
```

## 8. Responsive Strategy

Default strategy:

* mobile-first;
* CSS Grid and Flexbox before JS;
* container queries before global viewport media queries for section internals;
* breakpoint values only in layout tokens;
* typography through fluid scale / `clamp()`;
* spacing through fluid scale / `clamp()`;
* grids through named variants using `repeat()`, `minmax()`, `auto-fit` / `auto-fill`;
* images through registry metadata: intrinsic size, aspect ratio, `sizes`, loading and priority;
* decorative assets through `visibility` rules;
* complex UI mockups on mobile simplify, not overflow.

Density modes:

```text
compact      mobile and narrow containers
comfortable  tablet and regular desktop
expanded     wide desktop
wide         large viewport with constrained content and more breathing room
```

Section responsive contract:

```ts
type ResponsiveMode = "compact" | "comfortable" | "expanded" | "wide";

type SectionLayoutVariant = {
  mode: ResponsiveMode;
  gridVariant: string;
  assetVisibility: Record<LandingAssetKey, LandingAssetVisibility>;
  typographyScale: string;
  spacingScale: string;
};
```

JavaScript measurement is allowed only for cases CSS cannot solve: canvas/WebGL, unusual overlay math, preview tooling or real runtime measurement. Normal landing layout must not use viewport measuring loops.

## 9. Fluid Tokens And No Magic Numbers

Magic number: any local layout/visual value in a section/component that is not expressed through token, variant or registry metadata.

Forbidden:

```tsx
<div className="mt-[37px] w-[612px] rounded-[19px]" />
<div style={{ top: 41, left: 113, zIndex: 999 }} />
```

Allowed:

```tsx
<FloatingPanel slot="heroMetric" elevation="floating">
  ...
</FloatingPanel>
```

Token example:

```ts
const layoutTokens = {
  section: {
    heroPaddingBlock: "clamp(3.5rem, 8vw, 7rem)",
  },
  grid: {
    gap: "var(--space-6)",
  },
  hero: {
    metricOffset: "var(--hero-layer-offset-metric)",
  },
};
```

Pull request rule: if a reviewer sees an arbitrary number in a section, the change fails unless the value is in a contract file and has a semantic name.

## 10. Theme / Design Tokens

Token groups:

* `color.page`, `color.surface`, `color.text`, `color.border`;
* `color.brand`, `color.action`, `color.status`, `color.icon`;
* `gradient.*` only as semantic theme tokens;
* `typography.family`, `typography.size`, `typography.weight`, `typography.lineHeight`;
* `space.*` and section spacing scale;
* `radius.*`;
* `shadow.*`;
* `motion.duration`, `motion.easing`;
* `layout.*`;
* `component.button`, `component.card`, `component.badge`, `component.input`;
* `section.hero`, `section.documents`, `section.cta`.

Rules:

* sections never use direct colors;
* components do not accept arbitrary `color`, `background`, `shadow`, `radius`;
* component variants map to semantic tokens;
* theme can change visual mood without changing section JSX;
* high contrast and reduced motion must be supported by tokens, not by one-off section overrides.

## 11. Section Contracts

Common section props:

```ts
type LandingSectionProps<TContent> = {
  content: TContent;
  assets: LandingAssetResolver;
  icons: LandingIconResolver;
  actions: LandingActionResolver;
  analytics: LandingAnalytics;
  theme: LandingThemeContract;
  layout: LayoutTokens;
};
```

Section matrix:

| Section | Purpose | Required content | Assets/icons | CTA/analytics | Responsive behavior | Claim maturity concerns |
| --- | --- | --- | --- | --- | --- | --- |
| Header | Navigation and brand access | logo key, nav items, login action, primary action | `brand.logo`, nav icons | nav click, login, primary CTA | sticky/collapsible; mobile drawer | signup/pricing links may be `decision_needed` |
| Hero | Main positioning and conversion | title, description, primary/secondary actions, trust items, visual config | `hero.productUi`, `hero.chef`, `hero.dish`, feature icons | hero primary/secondary CTA | split desktop, stacked compact, simplified visual | target claims allowed; no current availability overclaim |
| Audience | Segment clarity | section title, audience items | audience photos/icons | optional audience click | 4-col, 2-col, 1-col | production/large food industry may be `decision_needed` |
| Benefits | Value proposition | benefit items | benefit icons | optional | 4-col to 2-col/1-col | cost/control wording must avoid full current cost engine |
| Workflow | Process explanation | ordered steps | workflow icons | step interaction optional | horizontal chain to vertical timeline | approval/export steps need roadmap/human-review wording |
| Documents Demo | Output preview | document types, dish card, calculation sample, output document card | document preview, dish image, status icons | document type click, sample CTA | split/table desktop, simplified cards mobile | DOCX/export/calculation cards are roadmap unless implemented |
| Standards | Trust and normative caution | cautious copy, standard list, disclaimer | standard icons, optional decor | standard info optional | readable list/cards | legal guarantee forbidden |
| Testimonials | Social proof | testimonials or placeholder mode | avatars, quote icon | carousel/click optional | carousel or stacked cards | fake testimonials as real forbidden |
| Final CTA | Conversion close | title, description, primary/secondary actions, terms | CTA decor, action icons | final CTA, demo request | centered/compact with optional decor | free trial/onboarding/pricing may be `decision_needed` |

Every section must define states:

* `ready`: valid content and registered dependencies;
* `empty`: optional list has no items and section can hide or show configured fallback;
* `invalid`: schema/reference validation failed before render;
* `disabled`: section disabled through section registry.

No section should silently render partial invalid content.

## 12. Component Contracts

### Button

```ts
type ButtonProps = {
  variant: "primary" | "secondary" | "ghost" | "outline";
  size: "sm" | "md" | "lg";
  action: LandingAction;
  iconLeft?: IconKey;
  iconRight?: IconKey;
  state?: "idle" | "disabled" | "busy";
};
```

Forbidden props: `color`, `background`, `style`, raw `href`, raw analytics event.

Accessibility: semantic `button` for actions, anchor for navigation; visible focus; busy/disabled state explicit.

### Card

```ts
type CardProps = {
  variant: "default" | "elevated" | "soft" | "interactive" | "metric" | "document";
  density?: "compact" | "comfortable";
};
```

Forbidden props: arbitrary shadow, radius, border color, local padding.

### Icon

```ts
type IconProps = {
  name: IconKey;
  variant?: "brand" | "neutral" | "success" | "warning" | "muted" | "inverse";
  size?: "sm" | "md" | "lg";
  decorative?: boolean;
  label?: string;
};
```

Icon renders only registered icons. No direct SVG imports in sections.

### AssetImage

```ts
type AssetImageProps = {
  assetKey: LandingAssetKey;
  fit?: "cover" | "contain";
  priority?: boolean;
  sizesToken?: string;
};
```

`AssetImage` resolves `src`, `alt`, `width`, `height`, `role`, `loading`, `visibility`, `aspectRatio` from Asset Registry.

### Layout Primitives

| Component | Allowed inputs | Forbidden |
| --- | --- | --- |
| `SectionShell` | `spacing`, `background`, `as`, `id` | raw padding, raw background |
| `Container` | `width`, `align` | raw max-width, raw padding |
| `ResponsiveGrid` | `variant`, `density` | raw grid-template in section |
| `Stack` | `gap`, `align` | raw margin-top chains |
| `Cluster` | `gap`, `justify`, `wrap` | one-off flex values |
| `AspectFrame` | `ratio`, `variant` | local height hacks |
| `FloatingPanel` | `slot`, `elevation`, `visibility` | absolute offsets outside tokens |

### Landing Components

`MetricCard`, `DocumentCard`, `StepCard`, `AudienceCard`, `BenefitCard`, `StandardsBadge`, `TestimonialCard` receive DTOs and emit intent events. They do not fetch data, compute claim maturity, or contain business rules.

## 13. Content Module Strategy

Recommended source format: JSON for v1.

Reasons:

* machine patch-friendly for agents;
* strict diff;
* no code execution;
* schema validation straightforward;
* can generate JSON Schema from Zod/TypeScript schemas later.

Content rules:

* stable `id` per content entity;
* stable item ids inside arrays;
* text max lengths enforced by schema;
* rich text disabled by default; if needed, use constrained blocks, not raw HTML;
* locale path starts with `content/ru/`;
* fallback exists for optional sections only;
* production testimonials require `isReal: true` and source approval;
* placeholder testimonials must be hidden or clearly internal before production.

Example:

```json
{
  "id": "landing.hero",
  "locale": "ru",
  "version": 1,
  "title": "Технологические карты и расчеты для общепита",
  "description": "Target Product storefront copy goes here.",
  "primaryActionId": "demo.request",
  "secondaryActionId": "sample.project.view",
  "claimRefs": ["claim.target.techcards", "claim.roadmap.cost"],
  "visual": {
    "layoutKey": "hero.targetProduct.v1",
    "productUiAssetKey": "hero.productUi",
    "chefAssetKey": "hero.chef",
    "dishAssetKey": "hero.dish"
  }
}
```

## 14. Asset / Icon Strategy

Asset rules:

* section content stores asset keys only;
* asset registry owns physical path, dimensions, alt, role, loading, visibility, theme behavior, rights status, asset kind, background mode, layer role, z-slot, overlap policy and safe area;
* decorative assets use empty alt and are hidden from screen readers;
* hero critical assets may be `priority`, below-fold assets lazy;
* mobile may hide or swap decorative assets through registry visibility rules;
* generated assets require approved/published status from AI Asset Generation Pipeline before registry use.
* `cutout` and `edgeDecor` assets require transparent background metadata.
* `contentImage` and `documentPreview` assets usually use embedded backgrounds.
* hero layer order stays inside `HeroVisual`; final CTA brand band protects text/CTA safe area.

Icon rules:

* simple pictograms render through `Icon` and `IconKey`;
* icon color comes from semantic variant/currentColor;
* no local SVG import in sections;
* unknown icon key is validation error.

## 15. CTA / Action Contract

<!-- STICKY-ACTION-POLICY:
CTA типа signup/pricing/export/MVP-entry не вырезаются из registry или content modules.
Секции получают resolved action state; visibility решается через landing mode, maturity и owner gates.
-->

CTA is not local section text + href. CTA is a registry-backed action.

```ts
type LandingAction = {
  id: string;
  label: string;
  href?: string;
  kind: "link" | "modal" | "form" | "scroll" | "disabled";
  analyticsEvent: string;
  maturity: ClaimMaturity;
  enabled: boolean;
  visibility: "visible" | "disabled" | "hidden";
  fallbackActionId?: string;
  ownerApproved?: boolean;
};
```

Action rules:

* `enabled: false` renders disabled state or fallback, not a broken link;
* `decision_needed` action cannot be primary in production without owner approval;
* `roadmap_claim` action cannot look available-now;
* every action has analytics event;
* every action has feedback: navigation, modal open, form state, scroll focus, or disabled explanation.
* future/commercial actions stay in the registry even when hidden or disabled.
* section code must not remove or invent CTA; it receives action ids from content and resolved state from the action layer.

Initial action candidates:

| Action id | Suggested kind | Maturity | Notes |
| --- | --- | --- | --- |
| `demo.request` | form/modal/link | `mvp_scope` / `implemented_now` if route exists | Safest primary until onboarding decision. |
| `sample.project.view` | link/modal | `mvp_scope` | Must show project/draft, not final legal document. |
| `signup.freeStart` | link | `decision_needed` | Needs real onboarding/free plan. |
| `pricing.view` | link | `decision_needed` | Needs pricing model. |
| `docx.download` | link | `roadmap_claim` | Disabled/hidden until export exists. |
| `nav.login` | link | `decision_needed` / `mvp_scope` after URL approval | Compact service entry into current MVP/test contour; not a primary marketing CTA. |

### Showcase Mode And Action Visibility

Current landing mode is `showcase`: Target Product storefront without open SaaS launch. The page may explain future product value, but actions that imply real commercial availability must be controlled by policy.

The action boundary should be:

```text
raw Action Registry
  + Landing Mode
  + Claim Maturity
  + Owner Gates
  + real function availability
  -> resolved LandingAction model for sections
```

Rules:

* sections do not decide whether signup, pricing, export, demo or MVP entry should appear;
* sections do not delete future actions;
* sections render resolved actions only;
* resolver/config decides `enabled`, `hidden`, `disabled`, `internal_only` or `owner_gated` semantics;
* current TypeScript surface may keep `visible | disabled | hidden` as render-level values, while resolver keeps richer policy states internally;
* `showcase` may show target-product copy and safe sample/demo actions;
* `beta` may enable limited request/demo flows after owner decision;
* `launch` may enable signup/pricing/commercial CTA only after real flows exist;
* MVP entry is a separate service action in the header, not a primary conversion CTA.

Current implementation status:

* `landingModeConfig` defines default `showcase` mode and owner/function gates;
* `resolveActionRegistry()` converts raw registry actions into resolved render actions;
* `getLandingPageModel()` passes resolved actions to sections and keeps raw actions as `rawActions`;
* `header.json` already points to `loginActionId: "nav.login"`;
* `nav.login` is currently hidden, `decision_needed` and owner-gated until MVP Entry Gate is closed;
* sections remain dumb renderers and must not implement local action visibility policy.

## 16. Claim Maturity Guardrails

Accepted enum:

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

Render policy:

| Maturity | Render policy |
| --- | --- |
| `implemented_now` | May render as current feature if no legal risk. |
| `mvp_scope` | May render as MVP/current capability; use project/draft wording where relevant. |
| `mvp_hypothesis` | May render as checked/tested hypothesis only with cautious wording. |
| `alpha_next` | Hidden from hero unless owner-approved. |
| `roadmap_claim` | May render as roadmap/future; never as active available-now CTA. |
| `target_product_claim` | May render as Target Product storefront value; avoid current availability. |
| `vision_claim` | Usually hidden from core landing or visually marked as vision/future. |
| `decision_needed` | Hidden/disabled until owner approval. |
| `forbidden_claim` | Never render. Validation error. |
| `unsupported_claim` | Never render without owner override and source update. |

UI does not decide maturity. UI reads maturity from content/claim registry and applies render policy.

## 17. Analytics Contract

Analytics registry owns event names.

Required event groups:

* hero primary/secondary CTA;
* final CTA;
* nav clicks;
* audience card click;
* document type click;
* sample project view/download click;
* standards info click if interactive;
* testimonial carousel/click if interactive;
* form open/submit/success/error if demo request exists;
* disabled CTA click if user-facing disabled explanation is shown.

Naming convention:

```text
landing_<section>_<element>_<action>
```

Examples:

```text
landing_hero_primary_cta_click
landing_documents_type_click
landing_sample_project_view_click
landing_demo_request_submit
landing_disabled_cta_click
```

Sections must not hardcode event strings.

## 18. Accessibility

Requirements:

* one H1;
* heading levels do not skip for visual styling;
* semantic landmarks: header, main, section, footer where applicable;
* buttons for actions, anchors for navigation;
* keyboard navigation through all interactive elements;
* visible focus from theme tokens;
* disabled and busy states explicit;
* aria labels for icon-only controls;
* alt text from Asset Registry;
* decorative images hidden from screen readers;
* reduced motion support;
* touch targets at least tokenized minimum size;
* contrast validated for every theme.

UI states required for interactive surfaces:

* loading/busy;
* error;
* empty;
* success/complete;
* disabled.

## 19. Performance

LCP strategy:

* hero text renders without waiting for non-critical images;
* critical hero asset is priority only if it contributes to LCP;
* decorative hero assets are optional on compact mode;
* below-fold images lazy-load;
* responsive image `sizes` comes from asset/layout metadata;
* no heavy animation before first paint;
* no viewport measurement loops;
* CSS-first layout;
* avoid hydration overload if framework is introduced.

Budget gates:

* no unbounded image dimensions;
* no layout shift from late image sizing;
* no large client bundle for static content if simple HTML/CSS can render it;
* no generated asset without optimized derivative.

## 20. Testing / Validation

Required checks:

* schema validation for all content modules;
* asset key validation;
* icon key validation;
* CTA/action registry validation;
* analytics event coverage;
* claim maturity validation;
* no `forbidden_claim` / `unsupported_claim` rendered;
* no direct image imports in sections;
* no direct paths `/images/...` in sections;
* no direct hex/rgb/hsl in sections;
* no local magic layout numbers in sections;
* responsive screenshots for mobile/tablet/desktop/wide;
* keyboard navigation smoke;
* accessibility checks;
* Lighthouse or equivalent performance pass;
* link check;
* visual regression for hero/documents/CTA;
* reduced-motion smoke.

Suggested static checks:

```text
rg -n "#[0-9a-fA-F]{3,8}|rgb\\(|hsl\\(" landing/sections landing/components
rg -n "/images/|\\.png|\\.webp|\\.svg" landing/sections
rg -n "style=|top:|left:|z-index:|width: [0-9]|height: [0-9]" landing/sections
rg -n "landing_.*_click" landing/sections
```

The exact commands must be adapted to the chosen stack.

## 21. Implementation Phases

### Phase 0 - Repo Audit

Confirm:

* framework/no-framework decision;
* separate landing app vs current Python/static runtime;
* build/test commands;
* image serving strategy;
* whether CSS modules, vanilla CSS, or token-generated CSS will be used.

Gate: no section implementation until stack decision is recorded.

### Phase 1 - Contracts

Create:

* theme contract;
* layout contract;
* typography/motion contracts;
* asset/icon/action/analytics registries;
* section registry;
* content schemas;
* claim maturity helper.

Gate: validation can read empty/sample content and registries.

### Phase 2 - Primitives

Create:

* Container;
* SectionShell;
* ResponsiveGrid;
* Stack;
* Cluster;
* Split;
* AspectFrame;
* FloatingPanel;
* Button;
* Card;
* Icon;
* AssetImage.

Gate: primitives have variants, accessibility states and no arbitrary style props.

### Phase 3 - Sections Scaffold

Create section skeletons:

* Header;
* Hero;
* Audience;
* Benefits;
* Workflow;
* Documents Demo;
* Standards;
* Testimonials;
* Final CTA.

Gate: sections render from mock validated DTOs and are isolated.

### Phase 4 - Content Integration

Connect:

* JSON content modules;
* schemas;
* section registry;
* action registry;
* analytics registry;
* asset/icon resolvers.

Gate: content changes do not require section source edits.

### Phase 5 - Visual Pass

Tune:

* warmKitchen theme;
* hero composition;
* document demo;
* CTA section;
* cards and badges.

Gate: all tuning is through tokens, variants or registry metadata.

### Phase 6 - Responsive Pass

Verify:

* compact/comfortable/expanded/wide modes;
* mobile navigation;
* hero simplification;
* document demo readability;
* decorative visibility;
* no overflow.

Gate: screenshots across target widths pass review.

### Phase 7 - Validation Pass

Run:

* schema/reference validation;
* static hardcode checks;
* accessibility smoke;
* performance smoke;
* visual regression;
* link check.

Gate: no blocking validation errors.

### Phase 8 - Owner Gates

Confirm:

* primary CTA;
* free onboarding / pricing;
* DOCX/PDF/Excel export wording;
* себестоимость wording;
* legal/standards copy;
* product UI mockups showing roadmap features;
* production testimonials or placeholder behavior.

Gate: production launch blocked until owner/legal decisions are closed.

## 22. Hero Visual Without Magic

Hero visual must be a named layer composition, not arbitrary absolute tuning.

Model:

```ts
type HeroVisualLayout = {
  aspectRatio: keyof LayoutTokens["ratio"];
  variant: "desktopRich" | "tabletBalanced" | "mobileCompact";
  layers: Array<{
    id: string;
    assetKey?: LandingAssetKey;
    component?: "ProductUiMock" | "MetricCard" | "DishImage" | "ChefImage";
    slot: "background" | "main" | "foreground" | "floatingTop" | "floatingBottom";
    visibility: LandingAssetVisibility;
    offsetToken: string;
    zIndexToken: keyof LayoutTokens["zIndex"];
  }>;
};
```

Allowed:

* layer slots;
* tokenized offsets;
* aspect-ratio container;
* responsive variants;
* decorative visibility rules;
* asset metadata;
* z-index tokens.

Forbidden:

* section-local `top: 37px`;
* per-asset local `left` hacks;
* raw z-index;
* raw dimensions;
* desktop composition simply scaled down to mobile.

## 23. Agent-Friendly Implementation

Future agent workflow must be possible:

1. list sections;
2. inspect module manifest;
3. read content schema;
4. see allowed assets/icons/actions;
5. see claim maturity sources;
6. patch content module;
7. validate references and claims;
8. preview section/page;
9. view diff;
10. rollback.

Manifest minimum:

```json
{
  "id": "landing.hero",
  "section": "HeroSection",
  "contentFile": "content/ru/hero.json",
  "schemaFile": "schemas/hero.schema.ts",
  "allowedAssetKeys": ["hero.productUi", "hero.chef", "hero.dish"],
  "allowedIconKeys": ["feature.aiAssistant", "feature.compliance"],
  "allowedActionIds": ["demo.request", "sample.project.view"],
  "riskLevel": "medium",
  "claimMaturityRefs": ["claim.target.techcards", "claim.roadmap.cost"],
  "previewMode": "isolated-and-page"
}
```

Agent must not edit raw JSX for content-only tasks.

## 24. Acceptance Criteria

The landing implementation is not accepted if any item below fails:

1. All sections render from content modules.
2. No business text is hardcoded in section JSX/HTML.
3. All colors come from theme tokens.
4. No direct hex/rgb/hsl in sections.
5. All spacing/radius/shadow/layout values come from tokens or variants.
6. No local magic numbers in sections.
7. All images resolve through Asset Registry.
8. All icons resolve through Icon Registry.
9. All CTA resolve through Action Registry.
10. Every CTA has analytics event.
11. Disabled/busy states are explicit.
12. `forbidden_claim` never renders.
13. `unsupported_claim` never renders without owner override and source update.
14. `decision_needed` CTA/claim is hidden or disabled until approval.
15. Roadmap claims do not look available-now.
16. Legal/compliance copy uses cautious wording and has review gate.
17. Sections are independent and can be reordered/disabled through config.
18. Header, Hero, Documents, Standards and Final CTA pass mobile/tablet/desktop/wide checks.
19. Hero visual has tokenized layers and responsive variants.
20. Decorative assets can be hidden on compact mode.
21. Semantic HTML and keyboard navigation pass smoke.
22. Focus states are visible.
23. Images have correct alt or decorative role.
24. Reduced motion is respected.
25. LCP strategy is documented and critical assets are bounded.
26. No direct section dependency on physical asset paths.
27. No section-local analytics event strings.
28. Validation can catch missing asset/icon/action keys.
29. There is a rollback path for content/config changes.
30. Owner gates for CTA, legal, exports and roadmap UI mockups are closed before public launch.

## 25. Owner Decisions Before Freeze

Still needed:

1. Primary CTA for first public version.
2. Whether `Начать бесплатно` has real onboarding/free plan.
3. Whether `Посмотреть тарифы` is visible before pricing model.
4. Whether DOCX/PDF/Excel export is hidden, disabled, alpha-next or roadmap-only.
5. How себестоимость appears: core target claim, SEO-only or roadmap-only.
6. Which document types appear in first Documents Demo.
7. Exact legal wording for standards block.
8. Which roadmap features may appear in product UI mockups.
9. Whether testimonials are hidden, placeholder-internal, or real approved quotes.

## 26. Handoff Summary For Implementer

Build the landing as a contract system:

* content in modules;
* visuals through theme/layout tokens;
* assets/icons/actions through registries;
* sections isolated;
* responsive behavior CSS-native;
* claim maturity enforced before render/publication;
* agent operations anticipated through manifests.

Do not build a one-off page. Do not hardcode. Do not convert Target Product storefront into MVP-only copy.
