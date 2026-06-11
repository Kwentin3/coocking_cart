import { cx } from "@/landing/lib/classNames";
import { resolveIcon, type IconKey } from "@/landing/registries/icon.registry";

type IconProps = {
  name: IconKey;
  variant?: "brand" | "neutral" | "success" | "warning" | "muted" | "inverse";
  size?: "sm" | "md" | "lg";
  decorative?: boolean;
  label?: string;
};

export function Icon({ name, variant = "neutral", size = "md", decorative = true, label }: IconProps) {
  const icon = resolveIcon(name);
  const IconComponent = icon.component;
  const accessibleLabel = label ?? icon.label;

  return (
    <IconComponent
      aria-hidden={decorative}
      aria-label={decorative ? undefined : accessibleLabel}
      focusable="false"
      className={cx("icon", `icon--${variant}`, `icon--${size}`)}
    />
  );
}
