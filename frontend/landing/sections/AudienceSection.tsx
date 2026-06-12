import type { AudienceContent } from "@/landing/schemas";
import { AudienceCard } from "@/landing/components/landing";
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
              <AudienceCard
                key={item.id}
                title={item.title}
                description={item.description}
                imageAssetKey={item.imageAssetKey}
                iconKey={item.iconKey}
                iconVariant={item.iconVariant}
              />
            ))}
          </ResponsiveGrid>
        </Stack>
      </Container>
    </SectionShell>
  );
}
