"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { API_BASE_URL } from '../../lib/config';
import { useUser } from '../../context/UserContext';

export default function HistoryPage() {
  const { user } = useUser();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/newsletter/history?user_id=${user.id}`);
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
    fetchHistory();
  }, [user.id]);

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
        <div className="relative border-l-2 border-outline-variant/30 pl-8 ml-4 flex flex-col gap-12">
          {filteredHistory.map((briefing, index) => {
            const date = new Date(briefing.generated_at);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            return (
              <div key={briefing.id} className="relative">
                {/* Timeline Dot */}
                <div className="absolute -left-[41px] top-6 w-5 h-5 rounded-full bg-surface border-4 border-primary shadow-sm z-10"></div>
                
                {/* Narrative Element */}
                <div className="mb-4 flex items-center gap-4">
                  <span className="text-primary font-bold text-lg tracking-wide">{dateStr}</span>
                  {briefing.top_signal && (
                    <span className="text-on-surface-variant text-md font-medium px-4 py-1 rounded-full bg-surface-container-high border border-outline-variant/30 hidden md:block">
                      {briefing.top_signal.title.length > 50 ? briefing.top_signal.title.substring(0, 50) + "..." : briefing.top_signal.title}
                    </span>
                  )}
                </div>

                <Link href={`/history/${briefing.id}`} className="block group">
                  <div className="bg-surface rounded-3xl p-8 border border-outline-variant/40 shadow-sm transition-all duration-300 hover:shadow-lg hover:-translate-y-1 hover:border-primary/30 flex flex-col md:flex-row gap-8 justify-between">
                    
                    <div className="flex-1 flex flex-col justify-center">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="font-headline text-2xl font-bold text-on-surface group-hover:text-primary transition-colors">{briefing.title}</h3>
                        <span className="px-3 py-1 bg-tertiary-container text-on-tertiary-container rounded-lg text-xs font-bold uppercase tracking-widest">
                          SQI: {briefing.signal_quality_index || 100}/100
                        </span>
                      </div>
                      
                      {briefing.dominant_topics && briefing.dominant_topics.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4">
                          {briefing.dominant_topics.slice(0, 3).map(topic => (
                            <span key={topic} className="px-3 py-1 rounded-full bg-surface-variant text-on-surface-variant text-sm font-medium">
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
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
