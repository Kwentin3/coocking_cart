import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type StackProps = {
  gap?: "xs" | "sm" | "md" | "lg" | "xl";
  align?: "start" | "center" | "stretch";
  children: ReactNode;
};

export function Stack({ gap = "md", align = "stretch", children }: StackProps) {
  return <div className={cx("stack", `stack--${gap}`, `stack--${align}`)}>{children}</div>;
}
