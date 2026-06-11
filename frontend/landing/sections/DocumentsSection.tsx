import type { DocumentsContent } from "@/landing/schemas";
import type { ResolvedLandingAction } from "@/landing/lib/actionVisibilityResolver";
import type { LandingActionId } from "@/landing/registries/cta.registry";
import { DocumentCard } from "@/landing/components/landing";
import { AspectFrame, AssetImage, Button, Cluster, Container, ResponsiveGrid, SectionShell, Stack } from "@/landing/components/primitives";

type DocumentsSectionProps = {
  content: DocumentsContent;
  actions: Record<LandingActionId, ResolvedLandingAction>;
};

export function DocumentsSection({ content, actions }: DocumentsSectionProps) {
  return (
    <SectionShell id="documents" labelledBy="documents-title" spacing="regular" background="surface">
      <Container width="wide">
        <ResponsiveGrid variant="documents">
          <Stack gap="lg">
            <div className="sectionIntro sectionIntro--left">
              <h2 id="documents-title">{content.title}</h2>
              <p>{content.description}</p>
            </div>
            <div className="documentList">
              {content.documentTypes.map((item) => (
                <DocumentCard key={item.id} title={item.title} description={item.description} iconKey={item.iconKey} />
              ))}
            </div>
            <Cluster gap="md">
              <Button action={actions[content.sampleActionId]} variant="secondary" iconLeft="action.play" />
              <Button action={actions[content.exportActionId]} variant="outline" />
            </Cluster>
            <p className="sectionDisclaimer">{content.disclaimer}</p>
          </Stack>
          <div className="documentPreviews" aria-label="Примеры документов">
            {content.previewAssetKeys.map((assetKey) => (
              <AspectFrame key={assetKey} ratio="documentPreview" variant="raised">
                <AssetImage assetKey={assetKey} sizesToken="document" fit="contain" />
              </AspectFrame>
            ))}
          </div>
        </ResponsiveGrid>
      </Container>
    </SectionShell>
  );
}
