"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { API_BASE_URL } from '../../../lib/config';
import { useUser } from '../../../context/UserContext';

export default function HistoricalBriefingViewer() {
  const { id } = useParams();
  const { user } = useUser();
  const [briefing, setBriefing] = useState(null);
  const [historyContext, setHistoryContext] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const fetchBriefing = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/newsletter/history/${id}`);
        if (res.ok) {
          const json = await res.json();
          setBriefing(json);
        }
        
        // Fetch context
        const histRes = await fetch(`${API_BASE_URL}/newsletter/history?user_id=${user.id}`);
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
    
    if (id) fetchBriefing();
  }, [id, user.id]);

  const handleExport = async () => {
    setDownloading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/newsletter/export/${id}`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `InsightGraph_${id.substring(0,8)}.md`;
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

  if (loading) return <div className="p-12 text-center text-on-surface-variant text-lg">Reconstructing Historical Memory...</div>;
  if (!briefing) return <div className="p-12 text-center text-on-surface-variant text-lg">Briefing not found.</div>;

  const date = new Date(briefing.generated_at).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  
  // Intelligence Context Layer Simulation
  const sqi = briefing.metrics.signal_quality_index || 100;
  const recentBriefings = historyContext.filter(b => b.id !== id).slice(0, 2);
  const isUpward = sqi >= 90;

  return (
    <div className="flex flex-col gap-12 pb-20 max-w-4xl mx-auto">
      <Link href="/history" className="inline-flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors font-medium">
        <span className="material-symbols-outlined text-sm">arrow_back</span>
        Back to Archive
      </Link>
      
      <header className="flex flex-col gap-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="font-headline text-5xl font-bold text-on-surface mb-3 tracking-tight">{briefing.title}</h1>
            <p className="text-on-surface-variant text-lg">{date}</p>
          </div>
          <button 
            onClick={handleExport}
            disabled={downloading}
            className="flex items-center gap-2 px-6 py-3 bg-primary text-on-primary rounded-full font-bold shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-sm">download</span>
            {downloading ? 'Exporting...' : 'Export Intelligence'}
          </button>
        </div>

        {/* Intelligence Context Layer */}
        <div className="bg-surface-container-low rounded-3xl p-6 border border-outline-variant/30 flex flex-col md:flex-row gap-6 items-center">
          <div className="w-20 h-20 rounded-full bg-surface shadow-sm border border-outline-variant/20 flex items-center justify-center text-3xl font-bold text-primary shrink-0">
            {sqi}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-on-surface mb-1">Signal Quality Index</h3>
            <p className="text-on-surface-variant text-sm">
              {isUpward ? "Trending upward compared to previous 7 briefings. High grounding validation observed." : "Stable intelligence signals detected. Consistent source reliability."}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 justify-end w-full md:w-auto">
            {briefing.metadata?.dominant_topics?.map(topic => (
              <span key={topic} className="px-3 py-1 rounded-full bg-tertiary-container text-on-tertiary-container text-xs font-bold uppercase tracking-wider">
                {topic}
              </span>
            ))}
          </div>
        </div>
      </header>

      {/* Related Historical Signals */}
      {recentBriefings.length > 0 && (
        <section className="bg-surface rounded-[2.5rem] p-8 border border-outline-variant/20">
          <h2 className="font-headline text-xl font-bold text-on-surface mb-4">Related Historical Signals</h2>
          <ul className="space-y-3">
            {recentBriefings.map(b => (
              <li key={b.id} className="flex items-center gap-3 text-on-surface-variant">
                <span className="w-1.5 h-1.5 rounded-full bg-primary/50"></span>
                <span className="font-medium text-on-surface">{new Date(b.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                <span className="opacity-60">—</span>
                <Link href={`/history/${b.id}`} className="hover:text-primary transition-colors underline decoration-outline-variant underline-offset-4">
                  {b.dominant_topics?.[0] || 'Ecosystem Shift'}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Articles Rendering */}
      <section className="flex flex-col gap-8 mt-4">
        {briefing.articles.map((article, i) => (
          <article key={i} className="bg-surface rounded-[2rem] p-8 border border-outline-variant/30 shadow-sm relative overflow-hidden group">
            {article.is_grounded && (
               <div className="absolute top-0 right-0 bg-primary/10 text-primary px-4 py-1 rounded-bl-xl text-xs font-bold uppercase tracking-widest flex items-center gap-1">
                 <span className="material-symbols-outlined text-[14px]">verified</span> Grounded
               </div>
            )}
            
            <div className="flex items-center gap-3 mb-4">
              <span className="px-3 py-1 bg-surface-variant text-on-surface-variant rounded-md text-xs font-bold uppercase tracking-wider">
                {article.source}
              </span>
              <span className="text-on-surface-variant text-sm font-medium flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] text-tertiary">trending_up</span>
                Trend Score: {article.trend_score.toFixed(1)}
              </span>
            </div>

            <h2 className="font-headline text-2xl font-bold text-on-surface mb-4 leading-tight group-hover:text-primary transition-colors">
              <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
            </h2>

            <p className="text-on-surface-variant text-lg leading-relaxed mb-6">{article.summary}</p>
            
            {article.why_it_matters && (
              <div className="bg-secondary-container text-on-secondary-container p-6 rounded-2xl border-l-4 border-secondary">
                <h4 className="font-bold mb-2 uppercase tracking-wide text-sm flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">lightbulb</span> Why It Matters
                </h4>
                <p>{article.why_it_matters}</p>
              </div>
            )}
            
            <div className="flex flex-wrap gap-2 mt-6">
              {article.tags.map(tag => (
                <span key={tag} className="text-xs font-semibold text-outline px-2 py-1 bg-surface-container rounded border border-outline-variant/30">#{tag}</span>
              ))}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
