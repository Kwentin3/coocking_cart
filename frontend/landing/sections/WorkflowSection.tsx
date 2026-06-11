import type { WorkflowContent } from "@/landing/schemas";
import { StepCard } from "@/landing/components/landing";
import { Container, ResponsiveGrid, SectionShell, Stack } from "@/landing/components/primitives";

type WorkflowSectionProps = {
  content: WorkflowContent;
};

export function WorkflowSection({ content }: WorkflowSectionProps) {
  return (
    <SectionShell id="workflow" labelledBy="workflow-title" spacing="regular" background="page">
      <Container width="wide">
        <Stack gap="lg">
          <div className="sectionIntro">
            <h2 id="workflow-title">{content.title}</h2>
            <p>{content.description}</p>
          </div>
          <ResponsiveGrid variant="timeline">
            {content.steps.map((step, index) => (
              <StepCard key={step.id} index={index + 1} title={step.title} description={step.description} iconKey={step.iconKey} />
            ))}
          </ResponsiveGrid>
        </Stack>
      </Container>
    </SectionShell>
  );
}
