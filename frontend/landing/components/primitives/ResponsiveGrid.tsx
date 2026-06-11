import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type ResponsiveGridProps = {
  variant: "heroSplit" | "cards" | "twoColumn" | "timeline" | "documents";
  density?: "compact" | "comfortable";
  children: ReactNode;
};

export function ResponsiveGrid({ variant, density = "comfortable", children }: ResponsiveGridProps) {
  return <div className={cx("responsiveGrid", `responsiveGrid--${variant}`, `responsiveGrid--${density}`)}>{children}</div>;
}
