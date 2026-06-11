import type { StandardsContent } from "@/landing/schemas";
import { StandardsBadge } from "@/landing/components/landing";
import { Container, SectionShell, Stack } from "@/landing/components/primitives";

type StandardsSectionProps = {
  content: StandardsContent;
};

export function StandardsSection({ content }: StandardsSectionProps) {
  return (
    <SectionShell id="standards" labelledBy="standards-title" spacing="compact" background="page">
      <Container width="narrow">
        <Stack gap="lg">
          <div className="sectionIntro">
            <h2 id="standards-title">{content.title}</h2>
            <p>{content.description}</p>
          </div>
          <ul className="standardsList">
            {content.items.map((item) => (
              <StandardsBadge key={item.id} text={item.text} iconKey={item.iconKey} />
            ))}
          </ul>
          <p className="sectionDisclaimer sectionDisclaimer--center">{content.disclaimer}</p>
        </Stack>
      </Container>
    </SectionShell>
  );
}
