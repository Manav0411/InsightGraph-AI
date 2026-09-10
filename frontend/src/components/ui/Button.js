/**
 * Button — the one button in the design system.
 * variant: primary | outline | ghost | subtle
 * size: sm | md | lg
 * `as` lets it render as <a> / Next <Link> while keeping the styling.
 */
const BASE =
  "inline-flex items-center justify-center gap-2 font-mono font-semibold tracking-tight rounded-lg " +
  "transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary " +
  "focus-visible:ring-offset-2 focus-visible:ring-offset-surface disabled:opacity-50 disabled:pointer-events-none";

const SIZES = {
  sm: "text-[12px] px-3 py-1.5",
  md: "text-[13px] px-4 py-2.5",
  lg: "text-sm px-6 py-3",
};

const VARIANTS = {
  primary:
    "bg-primary text-on-primary shadow-[0_6px_18px_-6px_rgba(74,124,89,0.38)] " +
    "hover:-translate-y-px hover:shadow-[0_11px_26px_-8px_rgba(74,124,89,0.42)]",
  outline:
    "border border-outline-variant/60 text-on-surface hover:border-primary/50 hover:text-primary",
  ghost: "text-on-surface-variant hover:text-primary hover:bg-surface-variant/40",
  subtle: "bg-surface-variant/50 text-on-surface hover:bg-surface-variant",
};

export function Button({
  variant = "primary",
  size = "md",
  as: As = "button",
  className = "",
  ...props
}) {
  return (
    <As
      className={`${BASE} ${SIZES[size]} ${VARIANTS[variant] || VARIANTS.primary} ${className}`}
      {...props}
    />
  );
}

export default Button;
