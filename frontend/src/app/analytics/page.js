"use client";

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../lib/config';
import { useUser } from '../../context/UserContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

export default function Analytics() {
  const { user, getToken } = useUser();
  const [trendsData, setTrendsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/analytics/trends`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const json = await res.json();
          
          // Convert ISO UTC strings to localized short strings for chart axes
          const formatChartDate = (isoString) => {
            const d = new Date(isoString);
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
          };
          
          if (json.latency_trends) {
            json.latency_trends.forEach(item => item.date = formatChartDate(item.date));
          }
          if (json.token_trends) {
            json.token_trends.forEach(item => item.date = formatChartDate(item.date));
          }
          
          setTrendsData(json);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchAnalytics();
  }, [user?.id, getToken]);

  if (loading) return <div className="p-12 text-center text-on-surface-variant text-lg">Loading Platform Intelligence...</div>;
  
  if (!trendsData || trendsData.latency_trends?.length === 0) {
    return (
      <div className="p-16 flex flex-col items-center justify-center text-center">
        <span className="material-symbols-outlined text-6xl text-outline mb-4">monitoring</span>
        <h2 className="text-2xl font-headline font-bold text-on-surface mb-2">No historical intelligence found.</h2>
        <p className="text-on-surface-variant max-w-md">Run the orchestrator to generate briefings and populate your longitudinal ecosystem analytics.</p>
      </div>
    );
  }

  const { token_trends, latency_trends, fastest_growing_topics, source_distribution } = trendsData;

  const topTopic = fastest_growing_topics?.[0]?.topic || "AI Agents";
  const topSource = source_distribution?.[0]?.source || "Tavily";
  const avgSqi = (latency_trends.reduce((sum, item) => sum + (item.sqi || 0), 0) / latency_trends.length).toFixed(1);

  return (
    <div className="flex flex-col gap-16 pb-20">
      <header className="max-w-4xl">
        <h1 className="font-headline text-5xl md:text-6xl font-bold text-on-surface mb-4 tracking-tight leading-tight">Ecosystem Intelligence</h1>
        <p className="text-on-surface-variant text-xl leading-relaxed">Longitudinal platform memory and signal evolution across historical briefings.</p>
      </header>

      {/* Section A: Platform Intelligence Trends */}
      <section className="flex flex-col gap-8">
        <div className="flex items-center gap-3 border-b border-outline-variant/30 pb-4">
          <span className="material-symbols-outlined text-primary text-3xl">insights</span>
          <h2 className="font-headline text-3xl font-bold text-on-surface">Platform Intelligence Trends</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-surface-container-low rounded-[2rem] p-8 border border-outline-variant/50">
            <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-2">Fastest Growing Topic</h3>
            <div className="text-4xl font-headline font-bold text-on-surface mb-2">{topTopic}</div>
            <div className="text-sm font-medium text-primary flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">trending_up</span> High Signal Velocity
            </div>
          </div>
          <div className="bg-surface-container-low rounded-[2rem] p-8 border border-outline-variant/50">
            <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-2">Most Reliable Source</h3>
            <div className="text-4xl font-headline font-bold text-on-surface mb-2">{topSource}</div>
            <div className="text-sm font-medium text-primary flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">verified</span> Consistent quality
            </div>
          </div>
          <div className="bg-surface-container-low rounded-[2rem] p-8 border border-outline-variant/50">
            <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-2">Avg. Signal Quality</h3>
            <div className="text-4xl font-headline font-bold text-on-surface mb-2">{avgSqi}/100</div>
            <div className="text-sm font-medium text-primary flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">check_circle</span> Grounding verified
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-4">
          <div className="bg-surface rounded-[2.5rem] p-8 border border-outline-variant/30">
            <h3 className="font-headline text-2xl font-bold text-on-surface mb-8">Signal Quality Evolution</h3>
            <div style={{ width: '100%', height: 256 }}>
              <ResponsiveContainer width="99%" height={256}>
                <AreaChart data={latency_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSqi" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="rgb(var(--color-primary))" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="rgb(var(--color-primary))" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--color-outline-variant))" opacity={0.3} />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: 'rgb(var(--color-on-surface-variant))', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: 'rgb(var(--color-on-surface-variant))', fontSize: 12}} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgb(var(--color-surface-container-high))', borderRadius: '12px', border: 'none', color: 'rgb(var(--color-on-surface))', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                    itemStyle={{ color: 'rgb(var(--color-primary))', fontWeight: 'bold' }}
                  />
                  <Area type="monotone" dataKey="sqi" name="Signal Quality" stroke="rgb(var(--color-primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorSqi)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-surface rounded-[2.5rem] p-8 border border-outline-variant/30 flex flex-col">
            <h3 className="font-headline text-2xl font-bold text-on-surface mb-6">Topic Evolution & Sources</h3>
            <div className="flex-1 flex flex-col justify-center gap-6">
              <div>
                <h4 className="text-sm font-semibold text-on-surface-variant mb-3 uppercase tracking-wider">Top Topics</h4>
                <div className="flex flex-wrap gap-2">
                  {fastest_growing_topics?.map(t => (
                    <span key={t.topic} className="px-4 py-2 rounded-xl bg-secondary-container text-on-secondary-container font-medium text-sm flex items-center gap-2">
                      {t.topic} <span className="opacity-60 text-xs">{t.count}</span>
                    </span>
                  ))}
                </div>
              </div>
              <hr className="border-outline-variant/30" />
              <div>
                <h4 className="text-sm font-semibold text-on-surface-variant mb-3 uppercase tracking-wider">Top Sources</h4>
                <div className="flex flex-wrap gap-2">
                  {source_distribution?.map(s => (
                    <span key={s.source} className="px-4 py-2 rounded-xl bg-tertiary-container text-on-tertiary-container font-medium text-sm flex items-center gap-2">
                      {s.source} <span className="opacity-60 text-xs">{s.count}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section C: Operational Telemetry */}
      <section className="flex flex-col gap-8">
        <div className="flex items-center gap-3 border-b border-outline-variant/30 pb-4">
          <span className="material-symbols-outlined text-on-surface-variant text-2xl">memory</span>
          <h2 className="font-headline text-2xl font-bold text-on-surface-variant">Operational Telemetry</h2>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-surface-container-lowest rounded-3xl p-6 border border-outline-variant/20">
            <h3 className="font-headline text-lg font-bold text-on-surface-variant mb-6">Token Usage Trends</h3>
            <div style={{ width: '100%', height: 192 }}>
              <ResponsiveContainer width="99%" height={192}>
                <AreaChart data={token_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                   <defs>
                    <linearGradient id="colorPrompt" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="rgb(var(--color-secondary))" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="rgb(var(--color-secondary))" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--color-outline-variant))" opacity={0.2} />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: 'rgb(var(--color-on-surface-variant))', fontSize: 10}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: 'rgb(var(--color-on-surface-variant))', fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgb(var(--color-surface-container-high))', borderRadius: '8px', border: 'none', color: 'rgb(var(--color-on-surface))' }}/>
                  <Area type="monotone" dataKey="prompt" stackId="1" name="Prompt Tokens" stroke="rgb(var(--color-secondary))" fill="url(#colorPrompt)" />
                  <Area type="monotone" dataKey="completion" stackId="1" name="Completion Tokens" stroke="rgb(var(--color-tertiary))" fill="rgb(var(--color-tertiary-container))" opacity={0.8} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-surface-container-lowest rounded-3xl p-6 border border-outline-variant/20">
            <h3 className="font-headline text-lg font-bold text-on-surface-variant mb-6">Execution Latency (Seconds)</h3>
            <div style={{ width: '100%', height: 192 }}>
              <ResponsiveContainer width="99%" height={192}>
                <LineChart data={latency_trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgb(var(--color-outline-variant))" opacity={0.2} />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: 'rgb(var(--color-on-surface-variant))', fontSize: 10}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: 'rgb(var(--color-on-surface-variant))', fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgb(var(--color-surface-container-high))', borderRadius: '8px', border: 'none', color: 'rgb(var(--color-on-surface))' }}/>
                  <Line type="monotone" dataKey="latency" name="Latency (s)" stroke="rgb(var(--color-error))" strokeWidth={2} dot={{r: 4, fill: 'rgb(var(--color-error))'}} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>
      
    </div>
  );
}
