import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type FloatingPanelProps = {
  slot: "heroMetric" | "heroStatus" | "documentNote";
  elevation?: "raised" | "floating";
  visibility?: "always" | "hideCompact";
  children: ReactNode;
};

export function FloatingPanel({ slot, elevation = "raised", visibility = "always", children }: FloatingPanelProps) {
  return <div className={cx("floatingPanel", `floatingPanel--${slot}`, `floatingPanel--${elevation}`, `floatingPanel--${visibility}`)}>{children}</div>;
}
