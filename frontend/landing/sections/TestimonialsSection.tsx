import type { TestimonialsContent } from "@/landing/schemas";
import { Card, Container, ResponsiveGrid, SectionShell, Stack } from "@/landing/components/primitives";

type TestimonialsSectionProps = {
  content: TestimonialsContent;
};

export function TestimonialsSection({ content }: TestimonialsSectionProps) {
  if (content.mode !== "approved") {
    return null;
  }

  return (
    <SectionShell id="testimonials" labelledBy="testimonials-title" spacing="regular" background="surface">
      <Container width="wide">
        <Stack gap="lg">
          <div className="sectionIntro">
            <h2 id="testimonials-title">{content.title}</h2>
          </div>
          <ResponsiveGrid variant="cards">
            {content.items.map((item) => (
              <Card key={item.id} variant="default">
                <Stack gap="sm">
                  <blockquote className="testimonialQuote">{item.quote}</blockquote>
                  <p className="testimonialAuthor">{item.author}</p>
                  <p className="cardText">{item.role}</p>
                </Stack>
              </Card>
            ))}
          </ResponsiveGrid>
        </Stack>
      </Container>
    </SectionShell>
  );
}
