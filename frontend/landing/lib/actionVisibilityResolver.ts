import { isForbiddenMaturity } from "@/landing/lib/claimMaturity";
import type { LandingMode, LandingModeConfig } from "@/landing/config/landingMode.config";
import { landingModeConfig } from "@/landing/config/landingMode.config";
import type { LandingAction, LandingActionId, LandingActionVisibility } from "@/landing/registries/cta.registry";

export type LandingActionPolicyState = "enabled" | "disabled" | "hidden" | "internal_only" | "owner_gated";

export type ResolvedLandingAction = LandingAction & {
  landingMode: LandingMode;
  policyState: LandingActionPolicyState;
  sourceEnabled: boolean;
  sourceVisibility: LandingActionVisibility;
  policyReason: string;
};

export type ResolvedLandingActions = Record<LandingActionId, ResolvedLandingAction>;

function disabledAction(
  action: LandingAction,
  config: LandingModeConfig,
  policyState: Exclude<LandingActionPolicyState, "enabled">,
  visibility: LandingActionVisibility,
  policyReason: string,
): ResolvedLandingAction {
  return {
    ...action,
    href: undefined,
    kind: "disabled",
    enabled: false,
    visibility,
    landingMode: config.mode,
    policyState,
    sourceEnabled: action.enabled,
    sourceVisibility: action.visibility,
    policyReason,
    disabledReason: action.disabledReason ?? policyReason,
  };
}

function enabledAction(action: LandingAction, config: LandingModeConfig): ResolvedLandingAction {
  return {
    ...action,
    enabled: true,
    visibility: "visible",
    landingMode: config.mode,
    policyState: "enabled",
    sourceEnabled: action.enabled,
    sourceVisibility: action.visibility,
    policyReason: "Action is available in the current landing mode.",
  };
}

function enabledMvpEntryAction(action: LandingAction, config: LandingModeConfig): ResolvedLandingAction {
  return {
    ...enabledAction(action, config),
    href: config.mvpEntry.href,
    kind: "link",
    policyReason: "MVP entry is owner-approved for showcase as an icon-only service action.",
  };
}

function gateVisibility(action: LandingAction): Exclude<LandingActionVisibility, "visible"> {
  return action.visibility === "hidden" ? "hidden" : "disabled";
}

function isFunctionAvailable(action: LandingAction, config: LandingModeConfig) {
  return config.functionAvailability[action.requiredFunction] === true;
}

function isOwnerGateOpen(action: LandingAction, config: LandingModeConfig) {
  return action.ownerApproved && config.ownerGates[action.requiredFunction] === true;
}

function canEnablePublicAction(action: LandingAction, config: LandingModeConfig) {
  return action.enabled && isFunctionAvailable(action, config) && !isForbiddenMaturity(action.maturity);
}

// STICKY-ACTION-POLICY:
// Showcase mode may expose MVP entry when owner-approved.
// Commercial actions remain hidden/disabled until beta/launch gates are closed.
export function resolveLandingAction(action: LandingAction, config: LandingModeConfig = landingModeConfig): ResolvedLandingAction {
  if (isForbiddenMaturity(action.maturity)) {
    return disabledAction(action, config, "hidden", "hidden", `Action ${action.id} has forbidden maturity ${action.maturity}.`);
  }

  if (action.role === "mvp_entry") {
    if (
      (config.mode === "showcase" || config.mode === "beta" || config.mode === "internal") &&
      canEnablePublicAction(action, config) &&
      isOwnerGateOpen(action, config) &&
      config.mvpEntry.href
    ) {
      return enabledMvpEntryAction(action, config);
    }

    return disabledAction(action, config, "owner_gated", "hidden", "MVP entry remains hidden until NEXT_PUBLIC_MVP_ENTRY_URL is configured.");
  }

  if (action.maturity === "decision_needed" && !isOwnerGateOpen(action, config)) {
    return disabledAction(action, config, "owner_gated", gateVisibility(action), `Action ${action.id} requires owner approval.`);
  }

  if (action.role === "internal") {
    if (config.mode === "internal" && canEnablePublicAction(action, config) && isOwnerGateOpen(action, config)) {
      return enabledAction(action, config);
    }

    return disabledAction(action, config, "internal_only", "hidden", `Action ${action.id} is internal-only in mode ${config.mode}.`);
  }

  if (action.role === "commercial") {
    if (config.mode === "launch" && canEnablePublicAction(action, config) && isOwnerGateOpen(action, config)) {
      return enabledAction(action, config);
    }

    return disabledAction(action, config, "owner_gated", gateVisibility(action), `Commercial action ${action.id} is gated in mode ${config.mode}.`);
  }

  if (action.role === "roadmap") {
    if (config.mode === "launch" && action.maturity !== "roadmap_claim" && canEnablePublicAction(action, config) && isOwnerGateOpen(action, config)) {
      return enabledAction(action, config);
    }

    return disabledAction(action, config, gateVisibility(action) === "hidden" ? "hidden" : "disabled", gateVisibility(action), `Roadmap action ${action.id} is not available-now.`);
  }

  if (!canEnablePublicAction(action, config)) {
    return disabledAction(action, config, gateVisibility(action), gateVisibility(action), `Action ${action.id} is unavailable in mode ${config.mode}.`);
  }

  return enabledAction(action, config);
}

export function resolveActionRegistry(
  actions: Record<LandingActionId, LandingAction>,
  config: LandingModeConfig = landingModeConfig,
): ResolvedLandingActions {
  return Object.fromEntries(
    Object.entries(actions).map(([actionId, action]) => [actionId, resolveLandingAction(action, config)]),
  ) as ResolvedLandingActions;
}
