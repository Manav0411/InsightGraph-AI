"use client";

import { useState, useEffect } from 'react';
import PipelineProgress from '../components/orchestration/PipelineProgress';
import { API_BASE_URL } from '../lib/config';
import { useUser } from '../context/UserContext';

export default function CommandCenter() {
  const { user, preferences } = useUser();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateProgress, setGenerateProgress] = useState(null);

  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const initDashboard = async () => {
      await Promise.all([fetchLatest(), fetchAnalytics()]);
      setLoading(false);
    };
    initDashboard();
  }, [user.id]);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/analytics/trends?user_id=${user.id}`);
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
      const res = await fetch(`${API_BASE_URL}/newsletter/latest`);
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
    setGenerateProgress({ stage: 'Initializing...', log: [], elapsed: '0.0s', progress: 0 });
    const startTime = Date.now();
    let currentLogs = [];
    
    // Update elapsed time
    const timerInterval = setInterval(() => {
      setGenerateProgress(prev => prev ? { ...prev, elapsed: ((Date.now() - startTime) / 1000).toFixed(1) + 's' } : null);
    }, 100);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s global timeout for stream

      const response = await fetch(`${API_BASE_URL}/newsletter/generate-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({ 
          user_id: user.id
        })
      });
      
      clearTimeout(timeoutId);
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let stagesCount = 0;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6);
            if (dataStr) {
              const eventData = JSON.parse(dataStr);
              
              if (eventData.status === 'started') {
                stagesCount++;
                const newLog = `[AGENT] INFO: Started ${eventData.stage}`;
                currentLogs = [...currentLogs, newLog].slice(-4);
                
                setGenerateProgress(prev => ({
                  ...prev,
                  stage: eventData.stage,
                  log: currentLogs,
                  progress: Math.min((stagesCount / 6) * 100, 95)
                }));
              } else if (eventData.stage === 'Done') {
                clearInterval(timerInterval);
                setGenerateProgress(prev => ({ ...prev, progress: 100, stage: 'Complete' }));
                setTimeout(() => {
                  window.location.href = '/briefing';
                }, 2500);
              } else if (eventData.stage === 'Error') {
                clearInterval(timerInterval);
                currentLogs = [...currentLogs, `[SYS] ERROR: ${eventData.error}`].slice(-4);
                setGenerateProgress(prev => ({ ...prev, stage: 'Failed', log: currentLogs }));
                setTimeout(() => setIsGenerating(false), 3000);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('SSE Error:', error);
      clearInterval(timerInterval);
      
      const errorMsg = error.name === 'AbortError' ? 'Stream timed out' : 'Network error';
      currentLogs = [...currentLogs, `[SYS] ERROR: ${errorMsg}. Signal synthesis interrupted.`].slice(-4);
      setGenerateProgress(prev => ({ ...prev, stage: 'Failed', log: currentLogs }));
      
      // Let user read the error before resetting
      setTimeout(() => setIsGenerating(false), 5000);
    }
  };

  if (loading) return <div className="p-8 font-body text-on-surface-variant">Loading Intelligence Feed...</div>;

  const mainArticle = data?.recommended_articles?.[0] || data?.articles?.[0];
  const trustMetrics = data?.trust_metrics || { grounding_reliability_pct: 0, validation_success_rate: 0 };
  const totalSignals = trustMetrics.total_signals_processed || 0;

  return (
    <>
      <header className="mb-10">
        <h1 className="font-headline text-4xl md:text-5xl font-bold text-on-surface mb-3 tracking-tight">Mission Control</h1>
        <p className="text-on-surface-variant text-lg max-w-2xl">Live ecosystem pulse. Orchestration stability is nominal.</p>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Main Featured Column */}
        <div className="xl:col-span-2 flex flex-col gap-8">
          
          {/* Ecosystem Pulse (Hero Telemetry) */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 soft-shadow">
              <h3 className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest mb-2">Fastest Growing</h3>
              <div className="text-xl font-headline font-bold text-primary truncate">
                {analytics?.fastest_growing_topics?.[0]?.topic || 'AI Agents'}
              </div>
              <div className="text-xs font-bold text-tertiary mt-2">↑ Momentum Accelerating</div>
            </div>
            
            <div className="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 soft-shadow">
              <h3 className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest mb-2">Most Reliable Source</h3>
              <div className="text-xl font-headline font-bold text-on-surface truncate capitalize">
                {analytics?.source_distribution?.[0]?.source || 'github'}
              </div>
              <div className="text-xs font-bold text-primary mt-2">94% Grounding Score</div>
            </div>

            <div className="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 soft-shadow">
              <h3 className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest mb-2">Signal Velocity</h3>
              <div className="text-xl font-headline font-bold text-on-surface truncate">
                {totalSignals} / hr
              </div>
              <div className="text-xs font-bold text-tertiary mt-2">High Inbound Rate</div>
            </div>

            <div className="bg-surface-container-low rounded-xl p-5 border border-outline-variant/30 soft-shadow">
              <h3 className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest mb-2">System Pulse</h3>
              <div className="text-xl font-headline font-bold text-primary truncate">
                {trustMetrics.grounding_reliability_pct.toFixed(1)}%
              </div>
              <div className="text-xs font-bold text-primary mt-2">Nodes Healthy</div>
            </div>
          </section>

          {/* Today's Signals */}
          <section>
            <h2 className="font-headline text-xl font-bold text-on-surface mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-tertiary text-[20px]">radar</span> 
              Live Intelligence Signals
            </h2>
            <div className="flex flex-col gap-3">
              {data?.articles?.map((article, idx) => (
                <div key={idx} className="bg-surface-container p-4 rounded-xl border border-outline-variant/20 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-primary/30 transition-colors">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1.5">
                      <span className="text-[10px] font-bold text-tertiary uppercase tracking-widest bg-tertiary-container/30 px-2 py-0.5 rounded-full">
                        {article.tags?.[0] || 'Signal'}
                      </span>
                      {article.grounding_verified && (
                        <span className="text-[10px] text-primary flex items-center gap-1 font-bold uppercase tracking-wider">
                          <span className="material-symbols-outlined text-[12px]">verified</span> Grounded
                        </span>
                      )}
                    </div>
                    <h3 className="font-headline font-bold text-on-surface text-base">{article.title}</h3>
                  </div>
                  
                  <div className="flex items-center gap-6 shrink-0">
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Momentum</span>
                      <div className="flex gap-0.5 h-2">
                        <div className={`w-1.5 rounded-full ${article.trend_score > 3 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                        <div className={`w-1.5 rounded-full ${article.trend_score > 5 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                        <div className={`w-1.5 rounded-full ${article.trend_score > 7 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                        <div className={`w-1.5 rounded-full ${article.trend_score > 8.5 ? 'bg-tertiary' : 'bg-surface-variant'}`}></div>
                      </div>
                    </div>
                    <div className="w-[1px] h-8 bg-outline-variant/30"></div>
                    <div className="flex flex-col items-end min-w-[60px]">
                      <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">Source</span>
                      <span className="font-bold text-xs text-on-surface uppercase">{article.source}</span>
                    </div>
                  </div>
                </div>
              ))}
              {!data?.articles?.length && (
                <div className="text-center p-8 text-on-surface-variant bg-surface-container-low rounded-xl border border-outline-variant/20">
                  No signals detected. Awaiting orchestration loop.
                </div>
              )}
            </div>
          </section>

          {/* Ecosystem Momentum Micro-trends */}
          <section className="bg-surface-container-low p-6 rounded-xl border border-outline-variant/30 soft-shadow">
             <h2 className="font-headline text-lg font-bold text-on-surface mb-4">Ecosystem Momentum</h2>
             <div className="flex flex-col gap-4">
                {analytics?.fastest_growing_topics?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex justify-between items-center border-b border-outline-variant/20 pb-3 last:border-0 last:pb-0">
                    <span className="font-medium text-sm text-on-surface capitalize">{t.topic}</span>
                    <span className="font-bold text-xs text-tertiary flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">trending_up</span> Accelerating
                    </span>
                  </div>
                ))}
             </div>
          </section>

        </div>

        {/* Right Sidebar Column */}
        <div className="flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <h3 className="font-headline text-xl font-bold text-on-surface">Recent Briefing</h3>
            <a className="text-sm text-primary font-semibold hover:underline" href="/briefing">Open Workspace</a>
          </div>

          <div className="bg-surface-container-low p-5 rounded-xl border border-outline-variant/30 soft-shadow flex flex-col gap-3">
             <div className="flex justify-between items-start">
               <div className="text-3xl font-headline font-bold text-primary">{data?.metrics?.avg_sqi?.toFixed(1) || '8.5'}</div>
               <span className="text-xs font-bold text-on-surface-variant bg-surface-variant px-2 py-1 rounded-full uppercase tracking-wider">SQI</span>
             </div>
             <p className="text-xs text-on-surface-variant font-medium">
               Latest intelligence synthesized successfully. Read the full contextual analysis in the Briefing Workspace.
             </p>
             <a href="/briefing" className="mt-2 text-sm font-bold text-surface bg-on-surface py-2 rounded-lg text-center hover:bg-on-surface/90 transition-colors">
               Read Full Briefing
             </a>
          </div>

          <button 
            onClick={generateBriefing}
            disabled={isGenerating}
            className={`mt-4 w-full py-3.5 rounded-xl font-bold transition-all duration-300 flex items-center justify-center gap-2 shadow-sm
              ${isGenerating 
                ? 'bg-surface-variant text-on-surface-variant cursor-not-allowed opacity-70' 
                : 'bg-on-surface text-surface hover:bg-on-surface/90 hover:shadow-md hover:-translate-y-0.5'}`}
          >
            {isGenerating ? (
              <>
                <span className="material-symbols-outlined text-[20px] animate-spin">refresh</span> Orchestrating...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[20px]">add</span> Synthesize Intelligence Briefing
              </>
            )}
          </button>

        </div>
      </div>

      <PipelineProgress active={isGenerating} progressData={generateProgress} />
    </>
  );
}
