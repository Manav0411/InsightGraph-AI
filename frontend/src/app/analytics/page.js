"use client";

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../lib/config';
import { useUser } from '../../context/UserContext';

export default function Analytics() {
  const { user } = useUser();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLatest();
  }, []);

  const fetchLatest = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/metrics`);
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

  if (loading) return <div className="p-8">Loading Analytics...</div>;

  const metrics = data || {};
  const trustMetrics = data?.trust_metrics || { grounding_reliability_pct: 0, validation_success_rate: 0 };
  const tokens = { prompt_tokens: data?.total_prompt_tokens || 0, completion_tokens: data?.total_completion_tokens || 0 };
  const totalTokens = (tokens.prompt_tokens + tokens.completion_tokens).toLocaleString();
  const timings = data?.timings || {};

  return (
    <div className="flex flex-col gap-10">
      <style dangerouslySetInnerHTML={{__html: `
        .shadow-terra { box-shadow: 0 4px 20px rgba(46, 50, 48, 0.06); }
        .blob-1 { border-radius: 40px 20px 40px 20px; }
        .blob-2 { border-radius: 20px 40px 20px 40px; }
        .blob-3 { border-radius: 30px; }
      `}} />
      <header>
        <h1 className="font-headline text-4xl md:text-5xl font-bold text-on-surface mb-3 tracking-tight">Workflow Analytics</h1>
        <p className="text-on-surface-variant text-lg">Observability telemetry and orchestration tracing.</p>
      </header>

      {/* Section A: Workflow Overview */}
      <section>
        <h2 className="font-headline text-2xl font-bold text-on-surface mb-6 border-b border-outline-variant/30 pb-3">Workflow Overview</h2>
        <div className="bg-surface shadow-terra rounded-[2rem] p-6 md:p-8 border border-outline-variant/30 flex flex-col">
          <div className="flex justify-between items-center mb-8">
            <h3 className="font-headline text-2xl font-semibold text-on-surface">Inference Flow Topology</h3>
            <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary font-bold text-sm">
              <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-40 bg-primary"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span></span>
              Orchestration Active
            </span>
          </div>
          <div className="relative w-full py-10 flex flex-col md:flex-row items-center justify-between gap-12 md:gap-4 px-4 md:px-16">
            <div className="hidden md:block absolute top-1/2 left-24 right-24 h-1 bg-surface-variant rounded-full -translate-y-1/2 z-0">
              <div className="h-full bg-gradient-to-r from-surface-variant via-primary-container to-tertiary-container opacity-50 rounded-full w-full"></div>
            </div>
            
            {/* Retriever */}
            <div className="relative z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-32 h-32 bg-surface-container blob-1 shadow-terra flex items-center justify-center text-on-surface transition-transform duration-300 group-hover:-translate-y-2 group-hover:bg-surface-container-high border-2 border-transparent group-hover:border-outline-variant/50">
                <span className="material-symbols-outlined text-6xl opacity-80">search</span>
              </div>
              <div className="mt-6 text-center">
                <h4 className="font-headline font-semibold text-on-surface text-lg">Retriever</h4>
                <div className="flex items-center justify-center gap-1.5 mt-1 text-sm text-on-surface-variant">
                  <span className={`w-2 h-2 rounded-full ${timings.retriever > 5 ? 'bg-error' : timings.retriever > 2 ? 'bg-tertiary' : 'bg-primary'}`}></span>
                  {timings.retriever ? `${timings.retriever.toFixed(1)}s` : '0.0s'}
                </div>
              </div>
            </div>
            
            <div className="md:hidden w-1 h-12 bg-surface-variant rounded-full my-2"></div>
            
            {/* Validator */}
            <div className="relative z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-40 h-40 bg-primary-container text-on-primary-container blob-2 shadow-terra flex items-center justify-center transition-transform duration-300 group-hover:-translate-y-2 group-hover:shadow-lg border-4 border-surface">
                <span className="material-symbols-outlined text-7xl">verified_user</span>
              </div>
              <div className="mt-6 text-center">
                <h4 className="font-headline font-semibold text-on-surface text-lg">Validator</h4>
                <div className="flex items-center justify-center gap-1.5 mt-1 text-sm text-primary font-medium">
                  <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                  Processing active
                </div>
              </div>
            </div>
            
            <div className="md:hidden w-1 h-12 bg-surface-variant rounded-full my-2"></div>
            
            {/* Ranker */}
            <div className="relative z-10 flex flex-col items-center group cursor-pointer">
              <div className="w-32 h-32 bg-tertiary-container text-on-tertiary-container blob-3 shadow-terra flex items-center justify-center transition-transform duration-300 group-hover:-translate-y-2 group-hover:bg-[#cfae70]">
                <span className="material-symbols-outlined text-6xl opacity-90">format_list_numbered</span>
              </div>
              <div className="mt-6 text-center">
                <h4 className="font-headline font-semibold text-on-surface text-lg">Ranker</h4>
                <div className="flex items-center justify-center gap-1.5 mt-1 text-sm text-on-surface-variant">
                  <span className={`w-2 h-2 rounded-full ${timings.ranker > 5 ? 'bg-error' : timings.ranker > 2 ? 'bg-tertiary' : 'bg-primary'}`}></span>
                  {timings.ranker ? `${timings.ranker.toFixed(1)}s` : '0.0s'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section B: Pipeline Health */}
      <section>
        <h2 className="font-headline text-2xl font-bold text-on-surface mb-6 border-b border-outline-variant/30 pb-3">Pipeline Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-gradient-to-br from-surface-container-low to-transparent shadow-sm rounded-xl p-6 border border-outline-variant/30">
            <h3 className="font-body text-on-surface-variant text-[11px] font-bold uppercase tracking-wider mb-2">Grounding Reliability</h3>
            <div className="text-4xl font-headline font-bold text-on-surface">{trustMetrics.grounding_reliability_pct.toFixed(1)}%</div>
          </div>
          <div className="bg-gradient-to-br from-surface-container-low to-transparent shadow-sm rounded-xl p-6 border border-outline-variant/30">
            <h3 className="font-body text-on-surface-variant text-[11px] font-bold uppercase tracking-wider mb-2">Validation Success</h3>
            <div className="text-4xl font-headline font-bold text-on-surface">{trustMetrics.validation_success_rate.toFixed(1)}%</div>
          </div>
          <div className="bg-gradient-to-br from-surface-container-low to-transparent shadow-sm rounded-xl p-6 border border-outline-variant/30">
            <h3 className="font-body text-on-surface-variant text-[11px] font-bold uppercase tracking-wider mb-2">Source Diversity</h3>
            <div className={`text-2xl font-headline font-bold mt-2 ${trustMetrics.source_diversity_healthy ? 'text-primary' : 'text-error'}`}>
              {trustMetrics.source_diversity_healthy ? 'Healthy' : 'Degraded'}
            </div>
          </div>
          <div className="bg-gradient-to-br from-surface-container-low to-transparent shadow-sm rounded-xl p-6 border border-outline-variant/30">
            <h3 className="font-body text-on-surface-variant text-[11px] font-bold uppercase tracking-wider mb-2">Retry Count</h3>
            <div className="text-4xl font-headline font-bold text-on-surface">0</div>
          </div>
        </div>
      </section>

      {/* Section C: Token & Timing Analytics */}
      <section>
        <h2 className="font-headline text-2xl font-bold text-on-surface mb-6 border-b border-outline-variant/30 pb-3">Token & Timing Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-surface-container-low to-transparent shadow-sm rounded-xl p-8 border border-outline-variant/30 flex justify-between items-center">
            <div>
              <h3 className="font-body text-on-surface-variant text-[12px] font-bold uppercase tracking-wider mb-1">Total Token Usage</h3>
              <p className="text-[13px] text-on-surface-variant">Prompt & Completion Tokens</p>
            </div>
            <div className="text-5xl font-headline font-bold text-primary">{totalTokens}</div>
          </div>
          <div className="bg-gradient-to-br from-surface-container-low to-transparent shadow-sm rounded-xl p-8 border border-outline-variant/30 flex justify-between items-center">
            <div>
              <h3 className="font-body text-on-surface-variant text-[12px] font-bold uppercase tracking-wider mb-1">Execution Latency</h3>
              <p className="text-[13px] text-on-surface-variant">End-to-end pipeline speed</p>
            </div>
            <div className="text-5xl font-headline font-bold text-tertiary">{data?.execution_time_seconds?.toFixed(1)}s</div>
          </div>
        </div>
      </section>

      {/* Section D: Trace Explorer */}
      <section>
        <div className="flex items-center justify-between mb-6 border-b border-outline-variant/30 pb-3">
          <h2 className="font-headline text-2xl font-bold text-on-surface">Trace Explorer</h2>
          <button className="text-primary hover:text-on-primary-fixed-variant font-medium text-sm flex items-center gap-1 transition-colors">
            View full traces
            <span className="material-symbols-outlined text-sm">arrow_forward</span>
          </button>
        </div>
        <div className="bg-surface shadow-terra rounded-2xl p-2 border border-outline-variant/30 flex flex-col gap-1">
          <div className="flex items-start gap-5 p-5 hover:bg-surface-container-low transition-colors rounded-xl cursor-pointer group">
            <div className="mt-1 bg-primary/10 p-2 rounded-full text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">sync</span>
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start mb-1">
                <h5 className="font-body font-semibold text-on-surface text-base">Pipeline generated new intelligence briefing</h5>
                <span className="text-xs text-on-surface-variant font-medium">{new Date(data?.generated_at || Date.now()).toLocaleTimeString()}</span>
              </div>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Retrieved, validated, and ranked {trustMetrics.total_signals_processed} intelligence signals.
                Rejected {trustMetrics.hallucination_rejections} invalid sources.
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-5 p-5 hover:bg-surface-container-low transition-colors rounded-xl cursor-pointer group">
            <div className="mt-1 bg-tertiary/10 p-2 rounded-full text-tertiary group-hover:bg-tertiary group-hover:text-on-tertiary transition-colors flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">tune</span>
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start mb-1">
                <h5 className="font-body font-semibold text-on-surface text-base">Token consumption logged</h5>
                <span className="text-xs text-on-surface-variant font-medium">{new Date(data?.generated_at || Date.now()).toLocaleTimeString()}</span>
              </div>
              <p className="text-sm text-on-surface-variant leading-relaxed">Model orchestration utilized {tokens.prompt_tokens} prompt tokens and {tokens.completion_tokens} completion tokens.</p>
            </div>
          </div>
          
          <div className="flex items-start gap-5 p-5 hover:bg-surface-container-low transition-colors rounded-xl cursor-pointer group">
            <div className="mt-1 bg-secondary/10 p-2 rounded-full text-secondary group-hover:bg-secondary group-hover:text-on-secondary transition-colors flex items-center justify-center">
              <span className="material-symbols-outlined text-xl">speed</span>
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start mb-1">
                <h5 className="font-body font-semibold text-on-surface text-base">Latency telemetry captured</h5>
                <span className="text-xs text-on-surface-variant font-medium">{new Date(data?.generated_at || Date.now()).toLocaleTimeString()}</span>
              </div>
              <p className="text-sm text-on-surface-variant leading-relaxed">End-to-end execution completed in {data?.execution_time_seconds?.toFixed(1)}s. Retriever step latency: {timings.retriever?.toFixed(1)}s.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
