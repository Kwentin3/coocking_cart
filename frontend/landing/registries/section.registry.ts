export const sectionIds = [
  "header",
  "hero",
  "audience",
  "benefits",
  "workflow",
  "documents",
  "standards",
  "testimonials",
  "finalCta",
] as const;

export type LandingSectionId = (typeof sectionIds)[number];

export type SectionRegistryItem = {
  id: LandingSectionId;
  order: number;
  enabled: boolean;
  component: string;
  contentKey: string;
  riskLevel: "low" | "medium" | "high";
  reason?: string;
};

export const sectionRegistry: SectionRegistryItem[] = [
  { id: "header", order: 10, enabled: true, component: "HeaderSection", contentKey: "header", riskLevel: "low" },
  { id: "hero", order: 20, enabled: true, component: "HeroSection", contentKey: "hero", riskLevel: "medium" },
  { id: "audience", order: 30, enabled: true, component: "AudienceSection", contentKey: "audience", riskLevel: "low" },
  { id: "benefits", order: 40, enabled: true, component: "BenefitsSection", contentKey: "benefits", riskLevel: "medium" },
  { id: "workflow", order: 50, enabled: true, component: "WorkflowSection", contentKey: "workflow", riskLevel: "medium" },
  { id: "documents", order: 60, enabled: true, component: "DocumentsSection", contentKey: "documents", riskLevel: "high" },
  { id: "standards", order: 70, enabled: true, component: "StandardsSection", contentKey: "standards", riskLevel: "high" },
  {
    id: "testimonials",
    order: 80,
    enabled: false,
    component: "TestimonialsSection",
    contentKey: "testimonials",
    riskLevel: "high",
    reason: "Нет approved real testimonials; fake testimonials не выводятся публично.",
  },
  { id: "finalCta", order: 90, enabled: true, component: "FinalCtaSection", contentKey: "finalCta", riskLevel: "medium" },
];
