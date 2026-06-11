export type ResponsiveMode = "compact" | "comfortable" | "expanded" | "wide";

export const layoutTokens = {
  viewport: {
    compact: "22.5rem",
    comfortable: "48rem",
    expanded: "64rem",
    wide: "80rem",
  },
  container: {
    default: "var(--container)",
    wide: "var(--container-wide)",
    narrow: "min(100% - (var(--space-5) * 2), 54rem)",
  },
  grid: {
    heroSplit: "heroSplit",
    cards: "cards",
    twoColumn: "twoColumn",
    timeline: "timeline",
  },
  section: {
    regular: "regular",
    hero: "hero",
    compact: "compact",
  },
  ratio: {
    heroVisual: "16 / 11",
    cardImage: "4 / 3",
    documentPreview: "3 / 4",
    avatar: "1 / 1",
  },
  zIndex: {
    base: "base",
    raised: "raised",
    overlay: "overlay",
    header: "header",
    modal: "modal",
  },
} as const;

export type LayoutTokens = typeof layoutTokens;
