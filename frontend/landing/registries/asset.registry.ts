export const assetKeys = [
  "brand.logoMark",
  "hero.productUi",
  "hero.dish",
  "audience.restaurant",
  "audience.chef",
  "audience.production",
  "audience.technologist",
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
  | "audienceCardMedia"
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
  debugId: string;
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
    debugId: "A01",
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
    debugId: "A02",
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
    debugId: "A03",
    src: "/landing/assets/hero-dish-borscht.png",
    alt: "Тарелка борща на прозрачном фоне",
    width: 1024,
    height: 1024,
    role: "content",
    assetKind: "cutout",
    backgroundMode: "transparent",
    transparentBackground: true,
    layerRole: "heroForegroundObject",
    zSlot: "foreground",
    overlapPolicy: "productUiOnly",
    safeArea: "preserveProductUiCore",
    cropPolicy: "mayBleed",
    shadowPolicy: "cssShadowAllowed",
    loading: "lazy",
    priority: false,
    visibility: "hideCompact",
    aspectRatio: "1 / 1",
    rightsStatus: "approved",
  },
  "audience.restaurant": {
    key: "audience.restaurant",
    debugId: "A07",
    src: "/landing/assets/audience-restaurant.webp",
    alt: "Dining room and prep area in a restaurant context",
    width: 1536,
    height: 864,
    role: "content",
    assetKind: "contentImage",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "audienceCardMedia",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "preserveCardContent",
    cropPolicy: "coverCrop",
    shadowPolicy: "none",
    loading: "lazy",
    priority: false,
    visibility: "always",
    aspectRatio: "16 / 9",
    rightsStatus: "approved",
  },
  "audience.chef": {
    key: "audience.chef",
    debugId: "A08",
    src: "/landing/assets/audience-chef.webp",
    alt: "Chef preparing food at a professional kitchen station",
    width: 1536,
    height: 864,
    role: "content",
    assetKind: "contentImage",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "audienceCardMedia",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "preserveCardContent",
    cropPolicy: "coverCrop",
    shadowPolicy: "none",
    loading: "lazy",
    priority: false,
    visibility: "always",
    aspectRatio: "16 / 9",
    rightsStatus: "approved",
  },
  "audience.production": {
    key: "audience.production",
    debugId: "A09",
    src: "/landing/assets/audience-production.webp",
    alt: "Food production team working in a clean kitchen line",
    width: 1536,
    height: 864,
    role: "content",
    assetKind: "contentImage",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "audienceCardMedia",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "preserveCardContent",
    cropPolicy: "coverCrop",
    shadowPolicy: "none",
    loading: "lazy",
    priority: false,
    visibility: "always",
    aspectRatio: "16 / 9",
    rightsStatus: "approved",
  },
  "audience.technologist": {
    key: "audience.technologist",
    debugId: "A10",
    src: "/landing/assets/audience-technologist.webp",
    alt: "Kitchen technologist reviewing production data on a tablet",
    width: 1536,
    height: 864,
    role: "content",
    assetKind: "contentImage",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "audienceCardMedia",
    zSlot: "none",
    overlapPolicy: "none",
    safeArea: "preserveCardContent",
    cropPolicy: "coverCrop",
    shadowPolicy: "none",
    loading: "lazy",
    priority: false,
    visibility: "always",
    aspectRatio: "16 / 9",
    rightsStatus: "approved",
  },
  "documents.techCardPreview": {
    key: "documents.techCardPreview",
    debugId: "A04",
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
    debugId: "A05",
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
    debugId: "A06",
    src: "/landing/assets/cta-kitchen-board.generated.webp",
    alt: "",
    width: 1536,
    height: 864,
    role: "decorative",
    assetKind: "backdrop",
    backgroundMode: "embedded",
    transparentBackground: false,
    layerRole: "finalCtaBrandBand",
    zSlot: "backdrop",
    overlapPolicy: "none",
    safeArea: "preserveTextAndCta",
    cropPolicy: "coverCrop",
    shadowPolicy: "none",
    loading: "lazy",
    priority: false,
    visibility: "decorativeOnly",
    aspectRatio: "16 / 9",
    rightsStatus: "approved",
  },
};

export function resolveAsset(assetKey: LandingAssetKey) {
  return assetRegistry[assetKey];
}
