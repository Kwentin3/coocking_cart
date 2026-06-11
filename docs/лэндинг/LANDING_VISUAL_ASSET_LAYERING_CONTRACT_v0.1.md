# Landing Visual Asset Layering Contract v0.1

<!-- STICKY-ASSET-LAYERS:
Лендинг использует не один тип "картинок", а разные asset kinds: cutout, content image, backdrop, product UI and edge decor.
Прозрачный фон нужен только там, где ассет является слоем сцены. Content image внутри карточки обычно должен иметь встроенный фон.
-->

Статус: рабочий визуальный контракт для графических ассетов, layered hero scene и final CTA brand band.
Дата: 2026-06-11.

Связанные документы:

- [Visual Tech Contract](LANDING_VISUAL_TECH_CONTRACT_v0.1.md)
- [Production Asset Brief](LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md)
- [Asset & Icon Registry Contract](LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
- [Landing Implementation Handoff](LANDING_IMPLEMENTATION_HANDOFF_v0.1.md)
- [AI Asset Generation Pipeline](../ai-asset-generation-pipeline.md)
- [Asset Provenance and Rights](../asset-provenance-and-rights.md)

## 1. Executive Summary

Визуальная модель лендинга должна поддерживать живую композицию, похожую на референс:

- hero работает как layered product scene;
- часть объектов может иметь прозрачный фон и пересекать границы визуальной зоны;
- product UI может перекрываться foreground objects, но его ключевые зоны должны оставаться читаемыми;
- final CTA работает как high-contrast brand band с фоновым/краевым декором и белым/inverse текстом;
- content images внутри карточек остаются обычными изображениями с собственным фоном и не притворяются cutout-ассетами.

Главное правило: прозрачность, слои и overlap являются metadata ассета и композиции, а не локальным CSS-хакингом секции.

## 2. Asset Taxonomy

| Asset kind | Background mode | Typical use | Rule |
| --- | --- | --- | --- |
| `cutout` | `transparent` | тарелка с борщом в hero, человек/шеф, отдельные предметы | Требует PNG/WebP/SVG с alpha или прозрачным canvas; может участвовать в overlap. |
| `contentImage` | `embedded` | салат Цезарь в карточке, фото блюда, аудитория | Имеет собственный фон/кроп; используется внутри карточки или frame. |
| `backdrop` | `environment` / `embedded` / `solid` | кухня на фоне hero, красный/терракотовый CTA band | Не является foreground object; обязан сохранять readable overlay/safe area. |
| `productUi` | `embedded` | экран продукта, document UI, карточка интерфейса | Должен сохранять читаемость ключевых зон. |
| `edgeDecor` | `transparent` | овощи/зелень/специи по краям CTA/footer | Требует alpha; не перекрывает текст и кнопки. |
| `documentPreview` | `embedded` | preview ТК/ТТК/калькуляционной карты | Содержательное изображение с alt и фиксированным aspect ratio. |
| `avatar` | `embedded` | реальные approved testimonials или fallback portrait | Требует прав/approval; не выдаёт placeholder за реального человека. |
| `brand` | `solid` / `transparent` | логотип, знак | Управляется бренд-контрактом. |

## 3. Background Modes

| Mode | Meaning |
| --- | --- |
| `transparent` | У ассета нет baked background; он должен работать как слой поверх других объектов. |
| `embedded` | Фон является частью изображения или карточки. Это нормально для content images и document previews. |
| `environment` | Фоновая среда: кухня, интерьер, размытый production context. |
| `solid` | Знак, logo mark или плоский брендовый объект. |

Запрет: нельзя требовать прозрачный фон от всех ассетов. Это сломает карточки блюд и document previews.

## 4. Hero Layered Scene

Hero должен восприниматься как сцена, а не как "текст слева, картинка справа".

Целевые слои:

1. `heroBackdrop`: environment/backdrop image, например тёплая кухня.
2. `heroProductUi`: интерфейс продукта.
3. `heroHumanCutout`: человек/шеф на прозрачном фоне.
4. `heroForegroundObject`: тарелка/блюдо/предмет на прозрачном фоне или content card.
5. `heroMetricCard`: UI floating panel.
6. `heroDecor`: optional herbs/spices/light accents.

Overlap rules:

- cutout может пересекать product UI и backdrop;
- foreground food object может заходить на границу текстовой и визуальной зоны;
- product UI может частично перекрывать human cutout;
- human cutout может частично перекрывать product UI;
- H1, lead text, primary CTA и secondary CTA являются protected safe area;
- product UI core fields are protected safe area;
- no horizontal overflow on mobile/desktop.

## 5. Final CTA Brand Band

Final CTA должен работать как high-contrast brand band:

- насыщенный брендовый фон или bitmap backdrop;
- inverse text mode: белый/светлый текст через semantic token, не raw `#fff` в секции;
- CTA/buttons имеют отдельные inverse/brand variants;
- food/edge decor находится по краям и не перекрывает смысловой центр;
- safe area защищает heading, description, terms/owner gate и buttons;
- на mobile декоративные объекты могут скрываться или уходить ниже текста.

Это не обычный footer и не просто decorative image. Это финальная конверсионная сцена.

## 6. Required Registry Metadata

Каждый asset record должен иметь:

```ts
type LandingAsset = {
  assetKind: "brand" | "cutout" | "contentImage" | "backdrop" | "productUi" | "edgeDecor" | "documentPreview" | "avatar";
  backgroundMode: "transparent" | "embedded" | "environment" | "solid";
  transparentBackground: boolean;
  layerRole:
    | "none"
    | "brandMark"
    | "heroBackdrop"
    | "heroProductUi"
    | "heroHumanCutout"
    | "heroForegroundObject"
    | "documentContent"
    | "finalCtaBrandBand"
    | "finalCtaEdgeDecor";
  zSlot: "none" | "backdrop" | "base" | "midground" | "foreground" | "overlay";
  overlapPolicy: "none" | "sceneOnly" | "productUiOnly" | "edgeOnly";
  safeArea: "none" | "preserveTextAndCta" | "preserveProductUiCore" | "preserveCardContent";
  cropPolicy: "contained" | "coverCrop" | "mayBleed";
  shadowPolicy: "none" | "cssShadowAllowed" | "bakedShadowAllowed";
};
```

## 7. Validation Rules

Validation must fail if:

- `cutout` or `edgeDecor` does not use `transparentBackground: true` and `backgroundMode: "transparent"`;
- `contentImage` or `documentPreview` does not use `backgroundMode: "embedded"`;
- `productUi` does not preserve `preserveProductUiCore`;
- `finalCtaBrandBand` does not preserve `preserveTextAndCta`;
- `heroHumanCutout` is not a `cutout`;
- content assets have empty alt;
- decorative assets have non-empty alt.

Validation may warn if:

- a backdrop has no overlay/readability note;
- an edge decor asset is not hidden on compact screens;
- a hero cutout is priority-loaded without being LCP-critical.

## 8. Asset Generation Guidance

Первый production-пакет hero/final CTA ассетов описан в [Production Asset Brief](LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md). Этот layering contract задает правила типов, слоев и safe areas; production brief задает конкретные asset briefs, target keys and acceptance checklist.

Prompt templates and manual asset briefs must specify asset kind:

- for `cutout`: transparent background, clean alpha, no baked environment, predictable bounding box, optional separate/contact shadow;
- for `contentImage`: composed image with background, stable crop, no alpha requirement;
- for `backdrop`: environment image with calm center or overlay-ready area;
- for `edgeDecor`: transparent PNG/WebP, objects positioned for edges, no text;
- for `productUi`: readable UI, no fake current availability beyond claim maturity.

Generated people/human cutouts remain high risk and require manual approval.

## 9. Implementation Notes

- `HeroVisual` owns hero composition order.
- `FinalCtaSection` owns final CTA brand band safe area.
- `AssetImage` reads physical metadata from `AssetRegistry`.
- Sections must not use raw `z-index`, physical asset paths or local overlap rules.
- CSS can use stable hooks like `data-asset-kind`, `data-layer-role` and named classes, but values come from registry/theme contracts.

## 10. Current Scaffold State

Current scaffold assets are local SVGs, not production-ready generated/approved assets:

| Current key | Current interpretation | Placeholder policy |
| --- | --- | --- |
| `brand.logoMark` | `brand`, solid mark. | `local-scaffold`; not production brand freeze. |
| `hero.productUi` | `productUi`, embedded background, hero product UI layer. | `local-scaffold`; acceptable for showcase placeholder. |
| `hero.dish` | `contentImage`, embedded background, current scaffold foreground object/card. | `local-scaffold`; do not reclassify as `cutout` without transparent file. |
| `documents.techCardPreview` | `documentPreview`, embedded background. | `local-scaffold`; not final approved document sample. |
| `documents.costCardPreview` | `documentPreview`, embedded background. | `local-scaffold`; not final approved cost card sample. |
| `cta.kitchenBoard` | `backdrop`, embedded brand band/decor scaffold with text/CTA safe area requirement. | `local-scaffold`; acceptable for showcase placeholder. |

Current showcase publish may use these placeholder/scaffold assets. This is not a production asset freeze and does not create provenance/rights approval.

Future production replacement may add:

- `hero.chef` as `cutout` / `heroHumanCutout`;
- `hero.dishCutout` or replacement `hero.dish` as `cutout` / `heroForegroundObject`;
- `hero.decor.backgroundKitchen` as `backdrop` / `heroBackdrop`;
- `finalCta.decor.*` as `edgeDecor` / `finalCtaEdgeDecor`.

Those additions require actual files, registry entries, provenance/rights metadata and validation before public use.
Use [Production Asset Brief](LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md) before creating or reviewing those files.

Do not add those planned keys only to satisfy composition ambitions. Until real files exist, sections must continue to use the current registry-backed scaffold assets.
