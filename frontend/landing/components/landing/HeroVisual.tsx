import type { HeroContent } from "@/landing/schemas";
import { AspectFrame, AssetImage, Badge, FloatingPanel, Stack } from "@/landing/components/primitives";

type HeroVisualProps = {
  visual: HeroContent["visual"];
};

export function HeroVisual({ visual }: HeroVisualProps) {
  return (
    <div className="heroVisual" data-layout-key={visual.layoutKey}>
      {/* STICKY-ASSET-LAYERS:
          Hero is a layered scene. Product UI, cutouts and foreground objects must stay coordinated here,
          with physical asset metadata owned by AssetRegistry. */}
      <AspectFrame ratio="heroVisual" variant="raised">
        <AssetImage assetKey={visual.productUiAssetKey} priority sizesToken="hero" fit="contain" />
      </AspectFrame>
      <FloatingPanel slot="heroMetric" elevation="floating">
        <Stack gap="xs">
          <span className="metricCard__label">{visual.metricTitle}</span>
          <strong className="metricCard__value">{visual.metricValue}</strong>
          <span className="metricCard__note">{visual.metricNote}</span>
        </Stack>
      </FloatingPanel>
      <FloatingPanel slot="heroStatus" elevation="raised" visibility="hideCompact">
        <Badge variant="success" icon="standard.check">{visual.mockupStatus}</Badge>
      </FloatingPanel>
      <div className="heroVisual__dish" aria-hidden="true">
        <AssetImage assetKey={visual.dishAssetKey} sizesToken="decorative" fit="contain" />
      </div>
    </div>
  );
}
