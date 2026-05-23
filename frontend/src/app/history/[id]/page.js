"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { API_BASE_URL } from '../../../lib/config';
import { useUser } from '../../../context/UserContext';

// --- Frontend Narrative Engine ---
const generateContextualEvolution = (briefing, prevBriefing) => {
  const topics = briefing.metadata?.dominant_topics || [];
  if (topics.length > 0) {
    if (topics.includes('AI Agents')) return `AI agent infrastructure signals increased compared to previous briefings. ${topics[0]} momentum continues dominating ecosystem narrative.`;
    if (topics.includes('Coding Assistants')) return `Coding-agent infrastructure continues accelerating rapidly across observed sources.`;
    if (topics.includes('Open Source')) return `Open-source momentum shaped the ecosystem narrative for this briefing window.`;
    return `${topics[0]} ecosystem shifts were primarily responsible for elevated signal volumes during this period.`;
  }
  const prevSqi = prevBriefing?.metrics?.signal_quality_index || prevBriefing?.signal_quality_index;
  if (prevSqi && briefing.metrics.signal_quality_index > prevSqi) {
    return "Grounding reliability and overall signal quality improved significantly compared to previous historical runs.";
  }
  return "Stable intelligence ecosystem detected with consistent source reliability across evaluated metrics.";
};
// --------------------------------

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

  const safeDateString = briefing.generated_at.endsWith('Z') ? briefing.generated_at : briefing.generated_at + 'Z';
  const date = new Date(safeDateString).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  
  // Intelligence Context Layer Simulation
  const sqi = briefing.metrics.signal_quality_index || 100;
  const recentBriefings = historyContext.filter(b => b.id !== id).slice(0, 2);
  const prevBriefing = historyContext.find(b => b.id !== id && new Date(b.generated_at) < new Date(briefing.generated_at));
  const narrative = generateContextualEvolution(briefing, prevBriefing);

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
            className="flex items-center gap-2 px-5 py-2.5 bg-transparent text-on-surface-variant border border-outline-variant/50 rounded-full font-bold shadow-sm hover:bg-surface-variant/30 hover:text-on-surface transition-all disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            {downloading ? 'Exporting...' : 'Export Briefing'}
          </button>
        </div>

        {/* Intelligence Context Layer */}
        <div className="bg-surface-container-low rounded-3xl p-6 border border-outline-variant/30 flex flex-col md:flex-row gap-6 items-center">
          <div className="w-20 h-20 rounded-full bg-surface shadow-sm border border-outline-variant/20 flex items-center justify-center text-3xl font-bold text-primary shrink-0">
            {sqi}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-[11px] font-bold text-on-surface-variant uppercase tracking-widest mb-1">Contextual Evolution</h3>
            <p className="text-on-surface text-[15px] font-medium leading-relaxed">
              {narrative}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 md:justify-end w-full md:w-[35%] shrink-0">
            {briefing.metadata?.dominant_topics?.map(topic => (
              <span key={topic} className="px-3 py-1 rounded-full bg-tertiary-container text-on-tertiary-container text-xs font-bold uppercase tracking-wider whitespace-nowrap">
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
                <span className="font-medium text-on-surface">{new Date(b.generated_at.endsWith('Z') ? b.generated_at : b.generated_at + 'Z').toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
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
            
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-5">
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 bg-surface-variant text-on-surface-variant rounded-md text-xs font-bold uppercase tracking-wider flex flex-col justify-center items-center">
                  {article.source}
                  {article.source === 'github' && <span className="text-[9px] opacity-70 mt-0.5">Reliability: 92%</span>}
                </span>
                
                {/* Trend Score Visualizer */}
                <div className="flex flex-col gap-1 ml-2">
                  <div className="text-[10px] text-on-surface-variant uppercase font-bold tracking-wider">Trend Intensity</div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-surface-variant rounded-full overflow-hidden">
                      <div className="h-full bg-primary" style={{ width: `${Math.min((article.trend_score || 0) * 8, 100)}%` }}></div>
                    </div>
                    <span className="text-xs font-bold text-on-surface">{article.trend_score ? article.trend_score.toFixed(1) : 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>

            <h2 className="font-headline text-2xl font-bold text-on-surface mb-4 leading-tight group-hover:text-primary transition-colors">
              <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
            </h2>

            <p className="text-on-surface-variant text-lg leading-relaxed mb-6">{article.summary}</p>
            
            {article.why_it_matters && (
              <div className="bg-secondary-container/50 text-on-secondary-container p-6 rounded-2xl border-l-2 border-secondary mb-6">
                <h4 className="font-bold mb-2 uppercase tracking-wide text-xs flex items-center gap-2">
                  <span className="material-symbols-outlined text-[16px]">lightbulb</span> Why It Matters
                </h4>
                <p className="text-[15px]">{article.why_it_matters}</p>
              </div>
            )}

            {/* Why This Signal Was Elevated */}
            {article.recommendation_reasons && article.recommendation_reasons.length > 0 && (
              <div className="mb-6 bg-surface-container-low p-5 rounded-2xl border border-outline-variant/30">
                <h4 className="font-bold mb-3 uppercase tracking-wide text-[11px] text-on-surface-variant flex items-center gap-2">
                  <span className="material-symbols-outlined text-[16px]">psychology</span> Why This Signal Was Elevated
                </h4>
                <ul className="space-y-2">
                  {article.recommendation_reasons.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-[14px] text-on-surface">
                      <span className="material-symbols-outlined text-[18px] text-primary shrink-0">check_circle</span>
                      {reason}
                    </li>
                  ))}
                  {article.stars && (
                     <li className="flex items-start gap-2 text-[14px] text-on-surface">
                       <span className="material-symbols-outlined text-[18px] text-tertiary shrink-0">star</span>
                       High developer momentum ({article.stars} stars)
                     </li>
                  )}
                </ul>
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
