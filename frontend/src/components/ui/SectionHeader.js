/**
 * SectionHeader — mono eyebrow + display heading + reader description.
 * Mirrors the landing's section heads so in-app sections read the same way.
 */
export function SectionHeader({ eyebrow, title, description, className = "", as: Heading = "h2" }) {
  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {eyebrow && (
        <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">
          {eyebrow}
        </span>
      )}
      {title && (
        <Heading className="font-display text-3xl md:text-4xl leading-[1.12] text-on-surface">
          {title}
        </Heading>
      )}
      {description && (
        <p className="font-reader text-on-surface-variant text-base leading-relaxed max-w-[58ch]">
          {description}
        </p>
      )}
    </div>
  );
}

export default SectionHeader;
