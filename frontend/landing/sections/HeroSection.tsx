import type { HeroContent } from "@/landing/schemas";
import type { ResolvedLandingAction } from "@/landing/lib/actionVisibilityResolver";
import type { LandingActionId } from "@/landing/registries/cta.registry";
import { HeroVisual } from "@/landing/components/landing";
import { Badge, Button, Cluster, Container, Icon, ResponsiveGrid, SectionShell, Stack } from "@/landing/components/primitives";

type HeroSectionProps = {
  content: HeroContent;
  actions: Record<LandingActionId, ResolvedLandingAction>;
};

export function HeroSection({ content, actions }: HeroSectionProps) {
  return (
    <SectionShell id="hero" labelledBy="hero-title" spacing="hero" background="alt">
      <Container width="wide">
        <ResponsiveGrid variant="heroSplit">
          <Stack gap="lg">
            <Badge variant="success" icon="brand.spark">{content.eyebrow}</Badge>
            <Stack gap="md">
              <h1 id="hero-title" className="heroTitle">{content.title}</h1>
              <p className="heroLead">{content.description}</p>
            </Stack>
            <Cluster gap="md">
              <Button action={actions[content.primaryActionId]} variant="primary" size="lg" iconRight="action.arrowRight" />
              <Button action={actions[content.secondaryActionId]} variant="secondary" size="lg" iconLeft="action.play" />
            </Cluster>
            <ul className="trustList" aria-label="Ключевые свойства">
              {content.trustItems.map((item) => (
                <li key={item.id}>
                  <Icon name={item.iconKey} variant="success" decorative />
                  <span>{item.text}</span>
                </li>
              ))}
            </ul>
          </Stack>
          <HeroVisual visual={content.visual} />
        </ResponsiveGrid>
      </Container>
    </SectionShell>
  );
}
