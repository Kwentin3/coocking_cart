import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";
import type { IconKey } from "@/landing/registries/icon.registry";
import { Icon } from "./Icon";

type BadgeProps = {
  variant?: "neutral" | "success" | "warning";
  icon?: IconKey;
  children: ReactNode;
};

export function Badge({ variant = "neutral", icon, children }: BadgeProps) {
  return (
    <span className={cx("badge", `badge--${variant}`)}>
      {icon ? <Icon name={icon} size="sm" decorative /> : null}
      <span>{children}</span>
    </span>
  );
}
