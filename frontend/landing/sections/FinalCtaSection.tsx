import type { FinalCtaContent } from "@/landing/schemas";
import type { ResolvedLandingAction } from "@/landing/lib/actionVisibilityResolver";
import type { LandingActionId } from "@/landing/registries/cta.registry";
import { AssetImage, Button, Cluster, Container, SectionShell, Stack } from "@/landing/components/primitives";

type FinalCtaSectionProps = {
  content: FinalCtaContent;
  actions: Record<LandingActionId, ResolvedLandingAction>;
};

export function FinalCtaSection({ content, actions }: FinalCtaSectionProps) {
  const primaryAction = actions[content.primaryActionId];
  const secondaryAction = actions[content.secondaryActionId];
  const hasVisibleActions = primaryAction.visibility !== "hidden" || secondaryAction.visibility !== "hidden";

  return (
    <SectionShell id="final-cta" labelledBy="final-cta-title" spacing="regular" background="brand">
      {/* STICKY-FINAL-CTA-BAND:
          Final CTA backdrop is a full-viewport brand band with protected text safe area.
          Edge/backdrop assets must not cover the heading, description or future buttons. */}
      <div className="finalCta__asset" aria-hidden="true">
        <AssetImage assetKey={content.decorativeAssetKey} fit="cover" sizesToken="banner" />
      </div>
      <Container width="wide">
        <div className="finalCta">
          <Stack gap="lg">
            <div className="sectionIntro sectionIntro--inverse sectionIntro--left">
              <h2 id="final-cta-title">{content.title}</h2>
              <p>{content.description}</p>
            </div>
            {hasVisibleActions ? (
              <Cluster gap="md">
                <Button action={primaryAction} variant="primary" size="lg" iconRight="action.arrowRight" />
                <Button action={secondaryAction} variant="outline" size="lg" />
              </Cluster>
            ) : null}
          </Stack>
        </div>
      </Container>
    </SectionShell>
  );
}
