/**
 * Chip — pill token for topics / tags / filters.
 * selected — soft accent wash + accent border + accent text (never a hard fill)
 * muted    — dashed border + strike-through, for excluded / disabled terms
 * onRemove — renders a trailing × button
 * Pass `as="button"` (with onClick) for a toggleable chip.
 */
export function Chip({
  selected = false,
  muted = false,
  onRemove,
  as: As = "span",
  className = "",
  children,
  ...props
}) {
  const state = muted
    ? "border-dashed border-outline-variant/60 text-on-surface-variant/70 line-through"
    : selected
      ? "bg-primary/10 border-primary/40 text-primary"
      : "bg-surface border-outline-variant/50 text-on-surface-variant hover:border-primary/40 hover:text-on-surface";

  return (
    <As
      className={`inline-flex items-center gap-1.5 rounded-full border font-mono text-xs px-3 py-1.5 transition-colors ${state} ${className}`}
      {...props}
    >
      {children}
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove(e);
          }}
          aria-label="Remove"
          className="flex items-center -mr-1 hover:text-error transition-colors"
        >
          <span className="material-symbols-outlined text-[14px]">close</span>
        </button>
      )}
    </As>
  );
}

export default Chip;
