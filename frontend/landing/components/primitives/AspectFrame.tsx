import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type AspectFrameProps = {
  ratio: "heroVisual" | "cardImage" | "documentPreview" | "avatar";
  variant?: "plain" | "raised" | "muted";
  children: ReactNode;
};

export function AspectFrame({ ratio, variant = "plain", children }: AspectFrameProps) {
  return <div className={cx("aspectFrame", `aspectFrame--${ratio}`, `aspectFrame--${variant}`)}>{children}</div>;
}
