"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../lib/config';
import { useUser } from '../context/UserContext';

export default function IntelligenceReader() {
  const { user, getToken } = useUser();
  const router = useRouter();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);

  const [activeTask, setActiveTask] = useState(null);

  const fetchLatest = async () => {
    try {
      const token = await getToken();
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const resLatest = await fetch(`${API_BASE_URL}/newsletter/latest`, { headers });
      if (resLatest.ok) {
        const json = await resLatest.json();
        setData(json);
      }
    } catch (e) {
      console.error("Failed to fetch data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) fetchLatest();
    
    const taskId = localStorage.getItem('active_task_id');
    if (taskId) {
      setActiveTask(taskId);
    }
  }, [user?.id, getToken]);

  useEffect(() => {
    if (!activeTask) return;
    
    let isSubscribed = true;
    const pollTask = async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/newsletter/status/${activeTask}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok && isSubscribed) {
          const statusData = await res.json();
          if (statusData.status === 'completed') {
            localStorage.removeItem('active_task_id');
            setActiveTask(null);
            fetchLatest(); // Refresh data
          } else if (statusData.status === 'failed') {
            localStorage.removeItem('active_task_id');
            setActiveTask(null);
          }
        }
      } catch (e) {
        console.error("Polling error:", e);
      }
    };
    
    const intervalId = setInterval(pollTask, 3000);
    return () => {
      isSubscribed = false;
      clearInterval(intervalId);
    };
  }, [activeTask, getToken]);

  const handleRefresh = async () => {
    try {
      const token = await getToken();
      const genRes = await fetch(`${API_BASE_URL}/newsletter/generate-async`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ user_id: user.id })
      });
      if (genRes.ok) {
        const { task_id } = await genRes.json();
        localStorage.setItem('active_task_id', task_id);
        setActiveTask(task_id);
      }
    } catch (err) {
      console.error("Failed to refresh feed:", err);
    }
  };

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") setSelectedArticle(null);
    };

    if (selectedArticle) {
      document.body.style.overflow = 'hidden';
      document.addEventListener("keydown", handleEsc);
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { 
      document.body.style.overflow = 'unset'; 
      document.removeEventListener("keydown", handleEsc);
    }
  }, [selectedArticle]);

  if (loading || activeTask) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-outline-variant/30 border-t-primary rounded-full animate-spin"></div>
          <p className="font-headline text-on-surface-variant tracking-wide">
            {activeTask ? "Synthesizing your radar... this may take 5-10 minutes depending on ecosystem volume." : "Loading Intelligence Briefing..."}
          </p>
        </div>
      </div>
    );
  }

  const articles = data?.articles || [];
  const featuredArticle = articles.length > 0 ? articles[0] : null;
  const gridArticles = articles.length > 1 ? articles.slice(1) : [];

  return (
    <>
      <div className="w-full max-w-[1200px] mx-auto px-5 md:px-8 flex flex-col gap-16 relative pb-24">
        
        <header className="flex flex-col items-center text-center border-b border-outline-variant/30 pb-10 pt-4 relative">
          <div className="absolute top-0 right-0">
            <button 
              onClick={handleRefresh}
              className="text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center p-2 rounded-full hover:bg-surface-variant/30 group"
              title="Refresh Feed"
            >
              <span className="material-symbols-outlined text-[20px] group-hover:rotate-180 transition-transform duration-500">refresh</span>
            </button>
          </div>
          <div className="px-4 py-1.5 bg-surface-variant/40 rounded-lg text-[11px] font-bold text-primary uppercase tracking-widest mb-6">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
          <h1 className="font-headline text-5xl md:text-7xl font-bold text-on-surface tracking-tight leading-none mb-6">
            {data?.briefing?.title || "Intelligence Briefing"}
          </h1>
          <p className="text-on-surface-variant text-xl font-medium max-w-2xl">
            Curated signals and strategic analysis from the AI ecosystem, tailored to your intelligence profile.
          </p>
        </header>

        {articles.length === 0 ? (
          <div className="text-center py-24 text-on-surface-variant">
            <span className="material-symbols-outlined text-5xl text-outline-variant mb-4 opacity-50">radar</span>
            <p className="font-medium text-lg">Your radar is tuning. Your first briefing will be delivered at 8:00 AM.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-16">
            {featuredArticle && (
              <article 
                onClick={() => setSelectedArticle(featuredArticle)}
                className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 cursor-pointer group items-center"
              >
                <div className="relative aspect-[16/10] overflow-hidden rounded-2xl md:rounded-[2rem] w-full bg-surface-variant/30">
                  {featuredArticle.image_url ? (
                    <img 
                      src={featuredArticle.image_url} 
                      alt={featuredArticle.title} 
                      className="w-full h-full object-cover transition-transform duration-[800ms] ease-[cubic-bezier(0.25,1,0.5,1)] group-hover:scale-105" 
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center opacity-30 text-2xl font-headline">No Image</div>
                  )}
                  <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none flex items-center justify-center">
                    <span className="material-symbols-outlined text-white text-6xl opacity-0 group-hover:opacity-100 transform scale-50 group-hover:scale-100 transition-all duration-500 delay-100">add</span>
                  </div>
                </div>

                <div className="flex flex-col justify-center">
                  <div className="flex items-center gap-3 mb-5">
                    <span className="px-3 py-1 bg-primary/10 text-primary rounded-full font-bold uppercase tracking-wider text-[11px]">
                      Featured Signal
                    </span>
                    <span className="text-[12px] font-bold text-on-surface-variant uppercase tracking-widest">{featuredArticle.source}</span>
                  </div>
                  
                  <h2 className="font-headline text-4xl md:text-5xl font-bold leading-[1.1] text-on-surface tracking-tight mb-6 group-hover:text-primary transition-colors duration-300">
                    {featuredArticle.title}
                  </h2>
                  <p className="font-body text-on-surface-variant text-lg leading-relaxed mb-8 line-clamp-3">
                    {featuredArticle.summary}
                  </p>
                  
                  <div className="flex flex-wrap items-center gap-2">
                    {featuredArticle.tags?.map(tag => (
                      <span key={tag} className="text-xs font-semibold text-outline px-2.5 py-1 bg-surface-container rounded-md border border-outline-variant/30">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              </article>
            )}

            {gridArticles.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
                {gridArticles.map((article, idx) => (
                  <article 
                    key={idx} 
                    onClick={() => setSelectedArticle(article)}
                    className="flex flex-col cursor-pointer group"
                  >
                    <div className="relative aspect-[16/10] overflow-hidden rounded-2xl mb-5 bg-surface-variant/30">
                      {article.image_url ? (
                        <img 
                          src={article.image_url} 
                          alt={article.title} 
                          className="w-full h-full object-cover transition-transform duration-[800ms] ease-[cubic-bezier(0.25,1,0.5,1)] group-hover:scale-105" 
                        />
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center opacity-30 font-headline">No Image</div>
                      )}
                      <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none flex items-center justify-center">
                         <span className="material-symbols-outlined text-white text-5xl opacity-0 group-hover:opacity-100 transform scale-50 group-hover:scale-100 transition-all duration-500 delay-75">add</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">{article.source}</span>
                      <span className="w-1 h-1 rounded-full bg-outline-variant"></span>
                      <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">{article.trend_score.toFixed(1)} TREND</span>
                    </div>
                    <h3 className="font-headline text-2xl font-bold leading-tight text-on-surface mb-3 group-hover:text-primary transition-colors duration-300 line-clamp-3">
                      {article.title}
                    </h3>
                    <p className="font-body text-on-surface-variant text-[15px] leading-relaxed mb-4 line-clamp-2">
                      {article.summary}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {selectedArticle && (
        <div className="fixed inset-0 z-50 flex justify-center items-center bg-black/60 backdrop-blur-sm p-4 md:p-6 transition-opacity duration-300">
          <div className="w-full max-w-4xl bg-surface max-h-[90vh] overflow-y-auto shadow-2xl rounded-3xl md:rounded-[2.5rem] border border-outline-variant/20 flex flex-col relative transform transition-all duration-500 opacity-100 scale-100">
            <div className="p-6 md:p-12 flex-1 flex flex-col">
              
              <div className="flex justify-between items-start mb-10 gap-6">
                <h2 className="font-headline text-3xl md:text-5xl font-bold leading-[1.1] tracking-tight">{selectedArticle.title}</h2>
                <button 
                  onClick={() => setSelectedArticle(null)} 
                  className="w-12 h-12 flex items-center justify-center bg-surface-container hover:bg-surface-variant hover:text-primary rounded-full shrink-0 transition-colors shadow-sm"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
              
              {selectedArticle.image_url && (
                <div className="w-full aspect-[16/9] rounded-2xl overflow-hidden mb-10 shadow-sm bg-surface-variant/30">
                  <img src={selectedArticle.image_url} className="w-full h-full object-cover" alt="Article Hero" />
                </div>
              )}

              <h3 className="text-xl md:text-2xl font-bold italic mb-4 font-headline text-on-surface">At a Glance</h3>
              <p className="text-on-surface-variant text-[16px] md:text-lg leading-relaxed mb-10">
                {selectedArticle.summary}
              </p>

              {selectedArticle.details && selectedArticle.details.length > 0 && (
                <>
                  <h3 className="text-xl md:text-2xl font-bold italic mb-4 font-headline text-on-surface">Details</h3>
                  <ul className="list-none mb-10 space-y-4">
                    {selectedArticle.details.map((detail, idx) => (
                      <li key={idx} className="flex items-start gap-4 text-on-surface-variant text-[16px] md:text-[17px] leading-relaxed">
                        <span className="material-symbols-outlined text-primary text-[20px] mt-0.5 shrink-0">emergency</span>
                        {detail}
                      </li>
                    ))}
                  </ul>
                </>
              )}

              {selectedArticle.why_it_matters && (
                <>
                  <h3 className="text-xl md:text-2xl font-bold italic mb-4 font-headline text-on-surface">Why It Matters</h3>
                  <div className="bg-primary/5 border border-primary/20 p-6 md:p-8 rounded-3xl mb-10">
                    <p className="text-on-surface font-medium text-[16px] md:text-lg leading-relaxed">
                      {selectedArticle.why_it_matters}
                    </p>
                  </div>
                </>
              )}

              <div className="mt-auto pt-8 border-t border-outline-variant/30 flex flex-col gap-3">
                <div className="text-[15px] font-bold text-on-surface-variant flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">calendar_today</span>
                  When : {new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}
                </div>
                <a 
                  href={selectedArticle.url} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="inline-flex items-center gap-2 text-[15px] font-bold text-on-surface underline decoration-outline-variant underline-offset-4 hover:text-primary transition-colors w-fit"
                >
                  <span className="material-symbols-outlined text-[18px]">open_in_new</span>
                  Source
                </a>
              </div>

            </div>
          </div>
        </div>
      )}

    </>
  );
}
