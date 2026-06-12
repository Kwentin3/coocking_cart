import type { ClaimMaturity } from "@/landing/lib/claimMaturity";
import type { LandingFunctionKey } from "@/landing/config/landingMode.config";
import type { LandingAnalyticsEvent } from "./analytics.registry";

export const actionIds = [
  "demo.request",
  "sample.project.view",
  "signup.freeStart",
  "pricing.view",
  "docx.download",
  "nav.login",
] as const;

export type LandingActionId = (typeof actionIds)[number];
export type LandingActionKind = "link" | "modal" | "form" | "scroll" | "disabled";
export type LandingActionVisibility = "visible" | "disabled" | "hidden";
export type LandingActionRole = "public" | "commercial" | "roadmap" | "mvp_entry" | "internal";

export type LandingAction = {
  id: LandingActionId;
  label: string;
  href?: string;
  kind: LandingActionKind;
  role: LandingActionRole;
  requiredFunction: LandingFunctionKey;
  analyticsEvent: LandingAnalyticsEvent;
  maturity: ClaimMaturity;
  enabled: boolean;
  visibility: LandingActionVisibility;
  ownerApproved: boolean;
  disabledReason?: string;
  fallbackActionId?: LandingActionId;
};

// STICKY-ACTION-POLICY:
// Future/commercial actions are not removed from the registry.
// Visibility is resolved through landing mode + maturity + owner gates.
export const actionRegistry: Record<LandingActionId, LandingAction> = {
  "demo.request": {
    id: "demo.request",
    label: "Обсудить пилот",
    kind: "disabled",
    role: "commercial",
    requiredFunction: "demoRequest",
    analyticsEvent: "landing_demo_request_click",
    maturity: "decision_needed",
    enabled: false,
    visibility: "hidden",
    ownerApproved: false,
    disabledReason: "Pilot discussion flow is gated in showcase mode.",
  },
  "sample.project.view": {
    id: "sample.project.view",
    label: "Посмотреть пример",
    href: "#documents",
    kind: "scroll",
    role: "public",
    requiredFunction: "sampleProject",
    analyticsEvent: "landing_sample_project_view_click",
    maturity: "mvp_scope",
    enabled: true,
    visibility: "visible",
    ownerApproved: true,
  },
  "signup.freeStart": {
    id: "signup.freeStart",
    label: "Начать бесплатно",
    kind: "disabled",
    role: "commercial",
    requiredFunction: "signup",
    analyticsEvent: "landing_disabled_cta_click",
    maturity: "decision_needed",
    enabled: false,
    visibility: "hidden",
    ownerApproved: false,
    disabledReason: "Free onboarding требует решения владельца продукта.",
    fallbackActionId: "demo.request",
  },
  "pricing.view": {
    id: "pricing.view",
    label: "Посмотреть тарифы",
    kind: "disabled",
    role: "commercial",
    requiredFunction: "pricing",
    analyticsEvent: "landing_disabled_cta_click",
    maturity: "decision_needed",
    enabled: false,
    visibility: "hidden",
    ownerApproved: false,
    disabledReason: "Публичная модель тарифов ещё не зафиксирована.",
  },
  "docx.download": {
    id: "docx.download",
    label: "Скачать DOCX",
    kind: "disabled",
    role: "roadmap",
    requiredFunction: "documentExport",
    analyticsEvent: "landing_disabled_cta_click",
    maturity: "roadmap_claim",
    enabled: false,
    visibility: "disabled",
    ownerApproved: false,
    disabledReason: "Экспорт документов показывается как roadmap capability, не как доступная функция.",
  },
  "nav.login": {
    id: "nav.login",
    label: "Вход в MVP",
    kind: "link",
    role: "mvp_entry",
    requiredFunction: "mvpEntry",
    analyticsEvent: "landing_nav_login_click",
    maturity: "mvp_scope",
    enabled: true,
    visibility: "visible",
    ownerApproved: true,
    disabledReason: "MVP entry requires NEXT_PUBLIC_MVP_ENTRY_URL.",
  },
};

export function getAction(actionId: LandingActionId) {
  return actionRegistry[actionId];
}
