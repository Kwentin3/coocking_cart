import type { AudienceContent } from "@/landing/schemas";
import { InfoCard } from "@/landing/components/landing";
import { Container, ResponsiveGrid, SectionShell, Stack } from "@/landing/components/primitives";

type AudienceSectionProps = {
  content: AudienceContent;
};

export function AudienceSection({ content }: AudienceSectionProps) {
  return (
    <SectionShell id="audience" labelledBy="audience-title" spacing="regular" background="page">
      <Container width="wide">
        <Stack gap="lg">
          <div className="sectionIntro">
            <h2 id="audience-title">{content.title}</h2>
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
