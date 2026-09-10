"use client";

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import PipelineProgress from '../../../components/orchestration/PipelineProgress';
import { API_BASE_URL } from '../../../lib/config';
import { useUser } from '../../../context/UserContext';
import { PageShell, PageHeader, Card, Chip, Button } from '../../../components/ui';

const TASK_KEY = 'active_task_id';
const MAX_RUN_MS = 30 * 60 * 1000; // give up watching after 30 min

// Map the backend pipeline_stage to a rough completion percentage so the ring
// advances meaningfully instead of counting distinct stage strings.
const STAGE_PCT = {
  initialized: 5,
  retrieval: 20,
  validation: 38,
  ranking: 50,
  analysis: 78,
  evaluation: 90,
  composition: 96,
};

function stageLabel(raw) {
  if (!raw) return 'Working';
  return raw.replace(/^Running:\s*/i, '').trim() || 'Working';
}

function Metric({ label, value, status }) {
  return (
    <Card className="p-5 flex flex-col gap-2">
      <span className="font-mono text-[10.5px] uppercase tracking-[0.1em] text-on-surface-variant">{label}</span>
      <span className="font-display text-4xl leading-none text-on-surface tabular-nums">{value}</span>
      {status && <span className="font-mono text-[11px] text-primary">{status}</span>}
    </Card>
  );
}

export default function CommandCenter() {
  const { user, preferences, getToken } = useUser();
  const router = useRouter();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateProgress, setGenerateProgress] = useState(null);
  const [activeTask, setActiveTask] = useState(null);
  const runStartRef = useRef(null);

  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const initDashboard = async () => {
      await Promise.all([fetchLatest(), fetchAnalytics(), fetchHistory()]);
      setLoading(false);
    };
    if (user?.id) {
      initDashboard();
    }
  }, [user?.id, getToken]);

  // Resume watching an in-flight run if the user navigated away and back.
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const existing = window.localStorage.getItem(TASK_KEY);
    if (existing && !activeTask) {
      runStartRef.current = Date.now();
      setGenerateProgress({ stage: 'Reconnecting', log: [], elapsed: '0.0s', progress: 10 });
      setIsGenerating(true);
      setActiveTask(existing);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Single polling loop, keyed on the task id. Survives remounts.
  useEffect(() => {
    if (!activeTask) return;
    if (!runStartRef.current) runStartRef.current = Date.now();

    let cancelled = false;
    let consecutiveFailures = 0;

    const finish = () => {
      cancelled = true;
      window.localStorage.removeItem(TASK_KEY);
    };

    const tick = async () => {
      if (cancelled) return;

      if (Date.now() - runStartRef.current > MAX_RUN_MS) {
        finish();
        setActiveTask(null);
        setGenerateProgress((p) => ({
          ...(p || {}),
          stage: 'Timed out',
          error: 'Still running after 30 minutes. It may finish in the background — check History shortly.',
        }));
        return;
      }

      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/newsletter/status/${activeTask}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (res.status === 404) {
          // Task record gone (server restart). Assume it landed; send them to the reader.
          finish();
          setActiveTask(null);
          router.push('/');
          return;
        }

        if (!res.ok) throw new Error(`status ${res.status}`);
        consecutiveFailures = 0;

        const s = await res.json();
        const elapsed = ((Date.now() - runStartRef.current) / 1000).toFixed(1) + 's';

        if (s.status === 'completed') {
          finish();
          setGenerateProgress((p) => ({ ...(p || {}), stage: 'Complete', progress: 100, elapsed }));
          setTimeout(() => { setActiveTask(null); router.push('/'); }, 1800);
        } else if (s.status === 'failed') {
          finish();
          setActiveTask(null);
          setGenerateProgress((p) => ({
            ...(p || {}),
            stage: 'Failed',
            elapsed,
            error: s.error || 'The pipeline reported a failure.',
          }));
        } else {
          const label = stageLabel(s.stage);
          setGenerateProgress((p) => ({
            ...(p || {}),
            stage: label,
            elapsed,
            progress: STAGE_PCT[label.toLowerCase()] ?? p?.progress ?? 10,
            log: [`[AGENT] INFO: ${label}`].slice(-4),
          }));
        }
      } catch (err) {
        consecutiveFailures += 1;
        // Render free tier often 5xx's while the pipeline hogs the worker — keep
        // trying, just surface that we're waiting.
        if (consecutiveFailures >= 5) {
          setGenerateProgress((p) => ({ ...(p || {}), stage: 'Reconnecting' }));
        }
        console.error('Polling error:', err);
      }
    };

    tick();
    const id = setInterval(tick, 4000);
    return () => { cancelled = true; clearInterval(id); };
  }, [activeTask, getToken, router]);

  const fetchHistory = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE_URL}/newsletter/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setHistory(json);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE_URL}/analytics/trends`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setAnalytics(json);
      }
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
    }
  };

  const fetchLatest = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE_URL}/newsletter/latest`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateBriefing = async () => {
    setIsGenerating(true);
    setGenerateProgress({ stage: 'Queued', log: [], elapsed: '0.0s', progress: 5 });
    runStartRef.current = Date.now();

    try {
      const token = await getToken();
      const res = await fetch(`${API_BASE_URL}/newsletter/generate-async`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ user_id: user.id }),
      });

      if (!res.ok) {
        let detail = 'Failed to start generation task';
        try { detail = (await res.json()).detail || detail; } catch {}
        throw new Error(detail);
      }

      const { task_id } = await res.json();
      window.localStorage.setItem(TASK_KEY, task_id);
      setActiveTask(task_id); // polling useEffect takes over from here
    } catch (error) {
      console.error('Generation Error:', error);
      setGenerateProgress((p) => ({ ...(p || {}), stage: 'Failed', error: error.message }));
    }
  };

  const dismissProgress = () => {
    setIsGenerating(false);
    setGenerateProgress(null);
  };

  if (loading) {
    return (
      <PageShell width="wide">
        <p className="font-mono text-[13px] text-on-surface-variant py-16 text-center">Loading telemetry…</p>
      </PageShell>
    );
  }

  // Real telemetry derived from the most recent persisted briefing (/newsletter/history).
  const latestBriefing = history?.[0] || null;
  const grounding = latestBriefing?.grounding_reliability ?? null;
  const sqiScore = latestBriefing?.signal_quality_index ?? null;
  const signalsDelivered = latestBriefing?.total_articles ?? (data?.articles?.length ?? 0);
  const execTime = latestBriefing?.execution_time_seconds ?? null;
  const lastRunAt = latestBriefing?.generated_at
    ? new Date(latestBriefing.generated_at.endsWith('Z') ? latestBriefing.generated_at : latestBriefing.generated_at + 'Z')
    : null;
  const fmt = (v, digits = 1) => (v === null || v === undefined ? '—' : Number(v).toFixed(digits));

  return (
    <PageShell width="wide" className="flex flex-col gap-8">
      <PageHeader
        title="Mission control"
        subtitle="Trigger a run, watch the pipeline, and read the telemetry from the last one."
        actions={
          <Button onClick={generateBriefing} disabled={isGenerating}>
            <span className={`material-symbols-outlined text-[18px] ${isGenerating ? 'animate-spin' : ''}`}>
              {isGenerating ? 'autorenew' : 'bolt'}
            </span>
            {isGenerating ? 'Running…' : 'Synthesize briefing'}
          </Button>
        }
      />

      <PipelineProgress active={isGenerating} progressData={generateProgress} onClose={dismissProgress} />

      <section className="flex flex-col gap-4">
        <div className="flex items-baseline justify-between">
          <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">last run</span>
          <span className="font-mono text-[11px] text-on-surface-variant">
            {lastRunAt ? lastRunAt.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : 'no runs yet'}
          </span>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Metric
            label="Grounding"
            value={`${fmt(grounding)}%`}
            status={grounding === null ? 'no data' : grounding >= 90 ? 'stable' : 'degraded'}
          />
          <Metric
            label="SQI"
            value={fmt(sqiScore)}
            status={sqiScore === null ? 'no data' : sqiScore >= 60 ? 'healthy' : sqiScore >= 45 ? 'fair' : 'low'}
          />
          <Metric label="Signals" value={signalsDelivered} />
          <Metric label="Execution" value={execTime === null ? '—' : `${execTime.toFixed(0)}s`} />
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="p-6 flex flex-col gap-4 lg:col-span-1">
          <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary">active parameters</span>
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10.5px] uppercase tracking-[0.08em] text-on-surface-variant">topics</span>
              <div className="flex flex-wrap gap-1.5">
                {preferences?.preferred_topics?.slice(0, 4).map((topic, i) => (
                  <Chip key={i} selected>{topic}</Chip>
                ))}
                {(preferences?.preferred_topics?.length || 0) > 4 && (
                  <Chip>+{(preferences?.preferred_topics?.length || 0) - 4}</Chip>
                )}
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10.5px] uppercase tracking-[0.08em] text-on-surface-variant">exclusions</span>
              <div className="flex flex-wrap gap-1.5">
                {preferences?.excluded_topics?.length > 0 ? (
                  preferences.excluded_topics.slice(0, 4).map((exclusion, i) => (
                    <Chip key={i} muted>{exclusion}</Chip>
                  ))
                ) : (
                  <span className="font-reader text-sm text-on-surface-variant">None</span>
                )}
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6 flex flex-col gap-4 lg:col-span-2">
          <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary">signal radar</span>
          <div className="flex flex-col divide-y divide-outline-variant/20 max-h-[340px] overflow-y-auto -my-1">
            {data?.articles?.length ? data.articles.map((article, idx) => (
              <div key={idx} className="flex items-center justify-between gap-4 py-2.5">
                <div className="flex flex-col min-w-0">
                  <span className="font-mono text-[10px] uppercase tracking-[0.08em] text-on-surface-variant">
                    {article.tags?.[0] || article.source}
                  </span>
                  <span className="font-reader text-sm text-on-surface truncate">{article.title}</span>
                </div>
                <span className="font-mono text-[11px] text-on-surface-variant shrink-0">
                  trend {article.trend_score != null ? article.trend_score.toFixed(1) : '—'}
                </span>
              </div>
            )) : (
              <p className="font-reader text-sm text-on-surface-variant py-4">
                Radar clear. Synthesize a briefing to acquire signals.
              </p>
            )}
          </div>
        </Card>
      </div>

      <section className="flex flex-col gap-3">
        <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary">recent runs</span>
        {history?.length ? (
          <div className="flex flex-col gap-2">
            {history.slice(0, 5).map((run, i) => (
              <Link
                key={i}
                href={`/history/${run.id}`}
                className="flex items-center justify-between gap-4 py-2.5 px-4 rounded-lg border border-outline-variant/30 hover:border-primary/30 transition-colors"
              >
                <span className="font-mono text-[11px] text-on-surface-variant shrink-0">
                  {new Date(run.generated_at.endsWith('Z') ? run.generated_at : run.generated_at + 'Z').toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })}
                </span>
                <span className="font-reader text-sm text-on-surface truncate flex-1">{run.title || run.dominant_topics?.[0] || 'Briefing'}</span>
                <span className="font-mono text-[11px] text-primary shrink-0">SQI {run.signal_quality_index?.toFixed(1) || '—'}</span>
              </Link>
            ))}
          </div>
        ) : (
          <p className="font-reader text-sm text-on-surface-variant">No runs yet.</p>
        )}
      </section>

      <Link href="/" className="inline-flex items-center gap-1.5 font-mono text-[12px] text-on-surface-variant hover:text-primary transition-colors">
        Intelligence reader
        <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
      </Link>
    </PageShell>
  );
}
