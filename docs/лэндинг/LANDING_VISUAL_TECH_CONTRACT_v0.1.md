# Визуальный и технический контракт лендинга «ТехКухня»

Статус: рабочий визуально-технический контракт для верстки публичного лендинга.

Связанные документы:

* [Индекс пакета](README.md)
* [PRD лендинга](LANDING_PRD_v0.1.md)
* [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
* [Visual Asset Layering Contract](LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md)

Версия: 0.1
Назначение: описать управляемую, модульную и контрактную реализацию визуального слоя лендинга без хардкода цветов, ассетов и декоративных решений внутри секций.

## 1. Главный принцип

Лендинг не должен быть набором вручную сверстанных блоков с локальными цветами, картинками и стилями.

Лендинг должен быть собран как управляемая система:

* цветовые решения берутся из единого theme contract;
* изображения, иконки и декоративные элементы берутся из asset registry;
* тексты и структура секций берутся из content config;
* секции изолированы и не знают физические пути ассетов;
* компоненты используют semantic tokens, а не конкретные значения цветов;
* замена темы, ассетов или контента не требует переписывания секций.

## 2. Архитектурная модель

Рекомендуемая структура:

```text
landing/
  page.tsx
  landing.config.ts
  content/
    hero.content.ts
    audience.content.ts
    benefits.content.ts
    workflow.content.ts
    documents.content.ts
    standards.content.ts
    testimonials.content.ts
    cta.content.ts
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
    IconBadge/
    SectionShell/
    MetricCard/
    DocumentCard/
    StepCard/
    AssetImage/
  theme/
    theme.contract.ts
    themes/
      default.theme.ts
      warmKitchen.theme.ts
      neutralBusiness.theme.ts
  assets/
    asset.contract.ts
    asset.registry.ts
    asset.types.ts
```

## 3. Контракт темы

Все визуальные решения должны использовать semantic tokens.

Запрещено в секциях:

* использовать прямые hex/rgb/hsl значения;
* использовать классы вида `bg-orange-500`, `text-red-700`, если они не являются алиасами design tokens;
* задавать локальные градиенты без theme token;
* задавать локальные цвета теней, рамок, фонов;
* импортировать тему частично и обходить контракт.

Разрешено:

* использовать только semantic token names;
* использовать CSS variables, созданные на основе theme contract;
* использовать component variants, которые внутри ссылаются на tokens.

### 3.1. Базовая структура theme contract

```ts
export type LandingThemeContract = {
  color: {
    page: {
      background: string;
      backgroundMuted: string;
      foreground: string;
    };

    surface: {
      primary: string;
      secondary: string;
      elevated: string;
      muted: string;
      glass: string;
      inverse: string;
    };

    text: {
      primary: string;
      secondary: string;
      muted: string;
      inverse: string;
      accent: string;
      success: string;
      danger: string;
    };

    border: {
      subtle: string;
      default: string;
      strong: string;
      focus: string;
    };

    brand: {
      primary: string;
      primaryHover: string;
      primaryActive: string;
      secondary: string;
      soft: string;
      contrast: string;
    };

    action: {
      primaryBackground: string;
      primaryForeground: string;
      primaryHoverBackground: string;
      secondaryBackground: string;
      secondaryForeground: string;
      secondaryBorder: string;
    };

    status: {
      successBackground: string;
      successForeground: string;
      warningBackground: string;
      warningForeground: string;
      infoBackground: string;
      infoForeground: string;
    };

    icon: {
      default: string;
      muted: string;
      brand: string;
      success: string;
      warning: string;
      inverse: string;
    };

    decorative: {
      heroGlow: string;
      heroOverlay: string;
      ctaBackground: string;
      standardsBand: string;
      cardWarmTint: string;
    };
  };

  gradient: {
    heroBackground: string;
    heroVisualOverlay: string;
    ctaBackground: string;
    standardsBackground: string;
    cardHighlight: string;
  };

  shadow: {
    card: string;
    cardHover: string;
    floatingPanel: string;
    heroVisual: string;
    button: string;
  };

  radius: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    pill: string;
  };

  spacing: {
    sectionY: string;
    sectionYCompact: string;
    containerX: string;
    cardPadding: string;
    gridGap: string;
  };

  typography: {
    fontFamily: {
      heading: string;
      body: string;
      ui: string;
    };
    size: {
      heroTitle: string;
      h1: string;
      h2: string;
      h3: string;
      body: string;
      bodySmall: string;
      caption: string;
      button: string;
    };
    weight: {
      regular: string;
      medium: string;
      semibold: string;
      bold: string;
    };
    lineHeight: {
      tight: string;
      normal: string;
      relaxed: string;
    };
  };

  layout: {
    containerMaxWidth: string;
    heroMinHeight: string;
    headerHeight: string;
    cardMinHeight: string;
  };

  motion: {
    durationFast: string;
    durationNormal: string;
    durationSlow: string;
    easingStandard: string;
    easingEmphasized: string;
  };
};
```

## 4. Контракт ассетов

Этот раздел задаёт базовую границу. Детальный и приоритетный реестр ассетов и пиктограмм описан в [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md). Если базовый список ключей ниже расходится с детальным реестром, для реализации используется детальный реестр.


Секции не должны импортировать изображения напрямую.

Запрещено:

```ts
import heroChef from "@/public/images/chef.png";
```

Разрешено:

```ts
const asset = getLandingAsset("hero.chef");
```

### 4.1. Asset registry

```ts
export type LandingAssetKey =
  | "brand.logo"
  | "hero.chef"
  | "hero.productUi"
  | "hero.dish"
  | "hero.decor.herbs"
  | "hero.decor.spices"
  | "audience.restaurant"
  | "audience.chef"
  | "audience.production"
  | "audience.technologist"
  | "documents.dishSample"
  | "documents.wordIcon"
  | "standards.decor.herbs"
  | "cta.decor.tomatoes"
  | "cta.decor.pepper"
  | "testimonials.avatar.chef"
  | "testimonials.avatar.manager"
  | "testimonials.avatar.technologist";

export type LandingAsset = {
  key: LandingAssetKey;
  src: string;
  alt: string;
  width?: number;
  height?: number;
  role: "content" | "decorative" | "ui";
  assetKind: "brand" | "cutout" | "contentImage" | "backdrop" | "productUi" | "edgeDecor" | "documentPreview" | "avatar";
  backgroundMode: "transparent" | "embedded" | "environment" | "solid";
  transparentBackground: boolean;
  layerRole: string;
  zSlot: string;
  overlapPolicy: string;
  safeArea: string;
  loading?: "eager" | "lazy";
  priority?: boolean;
};

export type LandingAssetRegistry = Record<LandingAssetKey, LandingAsset>;
```

### 4.2. Правила использования ассетов

Hero assets:

* `hero.chef`, `hero.productUi`, `hero.dish` могут иметь priority loading;
* декоративные элементы не должны ухудшать LCP;
* декоративные элементы должны иметь `role: "decorative"` и пустой alt.
* `cutout`/`edgeDecor` требуют transparent background metadata.
* `contentImage`/`documentPreview` используют embedded background и фиксированный crop.
* Hero/final CTA слои описываются через `layerRole`, `zSlot`, `overlapPolicy`, `safeArea`.

Audience assets:

* каждая карточка аудитории использует image key из content config;
* карточка не знает физический путь изображения.

CTA assets:

* декоративные овощи, специи, зелень и прочие элементы подключаются только через asset registry;
* при смене темы можно заменить набор декораций без изменения секции.

## 5. Контракт контента

Контент секций должен быть data-driven.

Пример общего конфига:

```ts
export type LandingPageContent = {
  header: HeaderContent;
  hero: HeroContent;
  audience: AudienceContent;
  benefits: BenefitsContent;
  workflow: WorkflowContent;
  documents: DocumentsContent;
  standards: StandardsContent;
  testimonials: TestimonialsContent;
  finalCta: FinalCtaContent;
};
```

### 5.1. Hero content contract

```ts
export type HeroContent = {
  eyebrow?: string;
  title: string;
  description: string;
  primaryAction: LandingAction;
  secondaryAction: LandingAction;
  trustItems: Array<{
    icon: IconKey;
    title: string;
    description?: string;
  }>;
  visual: {
    chefAssetKey: LandingAssetKey;
    productUiAssetKey: LandingAssetKey;
    dishAssetKey: LandingAssetKey;
    metricCard: {
      title: string;
      items: Array<{
        label: string;
        value: string;
      }>;
    };
  };
};
```

### 5.2. Audience content contract

```ts
export type AudienceContent = {
  title: string;
  items: Array<{
    id: string;
    title: string;
    description: string;
    imageAssetKey: LandingAssetKey;
    icon: IconKey;
    href?: string;
  }>;
};
```

### 5.3. Workflow content contract

```ts
export type WorkflowContent = {
  title: string;
  steps: Array<{
    id: string;
    number: number;
    icon: IconKey;
    title: string;
    description: string;
  }>;
};
```

### 5.4. Documents content contract

```ts
export type DocumentsContent = {
  title: string;
  documentTypes: Array<{
    id: string;
    label: string;
    isPrimary?: boolean;
  }>;
  dishCard: {
    imageAssetKey: LandingAssetKey;
    title: string;
    meta: Array<{
      label: string;
      value: string;
    }>;
    statusLabel?: string;
  };
  calculationExample: {
    title: string;
    columns: Array<{
      id: string;
      label: string;
    }>;
    rows: Array<{
      id: string;
      label: string;
      values: Record<string, string>;
    }>;
  };
  outputDocument: {
    title: string;
    subtitle: string;
    checks: string[];
    action: LandingAction;
  };
};
```

## 6. Контракт секций

Каждая секция получает только:

* content;
* theme-derived className/style tokens;
* asset resolver;
* analytics handler при необходимости.

Секция не должна:

* обращаться к глобальным изображениям напрямую;
* знать конкретные цвета темы;
* содержать неуправляемый текст;
* создавать собственные локальные design tokens;
* использовать бизнес-данные вне своего content contract.

Пример:

```ts
type LandingSectionProps<TContent> = {
  content: TContent;
  assets: LandingAssetResolver;
  analytics?: LandingAnalytics;
};
```

## 7. Компонентный контракт

### 7.1. Button

```ts
export type ButtonVariant =
  | "primary"
  | "secondary"
  | "ghost"
  | "outline";

export type ButtonProps = {
  variant: ButtonVariant;
  size: "sm" | "md" | "lg";
  href?: string;
  onClick?: () => void;
  iconRight?: IconKey;
  iconLeft?: IconKey;
  children: React.ReactNode;
};
```

Button не принимает произвольный цвет. Цвет определяется только через `variant`.

### 7.2. Card

```ts
export type CardVariant =
  | "default"
  | "elevated"
  | "soft"
  | "interactive"
  | "metric"
  | "document";

export type CardProps = {
  variant: CardVariant;
  children: React.ReactNode;
};
```

Card не принимает прямые цвета, тени и радиусы. Всё определяется variant → theme tokens.

### 7.3. IconBadge

```ts
export type IconBadgeVariant =
  | "brand"
  | "success"
  | "warning"
  | "neutral";

export type IconBadgeProps = {
  icon: IconKey;
  variant: IconBadgeVariant;
  size: "sm" | "md" | "lg";
};
```

IconBadge не принимает hex и не знает конкретную палитру.

### 7.4. AssetImage

```ts
export type AssetImageProps = {
  assetKey: LandingAssetKey;
  className?: string;
  sizes?: string;
};
```

`AssetImage` сам получает `src`, `alt`, `width`, `height`, `loading`, `priority` из asset registry.

## 8. Визуальные принципы референса

Лендинг должен сохранить следующие визуальные свойства референса:

1. Тёплая гастрономическая атмосфера.
2. Сочетание человеческого образа, блюда и интерфейса продукта.
3. Мягкие карточки с лёгкой глубиной.
4. Крупный editorial-заголовок в hero.
5. Чистые UI-панели, похожие на реальный SaaS.
6. Много воздуха между блоками.
7. Дружелюбная, но деловая подача.
8. Акцент на документах, расчётах и стандартах.
9. Финальный CTA с более плотной визуальной заливкой.
10. Декоративные food-элементы как поддержка темы, а не как визуальный шум.

## 9. Визуальные зоны страницы

### 9.1. Page background

Использует:

* `color.page.background`;
* `gradient.heroBackground` для верхней зоны;
* `color.page.backgroundMuted` для мягких секционных переходов.

Нельзя задавать фон секций напрямую.

### 9.2. Hero visual

<!-- STICKY-ASSET-LAYERS:
Hero visual is a layered product scene, not a single right-column image.
Cutout/background/content-image rules are defined in LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md.
-->

Состоит из слоёв:

1. Фоновый декоративный слой.
2. Product UI card.
3. Human/chef image.
4. Dish image.
5. Metric floating card.
6. Decorative overlay.

Все слои управляются через `HeroVisual` component.

```ts
export type HeroVisualProps = {
  productUiAssetKey: LandingAssetKey;
  chefAssetKey: LandingAssetKey;
  dishAssetKey: LandingAssetKey;
  metricCard: MetricCardContent;
};
```

Порядок слоёв не должен быть размазан по секции. Он должен жить внутри `HeroVisual`.

Hero scene rules:

* `heroBackdrop` задаёт атмосферу, но не спорит с текстом и product UI.
* `heroHumanCutout` и `heroForegroundObject` могут иметь прозрачный фон и пересекать product UI.
* Product UI core fields, H1 and CTA row are protected safe areas.
* Content images внутри карточек не требуют прозрачного фона.
* Любой слой получает kind/background/layer metadata из `AssetRegistry`.

### 9.2.1. Final CTA brand band

Финальный CTA работает как high-contrast brand band:

* фон может быть bitmap/backdrop или tokenized brand fill;
* текст использует inverse semantic tone, а не локальный raw white;
* food/edge decor остаётся на краях и не перекрывает heading, terms or CTA;
* на mobile edge decor можно скрывать без потери смысла;
* safe area для текста и кнопок обязательна.

### 9.3. Audience cards

Карточка аудитории содержит:

* image;
* floating icon badge;
* title;
* description.

Цвет бейджа определяется не карточкой, а `audience.item.iconVariant`.

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

### 9.4. Workflow steps

Workflow не должен быть просто сеткой карточек. Он должен восприниматься как процесс.

Desktop:

* горизонтальная цепочка;
* визуальная связь между шагами;
* номер шага в badge.

Mobile:

* вертикальная timeline;
* connection line через token `border.subtle` или semantic equivalent.

### 9.5. Documents demo

Блок документов должен выглядеть как мини-демонстрация продукта:

* список типов документов;
* карточка блюда;
* таблица расчётов;
* карточка готового документа.

Все mock-значения должны быть вынесены в `documents.content.ts`.

## 10. Темизация

Минимальный набор тем:

1. `warmKitchen` — основная тёплая ресторанная тема.
2. `neutralBusiness` — более строгая B2B-тема.
3. `contrast` или `accessible` — тема для повышенной читаемости.

Требование:

* смена темы не должна требовать изменения JSX секций;
* тема может менять:

  * цвета;
  * градиенты;
  * тени;
  * радиусы;
  * типографику;
  * декоративные ассеты через registry mapping;
* тема не должна менять смысловую структуру страницы.

## 11. Запреты для реализации

Запрещено:

1. Хардкодить цвета в компонентах и секциях.
2. Хардкодить пути изображений в секциях.
3. Использовать изображения напрямую без asset registry.
4. Дублировать один и тот же визуальный паттерн локально в нескольких местах.
5. Размещать тексты лендинга прямо в JSX без content config.
6. Делать секции зависимыми друг от друга.
7. Делать Hero источником стилей для остальных секций.
8. Создавать «одноразовые» компоненты, если паттерн повторяется.
9. Использовать реальные юридические утверждения без проверки.
10. Привязывать визуальную тему к одному набору цветов.

## 12. Acceptance Criteria

### 12.1. Theme acceptance

* В коде секций нет прямых цветовых значений.
* Все цвета доступны через `LandingThemeContract`.
* Все компоненты используют semantic tokens.
* При замене темы лендинг визуально перестраивается без изменения секций.

### 12.2. Asset acceptance

* Все изображения зарегистрированы в `asset.registry.ts`.
* Секции используют только asset keys.
* У каждого ассета есть `alt`, `role`, loading strategy.
* Декоративные ассеты не озвучиваются screen reader.

### 12.3. Content acceptance

* Все тексты секций вынесены в content modules.
* Секции можно переставить или отключить через `landing.config.ts`.
* Количество карточек в audience, benefits, testimonials не захардкожено.

### 12.4. Component acceptance

* Button, Card, IconBadge, AssetImage используются повторно.
* Варианты компонентов описаны явно.
* Компоненты не принимают произвольные цвета.
* Hover/focus/active состояния управляются темой.

### 12.5. Layout acceptance

* Desktop, tablet и mobile раскладки реализованы.
* Hero не ломается при длинном тексте.
* Карточки сохраняют читаемость при разной длине описаний.
* Workflow корректно превращается из горизонтального процесса в mobile timeline.

## 13. Рекомендуемый порядок реализации

1. Создать `theme.contract.ts`.
2. Создать первую тему `warmKitchen.theme.ts`.
3. Создать `asset.contract.ts` и `asset.registry.ts`.
4. Создать content modules для всех секций.
5. Реализовать базовые компоненты:

   * Button;
   * Card;
   * IconBadge;
   * AssetImage;
   * SectionShell.
6. Реализовать Header и Hero.
7. Реализовать остальные секции.
8. Подключить аналитику CTA.
9. Проверить адаптивность.
10. Проверить отсутствие hardcoded colors/assets.
11. Провести визуальную сверку с референсом.
12. Подготовить вторую тему для проверки архитектуры темизации.

## 14. Контрольная проверка перед сдачей

Перед сдачей агент или разработчик должен ответить:

1. Можно ли заменить всю цветовую тему одним файлом?
2. Можно ли заменить hero-изображения без изменения HeroSection?
3. Можно ли добавить пятую аудиторию без изменения layout-кода?
4. Можно ли изменить список документов без изменения DocumentsSection?
5. Есть ли прямые hex/rgb/hsl значения внутри секций?
6. Есть ли прямые импорты изображений внутри секций?
7. Все ли CTA имеют analytics event?
8. Работает ли мобильная версия без потери смысла?
9. Есть ли alt-тексты у содержательных изображений?
10. Можно ли отключить testimonials через config без поломки страницы?
11. Все ли фотографии, декоративные изображения и продуктовые мокапы зарегистрированы в asset registry?
12. Все ли пиктограммы зарегистрированы в icon registry и окрашиваются только через semantic variants?

Если хотя бы на один из пунктов ответ отрицательный, архитектура лендинга считается недостаточно контрактной.
