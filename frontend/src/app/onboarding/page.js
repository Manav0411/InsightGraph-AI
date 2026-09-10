"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '../../context/UserContext';
import { API_BASE_URL } from '../../lib/config';
import { PageShell, Card, Chip, Button } from '../../components/ui';

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

const MAX_TOPICS = 10;

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
    } else if (selectedTopics.length < MAX_TOPICS) {
      setSelectedTopics([...selectedTopics, topic]);
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
      <PageShell width="narrow">
        <div className="flex justify-center items-center min-h-[55vh]">
          <div className="w-9 h-9 border-2 border-outline-variant/30 border-t-primary rounded-full animate-spin" />
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell width="narrow">
      <Card className="p-8 md:p-12 flex flex-col gap-8">
        <div className="flex flex-col gap-3">
          <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">first run</span>
          <h1 className="font-display text-4xl md:text-5xl leading-[1.05] text-on-surface">
            Tune your radar
          </h1>
          <p className="font-reader text-on-surface-variant text-lg leading-relaxed">
            Pick up to {MAX_TOPICS} topics. The ranker boosts anything matching them, so your beats
            float to the top of each run. You can change these anytime in Preferences.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-2">
            {TOPICS.map(topic => {
              const isSelected = selectedTopics.includes(topic);
              const atLimit = !isSelected && selectedTopics.length >= MAX_TOPICS;
              return (
                <Chip
                  key={topic}
                  as="button"
                  type="button"
                  selected={isSelected}
                  onClick={() => toggleTopic(topic)}
                  disabled={atLimit}
                  className={atLimit ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}
                >
                  {topic}
                </Chip>
              );
            })}
          </div>
          <span className="font-mono text-[11px] text-on-surface-variant">
            {selectedTopics.length} / {MAX_TOPICS} selected
          </span>
        </div>

        <div className="flex flex-col items-stretch gap-3 border-t border-outline-variant/30 pt-6">
          <Button
            size="lg"
            onClick={handleComplete}
            disabled={isSaving || selectedTopics.length === 0}
          >
            {isSaving ? "Scheduling your first run…" : "Start my first briefing"}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
            Skip for now
          </Button>
        </div>
      </Card>
    </PageShell>
  );
}
