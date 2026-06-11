import { cx } from "@/landing/lib/classNames";
import type { ResolvedLandingAction } from "@/landing/lib/actionVisibilityResolver";
import type { IconKey } from "@/landing/registries/icon.registry";
import { Icon } from "./Icon";

type ButtonProps = {
  variant?: "primary" | "secondary" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
  action: ResolvedLandingAction;
  iconLeft?: IconKey;
  iconRight?: IconKey;
  iconOnly?: boolean;
  ariaLabel?: string;
  state?: "idle" | "disabled" | "busy";
};

export function Button({
  variant = "primary",
  size = "md",
  action,
  iconLeft,
  iconRight,
  iconOnly = false,
  ariaLabel,
  state = "idle",
}: ButtonProps) {
  if (action.visibility === "hidden") {
    return null;
  }

  const disabled = !action.enabled || action.kind === "disabled" || state === "disabled";
  const busy = state === "busy";
  const className = cx("button", `button--${variant}`, `button--${size}`, iconOnly && "button--iconOnly", disabled && "button--disabled");
  const accessibleLabel = ariaLabel ?? (iconOnly ? action.label : undefined);
  const content = (
    <>
      {iconLeft ? <Icon name={iconLeft} size="sm" decorative /> : null}
      {iconOnly ? null : <span>{action.label}</span>}
      {busy ? <span className="button__status" aria-live="polite">...</span> : null}
      {disabled ? <Icon name="action.lock" size="sm" decorative /> : iconRight ? <Icon name={iconRight} size="sm" decorative /> : null}
    </>
  );

  if (disabled) {
    return (
      <button
        type="button"
        className={className}
        disabled
        data-analytics-event={action.analyticsEvent}
        aria-label={accessibleLabel}
        title={action.disabledReason}
      >
        {content}
      </button>
    );
  }

  return (
    <a
      className={className}
      href={action.href}
      data-analytics-event={action.analyticsEvent}
      aria-busy={busy}
      aria-label={accessibleLabel}
    >
      {content}
    </a>
  );
}
