import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type ClusterProps = {
  gap?: "sm" | "md" | "lg";
  justify?: "start" | "center" | "between" | "end";
  children: ReactNode;
};

export function Cluster({ gap = "md", justify = "start", children }: ClusterProps) {
  return <div className={cx("cluster", `cluster--${gap}`, `cluster--${justify}`)}>{children}</div>;
}
