import Image from "next/image";
import { cx } from "@/landing/lib/classNames";
import { resolveAsset, type LandingAssetKey } from "@/landing/registries/asset.registry";

type AssetImageProps = {
  assetKey: LandingAssetKey;
  fit?: "cover" | "contain";
  priority?: boolean;
  sizesToken?: "hero" | "document" | "card" | "decorative";
};

const sizesByToken: Record<NonNullable<AssetImageProps["sizesToken"]>, string> = {
  hero: "(min-width: 1024px) 48rem, 100vw",
  document: "(min-width: 1024px) 22rem, 70vw",
  card: "(min-width: 768px) 24rem, 100vw",
  decorative: "(min-width: 1024px) 34rem, 0vw",
};

export function AssetImage({ assetKey, fit = "cover", priority = false, sizesToken = "card" }: AssetImageProps) {
  const asset = resolveAsset(assetKey);
  const isPriority = priority || asset.priority;

  return (
    <span
      className={cx(
        "assetImageShell",
        `assetImageShell--${asset.visibility}`,
        `assetImageShell--${asset.assetKind}`,
        asset.transparentBackground && "assetImageShell--transparent",
      )}
      data-asset-key={asset.key}
      data-asset-debug-id={asset.debugId}
    >
      <Image
        src={asset.src}
        alt={asset.alt}
        width={asset.width}
        height={asset.height}
        priority={isPriority}
        loading={isPriority ? undefined : asset.loading}
        sizes={sizesByToken[sizesToken]}
        unoptimized={asset.src.endsWith(".svg")}
        aria-hidden={asset.role === "decorative"}
        data-asset-kind={asset.assetKind}
        data-background-mode={asset.backgroundMode}
        data-layer-role={asset.layerRole}
        data-z-slot={asset.zSlot}
        className={cx(
          "assetImage",
          `assetImage--${fit}`,
          `assetImage--${asset.visibility}`,
          `assetImage--${asset.assetKind}`,
          asset.transparentBackground && "assetImage--transparent",
        )}
      />
      <span className="assetDebugId" aria-hidden="true">
        {asset.debugId}
      </span>
    </span>
  );
}
