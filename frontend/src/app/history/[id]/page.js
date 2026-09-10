"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { API_BASE_URL } from '../../../lib/config';
import { useUser } from '../../../context/UserContext';
import { PageShell, Card, Chip, Button } from '../../../components/ui';

export default function HistoricalBriefingViewer() {
  const { id } = useParams();
  const { user, getToken } = useUser();
  const [briefing, setBriefing] = useState(null);
  const [historyContext, setHistoryContext] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const fetchBriefing = async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/newsletter/history/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const json = await res.json();
          setBriefing(json);
        }

        const histRes = await fetch(`${API_BASE_URL}/newsletter/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (histRes.ok) {
          const histJson = await histRes.json();
          setHistoryContext(histJson);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (id && user?.id) fetchBriefing();
  }, [id, user?.id, getToken]);

  const handleExport = async () => {
    setDownloading(true);
    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE_URL}/newsletter/export/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `InsightGraph_${id.substring(0, 8)}.md`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <PageShell width="narrow">
        <p className="font-mono text-[13px] text-on-surface-variant py-16 text-center">Loading briefing…</p>
      </PageShell>
    );
  }
  if (!briefing) {
    return (
      <PageShell width="narrow">
        <p className="font-mono text-[13px] text-on-surface-variant py-16 text-center">Briefing not found.</p>
      </PageShell>
    );
  }

  const safeDateString = briefing.generated_at.endsWith('Z') ? briefing.generated_at : briefing.generated_at + 'Z';
  const date = new Date(safeDateString).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  const sqi = briefing.metrics.signal_quality_index || 100;
  const recentBriefings = historyContext.filter(b => b.id !== id).slice(0, 3);

  return (
    <PageShell width="narrow" className="flex flex-col gap-10">
      <Link href="/history" className="inline-flex items-center gap-1.5 font-mono text-[12px] text-on-surface-variant hover:text-primary transition-colors">
        <span className="material-symbols-outlined text-[16px]">arrow_back</span>
        Archive
      </Link>

      <header className="flex flex-col gap-5 border-b border-outline-variant/30 pb-8">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div className="flex flex-col gap-3">
            <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">
              {date} · SQI {sqi}
            </span>
            <h1 className="font-display text-4xl md:text-5xl leading-[1.05] text-on-surface">
              {briefing.title}
            </h1>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            disabled={downloading}
            className="shrink-0"
          >
            <span className="material-symbols-outlined text-[16px]">download</span>
            {downloading ? 'Exporting…' : 'Export'}
          </Button>
        </div>

        {briefing.metadata?.dominant_topics?.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {briefing.metadata.dominant_topics.map(topic => (
              <Chip key={topic} selected>{topic}</Chip>
            ))}
          </div>
        )}
      </header>

      {recentBriefings.length > 0 && (
        <Card variant="flat" className="p-6 flex flex-col gap-3">
          <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-on-surface-variant">
            Other briefings
          </span>
          <ul className="flex flex-col gap-2">
            {recentBriefings.map(b => (
              <li key={b.id} className="flex items-center gap-3 font-reader text-sm">
                <span className="font-mono text-[11px] text-on-surface-variant shrink-0">
                  {new Date(b.generated_at.endsWith('Z') ? b.generated_at : b.generated_at + 'Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
                <Link href={`/history/${b.id}`} className="text-on-surface hover:text-primary transition-colors">
                  {b.title || b.dominant_topics?.[0] || 'Briefing'}
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <section className="flex flex-col gap-6">
        {briefing.articles.map((article, i) => (
          <Card key={i} className="p-6 md:p-8 flex flex-col gap-4">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11px] uppercase tracking-[0.08em] text-on-surface-variant">
              <span className="text-primary">{article.source}</span>
              {article.trend_score != null && <span>trend {article.trend_score.toFixed(1)}</span>}
              {article.is_grounded && (
                <span className="inline-flex items-center gap-1 text-primary">
                  <span className="material-symbols-outlined text-[13px]">verified</span>grounded
                </span>
              )}
            </div>

            <h2 className="font-reader font-semibold text-xl leading-snug text-on-surface">
              <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                {article.title}
              </a>
            </h2>

            <p className="font-reader text-on-surface-variant text-base leading-relaxed">{article.summary}</p>

            {article.why_it_matters && (
              <div className="border-l-2 border-primary pl-4 flex flex-col gap-1">
                <span className="font-mono text-[10.5px] uppercase tracking-[0.1em] text-primary">Why it matters</span>
                <p className="font-reader text-[15px] text-on-surface leading-relaxed">{article.why_it_matters}</p>
              </div>
            )}

            {article.recommendation_reasons?.length > 0 && (
              <Card variant="flat" className="p-4 flex flex-col gap-2">
                <span className="font-mono text-[10.5px] uppercase tracking-[0.1em] text-on-surface-variant">
                  Why this signal was elevated
                </span>
                <ul className="flex flex-col gap-1.5">
                  {article.recommendation_reasons.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-2 font-reader text-sm text-on-surface">
                      <span className="material-symbols-outlined text-[16px] text-primary shrink-0 mt-0.5">check</span>
                      {reason}
                    </li>
                  ))}
                  {article.stars && (
                    <li className="flex items-start gap-2 font-reader text-sm text-on-surface">
                      <span className="material-symbols-outlined text-[16px] text-tertiary shrink-0 mt-0.5">star</span>
                      High developer momentum ({article.stars} stars)
                    </li>
                  )}
                </ul>
              </Card>
            )}

            {article.tags?.length > 0 && (
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11px] text-on-surface-variant">
                {article.tags.map(tag => (
                  <span key={tag}>#{tag}</span>
                ))}
              </div>
            )}
          </Card>
        ))}
      </section>
    </PageShell>
  );
}
