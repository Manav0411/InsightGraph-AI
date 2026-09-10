"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '../lib/config';
import { useUser } from '../context/UserContext';
import { PageShell, SignalCard, Card, Button } from './ui';

export default function IntelligenceReader() {
  const { user, getToken } = useUser();
  const router = useRouter();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);

  const isAdmin = user?.primaryEmailAddress?.emailAddress &&
    (process.env.NEXT_PUBLIC_ADMIN_EMAILS || '').split(',').map(e => e.trim().toLowerCase()).includes(user.primaryEmailAddress.emailAddress.toLowerCase());

  const [activeTask, setActiveTask] = useState(null);

  const fetchLatest = async () => {
    try {
      const token = await getToken();
      const headers = { 'Authorization': `Bearer ${token}` };

      const resLatest = await fetch(`${API_BASE_URL}/newsletter/latest`, { headers });
      if (resLatest.ok) {
        const json = await resLatest.json();
        setData(json);
      } else if (resLatest.status === 404) {
        if (!localStorage.getItem('active_task_id')) {
          router.replace('/onboarding');
        }
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

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  if (loading || activeTask) {
    return (
      <PageShell width="wide">
        <div className="flex justify-center items-center min-h-[55vh]">
          <div className="flex flex-col items-center gap-4">
            <div className="w-9 h-9 border-2 border-outline-variant/30 border-t-primary rounded-full animate-spin" />
            <p className="font-mono text-[13px] text-on-surface-variant text-center max-w-sm">
              {activeTask
                ? "Synthesizing your radar — this can take 5–10 minutes depending on ecosystem volume."
                : "Loading your briefing…"}
            </p>
          </div>
        </div>
      </PageShell>
    );
  }

  const articles = data?.articles || [];
  const featuredArticle = articles.length > 0 ? articles[0] : null;
  const gridArticles = articles.length > 1 ? articles.slice(1) : [];

  return (
    <>
      <PageShell width="wide" className="flex flex-col gap-16">

        <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-5 border-b border-outline-variant/30 pb-8">
          <div className="flex flex-col gap-3">
            <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">
              {today}
            </span>
            <h1 className="font-display text-4xl md:text-6xl leading-[1.05] text-on-surface">
              {data?.briefing?.title || "Your briefing"}
            </h1>
            <p className="font-reader text-on-surface-variant text-lg leading-relaxed max-w-2xl">
              Curated signals and grounded analysis from the AI ecosystem, ranked against your topics.
            </p>
          </div>
          {isAdmin && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRefresh}
              title="Run a fresh briefing"
              className="shrink-0"
            >
              <span className="material-symbols-outlined text-[18px]">refresh</span>
              Run now
            </Button>
          )}
        </header>

        {articles.length === 0 ? (
          <Card variant="flat" className="p-12 md:p-16 flex flex-col items-center text-center gap-3">
            <span className="material-symbols-outlined text-4xl text-outline-variant">radar</span>
            <p className="font-reader text-on-surface-variant text-lg max-w-sm">
              Your radar is tuning. Your first briefing will be delivered at 8:00 AM.
            </p>
          </Card>
        ) : (
          <div className="flex flex-col gap-16">
            {featuredArticle && (
              <article
                onClick={() => setSelectedArticle(featuredArticle)}
                className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 items-center cursor-pointer group"
              >
                <div className="relative aspect-[16/10] overflow-hidden rounded-2xl w-full bg-surface-variant/30 order-last md:order-first">
                  {featuredArticle.image_url ? (
                    <img
                      src={featuredArticle.image_url}
                      alt={featuredArticle.title}
                      className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-[1.03]"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center opacity-30 font-display text-2xl">
                      No image
                    </div>
                  )}
                </div>

                <div className="flex flex-col">
                  <div className="flex items-center gap-3 mb-4 font-mono text-[11px] uppercase tracking-[0.09em] text-primary">
                    <span>featured signal</span>
                    <span className="w-1 h-1 rounded-full bg-outline-variant" />
                    <span className="text-on-surface-variant">{featuredArticle.source}</span>
                  </div>
                  <h2 className="font-display text-3xl md:text-5xl leading-[1.08] text-on-surface mb-5 group-hover:text-primary transition-colors">
                    {featuredArticle.title}
                  </h2>
                  <p className="font-reader text-on-surface-variant text-lg leading-relaxed mb-6 line-clamp-3">
                    {featuredArticle.summary}
                  </p>
                  {featuredArticle.tags?.length > 0 && (
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11px] text-on-surface-variant">
                      {featuredArticle.tags.map(tag => (
                        <span key={tag}>#{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              </article>
            )}

            {gridArticles.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {gridArticles.map((article, idx) => (
                  <SignalCard
                    key={idx}
                    onClick={() => setSelectedArticle(article)}
                    kicker={`${article.source} · trend ${article.trend_score.toFixed(1)}`}
                    title={article.title}
                    summary={article.summary}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </PageShell>

      {selectedArticle && (
        <div className="fixed inset-0 z-50 flex justify-center items-start md:items-center bg-black/60 backdrop-blur-sm p-4 md:p-8 overflow-y-auto">
          <Card className="w-full max-w-3xl my-auto flex flex-col">
            <div className="p-6 md:p-10 flex flex-col">

              <div className="flex justify-between items-start gap-6 mb-8">
                <h2 className="font-display text-2xl md:text-4xl leading-[1.1] text-on-surface">
                  {selectedArticle.title}
                </h2>
                <button
                  onClick={() => setSelectedArticle(null)}
                  aria-label="Close"
                  className="w-10 h-10 flex items-center justify-center rounded-full bg-surface-variant/50 hover:bg-surface-variant hover:text-primary shrink-0 transition-colors"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              {selectedArticle.image_url && (
                <div className="w-full aspect-[16/9] rounded-xl overflow-hidden mb-8 bg-surface-variant/30">
                  <img src={selectedArticle.image_url} className="w-full h-full object-cover" alt="" />
                </div>
              )}

              <h3 className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary mb-2">At a glance</h3>
              <p className="font-reader text-on-surface-variant text-base md:text-lg leading-relaxed mb-8">
                {selectedArticle.summary}
              </p>

              {selectedArticle.details && selectedArticle.details.length > 0 && (
                <>
                  <h3 className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary mb-3">Details</h3>
                  <ul className="flex flex-col gap-3 mb-8">
                    {selectedArticle.details.map((detail, idx) => (
                      <li key={idx} className="flex items-start gap-3 font-reader text-on-surface-variant text-[15px] md:text-base leading-relaxed">
                        <span className="material-symbols-outlined text-primary text-[18px] mt-1 shrink-0">chevron_right</span>
                        {detail}
                      </li>
                    ))}
                  </ul>
                </>
              )}

              {selectedArticle.why_it_matters && (
                <>
                  <h3 className="font-mono text-[11px] uppercase tracking-[0.1em] text-primary mb-3">Why it matters</h3>
                  <p className="font-reader text-on-surface text-[15px] md:text-base leading-relaxed border-l-2 border-primary pl-4 mb-8">
                    {selectedArticle.why_it_matters}
                  </p>
                </>
              )}

              <div className="mt-2 pt-6 border-t border-outline-variant/30 flex flex-wrap items-center justify-between gap-4 font-mono text-[12px] text-on-surface-variant">
                <span>
                  {new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}
                </span>
                <Button as="a" href={selectedArticle.url} target="_blank" rel="noreferrer" variant="outline" size="sm">
                  <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                  Source
                </Button>
              </div>

            </div>
          </Card>
        </div>
      )}
    </>
  );
}
