/**
 * Card — the standard surface. Rounded, hairline border, soft ambient shadow.
 * No hard offset shadows, no gradients (those are the old look).
 *
 * variant:
 *   default — white/elevated card on the page ground
 *   flat    — quiet container, no shadow (for nested / secondary panels)
 *   inset   — the dark "machine" panel from the landing; constant across themes
 * interactive — adds hover lift + pointer; pass an `as="button"` or wrap a <Link>.
 */
const VARIANTS = {
  default: "bg-surface border-outline-variant/40 ds-shadow",
  flat: "bg-surface-container-low border-outline-variant/30",
  inset: "bg-[#111a14] border-[#2a382f] text-[#e4e8dc]",
};

export function Card({
  variant = "default",
  interactive = false,
  as: As = "div",
  className = "",
  ...props
}) {
  const hover = interactive
    ? "ds-shadow-lift hover:-translate-y-0.5 hover:border-primary/30 cursor-pointer text-left w-full"
    : "";
  return (
    <As
      className={`rounded-2xl border ${VARIANTS[variant] || VARIANTS.default} ${hover} ${className}`}
      {...props}
    />
  );
}

export default Card;
