"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { API_BASE_URL } from '../../lib/config';
import { useUser } from '../../context/UserContext';

// --- Frontend Narrative Engine ---
const formatBriefingDate = (dateString) => {
  const safeDateString = dateString.endsWith('Z') ? dateString : dateString + 'Z';
  const date = new Date(safeDateString);
  const today = new Date();
  const isToday = date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
  
  const timeStr = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  if (isToday) {
    return `Today • ${timeStr}`;
  }
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return `${dateStr} • ${timeStr}`;
};

const getSqiClasses = (sqi) => {
  if (sqi >= 85) return 'bg-primary/15 text-primary border-primary/20';
  if (sqi >= 70) return 'bg-[#D4A373]/15 text-[#D4A373] border-[#D4A373]/20';
  return 'bg-surface-variant text-on-surface-variant border-outline-variant/30';
};

const generateNarrative = (briefing, prevBriefing) => {
  const topics = briefing.dominant_topics || [];
  if (topics.length > 0) {
    if (topics.includes('AI Agents')) return "AI Agents dominated today's ecosystem signals.";
    if (topics.includes('Coding Assistants')) return "Coding-agent infrastructure continues accelerating rapidly.";
    if (topics.includes('Open Source')) return "Open-source momentum shaped the ecosystem narrative.";
    return `${topics[0]} signals drove ecosystem shifts during this period.`;
  }
  if (prevBriefing && briefing.signal_quality_index > prevBriefing.signal_quality_index) {
    return "Grounding reliability and signal quality improved compared to previous runs.";
  }
  return "Stable ecosystem intelligence gathered across trusted sources.";
};
// --------------------------------

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

  if (loading) return <div className="p-12 text-center text-on-surface-variant text-lg">Loading Historical Intelligence...</div>;

  return (
    <div className="flex flex-col gap-12 pb-20 max-w-5xl mx-auto">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="font-headline text-5xl font-bold text-on-surface mb-3 tracking-tight">Intelligence Memory</h1>
          <p className="text-on-surface-variant text-xl">Searchable historical archive and longitudinal ecosystem narrative.</p>
        </div>
        
        <div className="relative w-full md:w-80">
          <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant">search</span>
          <input 
            type="text" 
            placeholder="Search topics, signals..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-surface-container-high text-on-surface rounded-full py-3 pl-12 pr-6 border border-outline-variant/30 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all placeholder-on-surface-variant/60"
          />
        </div>
      </header>

      {history.length === 0 ? (
        <div className="bg-surface-container rounded-[2.5rem] p-16 flex flex-col items-center justify-center text-center border border-outline-variant/20">
          <span className="material-symbols-outlined text-7xl text-outline mb-6">history_toggle_off</span>
          <h2 className="text-3xl font-headline font-bold text-on-surface mb-4">No intelligence memory found.</h2>
          <p className="text-on-surface-variant text-lg max-w-md">Your historical briefings will appear here, forming a longitudinal narrative of AI ecosystem shifts.</p>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="p-12 text-center text-on-surface-variant">No briefings matched your search.</div>
      ) : (
        <div className="relative border-l-2 border-transparent pl-8 ml-4 flex flex-col gap-12">
          {/* Add a gradient line overlay behind the transparent border */}
          <div className="absolute left-[-2px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-primary/50 via-outline-variant/30 to-transparent"></div>
          
          {filteredHistory.map((briefing, index) => {
            const dateStr = formatBriefingDate(briefing.generated_at);
            const prevBriefing = index < filteredHistory.length - 1 ? filteredHistory[index + 1] : null;
            const narrative = generateNarrative(briefing, prevBriefing);
            const sqiClass = getSqiClasses(briefing.signal_quality_index || 100);
            
            return (
              <div key={briefing.id} className="relative group/timeline">
                {/* Timeline Dot with Glow */}
                <div className="absolute -left-[41px] top-6 w-5 h-5 rounded-full bg-surface border-4 border-primary shadow-[0_0_15px_rgba(74,124,89,0)] group-hover/timeline:shadow-[0_0_15px_rgba(74,124,89,0.4)] transition-all duration-500 z-10"></div>
                
                {/* Narrative Element */}
                <div className="mb-4 flex items-center gap-4">
                  <span className="text-primary font-bold text-lg tracking-wide">{dateStr}</span>
                </div>

                <Link href={`/history/${briefing.id}`} className="block group">
                  <div className="bg-surface rounded-3xl p-8 border border-outline-variant/40 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1 hover:border-primary/30 flex flex-col gap-6">
                    
                    <div className="flex flex-col md:flex-row gap-8 justify-between">
                      <div className="flex-1 flex flex-col justify-center">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-headline text-2xl font-bold text-on-surface group-hover:text-primary transition-colors">{briefing.title}</h3>
                          <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-widest border ${sqiClass}`}>
                            SQI: {briefing.signal_quality_index || 100}/100
                          </span>
                        </div>
                        
                        <p className="text-on-surface-variant text-sm italic mb-4">{narrative}</p>
                        
                        {/* Top Signal moved here */}
                        {briefing.top_signal && (
                          <div className="mb-4">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-primary mb-1 block">Top Signal</span>
                            <div className="text-on-surface font-medium text-sm border-l-2 border-primary/30 pl-3 py-0.5">
                              {briefing.top_signal.title}
                            </div>
                          </div>
                        )}
                        
                        {briefing.dominant_topics && briefing.dominant_topics.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {briefing.dominant_topics.slice(0, 3).map(topic => (
                              <span key={topic} className="px-3 py-1 rounded-full bg-surface-variant text-on-surface-variant text-xs font-semibold">
                                {topic}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <div className="flex md:flex-col gap-4 md:gap-2 justify-center items-start md:items-end text-sm text-on-surface-variant">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[18px]">article</span>
                          {briefing.total_articles} Signals
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[18px] text-primary">trending_up</span>
                          {briefing.avg_trend_score ? briefing.avg_trend_score.toFixed(1) : 0} Avg Trend
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-[18px]">verified</span>
                          {briefing.grounding_reliability}% Grounded
                        </div>
                      </div>
                    </div>
                    
                    {/* Hover Expansion Layer */}
                    <div className="overflow-hidden max-h-0 opacity-0 group-hover:max-h-40 group-hover:opacity-100 group-hover:mt-2 transition-all duration-500 ease-in-out border-t border-outline-variant/10 pt-0 group-hover:pt-4 flex flex-wrap gap-6 text-sm">
                      <div className="flex flex-col">
                        <span className="text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Personalization Strength</span>
                        <span className="text-primary font-semibold">{(briefing.personalization_strength || 0).toFixed(1)}%</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Execution Time</span>
                        <span className="text-on-surface font-semibold">{briefing.execution_time_seconds ? `${briefing.execution_time_seconds.toFixed(1)}s` : 'N/A'}</span>
                      </div>
                      {briefing.matched_topics && briefing.matched_topics.length > 0 && (
                        <div className="flex flex-col">
                          <span className="text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Personalized Vectors</span>
                          <span className="text-on-surface font-semibold">{briefing.matched_topics.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
