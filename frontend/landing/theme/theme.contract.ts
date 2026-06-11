export type ColorToken =
  | "page"
  | "pageAlt"
  | "surface"
  | "surfaceMuted"
  | "surfaceRaised"
  | "text"
  | "textMuted"
  | "border"
  | "brand"
  | "brandStrong"
  | "action"
  | "actionStrong"
  | "actionSoft"
  | "success"
  | "warning"
  | "danger"
  | "focus";

export type ComponentTokenGroup = {
  button: {
    primary: string;
    secondary: string;
    ghost: string;
  };
  card: {
    default: string;
    raised: string;
    muted: string;
  };
  badge: {
    neutral: string;
    success: string;
    warning: string;
  };
};

export type LandingThemeContract = {
  name: "warmKitchen" | "neutralBusiness" | "accessible";
  colors: Record<ColorToken, string>;
  gradients: {
    hero: string;
  };
  components: ComponentTokenGroup;
};
