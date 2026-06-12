# Asset & Icon Registry Contract лендинга «ТехКухня»

Версия: 0.1
Статус: рабочий контракт для верстки публичного лендинга.

Связанные документы:

* [Индекс пакета](README.md)
* [PRD лендинга](LANDING_PRD_v0.1.md)
* [Визуальный и технический контракт](LANDING_VISUAL_TECH_CONTRACT_v0.1.md)
* [Visual Asset Layering Contract](LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md)

## 1. Назначение

Документ фиксирует архитектурный реестр визуальных материалов публичного лендинга: фотографии, продуктовые мокапы, декоративные изображения, аватары, document previews и пиктограммы.

Главное правило:

**Любой визуальный объект на лендинге должен иметь ключ в одном из реестров: `AssetRegistry` или `IconRegistry`.**

Это нужно, чтобы верстка не зависела от прямых путей к файлам, локальных SVG, случайных цветов и одноразовых декоративных решений.

## 2. Разделение реестров

Реестры разделяются на две разные сущности.

`AssetRegistry` — тяжелые или содержательные визуальные материалы:

* логотипы и брендовые изображения;
* фотографии;
* продуктовые UI-мокапы;
* декоративные food-объекты;
* аватары;
* document previews.

`IconRegistry` — пиктограммы и UI-иконки:

* иконки навигации;
* иконки кнопок;
* иконки карточек аудиторий;
* workflow-иконки;
* статусные иконки;
* иконки стандартов;
* иконки типов документов.

Иконки не должны храниться как обычные изображения, если это простые пиктограммы. Их нужно рендерить через единый `Icon` компонент и окрашивать только через `currentColor` или semantic token.

## 3. Базовые типы ассетов

```ts
export type LandingAssetKind =
  | "brand"
  | "cutout"
  | "contentImage"
  | "backdrop"
  | "productUi"
  | "edgeDecor"
  | "documentPreview"
  | "avatar";

export type LandingAssetRole =
  | "content"
  | "decorative"
  | "ui"
  | "brand";

export type LandingAssetVisibility =
  | "always"
  | "desktop-only"
  | "tablet-up"
  | "mobile-only"
  | "optional"
  | "theme-dependent";

export type LandingAssetThemeBehavior =
  | "theme-neutral"
  | "theme-mapped"
  | "uses-semantic-colors";

export type LandingAssetSection =
  | "header"
  | "hero"
  | "audience"
  | "benefits"
  | "workflow"
  | "documents"
  | "standards"
  | "testimonials"
  | "finalCta"
  | "global";

export type LandingAssetBackgroundMode =
  | "transparent"
  | "embedded"
  | "environment"
  | "solid";

export type LandingAssetLayerRole =
  | "none"
  | "brandMark"
  | "heroBackdrop"
  | "heroProductUi"
  | "heroHumanCutout"
  | "heroForegroundObject"
  | "audienceCardMedia"
  | "documentContent"
  | "finalCtaBrandBand"
  | "finalCtaEdgeDecor";

export type LandingAssetZSlot =
  | "none"
  | "backdrop"
  | "base"
  | "midground"
  | "foreground"
  | "overlay";

export type LandingAssetOverlapPolicy =
  | "none"
  | "sceneOnly"
  | "productUiOnly"
  | "edgeOnly";

export type LandingAssetSafeArea =
  | "none"
  | "preserveTextAndCta"
  | "preserveProductUiCore"
  | "preserveCardContent";

export type LandingAssetCropPolicy =
  | "contained"
  | "coverCrop"
  | "mayBleed";

export type LandingAssetShadowPolicy =
  | "none"
  | "cssShadowAllowed"
  | "bakedShadowAllowed";
```

## 4. Расширенный asset contract

```ts
export type LandingAsset = {
  key: LandingAssetKey;
  kind: LandingAssetKind;
  role: LandingAssetRole;
  backgroundMode: LandingAssetBackgroundMode;
  transparentBackground: boolean;
  layerRole: LandingAssetLayerRole;
  zSlot: LandingAssetZSlot;
  overlapPolicy: LandingAssetOverlapPolicy;
  safeArea: LandingAssetSafeArea;
  cropPolicy: LandingAssetCropPolicy;
  shadowPolicy: LandingAssetShadowPolicy;

  src: string;
  alt: string;

  width?: number;
  height?: number;

  loading?: "eager" | "lazy";
  priority?: boolean;

  visibility: LandingAssetVisibility;
  themeBehavior: LandingAssetThemeBehavior;
  section: LandingAssetSection;

  displayRules?: {
    minWidth?: number;
    maxWidth?: number;
    hideOnReducedMotion?: boolean;
    hideOnLowBandwidth?: boolean;
    hideWhenContentMissing?: boolean;
  };

  fallbackKey?: LandingAssetKey;
};

export type LandingAssetRegistry = Record<LandingAssetKey, LandingAsset>;
```

## 5. LandingAssetKey

```ts
export type LandingAssetKey =
  | "brand.logo"
  | "brand.logoMark"
  | "hero.productUi"
  | "hero.chef"
  | "hero.dish"
  | "hero.metricCard"
  | "hero.decor.backgroundKitchen"
  | "hero.decor.herbs"
  | "hero.decor.spices"
  | "audience.restaurant"
  | "audience.chef"
  | "audience.production"
  | "audience.technologist"
  | "documents.dishSample"
  | "documents.wordIcon"
  | "documents.preview.techCard"
  | "standards.decor.herbs"
  | "testimonials.avatar.chef"
  | "testimonials.avatar.manager"
  | "testimonials.avatar.technologist"
  | "finalCta.decor.tomatoes"
  | "finalCta.decor.pepper"
  | "finalCta.decor.spices"
  | "finalCta.decor.herbs";
```

## 6. Детальный реестр ассетов

| Ключ | Asset kind / background | Где используется | Роль | Условия отображения |
| --- | --- | --- | --- | --- |
| `brand.logo` | `brand` / `solid` или `transparent` | Header | `brand` | Всегда. |
| `brand.logoMark` | `brand` / `solid` или `transparent` | Favicon, mobile header, loading states | `brand` | Optional. |
| `hero.productUi` | `productUi` / `embedded` | Hero | `content` | Desktop/tablet priority; на mobile можно упростить. |
| `hero.chef` | `cutout` / `transparent` | Hero human layer | `content` | Desktop/tablet; на mobile допускается кроп или скрытие. |
| `hero.dish` | `cutout` / `transparent` или `contentImage` / `embedded` | Hero foreground object или карточка блюда | `content` или `decorative` | Tablet-up; на mobile optional. |
| `hero.metricCard` | `productUi` component | Hero floating card | `ui` / `content` | Desktop/tablet; mobile compact или hidden. |
| `hero.decor.backgroundKitchen` | `backdrop` / `environment` | Hero background | `decorative` | Desktop only или lazy background. |
| `hero.decor.herbs` | `edgeDecor` / `transparent` | Hero, нижний край | `decorative` | Optional; скрывать на mobile. |
| `hero.decor.spices` | `edgeDecor` / `transparent` | Hero или CTA | `decorative` | Optional. |
| `audience.restaurant` | `contentImage` / `embedded` | Карточка «Рестораны и кафе» | `content` / `audienceCardMedia` | Lazy. |
| `audience.chef` | `contentImage` / `embedded` | Карточка «Шеф-повара» | `content` / `audienceCardMedia` | Lazy. |
| `audience.production` | `contentImage` / `embedded` | Карточка «Производства и цеха» | `content` / `audienceCardMedia` | Lazy. |
| `audience.technologist` | `contentImage` / `embedded` | Карточка «Технологи и менеджеры» | `content` / `audienceCardMedia` | Lazy. |
| `documents.dishSample` | `contentImage` / `embedded` | Карточка блюда в блоке документов | `content` | Lazy. |
| `documents.wordIcon` | `documentPreview` или `productUi` image | Карточка готового DOCX | `ui` | Всегда при наличии output document. |
| `documents.preview.techCard` | `documentPreview` / `embedded` | Пример документа | `content` | Lazy; доступен для CTA «Посмотреть пример». |
| `standards.decor.herbs` | `edgeDecor` / `transparent` | Блок стандартов | `decorative` | Tablet-up, optional. |
| `testimonials.avatar.chef` | `avatar` | Отзывы | `content` | Lazy; fallback initials. |
| `testimonials.avatar.manager` | `avatar` | Отзывы | `content` | Lazy; fallback initials. |
| `testimonials.avatar.technologist` | `avatar` | Отзывы | `content` | Lazy; fallback initials. |
| `cta.kitchenBoard.desktop` | `backdrop` / `embedded` | Финальный CTA desktop band | `decorative` / `finalCtaBrandBand` | Desktop-only; full-width short footer ratio. |
| `cta.kitchenBoard.mobile` | `backdrop` / `embedded` | Финальный CTA mobile band | `decorative` / `finalCtaBrandBand` | Mobile-only; separate mobile composition, not desktop crop. |
| `finalCta.decor.tomatoes` | `edgeDecor` / `transparent` | Финальный CTA | `decorative` | Desktop/tablet, optional. |
| `finalCta.decor.pepper` | `edgeDecor` / `transparent` | Финальный CTA | `decorative` | Desktop/tablet, optional. |
| `finalCta.decor.spices` | `edgeDecor` / `transparent` | Финальный CTA | `decorative` | Optional. |
| `finalCta.decor.herbs` | `edgeDecor` / `transparent` | Финальный CTA | `decorative` | Optional. |

## 7. Правила alt и accessibility

* Содержательные изображения получают нормальный `alt`, который описывает смысл изображения.
* Декоративные изображения получают `role: "decorative"` и пустой `alt`.
* Аватары реальных людей получают `alt` с именем или ролью; placeholder-аватары не должны выдавать вымышленных людей за реальных.
* Продуктовые UI-мокапы получают `alt`, если несут содержательный смысл; если рядом есть текстовое описание, допускается пустой `alt`.
* Document previews должны иметь `alt`, объясняющий тип документа.

## 8. Правила загрузки

Hero assets:

* `hero.productUi`, `hero.chef` и при необходимости `hero.dish` могут иметь `priority: true`;
* decorative hero assets не должны ухудшать LCP;
* `hero.decor.*` должны отключаться или лениво грузиться на mobile при нехватке места.

Ниже первого экрана:

* audience images грузятся lazy;
* document previews грузятся lazy;
* testimonials avatars грузятся lazy;
* декоративные CTA assets грузятся lazy, если не попадают в первый экран.

## 8.1. Transparent Background And Layering Rules

<!-- STICKY-ASSET-LAYERS:
Не требуй прозрачный фон от всех изображений. Cutout/edgeDecor требуют alpha; contentImage/documentPreview обычно имеют embedded background.
-->

Правила:

* `cutout` и `edgeDecor` требуют `transparentBackground: true` и `backgroundMode: "transparent"`.
* `contentImage` и `documentPreview` требуют `backgroundMode: "embedded"`.
* `productUi` обязан иметь `safeArea: "preserveProductUiCore"`.
* `finalCtaBrandBand` обязан иметь `safeArea: "preserveTextAndCta"`.
* `heroHumanCutout` обязан быть `assetKind: "cutout"`.
* Hero overlap и z-order описываются через `layerRole`, `zSlot`, `overlapPolicy`, а не через локальный `z-index` в секции.
* Final CTA edge decor не должен перекрывать heading, условия и кнопки.

## 8.2. Current Placeholder Asset Policy

Текущая showcase-публикация может использовать placeholder/scaffold assets без production asset freeze.

Правила:

* placeholder asset остается обычной registry entry, а не локальным JSX/CSS исключением;
* placeholder должен иметь `rightsStatus: "local-scaffold"` или эквивалентный явный статус;
* placeholder не получает фиктивный `approved_for_public_landing`, `published` или provenance approval;
* `contentImage` placeholder может иметь `backgroundMode: "embedded"`;
* `hero.dish` нельзя переводить в `cutout`, пока файл не имеет реального transparent background;
* future production keys вроде `hero.chef`, `hero.decor.backgroundKitchen`, `finalCta.decor.*` не добавляются в code registry без реальных файлов;
* замена placeholder на production asset должна идти через `AssetRegistry` and provenance flow, без переписывания секций.

Current code registry scaffold set:

| Current key | Required status |
| --- | --- |
| `brand.logoMark` | `local-scaffold` |
| `hero.productUi` | `local-scaffold` |
| `hero.dish` | `local-scaffold` |
| `documents.techCardPreview` | `local-scaffold` |
| `documents.costCardPreview` | `local-scaffold` |
| `cta.kitchenBoard.desktop` | `approved` |
| `cta.kitchenBoard.mobile` | `approved` |

## 9. IconKey

```ts
export type IconKey =
  | "nav.chevronDown"
  | "action.arrowRight"
  | "action.play"
  | "feature.aiAssistant"
  | "feature.compliance"
  | "feature.costControl"
  | "audience.restaurant"
  | "audience.chef"
  | "audience.production"
  | "audience.technologist"
  | "benefit.time"
  | "benefit.calculation"
  | "benefit.shield"
  | "benefit.analytics"
  | "workflow.documentCreate"
  | "workflow.ingredients"
  | "workflow.calculator"
  | "workflow.approve"
  | "workflow.export"
  | "document.techCard"
  | "document.calculationCard"
  | "document.ttk"
  | "document.planMenu"
  | "document.label"
  | "document.instruction"
  | "status.check"
  | "status.approved"
  | "status.download"
  | "standard.sanpin"
  | "standard.trts"
  | "standard.haccp"
  | "standard.gost"
  | "standard.marking"
  | "testimonial.quote";
```

## 10. Icon definition

```ts
export type LandingIconDefinition = {
  key: IconKey;
  source: "lucide" | "custom-svg" | "inline-component";
  role: "decorative" | "semantic" | "action" | "status";
  themeBehavior: "uses-current-color" | "uses-semantic-colors";
  defaultVariant:
    | "brand"
    | "neutral"
    | "success"
    | "warning"
    | "muted"
    | "inverse";
};

export type LandingIconRegistry = Record<IconKey, LandingIconDefinition>;
```

Правило: секция не говорит «сделай иконку оранжевой». Секция передает `variant: "brand"` или `variant: "success"`, а тема решает итоговый цвет.

## 11. Пример использования

Запрещено:

```tsx
<img src="/images/tomatoes.png" />
<ChefHat color="#E35A2B" />
<div className="bg-orange-500" />
```

Разрешено:

```tsx
<AssetImage assetKey="finalCta.decor.tomatoes" />

<Icon name="workflow.export" variant="brand" />

<Button variant="primary">
  Начать бесплатно
</Button>
```

## 12. Связь с content config

Content config не хранит физические пути к файлам. Он хранит только ключи:

```ts
export type AudienceItem = {
  id: string;
  title: string;
  description: string;
  imageAssetKey: LandingAssetKey;
  icon: IconKey;
  iconVariant: IconBadgeVariant;
};
```

Если добавляется пятая аудитория, разработчик добавляет данные в content config и регистрирует изображение/иконку в соответствующем реестре. Layout-код секции не меняется.

## 13. Темизация ассетов

Тема может менять:

* набор декоративных ассетов;
* визуальные варианты иконок;
* цветовые tokens для `currentColor`;
* фоновые decorative layers;
* тени и радиусы контейнеров.

Тема не должна менять:

* смысловую структуру страницы;
* список обязательных секций;
* CTA;
* продуктовые обещания;
* реальные данные документа или расчета.

Для декоративных объектов используется `themeBehavior: "theme-mapped"`. Для фотографий и продуктовых мокапов обычно используется `themeBehavior: "theme-neutral"`.

## 14. Acceptance Criteria

### 14.1. Asset acceptance

* Все фотографии зарегистрированы в `asset.registry.ts`.
* Все продуктовые UI-мокапы зарегистрированы в `asset.registry.ts` или реализованы как composed components с ключом.
* Все декоративные изображения имеют `role: "decorative"` и пустой `alt`.
* Все содержательные изображения имеют нормальный `alt`.
* Hero assets имеют явную loading strategy.
* Декоративные food-assets можно отключить на mobile без поломки композиции.
* Для аватаров есть fallback.
* Для смены темы можно заменить набор декоративных ассетов без переписывания секций.

### 14.2. Icon acceptance

* Все иконки зарегистрированы в `icon.registry.ts`.
* Секции используют только `IconKey`.
* Иконки рендерятся через единый `Icon` компонент.
* Цвет иконок задается только через semantic variant или `currentColor`.
* В секциях нет прямых импортов SVG.
* В секциях нет прямого задания цвета иконки.

### 14.3. Implementation acceptance

* В секциях нет прямых импортов SVG/PNG/WebP.
* В секциях нет прямых путей вида `/images/...`.
* `AssetImage` сам получает `src`, `alt`, `width`, `height`, `loading`, `priority` из реестра.
* Любой новый визуальный объект добавляется сначала в registry contract, затем в код.
* Визуальная сверка с эскизами не приводит к локальному хардкоду в секциях.

## 15. Порядок обновления

Если появляется новый визуальный объект:

1. Определить, это asset или icon.
2. Добавить ключ в `LandingAssetKey` или `IconKey`.
3. Добавить запись в соответствующий registry.
4. Указать роль, alt, visibility, section, loading strategy и theme behavior.
5. Обновить content config, если объект управляется контентом.
6. Проверить PRD и визуально-технический контракт на расхождения.

## 16. Generated Assets Extension

Generated assets не должны попадать в лендинг напрямую. Для них используется отдельный workflow, описанный в [AI Asset Generation Pipeline](../ai-asset-generation-pipeline.md).

Дополнительные поля для generated/manual/licensed assets:

```ts
export type LandingAssetSource =
  | "manual"
  | "generated"
  | "licensed"
  | "stock"
  | "internal";

export type AssetRightsStatus =
  | "unchecked"
  | "approved_for_internal_preview"
  | "approved_for_public_landing"
  | "blocked"
  | "needs_legal_review";

export type AssetApprovalStatus =
  | "manual"
  | "pending_review"
  | "approved"
  | "published"
  | "rejected"
  | "archived";

export type LandingAssetGeneratedMetadata = {
  source: LandingAssetSource;
  generatedCandidateId?: string;
  provider?: string;
  model?: string;
  promptHash?: string;
  rightsStatus?: AssetRightsStatus;
  approvalStatus?: AssetApprovalStatus;
  approvedBy?: string;
  approvedAt?: string;
  version: number;
  replacesAssetKey?: LandingAssetKey;
  rollbackAssetKey?: LandingAssetKey;
  cdnUrl?: string;
  storagePath?: string;
};
```

Правила:

* `source: "generated"` требует `generatedCandidateId`, `provider`, `model`, `promptHash`, `rightsStatus`, `approvalStatus`.
* Public landing может использовать generated asset только после `approvalStatus: "published"` и `rightsStatus: "approved_for_public_landing"`.
* Rejected candidate не может быть asset key.
* При замене ассета старый ключ не удаляется сразу и используется как rollback target.
* Ассеты с людьми, логотипами, узнаваемыми брендами или reference images требуют отдельного high-risk gate.
