"use client";

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../../lib/config';
import { useUser } from '../../../context/UserContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { PageShell, PageHeader, Card, Chip } from '../../../components/ui';

const TOOLTIP_STYLE = {
  backgroundColor: 'rgb(var(--color-surface-container-high))',
  borderRadius: '10px',
  border: '1px solid rgb(var(--color-outline-variant) / 0.4)',
  color: 'rgb(var(--color-on-surface))',
  fontFamily: 'var(--font-mono, monospace)',
  fontSize: 12,
};

function StatCard({ label, value }) {
  return (
    <Card className="p-6 flex flex-col gap-1.5">
      <span className="font-mono text-[10.5px] uppercase tracking-[0.1em] text-on-surface-variant">{label}</span>
      <span className="font-display text-3xl leading-tight text-on-surface">{value}</span>
    </Card>
  );
}

function ChartCard({ label, children }) {
  return (
    <Card className="p-6 flex flex-col gap-5">
      <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">{label}</span>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer width="99%" height={240}>
          {children}
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export default function Analytics() {
  const { user, getToken } = useUser();
  const [trendsData, setTrendsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState('all');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/analytics/trends`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const json = await res.json();

          const formatChartDate = (isoString) => {
            const d = new Date(isoString);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
          };

          if (json.latency_trends) {
            json.latency_trends.forEach(item => {
              item.iso_date = item.date;
              item.date = formatChartDate(item.date);
            });
          }
          if (json.token_trends) {
            json.token_trends.forEach(item => {
              item.iso_date = item.date;
              item.date = formatChartDate(item.date);
            });
          }

          setTrendsData(json);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchAnalytics();
  }, [user?.id, getToken]);

  if (loading) {
    return (
      <PageShell>
        <p className="font-mono text-[13px] text-on-surface-variant py-16 text-center">Loading analytics…</p>
      </PageShell>
    );
  }

  if (!trendsData || trendsData.latency_trends?.length === 0) {
    return (
      <PageShell>
        <Card variant="flat" className="p-12 md:p-16 flex flex-col items-center text-center gap-3">
          <span className="material-symbols-outlined text-4xl text-outline-variant">monitoring</span>
          <p className="font-reader text-on-surface-variant text-lg max-w-sm">
            No history yet. Run the pipeline a few times and the trends fill in here.
          </p>
        </Card>
      </PageShell>
    );
  }

  const { token_trends, latency_trends, fastest_growing_topics, source_distribution } = trendsData;

  const filterByDate = (arr) => {
    if (!arr || dateFilter === 'all') return arr;
    const now = new Date();
    const days = dateFilter === '7d' ? 7 : 30;
    const cutoff = new Date(now.getTime() - (days * 24 * 60 * 60 * 1000));
    return arr.filter(item => new Date(item.iso_date) >= cutoff);
  };

  const filteredLatency = filterByDate(latency_trends);
  const filteredTokens = filterByDate(token_trends);

  const topTopic = fastest_growing_topics?.[0]?.topic || '—';
  const topSource = source_distribution?.[0]?.source || '—';
  const avgSqi = filteredLatency.length > 0
    ? (filteredLatency.reduce((sum, item) => sum + (item.sqi || 0), 0) / filteredLatency.length).toFixed(1)
    : '—';

  const RANGES = [['7d', '7 days'], ['30d', '30 days'], ['all', 'All time']];

  return (
    <PageShell width="wide" className="flex flex-col gap-8">
      <PageHeader
        title="Analytics"
        subtitle="Signal quality, token spend and latency across every run in your history."
        actions={
          <div className="inline-flex rounded-lg border border-outline-variant/40 p-0.5">
            {RANGES.map(([key, label]) => (
              <button
                key={key}
                onClick={() => setDateFilter(key)}
                className={`font-mono text-[12px] px-3 py-1.5 rounded-md transition-colors ${
                  dateFilter === key ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Fastest-growing topic" value={topTopic} />
        <StatCard label="Most frequent source" value={topSource} />
        <StatCard label="Avg signal quality" value={`${avgSqi}${avgSqi === '—' ? '' : ' / 100'}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard label="Signal quality over time">
          <AreaChart data={filteredLatency} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorSqi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgb(var(--color-primary))" stopOpacity={0.2} />
                <stop offset="95%" stopColor="rgb(var(--color-primary))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--color-outline-variant))" opacity={0.3} />
            <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--color-on-surface-variant))', fontSize: 11 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--color-on-surface-variant))', fontSize: 11 }} domain={[0, 100]} />
            <Tooltip contentStyle={TOOLTIP_STYLE} itemStyle={{ color: 'rgb(var(--color-primary))' }} />
            <Area type="monotone" dataKey="sqi" name="Signal quality" stroke="rgb(var(--color-primary))" strokeWidth={2.5} fillOpacity={1} fill="url(#colorSqi)" />
          </AreaChart>
        </ChartCard>

        <ChartCard label="Execution latency (s)">
          <LineChart data={filteredLatency} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--color-outline-variant))" opacity={0.25} />
            <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--color-on-surface-variant))', fontSize: 11 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--color-on-surface-variant))', fontSize: 11 }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} itemStyle={{ color: 'rgb(var(--color-error))' }} />
            <Line type="monotone" dataKey="latency" name="Latency (s)" stroke="rgb(var(--color-error))" strokeWidth={2} dot={{ r: 3, fill: 'rgb(var(--color-error))' }} />
          </LineChart>
        </ChartCard>

        <ChartCard label="Token usage">
          <AreaChart data={filteredTokens} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPrompt" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgb(var(--color-secondary))" stopOpacity={0.2} />
                <stop offset="95%" stopColor="rgb(var(--color-secondary))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--color-outline-variant))" opacity={0.2} />
            <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--color-on-surface-variant))', fontSize: 11 }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: 'rgb(var(--color-on-surface-variant))', fontSize: 11 }} />
            <Tooltip contentStyle={TOOLTIP_STYLE} />
            <Area type="monotone" dataKey="prompt" stackId="1" name="Prompt" stroke="rgb(var(--color-secondary))" fill="url(#colorPrompt)" />
            <Area type="monotone" dataKey="completion" stackId="1" name="Completion" stroke="rgb(var(--color-tertiary))" fill="rgb(var(--color-tertiary-container))" opacity={0.8} />
          </AreaChart>
        </ChartCard>

        <Card className="p-6 flex flex-col gap-5">
          <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">top topics &amp; sources</span>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10.5px] uppercase tracking-[0.08em] text-on-surface-variant">topics</span>
              <div className="flex flex-wrap gap-2">
                {fastest_growing_topics?.map(t => (
                  <Chip key={t.topic}>{t.topic} <span className="opacity-60">{t.count}</span></Chip>
                ))}
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10.5px] uppercase tracking-[0.08em] text-on-surface-variant">sources</span>
              <div className="flex flex-wrap gap-2">
                {source_distribution?.map(s => (
                  <Chip key={s.source}>{s.source} <span className="opacity-60">{s.count}</span></Chip>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </PageShell>
  );
}
