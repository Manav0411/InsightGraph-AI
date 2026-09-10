/**
 * TextInput — one input style for search boxes and inline add-fields.
 * icon — a Material Symbols name rendered on the left.
 */
export function TextInput({ icon, className = "", ...props }) {
  return (
    <div className={`relative ${className}`}>
      {icon && (
        <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px] pointer-events-none">
          {icon}
        </span>
      )}
      <input
        className={`w-full font-mono text-sm rounded-lg bg-surface border border-outline-variant/50 py-2.5 ${
          icon ? "pl-11" : "pl-4"
        } pr-4 text-on-surface placeholder:text-on-surface-variant/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:border-transparent transition`}
        {...props}
      />
    </div>
  );
}

export default TextInput;
