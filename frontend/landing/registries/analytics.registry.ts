export const analyticsEvents = [
  "landing_nav_item_click",
  "landing_nav_login_click",
  "landing_hero_primary_cta_click",
  "landing_hero_secondary_cta_click",
  "landing_audience_card_click",
  "landing_documents_type_click",
  "landing_sample_project_view_click",
  "landing_demo_request_click",
  "landing_disabled_cta_click",
  "landing_final_primary_cta_click",
] as const;

export type LandingAnalyticsEvent = (typeof analyticsEvents)[number];

export const analyticsRegistry: Record<LandingAnalyticsEvent, { event: LandingAnalyticsEvent; owner: string }> = {
  landing_nav_item_click: { event: "landing_nav_item_click", owner: "HeaderSection" },
  landing_nav_login_click: { event: "landing_nav_login_click", owner: "HeaderSection" },
  landing_hero_primary_cta_click: { event: "landing_hero_primary_cta_click", owner: "HeroSection" },
  landing_hero_secondary_cta_click: { event: "landing_hero_secondary_cta_click", owner: "HeroSection" },
  landing_audience_card_click: { event: "landing_audience_card_click", owner: "AudienceSection" },
  landing_documents_type_click: { event: "landing_documents_type_click", owner: "DocumentsSection" },
  landing_sample_project_view_click: { event: "landing_sample_project_view_click", owner: "DocumentsSection" },
  landing_demo_request_click: { event: "landing_demo_request_click", owner: "ActionRegistry" },
  landing_disabled_cta_click: { event: "landing_disabled_cta_click", owner: "ActionRegistry" },
  landing_final_primary_cta_click: { event: "landing_final_primary_cta_click", owner: "FinalCtaSection" },
};
