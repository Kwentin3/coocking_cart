import { analyticsRegistry } from "@/landing/registries/analytics.registry";
import { actionRegistry } from "@/landing/registries/cta.registry";
import { iconRegistry } from "@/landing/registries/icon.registry";
import { assetRegistry } from "@/landing/registries/asset.registry";
import { sectionRegistry } from "@/landing/registries/section.registry";
import { landingModeConfig, landingModes } from "@/landing/config/landingMode.config";
import { resolveActionRegistry } from "@/landing/lib/actionVisibilityResolver";
import { claimRegistry, getClaim, isForbiddenMaturity, type ClaimRef } from "@/landing/lib/claimMaturity";
import { parseLandingContent, type LandingContent } from "./landingContent";

export type LandingValidationResult = {
  ok: boolean;
  errors: string[];
  warnings: string[];
  content?: LandingContent;
};

function collectClaimRefs(content: LandingContent): ClaimRef[] {
  return [
    ...content.hero.claimRefs,
    ...content.audience.items.flatMap((item) => item.claimRefs),
    ...content.benefits.items.flatMap((item) => item.claimRefs),
    ...content.workflow.steps.flatMap((step) => step.claimRefs),
    ...content.documents.claimRefs,
    ...content.documents.documentTypes.flatMap((item) => item.claimRefs),
    ...content.standards.claimRefs,
    ...content.finalCta.claimRefs,
    ...content.seo.claimRefs,
  ];
}

export function validateLandingContent(): LandingValidationResult {
  const warnings: string[] = [];
  const errors: string[] = [];
  const parsed = parseLandingContent();
  const resolvedActions = resolveActionRegistry(actionRegistry, landingModeConfig);

  if (!parsed.content) {
    return { ok: false, errors: parsed.errors, warnings };
  }

  const { content } = parsed;

  if (!landingModes.includes(landingModeConfig.mode)) {
    errors.push(`Landing mode ${landingModeConfig.mode} is not supported.`);
  }

  for (const section of sectionRegistry) {
    if (!(section.contentKey in content)) {
      errors.push(`Section ${section.id} points to missing content key ${section.contentKey}.`);
    }
    if (!section.enabled && section.id === "testimonials") {
      warnings.push(`Section ${section.id} disabled: ${section.reason ?? "no reason provided"}`);
    }
  }

  for (const action of Object.values(actionRegistry)) {
    if (!(action.analyticsEvent in analyticsRegistry)) {
      errors.push(`Action ${action.id} references missing analytics event ${action.analyticsEvent}.`);
    }
    if (!(action.requiredFunction in landingModeConfig.functionAvailability)) {
      errors.push(`Action ${action.id} references missing function availability key ${action.requiredFunction}.`);
    }
    if (!(action.requiredFunction in landingModeConfig.ownerGates)) {
      errors.push(`Action ${action.id} references missing owner gate key ${action.requiredFunction}.`);
    }
    if (isForbiddenMaturity(action.maturity)) {
      errors.push(`Action ${action.id} has forbidden maturity ${action.maturity}.`);
    }
    if (action.maturity === "decision_needed" && action.enabled) {
      errors.push(`Action ${action.id} is decision_needed but enabled.`);
    }
    if (action.maturity === "roadmap_claim" && action.enabled) {
      errors.push(`Action ${action.id} is roadmap_claim but enabled as available-now.`);
    }
    if (landingModeConfig.mode === "showcase" && action.role === "commercial" && action.visibility !== "hidden") {
      errors.push(`Commercial action ${action.id} must be hidden in showcase mode.`);
    }
  }

  // STICKY-ACTION-POLICY:
  // Validate resolved actions, not only raw registry state. Unsafe combinations must fail before render.
  for (const action of Object.values(resolvedActions)) {
    if (action.enabled && action.visibility !== "visible") {
      errors.push(`Resolved action ${action.id} is enabled but visibility is ${action.visibility}.`);
    }
    if (action.enabled && action.kind !== "disabled" && !action.href && (action.kind === "link" || action.kind === "scroll")) {
      errors.push(`Resolved action ${action.id} is enabled but has no href.`);
    }
    if (isForbiddenMaturity(action.maturity) && action.visibility !== "hidden") {
      errors.push(`Resolved action ${action.id} has forbidden maturity ${action.maturity} but is not hidden.`);
    }
    if (action.maturity === "decision_needed" && action.enabled) {
      errors.push(`Resolved action ${action.id} is decision_needed but enabled.`);
    }
    if (action.maturity === "roadmap_claim" && action.enabled) {
      errors.push(`Resolved action ${action.id} is roadmap_claim but enabled as available-now.`);
    }
    if (!landingModeConfig.functionAvailability[action.requiredFunction] && action.enabled) {
      errors.push(`Resolved action ${action.id} is enabled without real function availability ${action.requiredFunction}.`);
    }
    if (landingModeConfig.mode !== "launch" && action.role === "commercial" && action.enabled) {
      errors.push(`Commercial action ${action.id} is enabled in non-launch mode ${landingModeConfig.mode}.`);
    }
    if (landingModeConfig.mode === "showcase" && action.role === "commercial" && action.visibility !== "hidden") {
      errors.push(`Resolved commercial action ${action.id} must be hidden in showcase mode.`);
    }
    if (!landingModeConfig.ownerGates.mvpEntry && action.id === "nav.login" && action.enabled) {
      errors.push("MVP entry nav.login is enabled while MVP Entry Gate is not closed.");
    }
    if (!landingModeConfig.ownerGates.mvpEntry && action.id === "nav.login" && action.visibility === "visible") {
      errors.push("MVP entry nav.login is visible while MVP Entry Gate is not closed.");
    }
  }

  const assetDebugIds = new Map<string, string>();
  for (const asset of Object.values(assetRegistry)) {
    if (!asset.src.startsWith("/landing/assets/")) {
      errors.push(`Asset ${asset.key} must be served from /landing/assets/.`);
    }
    if (!/^A\d{2}$/.test(asset.debugId)) {
      errors.push(`Asset ${asset.key} debugId must use A00 format.`);
    }
    const existingAssetKey = assetDebugIds.get(asset.debugId);
    if (existingAssetKey) {
      errors.push(`Asset debugId ${asset.debugId} is duplicated by ${existingAssetKey} and ${asset.key}.`);
    }
    assetDebugIds.set(asset.debugId, asset.key);
    if (asset.role === "decorative" && asset.alt !== "") {
      errors.push(`Decorative asset ${asset.key} must use empty alt.`);
    }
    if (asset.role !== "decorative" && asset.alt.length === 0) {
      errors.push(`Content asset ${asset.key} must define alt text.`);
    }
    if ((asset.assetKind === "cutout" || asset.assetKind === "edgeDecor") && (!asset.transparentBackground || asset.backgroundMode !== "transparent")) {
      errors.push(`Layered asset ${asset.key} must use transparent background metadata.`);
    }
    if (asset.transparentBackground && asset.backgroundMode !== "transparent") {
      errors.push(`Asset ${asset.key} is marked transparent but backgroundMode is ${asset.backgroundMode}.`);
    }
    if ((asset.assetKind === "contentImage" || asset.assetKind === "documentPreview") && asset.backgroundMode !== "embedded") {
      errors.push(`Content image asset ${asset.key} must use embedded background mode.`);
    }
    if (asset.assetKind === "productUi" && asset.safeArea !== "preserveProductUiCore") {
      errors.push(`Product UI asset ${asset.key} must preserve product UI core safe area.`);
    }
    if (asset.layerRole === "finalCtaBrandBand" && asset.safeArea !== "preserveTextAndCta") {
      errors.push(`Final CTA brand band asset ${asset.key} must preserve text and CTA safe area.`);
    }
    if (asset.layerRole === "heroHumanCutout" && asset.assetKind !== "cutout") {
      errors.push(`Hero human layer ${asset.key} must be a cutout asset.`);
    }
    if (asset.layerRole === "audienceCardMedia" && (asset.assetKind !== "contentImage" || asset.safeArea !== "preserveCardContent")) {
      errors.push(`Audience card media asset ${asset.key} must be an embedded content image preserving card content.`);
    }
    if (
      asset.zSlot === "none" &&
      asset.layerRole !== "none" &&
      asset.layerRole !== "brandMark" &&
      asset.layerRole !== "audienceCardMedia" &&
      asset.layerRole !== "documentContent"
    ) {
      errors.push(`Layered asset ${asset.key} must declare a non-none zSlot.`);
    }
  }

  for (const [key, icon] of Object.entries(iconRegistry)) {
    if (!icon.component || icon.label.length === 0) {
      errors.push(`Icon ${key} is incomplete.`);
    }
  }

  for (const claimRef of collectClaimRefs(content)) {
    const claim = getClaim(claimRef);
    if (!claim) {
      errors.push(`Missing claim registry entry for ${claimRef}.`);
      continue;
    }
    if (isForbiddenMaturity(claim.maturity)) {
      errors.push(`Claim ${claimRef} has forbidden maturity ${claim.maturity}.`);
    }
  }

  for (const claim of Object.values(claimRegistry)) {
    if (claim.maturity === "decision_needed") {
      warnings.push(`Claim ${claim.id} requires owner decision before public launch.`);
    }
  }

  warnings.push(`Landing mode: ${landingModeConfig.mode}.`);
  if (resolvedActions["nav.login"].policyState === "owner_gated") {
    warnings.push("MVP entry nav.login remains owner-gated.");
  }

  if (content.testimonials.mode !== "approved" && content.testimonials.items.some((item) => item.isReal)) {
    errors.push("Testimonials contain real-looking entries while testimonials mode is not approved.");
  }

  return {
    ok: errors.length === 0,
    errors,
    warnings,
    content,
  };
}

if (process.argv[1]?.endsWith("validateLandingContent.ts")) {
  const result = validateLandingContent();

  for (const warning of result.warnings) {
    console.warn(`warning: ${warning}`);
  }

  if (!result.ok) {
    for (const error of result.errors) {
      console.error(`error: ${error}`);
    }
    process.exit(1);
  }

  console.log("Landing content validation passed.");
}
