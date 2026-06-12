const enabledValues = new Set(["1", "true", "yes", "on"]);
const disabledValues = new Set(["0", "false", "no", "off"]);

export const landingVisualDebugConfig = {
  assetIdsEnabledByDefault: enabledValues.has(
    (process.env.NEXT_PUBLIC_LANDING_ASSET_DEBUG_IDS ?? "").trim().toLowerCase(),
  ),
  assetIdsQueryParam: "assetDebugIds",
  assetIdsStorageKey: "landing.assetDebugIds",
} as const;

export function parseVisualDebugToggle(value: string | null): boolean | null {
  if (value === null) {
    return null;
  }

  const normalized = value.trim().toLowerCase();
  if (enabledValues.has(normalized)) {
    return true;
  }
  if (disabledValues.has(normalized)) {
    return false;
  }
  return null;
}
