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

  useEffect(() => {
    fetchLatest();
  }, []);

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
          user_id: user.id,
          preferred_topics: preferences?.preferred_topics || [],
          preferred_sources: preferences?.preferred_sources || [],
          excluded_topics: preferences?.excluded_topics || []
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
        <h1 className="font-headline text-4xl md:text-5xl font-bold text-on-surface mb-3 tracking-tight">Intelligence Feed</h1>
        <p className="text-on-surface-variant text-lg max-w-2xl">Good morning. Orchestration stability is nominal. Reviewing latest intelligence signals across your monitored sectors.</p>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Main Featured Column */}
        <div className="xl:col-span-2 flex flex-col gap-8">
          
          {/* Hero / Featured Insight */}
          {mainArticle ? (
            <article className="relative overflow-hidden rounded-xl bg-surface-container-low soft-shadow p-8 flex flex-col md:flex-row gap-8 items-center border border-outline-variant/30 group">
              <div className="flex-1 space-y-5 z-10">
                <div className="flex flex-wrap items-center gap-2">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-tertiary-container/30 text-tertiary text-xs font-bold uppercase tracking-wider border border-tertiary/10">
                    <span className="material-symbols-outlined text-[14px]">bolt</span> High Priority
                  </div>
                  {trustMetrics.grounding_reliability_pct > 80 && (
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider border border-primary/10">
                      <span className="material-symbols-outlined text-[14px]">verified</span> Grounded
                    </div>
                  )}
                  {trustMetrics.validation_success_rate > 70 && (
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary/10 text-secondary text-xs font-bold uppercase tracking-wider border border-secondary/10">
                      <span className="material-symbols-outlined text-[14px]">fact_check</span> Source Verified
                    </div>
                  )}
                </div>
                <h2 className="font-headline text-[28px] md:text-3xl font-bold text-on-surface leading-tight mt-1">{mainArticle.title}</h2>
                <p className="text-on-surface-variant text-[15px] leading-relaxed line-clamp-3">{mainArticle.summary}</p>
                <div className="pt-2 flex flex-wrap gap-4 items-center">
                  <a href={mainArticle.url} target="_blank" rel="noreferrer" className="bg-gradient-to-r from-primary to-primary/80 text-on-primary px-6 py-2.5 rounded-xl font-bold hover:shadow-[0_4px_14px_rgba(74,124,89,0.35)] transition-all duration-300 inline-flex items-center gap-2">
                    Analyze Full Report
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </a>
                  <button className="bg-surface/50 text-on-surface-variant border border-outline-variant/40 px-6 py-2.5 rounded-xl font-bold hover:bg-surface-variant/50 transition-colors">
                    Dismiss
                  </button>
                </div>
              </div>
            </article>
          ) : (
            <article className="relative overflow-hidden rounded-xl bg-surface-container-low soft-shadow p-8 flex flex-col items-center justify-center text-center border border-outline-variant/30 min-h-[300px]">
              <span className="material-symbols-outlined text-4xl text-outline mb-4">search_off</span>
              <h2 className="font-headline text-2xl font-bold text-on-surface mb-2">No Intelligence Signals</h2>
              <p className="text-on-surface-variant">Run the orchestration pipeline to generate your first briefing.</p>
            </article>
          )}

          {/* Metrics Bento Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* System Pulse */}
            <div className="bg-surface-container-low rounded-xl p-6 soft-shadow border border-outline-variant/20 flex flex-col h-full">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="font-headline text-xl font-bold text-on-surface">System Pulse</h3>
                  <p className="text-sm text-on-surface-variant">Real-time node health</p>
                </div>
                <span className="material-symbols-outlined text-primary bg-primary-container/30 p-2 rounded-lg">favorite</span>
              </div>
              <div className="flex-1 flex items-end justify-between">
                <div className="space-y-1">
                  <div className="text-4xl font-headline font-bold text-primary">{trustMetrics.grounding_reliability_pct.toFixed(1)}%</div>
                  <div className="text-sm text-tertiary font-medium flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">verified</span> Grounding Integrity
                  </div>
                </div>
                <div className="flex items-end gap-1.5 h-16 w-32 opacity-80">
                  <div className="w-1/6 bg-primary-container rounded-t-sm h-[40%]"></div>
                  <div className="w-1/6 bg-primary-container rounded-t-sm h-[60%]"></div>
                  <div className="w-1/6 bg-primary rounded-t-sm h-[50%]"></div>
                  <div className="w-1/6 bg-primary-container rounded-t-sm h-[80%]"></div>
                  <div className="w-1/6 bg-tertiary rounded-t-sm h-[90%]"></div>
                  <div className="w-1/6 bg-primary rounded-t-sm h-[100%]"></div>
                </div>
              </div>
            </div>

            {/* Signal Volume */}
            <div className="bg-surface-container-low rounded-xl p-6 soft-shadow border border-outline-variant/20 flex flex-col h-full">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h3 className="font-headline text-xl font-bold text-on-surface">Signal Volume</h3>
                  <p className="text-sm text-on-surface-variant">Inbound data events</p>
                </div>
                <span className="material-symbols-outlined text-tertiary bg-tertiary-container/30 p-2 rounded-lg">wifi_tethering</span>
              </div>
              <div className="flex-1 flex items-end justify-between">
                <div className="space-y-1">
                  <div className="text-4xl font-headline font-bold text-on-surface">{totalSignals}</div>
                  <div className="text-sm text-on-surface-variant font-medium flex items-center gap-1">
                    <span className="material-symbols-outlined text-[16px]">horizontal_rule</span> Signals Processed
                  </div>
                </div>
                <div className="relative w-16 h-16">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path className="text-surface-variant" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
                    <path className="text-tertiary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="100, 100" strokeWidth="3"></path>
                  </svg>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Right Sidebar Column */}
        <div className="flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <h3 className="font-headline text-xl font-bold text-on-surface">Recent Briefings</h3>
            <a className="text-sm text-primary font-semibold hover:underline" href="/briefing">View All</a>
          </div>

          <div className="flex flex-col gap-4">
            {data?.articles?.slice(0, 3).map((article, i) => (
              <div key={i} className="bg-surface-container-low p-5 rounded-xl border border-outline-variant/30 soft-shadow hover:bg-surface-variant/30 transition-colors cursor-pointer group">
                <div className="flex gap-4">
                  <div className={`w-12 h-12 rounded-full ${i===0 ? 'bg-primary-container text-on-primary-container' : i===1 ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-surface-variant text-on-surface-variant'} flex items-center justify-center shrink-0`}>
                    <span className="material-symbols-outlined">{article.source === 'github' ? 'code' : 'article'}</span>
                  </div>
                  <div>
                    <div className="text-[11px] text-on-surface-variant font-bold mb-1 tracking-wider">{article.source.toUpperCase()}</div>
                    <h4 className="font-body font-semibold text-on-surface leading-snug group-hover:text-primary transition-colors text-sm">{article.title}</h4>
                    
                    {/* Signal Strength Visualizer */}
                    <div className="mt-3 flex items-center gap-2">
                      <div className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">Signal Strength</div>
                      <div className="flex gap-0.5 h-3">
                        <div className={`w-1 rounded-full ${article.trend_score > 3 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                        <div className={`w-1 rounded-full ${article.trend_score > 5 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                        <div className={`w-1 rounded-full ${article.trend_score > 7 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                        <div className={`w-1 rounded-full ${article.trend_score > 8.5 ? 'bg-tertiary' : 'bg-surface-variant'}`}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
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
