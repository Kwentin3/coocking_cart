import type { LandingThemeContract } from "./theme.contract";

export const warmKitchenTheme: LandingThemeContract = {
  name: "warmKitchen",
  colors: {
    page: "var(--color-page)",
    pageAlt: "var(--color-page-alt)",
    surface: "var(--color-surface)",
    surfaceMuted: "var(--color-surface-muted)",
    surfaceRaised: "var(--color-surface-raised)",
    text: "var(--color-text)",
    textMuted: "var(--color-text-muted)",
    border: "var(--color-border)",
    brand: "var(--color-brand)",
    brandStrong: "var(--color-brand-strong)",
    action: "var(--color-action)",
    actionStrong: "var(--color-action-strong)",
    actionSoft: "var(--color-action-soft)",
    success: "var(--color-success)",
    warning: "var(--color-warning)",
    danger: "var(--color-danger)",
    focus: "var(--color-focus)",
  },
  gradients: {
    hero: "var(--gradient-hero)",
  },
  components: {
    button: {
      primary: "buttonPrimary",
      secondary: "buttonSecondary",
      ghost: "buttonGhost",
    },
    card: {
      default: "cardDefault",
      raised: "cardRaised",
      muted: "cardMuted",
    },
    badge: {
      neutral: "badgeNeutral",
      success: "badgeSuccess",
      warning: "badgeWarning",
    },
  },
};
