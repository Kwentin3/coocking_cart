import type { BenefitsContent } from "@/landing/schemas";
import { InfoCard } from "@/landing/components/landing";
import { Container, ResponsiveGrid, SectionShell, Stack } from "@/landing/components/primitives";

type BenefitsSectionProps = {
  content: BenefitsContent;
};

export function BenefitsSection({ content }: BenefitsSectionProps) {
  return (
    <SectionShell id="benefits" labelledBy="benefits-title" spacing="regular" background="surface">
      <Container width="wide">
        <Stack gap="lg">
          <div className="sectionIntro">
            <h2 id="benefits-title">{content.title}</h2>
            <p>{content.description}</p>
          </div>
          <ResponsiveGrid variant="cards">
            {content.items.map((item) => (
              <InfoCard key={item.id} title={item.title} description={item.description} iconKey={item.iconKey} />
            ))}
          </ResponsiveGrid>
        </Stack>
      </Container>
    </SectionShell>
  );
}
