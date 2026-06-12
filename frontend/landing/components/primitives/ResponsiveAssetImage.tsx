import Image from "next/image";
import { cx } from "@/landing/lib/classNames";
import { resolveAsset, type LandingAssetKey } from "@/landing/registries/asset.registry";

type ResponsiveAssetImageProps = {
  desktopAssetKey: LandingAssetKey;
  mobileAssetKey: LandingAssetKey;
  fit?: "cover" | "contain";
  mobileMedia?: string;
};

export function ResponsiveAssetImage({
  desktopAssetKey,
  mobileAssetKey,
  fit = "cover",
  mobileMedia = "(max-width: 48rem)",
}: ResponsiveAssetImageProps) {
  const desktopAsset = resolveAsset(desktopAssetKey);
  const mobileAsset = resolveAsset(mobileAssetKey);
  const debugId = `${desktopAsset.debugId}/${mobileAsset.debugId}`;

  return (
    <span
      className={cx(
        "assetImageShell",
        "assetImageShell--responsive",
        `assetImageShell--${desktopAsset.assetKind}`,
        desktopAsset.transparentBackground && "assetImageShell--transparent",
      )}
      data-asset-key={`${desktopAsset.key} ${mobileAsset.key}`}
      data-asset-debug-id={debugId}
    >
      <picture className="assetImagePicture">
        <source media={mobileMedia} srcSet={mobileAsset.src} width={mobileAsset.width} height={mobileAsset.height} />
        <Image
          src={desktopAsset.src}
          alt={desktopAsset.alt}
          width={desktopAsset.width}
          height={desktopAsset.height}
          loading={desktopAsset.loading}
          sizes="100vw"
          aria-hidden={desktopAsset.role === "decorative"}
          data-asset-kind={desktopAsset.assetKind}
          data-background-mode={desktopAsset.backgroundMode}
          data-layer-role={desktopAsset.layerRole}
          data-z-slot={desktopAsset.zSlot}
          className={cx(
            "assetImage",
            `assetImage--${fit}`,
            `assetImage--${desktopAsset.assetKind}`,
            desktopAsset.transparentBackground && "assetImage--transparent",
          )}
        />
      </picture>
      <span className="assetDebugId" aria-hidden="true">
        {debugId}
      </span>
    </span>
  );
}
