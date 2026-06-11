export const assetKeys = [
  "brand.logoMark",
  "hero.productUi",
  "hero.dish",
  "documents.techCardPreview",
  "documents.costCardPreview",
  "cta.kitchenBoard",
] as const;

export type LandingAssetKey = (typeof assetKeys)[number];
export type LandingAssetRole = "brand" | "content" | "product-ui" | "document-preview" | "decorative";
export type LandingAssetVisibility = "always" | "hideCompact" | "decorativeOnly";
// STICKY-ASSET-LAYERS:
// Cutout assets require transparent backgrounds; content images usually keep embedded backgrounds.
// Layering belongs in registry metadata + composed visuals, not in section-local z-index hacks.
export type LandingAssetKind = "brand" | "cutout" | "contentImage" | "backdrop" | "productUi" | "edgeDecor" | "documentPreview" | "avatar";
export type LandingAssetBackgroundMode = "transparent" | "embedded" | "environment" | "solid";
export type LandingAssetLayerRole =
  | "none"
  | "brandMark"
  | "heroBackdrop"
  | "heroProductUi"
  | "heroHumanCutout"
  | "heroForegroundObject"
  | "documentContent"
  | "finalCtaBrandBand"
  | "finalCtaEdgeDecor";
export type LandingAssetZSlot = "none" | "backdrop" | "base" | "midground" | "foreground" | "overlay";
export type LandingAssetOverlapPolicy = "none" | "sceneOnly" | "productUiOnly" | "edgeOnly";
export type LandingAssetSafeArea = "none" | "preserveTextAndCta" | "preserveProductUiCore" | "preserveCardContent";
export type LandingAssetCropPolicy = "contained" | "coverCrop" | "mayBleed";
export type LandingAssetShadowPolicy = "none" | "cssShadowAllowed" | "bakedShadowAllowed";

export type LandingAsset = {
  key: LandingAssetKey;
  src: string;
  alt: string;
  width: number;
  height: number;
  role: LandingAssetRole;
  assetKind: LandingAssetKind;
  backgroundMode: LandingAssetBackgroundMode;
  transparentBackground: boolean;
  layerRole: LandingAssetLayerRole;
  zSlot: LandingAssetZSlot;
  overlapPolicy: LandingAssetOverlapPolicy;
  safeArea: LandingAssetSafeArea;
  cropPolicy: LandingAssetCropPolicy;
  shadowPolicy: LandingAssetShadowPolicy;
  loading: "eager" | "lazy";
  priority: boolean;
  visibility: LandingAssetVisibility;
  aspectRatio: string;
  rightsStatus: "local-scaffold" | "approved";
};

export const assetRegistry: Record<LandingAssetKey, LandingAsset> = {
  "brand.logoMark": {
    key: "brand.logoMark",
    src: "/landing/assets/logo-mark.svg",
    alt: "Знак ТехКухня",
    width: 96,
    height: 96,
    role: "brand",
    assetKind: "brand",
    backgroundMode: "solid",
    transparentBackground: false,
    layerRole: "brandMark",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "none",
    cropPolicy: "contained",
    shadowPolicy: "none",
    loading: "eager",
    priority: true,
    visibility: "always",
    aspectRatio: "1 / 1",
    rightsStatus: "local-scaffold",
  },
  "hero.productUi": {
    key: "hero.productUi",
    src: "/landing/assets/product-ui-preview.svg",
    alt: "Интерфейс ТехКухни с карточкой блюда, расчётами и документами",
    width: 960,
    height: 660,
    role: "product-ui",
    assetKind: "productUi",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "heroProductUi",
    zSlot: "base",
    overlapPolicy: "sceneOnly",
    safeArea: "preserveProductUiCore",
    cropPolicy: "contained",
    shadowPolicy: "cssShadowAllowed",
    loading: "eager",
    priority: true,
    visibility: "always",
    aspectRatio: "16 / 11",
    rightsStatus: "local-scaffold",
  },
  "hero.dish": {
    key: "hero.dish",
    src: "/landing/assets/dish-card.svg",
    alt: "Карточка блюда с выходом, себестоимостью и технологическим статусом",
    width: 720,
    height: 540,
    role: "content",
    assetKind: "contentImage",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "heroForegroundObject",
    zSlot: "foreground",
    overlapPolicy: "productUiOnly",
    safeArea: "preserveCardContent",
    cropPolicy: "contained",
    shadowPolicy: "cssShadowAllowed",
    loading: "lazy",
    priority: false,
    visibility: "hideCompact",
    aspectRatio: "4 / 3",
    rightsStatus: "local-scaffold",
  },
  "documents.techCardPreview": {
    key: "documents.techCardPreview",
    src: "/landing/assets/tech-card-preview.svg",
    alt: "Предпросмотр технологической карты",
    width: 720,
    height: 960,
    role: "document-preview",
    assetKind: "documentPreview",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "documentContent",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "preserveCardContent",
    cropPolicy: "contained",
    shadowPolicy: "cssShadowAllowed",
    loading: "lazy",
    priority: false,
    visibility: "always",
    aspectRatio: "3 / 4",
    rightsStatus: "local-scaffold",
  },
  "documents.costCardPreview": {
    key: "documents.costCardPreview",
    src: "/landing/assets/cost-card-preview.svg",
    alt: "Предпросмотр расчётной карточки блюда",
    width: 720,
    height: 960,
    role: "document-preview",
    assetKind: "documentPreview",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "documentContent",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "preserveCardContent",
    cropPolicy: "contained",
    shadowPolicy: "cssShadowAllowed",
    loading: "lazy",
    priority: false,
    visibility: "hideCompact",
    aspectRatio: "3 / 4",
    rightsStatus: "local-scaffold",
  },
  "cta.kitchenBoard": {
    key: "cta.kitchenBoard",
    src: "/landing/assets/kitchen-board.svg",
    alt: "",
    width: 900,
    height: 520,
    role: "decorative",
    assetKind: "backdrop",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "finalCtaBrandBand",
    zSlot: "backdrop",
    overlapPolicy: "edgeOnly",
    safeArea: "preserveTextAndCta",
    cropPolicy: "mayBleed",
    shadowPolicy: "none",
    loading: "lazy",
    priority: false,
    visibility: "decorativeOnly",
    aspectRatio: "16 / 9",
    rightsStatus: "local-scaffold",
  },
};

export function resolveAsset(assetKey: LandingAssetKey) {
  return assetRegistry[assetKey];
}
