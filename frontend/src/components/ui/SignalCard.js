import { Card } from "./Card";

/**
 * SignalCard — the compact text unit for a single signal, shared by the reader
 * grid and the history archive. Quiet inline data (no boxed metrics).
 *
 * kicker  — e.g. "top story · tavily"
 * trend   — number, rendered as "TREND 4.4"
 * sqi     — number, rendered as "SQI 61"
 * onClick — makes the whole card an interactive button
 */
export function SignalCard({
  kicker,
  title,
  summary,
  tags = [],
  trend,
  sqi,
  onClick,
  className = "",
}) {
  const interactive = typeof onClick === "function";
  const hasMeta = tags.length > 0 || trend != null || sqi != null;

  return (
    <Card
      as={interactive ? "button" : "div"}
      interactive={interactive}
      onClick={onClick}
      className={`group p-6 flex flex-col gap-3 ${className}`}
    >
      {kicker && (
        <span className="font-mono text-[10.5px] uppercase tracking-[0.09em] text-primary">
          {kicker}
        </span>
      )}
      {title && (
        <h3 className="font-reader font-semibold text-lg leading-snug text-on-surface group-hover:text-primary transition-colors">
          {title}
        </h3>
      )}
      {summary && (
        <p className="font-reader text-sm leading-relaxed text-on-surface-variant line-clamp-3">
          {summary}
        </p>
      )}
      {hasMeta && (
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 font-mono text-[11px] text-on-surface-variant">
          {tags.map((t) => (
            <span key={t}>#{t}</span>
          ))}
          {trend != null && <span>TREND {Number(trend).toFixed(1)}</span>}
          {sqi != null && <span>SQI {sqi}</span>}
        </div>
      )}
    </Card>
  );
}

export default SignalCard;
