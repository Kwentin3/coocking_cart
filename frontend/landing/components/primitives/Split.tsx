import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type SplitProps = {
  variant?: "balanced" | "hero" | "documents";
  children: ReactNode;
};

export function Split({ variant = "balanced", children }: SplitProps) {
  return <div className={cx("split", `split--${variant}`)}>{children}</div>;
}
