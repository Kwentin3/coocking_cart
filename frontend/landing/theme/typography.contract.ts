export const typographyTokens = {
  family: {
    body: "var(--font-sans)",
    display: "var(--font-display)",
  },
  size: {
    eyebrow: "var(--type-eyebrow)",
    body: "var(--type-body)",
    bodyLarge: "var(--type-body-large)",
    h1: "var(--type-h1)",
    h2: "var(--type-h2)",
    h3: "var(--type-h3)",
  },
  weight: {
    regular: 400,
    medium: 550,
    semibold: 650,
    bold: 750,
  },
  lineHeight: {
    tight: 1.08,
    heading: 1.15,
    body: 1.55,
  },
} as const;

export type TypographyTokens = typeof typographyTokens;
