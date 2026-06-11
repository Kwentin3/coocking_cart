import audienceRaw from "@/landing/content/ru/audience.json";
import benefitsRaw from "@/landing/content/ru/benefits.json";
import documentsRaw from "@/landing/content/ru/documents.json";
import finalCtaRaw from "@/landing/content/ru/finalCta.json";
import headerRaw from "@/landing/content/ru/header.json";
import heroRaw from "@/landing/content/ru/hero.json";
import seoRaw from "@/landing/content/ru/seo.json";
import standardsRaw from "@/landing/content/ru/standards.json";
import testimonialsRaw from "@/landing/content/ru/testimonials.json";
import workflowRaw from "@/landing/content/ru/workflow.json";
import {
  audienceSchema,
  benefitsSchema,
  documentsSchema,
  finalCtaSchema,
  headerSchema,
  heroSchema,
  seoSchema,
  standardsSchema,
  testimonialsSchema,
  workflowSchema,
  type AudienceContent,
  type BenefitsContent,
  type DocumentsContent,
  type FinalCtaContent,
  type HeaderContent,
  type HeroContent,
  type SeoContent,
  type StandardsContent,
  type TestimonialsContent,
  type WorkflowContent,
} from "@/landing/schemas";

export type LandingContent = {
  header: HeaderContent;
  hero: HeroContent;
  audience: AudienceContent;
  benefits: BenefitsContent;
  workflow: WorkflowContent;
  documents: DocumentsContent;
  standards: StandardsContent;
  testimonials: TestimonialsContent;
  finalCta: FinalCtaContent;
  seo: SeoContent;
};

const schemaEntries = {
  header: { raw: headerRaw, schema: headerSchema },
  hero: { raw: heroRaw, schema: heroSchema },
  audience: { raw: audienceRaw, schema: audienceSchema },
  benefits: { raw: benefitsRaw, schema: benefitsSchema },
  workflow: { raw: workflowRaw, schema: workflowSchema },
  documents: { raw: documentsRaw, schema: documentsSchema },
  standards: { raw: standardsRaw, schema: standardsSchema },
  testimonials: { raw: testimonialsRaw, schema: testimonialsSchema },
  finalCta: { raw: finalCtaRaw, schema: finalCtaSchema },
  seo: { raw: seoRaw, schema: seoSchema },
} as const;

export function parseLandingContent(): { content?: LandingContent; errors: string[] } {
  const errors: string[] = [];
  const parsed: Partial<LandingContent> = {};

  for (const [key, entry] of Object.entries(schemaEntries)) {
    const result = entry.schema.safeParse(entry.raw);
    if (!result.success) {
      errors.push(`${key}: ${result.error.issues.map((issue) => issue.message).join("; ")}`);
      continue;
    }
    Object.assign(parsed, { [key]: result.data });
  }

  if (errors.length > 0) {
    return { errors };
  }

  return { content: parsed as LandingContent, errors };
}
