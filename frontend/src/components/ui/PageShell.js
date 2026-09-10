/**
 * PageShell — consistent page width, gutters and vertical rhythm for every
 * signed-in surface, replacing the ad-hoc `max-w-* mx-auto px-*` wrappers.
 * width: narrow (prose) | default | wide (grids / the reader)
 */
const WIDTHS = {
  narrow: "max-w-2xl",
  default: "max-w-5xl",
  wide: "max-w-[1200px]",
};

export function PageShell({ children, width = "default", className = "" }) {
  return (
    <div className={`w-full ${WIDTHS[width] || WIDTHS.default} mx-auto px-5 md:px-8 py-10 md:py-14 ${className}`}>
      {children}
    </div>
  );
}

/**
 * PageHeader — the h1 block at the top of a surface. `actions` sits inline on
 * desktop, wraps below on mobile.
 */
export function PageHeader({ title, subtitle, actions, className = "" }) {
  return (
    <header className={`flex flex-col md:flex-row md:items-end md:justify-between gap-5 mb-10 ${className}`}>
      <div className="flex flex-col gap-2">
        <h1 className="font-display text-4xl md:text-5xl leading-[1.05] text-on-surface">{title}</h1>
        {subtitle && (
          <p className="font-reader text-on-surface-variant text-lg leading-relaxed max-w-2xl">
            {subtitle}
          </p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
    </header>
  );
}

export default PageShell;
