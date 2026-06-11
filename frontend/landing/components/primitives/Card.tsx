import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type CardProps = {
  variant?: "default" | "elevated" | "soft" | "interactive" | "metric" | "document";
  density?: "compact" | "comfortable";
  children: ReactNode;
};

export function Card({ variant = "default", density = "comfortable", children }: CardProps) {
  return <article className={cx("card", `card--${variant}`, `card--${density}`)}>{children}</article>;
}
