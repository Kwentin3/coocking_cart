import { AssetImage, Icon } from "@/landing/components/primitives";
import type { LandingAssetKey } from "@/landing/registries/asset.registry";
import type { IconKey } from "@/landing/registries/icon.registry";

type AudienceCardProps = {
  title: string;
  description: string;
  imageAssetKey: LandingAssetKey;
  iconKey: IconKey;
  iconVariant: "brand" | "action";
};

export function AudienceCard({ title, description, imageAssetKey, iconKey, iconVariant }: AudienceCardProps) {
  return (
    <article className="audienceCard">
      <div className="audienceCard__mediaWrap">
        <div className="audienceCard__media">
          <AssetImage assetKey={imageAssetKey} fit="cover" sizesToken="card" />
        </div>
        <span className={`audienceCard__icon audienceCard__icon--${iconVariant}`} aria-hidden="true">
          <Icon name={iconKey} variant="inverse" decorative />
        </span>
      </div>
      <div className="audienceCard__body">
        <h3 className="cardTitle">{title}</h3>
        <p className="cardText">{description}</p>
      </div>
    </article>
  );
}
