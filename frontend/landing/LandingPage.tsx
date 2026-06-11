import type { ReactNode } from "react";
import { getLandingPageModel } from "@/landing/lib/getLandingPageModel";
import type { LandingSectionId } from "@/landing/registries/section.registry";
import {
  AudienceSection,
  BenefitsSection,
  DocumentsSection,
  FinalCtaSection,
  HeaderSection,
  HeroSection,
  StandardsSection,
  TestimonialsSection,
  WorkflowSection,
} from "@/landing/sections";

type LandingPageModel = ReturnType<typeof getLandingPageModel>;

const renderers: Record<LandingSectionId, (model: LandingPageModel) => ReactNode> = {
  header: (model) => (
    <HeaderSection
      content={model.content.header}
      actions={model.registries.actions}
      navItemAnalyticsEvent={model.registries.analytics.landing_nav_item_click.event}
    />
  ),
  hero: (model) => <HeroSection content={model.content.hero} actions={model.registries.actions} />,
  audience: (model) => <AudienceSection content={model.content.audience} />,
  benefits: (model) => <BenefitsSection content={model.content.benefits} />,
  workflow: (model) => <WorkflowSection content={model.content.workflow} />,
  documents: (model) => <DocumentsSection content={model.content.documents} actions={model.registries.actions} />,
  standards: (model) => <StandardsSection content={model.content.standards} />,
  testimonials: (model) => <TestimonialsSection content={model.content.testimonials} />,
  finalCta: (model) => <FinalCtaSection content={model.content.finalCta} actions={model.registries.actions} />,
};

export function LandingPage() {
  const model = getLandingPageModel();
  const sections = [...model.registries.sections]
    .filter((section) => section.enabled)
    .sort((a, b) => a.order - b.order);
  const headerSection = sections.find((section) => section.id === "header");
  const pageSections = sections.filter((section) => section.id !== "header");

  return (
    <>
      {headerSection ? renderers[headerSection.id](model) : null}
      <main>
        {pageSections.map((section) => (
          <div key={section.id} data-section-id={section.id}>
            {renderers[section.id](model)}
          </div>
        ))}
      </main>
    </>
  );
}
