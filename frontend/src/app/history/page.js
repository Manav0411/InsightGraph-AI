"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { API_BASE_URL } from '../../lib/config';
import { useUser } from '../../context/UserContext';
import { PageShell, Card, Chip, TextInput } from '../../components/ui';

const formatBriefingDate = (dateString) => {
  const safeDateString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
  const date = new Date(safeDateString);
  const today = new Date();
  const isToday = date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();

  const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  if (isToday) return `Today · ${timeStr}`;
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return `${dateStr} · ${timeStr}`;
};

// SQI badge tone by tier — accent when strong, tertiary mid, muted low.
const sqiTone = (sqi) => {
  if (sqi >= 85) return 'text-primary border-primary/40 bg-primary/10';
  if (sqi >= 70) return 'text-tertiary border-tertiary/40 bg-tertiary/10';
  return 'text-on-surface-variant border-outline-variant/50 bg-surface-variant/40';
};

export default function HistoryPage() {
  const { user, getToken } = useUser();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/newsletter/history`, {
          headers: { 'Authorization': `Bearer ${token}` },
          cache: 'no-store'
        });
        if (res.ok) {
          const json = await res.json();
          setHistory(json);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchHistory();
  }, [user?.id, getToken]);

  const filteredHistory = history.filter(b =>
    b.title.toLowerCase().includes(search.toLowerCase()) ||
    (b.dominant_topics && b.dominant_topics.some(t => t.toLowerCase().includes(search.toLowerCase())))
  );

  if (loading) {
    return (
      <PageShell>
        <p className="font-mono text-[13px] text-on-surface-variant py-16 text-center">Loading your archive…</p>
      </PageShell>
    );
  }

  return (
    <PageShell className="flex flex-col gap-10">
      <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-5">
        <div className="flex flex-col gap-2">
          <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">archive</span>
          <h1 className="font-display text-4xl md:text-5xl leading-[1.05] text-on-surface">Every briefing, kept</h1>
          <p className="font-reader text-on-surface-variant text-lg leading-relaxed max-w-2xl">
            Your full run history — searchable, and the precedent each new briefing is written against.
          </p>
        </div>
        <TextInput
          icon="search"
          placeholder="Search titles, topics…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full md:w-72 shrink-0"
        />
      </header>

      {history.length === 0 ? (
        <Card variant="flat" className="p-12 md:p-16 flex flex-col items-center text-center gap-3">
          <span className="material-symbols-outlined text-4xl text-outline-variant">history_toggle_off</span>
          <p className="font-reader text-on-surface-variant text-lg max-w-sm">
            No briefings yet. Once your first run files, it lands here.
          </p>
        </Card>
      ) : filteredHistory.length === 0 ? (
        <p className="font-mono text-[13px] text-on-surface-variant py-12 text-center">Nothing matched “{search}”.</p>
      ) : (
        <div className="flex flex-col gap-5">
          {filteredHistory.map((briefing) => {
            const sqi = briefing.signal_quality_index ?? 100;
            return (
              <Card key={briefing.id} interactive as="div" className="p-0 overflow-hidden">
                <Link href={`/history/${briefing.id}`} className="block p-6 md:p-7 flex flex-col gap-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary">
                      {formatBriefingDate(briefing.generated_at)}
                    </span>
                    <span className={`font-mono text-[11px] px-2 py-0.5 rounded-full border ${sqiTone(sqi)}`}>
                      SQI {sqi}
                    </span>
                  </div>

                  <h3 className="font-reader font-semibold text-xl leading-snug text-on-surface">
                    {briefing.title}
                  </h3>

                  {briefing.top_signal && (
                    <p className="font-reader text-sm text-on-surface border-l-2 border-primary/40 pl-3 leading-relaxed">
                      {briefing.top_signal.title}
                    </p>
                  )}

                  {briefing.dominant_topics?.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {briefing.dominant_topics.slice(0, 4).map(topic => (
                        <Chip key={topic}>{topic}</Chip>
                      ))}
                    </div>
                  )}

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-on-surface-variant pt-1">
                    <span>{briefing.total_articles} signals</span>
                    <span>avg trend {briefing.avg_trend_score ? briefing.avg_trend_score.toFixed(1) : '0.0'}</span>
                    <span>{briefing.grounding_reliability}% grounded</span>
                    {briefing.execution_time_seconds != null && (
                      <span>{briefing.execution_time_seconds.toFixed(0)}s</span>
                    )}
                  </div>
                </Link>
              </Card>
            );
          })}
        </div>
      )}
    </PageShell>
  );
}
