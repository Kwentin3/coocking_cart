# Landing Production Asset Brief v0.1

<!-- STICKY-PRODUCTION-ASSET-BRIEF:
Этот brief фиксирует первый production-пакет визуальных ассетов для лендинга.
Не добавляй новые AssetRegistry keys до появления реальных файлов, provenance/rights metadata и ручного approval.
Cutout/edge decor требуют прозрачный фон; content image внутри карточки обычно должен иметь встроенный фон.
-->

Статус: рабочий production brief для генерации, ручной отрисовки и ревью ассетов лендинга.
Дата: 2026-06-11.

Связанные документы:

- [Visual Asset Layering Contract](LANDING_VISUAL_ASSET_LAYERING_CONTRACT_v0.1.md)
- [Visual Tech Contract](LANDING_VISUAL_TECH_CONTRACT_v0.1.md)
- [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
- [Landing Implementation Handoff](LANDING_IMPLEMENTATION_HANDOFF_v0.1.md)
- [AI Asset Generation Pipeline](../ai-asset-generation-pipeline.md)
- [Asset Provenance and Rights](../asset-provenance-and-rights.md)

Исходный визуальный референс:

```text
Референсы дизайна\dac12c44-5fb9-43fc-b966-e32971867bd7.png
```

## 1. Executive Summary

Лендинг должен получить живую layered-композицию, где изображения не воспринимаются как одна плоская иллюстрация.

Целевой production-пакет:

- hero backdrop: фоновая среда кухни или production context;
- hero human cutout: человек/шеф на прозрачном фоне;
- hero foreground food cutout: блюдо или предмет на прозрачном фоне;
- final CTA brand band: контрастная красно-терракотовая подложка с inverse text;
- final CTA edge decor: прозрачные food/decor объекты по краям;
- optional content image: карточка блюда/калькуляции с собственным фоном, например салат Цезарь.

Главное различие: прозрачный фон нужен только layered foreground/decor ассетам. Карточные и калькуляционные изображения должны быть полноценной композицией со своим фоном.

## 1.1. Current Showcase Placeholder Policy

Текущая showcase-публикация не блокируется ожиданием production asset freeze.

Допустимо использовать текущие registry-backed scaffold assets, если они:

- зарегистрированы в `AssetRegistry`;
- имеют `rightsStatus: "local-scaffold"`;
- имеют корректные `assetKind`, `backgroundMode`, `layerRole`, `zSlot`, `safeArea` and `alt`;
- не выдают себя за generated/approved/production-ready ассеты;
- могут быть заменены позже через registry/config без правки секций.

Текущий placeholder набор:

| Current key | Placeholder role | Production status |
| --- | --- | --- |
| `brand.logoMark` | local scaffold brand mark | Not production brand freeze. |
| `hero.productUi` | local scaffold product UI preview | Not final product UI screenshot. |
| `hero.dish` | embedded content image/card placeholder | Not a transparent food cutout. |
| `documents.techCardPreview` | document preview placeholder | Not final approved document sample. |
| `documents.costCardPreview` | document preview placeholder | Not final approved cost card sample. |
| `cta.kitchenBoard.desktop` | generated desktop final CTA brand band backdrop | Approved for current showcase; not a full production visual freeze. |
| `cta.kitchenBoard.mobile` | generated mobile final CTA brand band backdrop | Approved for current showcase; not a full production visual freeze. |

Production Asset Brief remains the future contract for generated/manual candidates, provenance, rights review and replacement. It is not a blocker for the current showcase stage.

## 2. Non-goals

- Не публиковать generated image напрямую в лендинг.
- Не добавлять registry entries для `hero.chef`, hero backdrop или final CTA edge decor до появления реальных файлов.
- Не генерировать production assets для текущего showcase только ради снятия placeholder status.
- Не создавать фиктивный provenance/rights approval для local scaffold assets.
- Не заменять product UI mockup generated art, если UI должен отражать фактический интерфейс продукта.
- Не использовать известных людей, чужие логотипы, брендовые предметы, персонажей или узнаваемые reference images без отдельного approval.
- Не обещать визуально функции, которые помечены как `unsupported_claim` или `forbidden_claim`.

## 3. Asset Package Matrix

| Target key | Asset kind | Background mode | Layer role | Z-slot | Primary use | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `hero.decor.backgroundKitchen` | `backdrop` | `environment` | `heroBackdrop` | `backdrop` | Среда hero-сцены | planned |
| `hero.chef` | `cutout` | `transparent` | `heroHumanCutout` | `midground` / `foreground` | Человеческий слой hero | planned, high-risk |
| `hero.dishCutout` or replacement `hero.dish` | `cutout` | `transparent` | `heroForegroundObject` | `foreground` | Блюдо поверх сцены/UI | planned |
| `cta.kitchenBoard.desktop` | `backdrop` | `embedded` | `finalCtaBrandBand` | `backdrop` | Контрастная финальная CTA-подложка desktop | generated/approved for showcase |
| `cta.kitchenBoard.mobile` | `backdrop` | `embedded` | `finalCtaBrandBand` | `backdrop` | Контрастная финальная CTA-подложка mobile | generated/approved for showcase |
| `finalCta.decor.*` | `edgeDecor` | `transparent` | `finalCtaEdgeDecor` | `foreground` | Декор по краям final CTA | planned |
| `documents.dishSample` or `documents.saladCaesar` | `contentImage` | `embedded` | `documentContent` | `none` | Карточка/калькуляционное изображение | optional |

`planned` означает, что asset contract уже описан, но registry entry нельзя создавать без файла, provenance and approval.

## 4. Hero Backdrop Brief

Target key: `hero.decor.backgroundKitchen`.

Role:

- background image для hero layered scene;
- задаёт теплую, профессиональную, ресторанно-производственную атмосферу;
- не является главным объектом и не спорит с текстом, product UI или cutouts.

Visual direction:

- современная кухня, ресторанный prep area или аккуратный production context;
- теплый, но не однотонно оранжевый свет;
- без видимых сторонних брендов, логотипов и читаемых этикеток;
- центр или левая часть должны оставаться спокойными под overlay/readability;
- допускается мягкая глубина резкости, но без темного stock-like blur.

Output:

- WebP/JPEG для production delivery;
- landscape crop, минимум desktop and mobile derivatives;
- no alpha requirement;
- contrast checked against hero text/product UI.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `backdrop` |
| `backgroundMode` | `environment` |
| `transparentBackground` | `false` |
| `layerRole` | `heroBackdrop` |
| `zSlot` | `backdrop` |
| `overlapPolicy` | `sceneOnly` |
| `safeArea` | `preserveTextAndCta` |
| `cropPolicy` | `coverCrop` |
| `shadowPolicy` | `none` |

## 5. Hero Human Cutout Brief

Target key: `hero.chef`.

Role:

- человек/шеф как живой слой hero-сцены;
- может частично перекрываться product UI и частично перекрывать его;
- работает только как approved cutout, а не как photo card.

Visual direction:

- реальный food-service professional, technologist, chef or production manager;
- neutral-to-confident pose, не рекламная улыбка в камеру;
- одежда аккуратная, без брендовых логотипов;
- не известный и не узнаваемый человек;
- без third-party props with visible brands.

Output:

- PNG/WebP with alpha;
- clean alpha edge around hair, hands, clothing;
- no baked background;
- predictable bounding box with enough transparent padding;
- optional separate contact shadow is allowed only as separate layer or CSS shadow.

Risk:

- `containsPeople: true`;
- requires manual rights/safety approval before public landing use;
- generated testimonial/person imagery cannot be presented as a real customer.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `cutout` |
| `backgroundMode` | `transparent` |
| `transparentBackground` | `true` |
| `layerRole` | `heroHumanCutout` |
| `zSlot` | `midground` or `foreground` |
| `overlapPolicy` | `sceneOnly` |
| `safeArea` | `preserveProductUiCore` |
| `cropPolicy` | `mayBleed` |
| `shadowPolicy` | `cssShadowAllowed` |

## 6. Hero Foreground Food Cutout Brief

Target key: `hero.dishCutout` or production replacement of `hero.dish`.

Role:

- foreground food object that adds depth and overlaps the scene;
- может заходить на границу hero visual, product UI frame или nearby shape;
- не должен закрывать H1, lead, CTA или product UI core fields.

Visual direction:

- тарелка, миска, борщ, суп, салат или другой визуально читаемый kitchen object;
- аппетитный, но не stock-like;
- angle compatible with product UI scene;
- no text, no labels, no logos.

Output:

- PNG/WebP with alpha;
- clean transparent background;
- stable bounding box;
- optional soft/contact shadow can be CSS-driven.

Important:

- текущий `hero.dish` в scaffold описан как `contentImage` with `embedded` background;
- менять его metadata на `cutout` можно только при фактической замене файла на transparent cutout;
- если нужен параллельный asset без риска, использовать новый key `hero.dishCutout`.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `cutout` |
| `backgroundMode` | `transparent` |
| `transparentBackground` | `true` |
| `layerRole` | `heroForegroundObject` |
| `zSlot` | `foreground` |
| `overlapPolicy` | `productUiOnly` or `sceneOnly` |
| `safeArea` | `preserveProductUiCore` |
| `cropPolicy` | `mayBleed` |
| `shadowPolicy` | `cssShadowAllowed` |

## 7. Final CTA Brand Band Brief

Target keys: `cta.kitchenBoard.desktop` and `cta.kitchenBoard.mobile`.

Legacy single-key note: `cta.kitchenBoard` is no longer sufficient for the full-width footer band because a 16:9 backdrop loses edge decor when cover-cropped into the desktop footer ratio.

Role:

- high-contrast final conversion band;
- визуально ближе к footer/reference treatment: насыщенная красно-терракотовая подложка, белый/inverse текст, strong CTA focus;
- не является обычной карточкой или декоративной картинкой.

Visual direction:

- глубокий red/terracotta/brand-food tone;
- texture or subtle kitchen/board/ingredients environment is allowed;
- center safe area must stay readable;
- text itself is rendered by UI, not baked into image;
- no logos, labels or visible third-party packaging.

Output:

- WebP/JPEG or CSS-backed bitmap depending on final implementation;
- no alpha requirement for the band itself;
- separate desktop/mobile raster derivatives, not one shared image scaled into both contexts;
- desktop derivative targets the short full-viewport footer band ratio;
- mobile derivative targets the compact mobile footer band ratio and preserves visible edge decor inside the narrow crop;
- enough contrast for inverse text tokens.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `backdrop` |
| `backgroundMode` | `embedded` or `environment` |
| `transparentBackground` | `false` |
| `layerRole` | `finalCtaBrandBand` |
| `zSlot` | `backdrop` |
| `overlapPolicy` | `none` |
| `safeArea` | `preserveTextAndCta` |
| `cropPolicy` | `coverCrop` |
| `shadowPolicy` | `none` |

## 8. Final CTA Edge Decor Brief

Target keys: `finalCta.decor.tomatoes`, `finalCta.decor.pepper`, `finalCta.decor.spices`, `finalCta.decor.herbs` or similar.

Role:

- edge decor around final CTA band;
- создает живость и глубину, но не конкурирует с heading/buttons;
- may bleed beyond band edges on desktop;
- may be hidden or simplified on compact screens.

Visual direction:

- food production objects: зелень, специи, овощи, доска, ложка, небольшие ингредиенты;
- no text, labels, packaging or brands;
- style compatible with hero food cutout and CTA band;
- objects should feel like real foreground material, not icons.

Output:

- PNG/WebP with alpha;
- clean transparent background;
- generous transparent padding;
- separate objects preferred over one baked collage if layout needs independent positioning.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `edgeDecor` |
| `backgroundMode` | `transparent` |
| `transparentBackground` | `true` |
| `layerRole` | `finalCtaEdgeDecor` |
| `zSlot` | `foreground` |
| `overlapPolicy` | `edgeOnly` |
| `safeArea` | `preserveTextAndCta` |
| `cropPolicy` | `mayBleed` |
| `shadowPolicy` | `cssShadowAllowed` |

## 9. Optional Content Image Brief

Target key: `documents.saladCaesar`, `documents.dishSample` or another approved document/card image.

Role:

- example image inside calculation/document card;
- communicates recipe, portion, ingredients or cost context;
- not a scene cutout.

Visual direction:

- Caesar salad with chicken or another recognizable dish;
- composed card/photo with its own background;
- crop must work inside stable card aspect ratio;
- can include plate/table/background as part of image;
- no alpha requirement.

Output:

- WebP/JPEG;
- embedded background;
- readable crop at document card size;
- no baked UI text unless it is part of an approved product/document mockup.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `contentImage` |
| `backgroundMode` | `embedded` |
| `transparentBackground` | `false` |
| `layerRole` | `documentContent` |
| `zSlot` | `none` |
| `overlapPolicy` | `none` |
| `safeArea` | `preserveCardContent` |
| `cropPolicy` | `coverCrop` or `contained` |
| `shadowPolicy` | `bakedShadowAllowed` |

## 9.1. Audience Card Media

Asset keys:

- `audience.restaurant`;
- `audience.chef`;
- `audience.production`;
- `audience.technologist`.

Role:

- top media layer inside an audience card;
- communicates a concrete food-service work context;
- not a product UI screenshot and not a transparent cutout.

Visual direction:

- realistic professional food-service photography;
- stable 16:9 crop for compact cards;
- no baked text, no logos, no readable labels, no third-party branded packaging;
- generic staff may appear, but the image must not rely on a recognizable person.

Registry target:

| Field | Value |
| --- | --- |
| `assetKind` | `contentImage` |
| `backgroundMode` | `embedded` |
| `transparentBackground` | `false` |
| `layerRole` | `audienceCardMedia` |
| `zSlot` | `none` |
| `overlapPolicy` | `none` |
| `safeArea` | `preserveCardContent` |
| `cropPolicy` | `coverCrop` |
| `shadowPolicy` | `none` |

## 10. Prompt Requirements

Every prompt or manual art request must include:

- target asset key and asset kind;
- background mode;
- transparency requirement;
- target section and layer role;
- aspect ratio and output format;
- forbidden elements: logos, labels, known people, brand packaging, fake UI text, unsupported claims;
- safe area rule;
- mobile behavior if the asset may be hidden or cropped.

For English-first providers, keep the production prompt in English and store a Russian operator summary next to it.

## 11. Acceptance Checklist

Before public use:

- cutout and edge decor assets have real alpha, clean edges and no baked environment;
- content images have embedded background and stable crop;
- backdrop/brand band preserve text and CTA readability;
- human asset has manual rights/safety approval;
- no visible third-party logos, labels, known characters or branded packaging;
- no generated readable UI text that implies unavailable product functions;
- registry metadata matches this brief and the Visual Asset Layering Contract;
- provenance record exists with source, provider/model if generated, prompt hash, rights status and approval status;
- mobile crop/hide behavior is checked;
- alt text is meaningful for content assets and empty for decorative assets.

## 12. Publishing Steps

1. Create or generate candidates outside public registry.
2. Review candidates against this brief and the reference composition.
3. Record provenance and rights metadata.
4. Approve selected candidates manually.
5. Add actual files under the approved landing asset storage path.
6. Add or update `AssetRegistry` keys only after files exist.
7. Run validation, lint, build and visual smoke checks.
8. Keep previous asset key or file available for rollback.

## 13. Follow-up Tasks

- Generate/review candidates for `hero.decor.backgroundKitchen`, `hero.chef`, hero food cutout and final CTA edge decor.
- Decide whether `hero.dish` is replaced in place or a new `hero.dishCutout` key is introduced.
- Keep final CTA brand band as separate `cta.kitchenBoard.desktop` and `cta.kitchenBoard.mobile` derivatives unless a future art direction changes the section ratio.
- Add asset provenance records before any public visual freeze.
- Re-run mobile/desktop screenshots after production assets are wired.
