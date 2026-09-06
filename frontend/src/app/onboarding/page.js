"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '../../context/UserContext';
import { API_BASE_URL } from '../../lib/config';

const TOPICS = [
  'AI Agents & Agentic Workflows',
  'Large Language Models (LLMs)',
  'Foundation Model Releases',
  'LLM Infrastructure & Serving',
  'Open Source AI',
  'RAG & Vector Databases',
  'AI Alignment & Safety',
  'LLMOps & MLOps',
  'Multimodal AI',
  'AI Regulation & Policy',
  'AI Hardware & Chips',
  'AI Coding Assistants',
  'Prompt Engineering & Evals',
  'AI Startups & Funding',
  'AI Reasoning & Planning'
];

export default function Onboarding() {
  const { user, getToken } = useUser();
  const router = useRouter();
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!user?.id) return;

    let cancelled = false;
    const guardAlreadyOnboarded = async () => {
      if (localStorage.getItem('active_task_id')) {
        router.replace('/');
        return;
      }
      try {
        const token = await getToken();
        const res = await fetch(`${API_BASE_URL}/newsletter/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const history = await res.json();
          if (!cancelled && Array.isArray(history) && history.length > 0) {
            router.replace('/');
            return;
          }
        }
      } catch (e) {
        console.error('Onboarding guard check failed:', e);
      }
      if (!cancelled) setChecking(false);
    };

    guardAlreadyOnboarded();
    return () => { cancelled = true; };
  }, [user?.id, getToken, router]);

  const toggleTopic = (topic) => {
    if (selectedTopics.includes(topic)) {
      setSelectedTopics(selectedTopics.filter(t => t !== topic));
    } else {
      if (selectedTopics.length < 10) {
        setSelectedTopics([...selectedTopics, topic]);
      }
    }
  };

  const handleComplete = async () => {
    if (!user) return;
    setIsSaving(true);
    try {
      const token = await getToken();
      await fetch(`${API_BASE_URL}/users/${user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ preferred_topics: selectedTopics })
      });
      
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
      }

      router.push('/');
    } catch (err) {
      console.error("Failed to initialize radar:", err);
      setIsSaving(false);
    }
  };

  if (checking) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="w-10 h-10 border-4 border-outline-variant/30 border-t-primary rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] max-w-2xl mx-auto py-12 px-6">
      <div className="w-full bg-surface-container shadow-2xl border border-outline-variant/30 p-10 md:p-14">
        
        <div className="mb-10 text-center">
          <span className="material-symbols-outlined text-[48px] text-primary mb-4">radar</span>
          <h1 className="font-headline text-4xl font-bold text-on-surface mb-3 tracking-tight">Tune Your Radar</h1>
          <p className="text-on-surface-variant font-body text-lg">
            Select up to 10 topics. InsightGraph will actively monitor the ecosystem for signals matching these parameters.
            <br/><span className="text-sm opacity-80 mt-1 inline-block">You can add more topics anytime in Preferences.</span>
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-3 mb-12">
          {TOPICS.map(topic => {
            const isSelected = selectedTopics.includes(topic);
            return (
              <button
                key={topic}
                onClick={() => toggleTopic(topic)}
                className={`px-4 py-2 text-sm font-bold uppercase tracking-wider transition-colors border
                  ${isSelected 
                    ? 'bg-primary text-on-primary border-primary shadow-[2px_2px_0px_0px_rgba(var(--color-primary),0.3)]' 
                    : 'bg-surface text-on-surface-variant border-outline-variant/60 hover:border-primary/50 hover:text-on-surface'
                  }
                `}
              >
                {topic}
              </button>
            );
          })}
        </div>

        <div className="flex flex-col items-center gap-4 border-t border-outline-variant/30 pt-8">
          <button
            onClick={handleComplete}
            disabled={isSaving || selectedTopics.length === 0}
            className={`w-full max-w-sm py-4 font-bold tracking-wide uppercase transition-colors
              ${selectedTopics.length > 0 && !isSaving
                ? 'bg-primary hover:bg-primary/90 text-on-primary shadow-[4px_4px_0px_0px_rgba(var(--color-outline-variant),0.3)]' 
                : 'bg-surface-variant text-on-surface-variant cursor-not-allowed border border-outline-variant/50'
              }
            `}
          >
            {isSaving ? "Calibrating..." : "Initialize Reader"}
          </button>
          
          <button 
            onClick={() => router.push('/')}
            className="text-xs font-bold text-on-surface-variant hover:text-primary uppercase tracking-widest mt-2"
          >
            Skip for now
          </button>
        </div>

      </div>
    </div>
  );
}
