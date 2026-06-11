import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type ContainerProps = {
  width?: "default" | "wide" | "narrow";
  children: ReactNode;
};

export function Container({ width = "default", children }: ContainerProps) {
  return <div className={cx("container", `container--${width}`)}>{children}</div>;
}
