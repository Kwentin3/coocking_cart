import type { FinalCtaContent } from "@/landing/schemas";
import type { ResolvedLandingAction } from "@/landing/lib/actionVisibilityResolver";
import type { LandingActionId } from "@/landing/registries/cta.registry";
import { AssetImage, Button, Cluster, Container, Icon, SectionShell, Stack } from "@/landing/components/primitives";

type FinalCtaSectionProps = {
  content: FinalCtaContent;
  actions: Record<LandingActionId, ResolvedLandingAction>;
};

export function FinalCtaSection({ content, actions }: FinalCtaSectionProps) {
  return (
    <SectionShell id="final-cta" labelledBy="final-cta-title" spacing="regular" background="brand">
      <Container width="wide">
        <div className="finalCta">
          <Stack gap="lg">
            <div className="sectionIntro sectionIntro--inverse sectionIntro--left">
              <h2 id="final-cta-title">{content.title}</h2>
              <p>{content.description}</p>
            </div>
            <Cluster gap="md">
              <Button action={actions[content.primaryActionId]} variant="primary" size="lg" iconRight="action.arrowRight" />
              <Button action={actions[content.secondaryActionId]} variant="outline" size="lg" />
            </Cluster>
            <div className="ownerGate" id="owner-gates">
              <h3>{content.ownerGateTitle}</h3>
              <ul>
                {content.ownerGateItems.map((item) => (
                  <li key={item}>
                    <Icon name="standard.check" variant="success" decorative />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </Stack>
          {/* STICKY-FINAL-CTA-BAND:
              Final CTA uses a high-contrast brand band with protected text/CTA safe area.
              Edge/backdrop assets must not cover the heading, terms or buttons. */}
          <div className="finalCta__asset" aria-hidden="true">
            <AssetImage assetKey={content.decorativeAssetKey} fit="contain" sizesToken="decorative" />
          </div>
        </div>
      </Container>
    </SectionShell>
  );
}
