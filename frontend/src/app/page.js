"use client";

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../lib/config';
import { useUser } from '../context/UserContext';

export default function IntelligenceReader() {
  const { user, getToken } = useUser();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const token = await getToken();
        const headers = { 'Authorization': `Bearer ${token}` };
        
        const [resLatest, resHistory] = await Promise.all([
          fetch(`${API_BASE_URL}/newsletter/latest`, { headers }),
          fetch(`${API_BASE_URL}/newsletter/history`, { headers })
        ]);
        if (resLatest.ok) {
          const json = await resLatest.json();
          setData(json);
        }
        if (resHistory.ok) {
          const json = await resHistory.json();
          setHistory(json);
        }
      } catch (e) {
        console.error("Failed to fetch data:", e);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchLatest();
  }, [user?.id, getToken]);

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

  const articles = data?.articles || [];

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-16 relative pb-24">
      
      {/* Header */}
      <header className="flex flex-col items-center text-center border-b border-outline-variant/30 pb-10 pt-4">
        <div className="text-[10px] font-bold text-primary uppercase tracking-widest mb-4">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </div>
        <h1 className="font-headline text-5xl md:text-6xl font-bold text-on-surface tracking-tight leading-tight mb-4">
          {data?.briefing?.title || "Intelligence Briefing"}
        </h1>
        <p className="text-on-surface-variant text-lg font-medium max-w-2xl">
          Your weekly dose of the most important AI updates
        </p>
      </header>

      {articles.length > 0 ? (
        <div className="flex flex-col gap-12">
          {articles.map((article, idx) => (
            <article key={idx} className="bg-surface-container-low rounded-3xl p-8 md:p-10 border border-outline-variant/20 shadow-sm relative overflow-hidden group hover:border-primary/30 transition-colors duration-500">
              
              {/* Top Meta Info */}
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <span className="px-3 py-1 bg-surface-variant/50 rounded-full font-bold uppercase tracking-wider text-[11px] text-on-surface-variant">
                  {article.source}
                </span>
                {article.grounding_verified && (
                  <span className="text-[11px] text-primary flex items-center gap-1 font-bold uppercase tracking-wider bg-primary/10 px-3 py-1 rounded-full">
                    <span className="material-symbols-outlined text-[14px]">verified</span> Grounded
                  </span>
                )}
                <div className="flex-1"></div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">Trend Strength</span>
                  <div className="flex gap-0.5 h-2">
                    <div className={`w-1.5 rounded-full ${article.trend_score > 3 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                    <div className={`w-1.5 rounded-full ${article.trend_score > 5 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                    <div className={`w-1.5 rounded-full ${article.trend_score > 7 ? 'bg-primary' : 'bg-surface-variant'}`}></div>
                    <div className={`w-1.5 rounded-full ${article.trend_score > 8.5 ? 'bg-tertiary' : 'bg-surface-variant'}`}></div>
                  </div>
                </div>
              </div>

              {/* Title */}
              <h2 className="font-headline text-3xl md:text-4xl font-bold leading-tight text-on-surface tracking-tight mb-6">
                {article.title}
              </h2>

              {/* Summary */}
              <p className="font-body text-on-surface-variant text-lg leading-relaxed mb-8">
                {article.summary}
              </p>

              {/* Why It Matters (Highlighted) */}
              {article.why_it_matters && (
                <div className="bg-gradient-to-br from-surface-container to-transparent border-l-4 border-tertiary p-6 rounded-r-2xl mb-8 relative">
                  <h3 className="text-xs font-bold text-tertiary uppercase tracking-widest mb-2 flex items-center gap-2">
                    <span className="material-symbols-outlined text-[16px]">psychology</span> Why It Matters
                  </h3>
                  <p className="font-headline text-xl text-on-surface leading-snug">
                    {article.why_it_matters}
                  </p>
                </div>
              )}

              {/* Footer Meta & Link */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-6 border-t border-outline-variant/20 mt-4">
                <div className="flex flex-wrap items-center gap-2">
                  {article.tags?.slice(0, 3).map(tag => (
                    <span key={tag} className="px-3 py-1.5 bg-surface rounded-full font-bold uppercase tracking-wider text-[10px] text-on-surface-variant border border-outline-variant/20">
                      #{tag}
                    </span>
                  ))}
                </div>
                <a href={article.url} target="_blank" rel="noreferrer" 
                   className="inline-flex items-center gap-2 text-primary font-bold text-sm hover:text-tertiary transition-colors group/link">
                  Read Full Source <span className="material-symbols-outlined text-[18px] transform group-hover/link:translate-x-1 transition-transform">arrow_forward</span>
                </a>
              </div>

            </article>
          ))}
        </div>
      ) : (
        <div className="text-center py-24 text-on-surface-variant">
          <span className="material-symbols-outlined text-5xl text-outline-variant mb-4 opacity-50">article</span>
          <p className="font-medium text-lg">No intelligence briefing available.</p>
          <a href="/mission-control" className="mt-6 inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-on-primary font-bold shadow-md hover:bg-primary/90 transition-colors">
            <span className="material-symbols-outlined text-[20px]">bolt</span> Go to Mission Control to Synthesize
          </a>
        </div>
      )}

    </div>
  );
}
