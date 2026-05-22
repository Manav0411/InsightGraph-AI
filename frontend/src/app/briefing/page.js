"use client";

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../lib/config';

export default function Briefing() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Orchestration State
  const [isGenerating, setIsGenerating] = useState(false);
  const [orchestrationStages, setOrchestrationStages] = useState([]);
  
  const fetchLatest = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/newsletter/latest`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error("Failed to fetch latest briefing:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatest();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setOrchestrationStages([]);
    
    try {
      const response = await fetch(`${API_BASE_URL}/newsletter/generate-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: "default_user", topic: "General Intelligence" })
      });
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n\\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.substring(6));
              setOrchestrationStages(prev => {
                const existing = prev.findIndex(s => s.stage === eventData.stage);
                if (existing >= 0) {
                  const updated = [...prev];
                  updated[existing] = eventData;
                  return updated;
                }
                return [...prev, eventData];
              });
              
              if (eventData.stage === 'Done' || eventData.stage === 'Error') {
                setTimeout(() => {
                  setIsGenerating(false);
                  fetchLatest();
                }, 2000);
              }
            } catch (e) {
              console.error("Failed to parse SSE line", line);
            }
          }
        }
      }
    } catch (e) {
      console.error("Generation failed", e);
      setIsGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-outline-variant/30 border-t-primary rounded-full animate-spin"></div>
          <p className="font-headline text-on-surface-variant tracking-wide">Loading Intelligence Briefing...</p>
        </div>
      </div>
    );
  }

  const mainArticle = data?.articles?.[0] || null;
  const relatedArticles = data?.articles?.slice(1) || [];
  const trustMetrics = data?.trust_metrics || null;

  return (
    <div className="w-full max-w-[1200px] mx-auto flex flex-col gap-12 relative">
      
      {/* Header with Generate Action */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-outline-variant/30 pb-6 gap-6">
        <div>
          <h1 className="font-headline text-4xl font-bold text-on-surface tracking-tight">Intelligence Briefing</h1>
          <p className="text-on-surface-variant mt-2 font-medium">
            {data ? `Synthesized in ${data.execution_time_seconds?.toFixed(1)}s • ${data.metrics?.total_articles_processed} Signals Processed` : "No briefing generated yet."}
          </p>
        </div>
        <button 
          onClick={handleGenerate} 
          disabled={isGenerating}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 shadow-sm
            ${isGenerating ? 'bg-surface-variant/50 text-on-surface-variant cursor-not-allowed opacity-70' : 'bg-gradient-to-r from-primary to-primary/80 text-on-primary hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(74,124,89,0.35)]'}`}
        >
          <span className={`material-symbols-outlined ${isGenerating ? 'animate-spin' : ''}`}>
            {isGenerating ? 'sync' : 'auto_awesome'}
          </span>
          {isGenerating ? 'Orchestrating...' : 'Synthesize New Briefing'}
        </button>
      </div>

      {/* Live Orchestration Panel Overlay */}
      {isGenerating && (
        <div className="fixed inset-0 bg-surface/80 backdrop-blur-md z-[100] flex justify-center items-center p-4">
          <div className="bg-surface-container-lowest p-10 rounded-[2rem] shadow-[0_20px_40px_rgba(0,0,0,0.1)] w-full max-w-lg border border-outline-variant/40">
            <h2 className="font-headline text-2xl mb-2 text-center text-on-surface font-bold">Live Orchestration</h2>
            <p className="text-on-surface-variant text-center mb-8 text-sm">Executing LangGraph Pipeline</p>
            
            <div className="flex flex-col gap-4">
              {orchestrationStages.map((stage, idx) => (
                <div key={idx} className={`flex items-center gap-4 p-4 rounded-xl transition-all duration-300
                  ${stage.status === 'started' ? 'bg-primary/10 border border-primary/30' : 'bg-surface-container border border-transparent'}`}>
                  
                  {stage.status === 'completed' ? (
                    <span className="material-symbols-outlined text-primary">check_circle</span>
                  ) : stage.status === 'failed' ? (
                    <span className="material-symbols-outlined text-error">error</span>
                  ) : (
                    <div className="w-6 h-6 border-[3px] border-primary/30 border-t-primary rounded-full animate-spin"></div>
                  )}
                  
                  <span className={`font-medium ${stage.status === 'started' ? 'font-bold text-primary' : 'text-on-surface'}`}>
                    {stage.stage}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {mainArticle ? (
        <div className="flex flex-col lg:flex-row gap-16 justify-between items-start">
          
          {/* Left Column: Article Body (Editorial Layout) */}
          <article className="flex-1 flex flex-col gap-10 max-w-[700px] w-full">
            <header className="flex flex-col gap-6">
              <div className="flex items-center gap-3 text-sm text-tertiary">
                {mainArticle.tags?.slice(0, 1).map(tag => (
                  <span key={tag} className="px-3 py-1 bg-[#c4a66a]/20 rounded-full font-bold uppercase tracking-wider text-xs">
                    {tag}
                  </span>
                ))}
                <span className="text-outline-variant">•</span>
                
                {/* Signal Strength Visualizer */}
                <div className="flex items-center gap-2">
                  <span className="text-on-surface-variant font-bold text-xs uppercase tracking-wider">Signal Strength</span>
                  <div className="flex gap-0.5 h-3">
                    <div className={`w-1 rounded-full ${mainArticle.trend_score > 3 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                    <div className={`w-1 rounded-full ${mainArticle.trend_score > 5 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                    <div className={`w-1 rounded-full ${mainArticle.trend_score > 7 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                    <div className={`w-1 rounded-full ${mainArticle.trend_score > 8.5 ? 'bg-tertiary' : 'bg-surface-variant'}`}></div>
                  </div>
                </div>
              </div>
              
              <h1 className="font-headline text-3xl md:text-[40px] font-bold leading-tight text-on-surface tracking-tight mt-1">
                {mainArticle.title}
              </h1>
              
              <div className="flex flex-wrap items-center gap-4 mt-2 py-4 border-y border-outline-variant/30">
                <div className="flex flex-col">
                  <span className="font-bold text-sm text-on-surface">Source: {mainArticle.source}</span>
                  <div className="flex items-center gap-3 mt-1.5">
                    {mainArticle.grounding_verified && (
                      <span className="text-xs text-primary flex items-center gap-1 font-bold uppercase tracking-wider">
                        <span className="material-symbols-outlined text-[14px]">verified</span> Grounded
                      </span>
                    )}
                    <span className="text-xs text-secondary flex items-center gap-1 font-bold uppercase tracking-wider">
                      <span className="material-symbols-outlined text-[14px]">fact_check</span> Confidence: High
                    </span>
                  </div>
                </div>
              </div>
            </header>

            <div className="font-body text-on-surface-variant text-lg leading-relaxed space-y-6">
              <p className="text-xl text-on-surface leading-loose">
                {mainArticle.summary}
              </p>
              
              {mainArticle.recommendation_reasons?.length > 0 && (
                <div className="my-8 bg-gradient-to-br from-surface-container-low to-transparent border border-outline-variant/30 rounded-2xl p-6 md:p-8 shadow-sm relative overflow-hidden group">
                  <div className="absolute top-0 left-0 w-1 h-full bg-tertiary/60"></div>
                  <div className="flex items-center gap-2 text-tertiary font-bold mb-4 uppercase tracking-wider text-[13px]">
                    <span className="material-symbols-outlined text-[16px]">psychology</span>
                    AI Thought Process
                  </div>
                  <p className="text-on-surface font-medium text-base mb-3">Signal ranked highly due to:</p>
                  <ul className="flex flex-col gap-3">
                    {mainArticle.recommendation_reasons.map((reason, i) => (
                      <li key={i} className="text-sm text-on-surface-variant flex items-start gap-3 leading-relaxed">
                        <span className="text-tertiary mt-1">•</span>
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {mainArticle.why_it_matters && (
                <blockquote className="my-12 pl-6 border-l-4 border-tertiary py-2 bg-gradient-to-r from-surface-container-low to-transparent">
                  <p className="font-headline text-2xl italic text-on-surface leading-relaxed">
                    {mainArticle.why_it_matters}
                  </p>
                  <footer className="mt-4 text-sm font-bold text-tertiary uppercase tracking-wider">— Contextual Analysis</footer>
                </blockquote>
              )}
            </div>
            
            <a href={mainArticle.url} target="_blank" rel="noreferrer" 
               className="inline-flex items-center gap-2 text-surface font-bold self-start bg-on-surface hover:bg-on-surface/90 hover:-translate-y-0.5 hover:shadow-md px-6 py-3 rounded-xl transition-all duration-300">
              Read Original Report <span className="material-symbols-outlined text-[18px]">open_in_new</span>
            </a>
          </article>

          {/* Right Column: Analytical Signals */}
          <aside className="w-full lg:w-[360px] flex flex-col gap-8 sticky top-12 shrink-0">
            
            {trustMetrics && (
              <div className="bg-surface-container-low rounded-2xl p-6 border border-outline-variant/30 shadow-sm">
                <div className="flex items-center gap-3 border-b border-outline-variant/30 pb-4 mb-6">
                  <span className="material-symbols-outlined text-primary text-3xl">monitoring</span>
                  <h2 className="font-headline text-xl font-bold">Trust Telemetry</h2>
                </div>
                
                <div className="flex flex-col gap-5">
                  <div>
                    <div className="flex justify-between items-end mb-2">
                      <span className="text-sm font-bold text-on-surface">Grounding Reliability</span>
                      <span className="text-[11px] font-bold text-primary">{trustMetrics.grounding_reliability_pct}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-outline-variant/20 rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full transition-all duration-1000" style={{ width: `${trustMetrics.grounding_reliability_pct}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-end mb-2">
                      <span className="text-sm font-bold text-on-surface">Validation Success</span>
                      <span className="text-[11px] font-bold text-tertiary">{trustMetrics.validation_success_rate}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-outline-variant/20 rounded-full overflow-hidden">
                      <div className="h-full bg-tertiary rounded-full transition-all duration-1000" style={{ width: `${trustMetrics.validation_success_rate}%` }}></div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center mt-2 p-3 bg-surface-container rounded-xl">
                    <span className="text-xs text-on-surface-variant font-medium">Source Diversity</span>
                    <span className={`text-xs font-bold ${trustMetrics.source_diversity_healthy ? 'text-primary' : 'text-error'}`}>
                      {trustMetrics.source_diversity_healthy ? "Healthy" : "Low"}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {relatedArticles.length > 0 && (
              <div className="flex flex-col gap-4">
                <h3 className="font-headline text-lg font-bold pl-2 text-on-surface">Related Intelligence</h3>
                
                {relatedArticles.map((article, idx) => (
                  <div key={idx} className="flex flex-col gap-2 p-5 bg-surface-container-low rounded-2xl border border-outline-variant/30 cursor-pointer hover:-translate-y-1 hover:shadow-md transition-all duration-200">
                    <div>
                      {article.tags?.[0] && (
                        <span className="text-[10px] font-bold text-tertiary uppercase tracking-wider mb-2 block">{article.tags[0]}</span>
                      )}
                      <h4 className="font-headline text-base font-bold leading-snug text-on-surface">{article.title}</h4>
                      <p className="text-xs text-on-surface-variant mt-2 line-clamp-2 leading-relaxed">{article.summary}</p>
                      
                      <div className="flex justify-between items-center mt-4">
                        <span className="text-[11px] font-bold uppercase text-on-surface-variant">{article.source}</span>
                        {article.personalization_boost > 0 && (
                          <span className="material-symbols-outlined text-[14px] text-tertiary" title="Personalized Match">stars</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </aside>

        </div>
      ) : (
        <div className="text-center py-24 text-on-surface-variant">
          <span className="material-symbols-outlined text-5xl text-outline-variant mb-4">article</span>
          <p className="font-medium">No intelligence briefing available. Generate one to get started.</p>
        </div>
      )}
    </div>
  );
}
