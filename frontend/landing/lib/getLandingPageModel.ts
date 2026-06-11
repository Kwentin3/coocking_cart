import { actionRegistry, analyticsRegistry, assetRegistry, iconRegistry, sectionRegistry } from "@/landing/registries";
import { landingModeConfig } from "@/landing/config/landingMode.config";
import { layoutTokens, motionTokens, typographyTokens, warmKitchenTheme } from "@/landing/theme";
import { resolveActionRegistry } from "./actionVisibilityResolver";
import { validateLandingContent } from "./validateLandingContent";

export function getLandingPageModel() {
  const validation = validateLandingContent();
  const resolvedActions = resolveActionRegistry(actionRegistry, landingModeConfig);

  if (!validation.ok || !validation.content) {
    throw new Error(`Landing validation failed: ${validation.errors.join(" | ")}`);
  }

  return {
    content: validation.content,
    landingMode: landingModeConfig.mode,
    landingModeConfig,
    registries: {
      actions: resolvedActions,
      rawActions: actionRegistry,
      analytics: analyticsRegistry,
      assets: assetRegistry,
      icons: iconRegistry,
      sections: sectionRegistry,
    },
    theme: warmKitchenTheme,
    layout: layoutTokens,
    typography: typographyTokens,
    motion: motionTokens,
    validation,
  };
}
