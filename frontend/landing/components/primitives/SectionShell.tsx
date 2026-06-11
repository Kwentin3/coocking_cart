import type { ReactNode } from "react";
import { cx } from "@/landing/lib/classNames";

type SectionShellProps = {
  id?: string;
  labelledBy?: string;
  spacing?: "hero" | "regular" | "compact";
  background?: "page" | "alt" | "surface" | "brand";
  children: ReactNode;
};

export function SectionShell({
  id,
  labelledBy,
  spacing = "regular",
  background = "page",
  children,
}: SectionShellProps) {
  return (
    <section
      id={id}
      aria-labelledby={labelledBy}
      className={cx("sectionShell", `sectionShell--${spacing}`, `sectionShell--${background}`)}
    >
      {children}
    </section>
  );
}
