import { Icon } from "@/landing/components/primitives";
import type { IconKey } from "@/landing/registries/icon.registry";

type StandardsBadgeProps = {
  text: string;
  iconKey: IconKey;
};

export function StandardsBadge({ text, iconKey }: StandardsBadgeProps) {
  return (
    <li className="standardsBadge">
      <Icon name={iconKey} variant="success" decorative />
      <span>{text}</span>
    </li>
  );
}
