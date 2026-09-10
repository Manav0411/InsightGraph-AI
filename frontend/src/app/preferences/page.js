"use client";

import { useState, useEffect, useRef } from 'react';
import { useUser } from '../../context/UserContext';
import { PageShell, PageHeader, Card, Chip, Button, TextInput } from '../../components/ui';

const SUGGESTED_TOPICS = [
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

function SectionCard({ label, description, children, action }) {
  return (
    <Card className="p-6 md:p-8 flex flex-col gap-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">{label}</span>
          {description && <p className="font-reader text-sm text-on-surface-variant leading-relaxed">{description}</p>}
        </div>
        {action}
      </div>
      {children}
    </Card>
  );
}

export default function Preferences() {
  const { preferences, updatePreferences, loading: contextLoading } = useUser();
  const [topics, setTopics] = useState([]);
  const [exclusions, setExclusions] = useState([]);
  const [sources, setSources] = useState([]);
  const [emailDelivery, setEmailDelivery] = useState(true);
  const [newTopic, setNewTopic] = useState('');
  const [newExclusion, setNewExclusion] = useState('');
  const [newSource, setNewSource] = useState('');
  const [isAddingTopic, setIsAddingTopic] = useState(false);
  const [isAddingSource, setIsAddingSource] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [saving, setSaving] = useState(false);
  const suggestionsRef = useRef(null);

  useEffect(() => {
    if (preferences) {
      setTopics(preferences.preferred_topics || []);
      setExclusions(preferences.excluded_topics || []);
      setSources(preferences.preferred_sources || []);
      if (preferences.email_delivery_enabled !== undefined) {
        setEmailDelivery(preferences.email_delivery_enabled);
      }
    }
  }, [preferences]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const savePreferences = async () => {
    setSaving(true);
    try {
      await updatePreferences({
        preferred_topics: topics,
        excluded_topics: exclusions,
        preferred_sources: sources,
        email_delivery_enabled: emailDelivery
      });
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const removeTopic = (index) => setTopics(topics.filter((_, i) => i !== index));
  const removeExclusion = (index) => setExclusions(exclusions.filter((_, i) => i !== index));
  const removeSource = (index) => setSources(sources.filter((_, i) => i !== index));

  const addTopic = (e) => {
    if (e.key === 'Enter' && newTopic.trim()) {
      if (!topics.includes(newTopic.trim())) setTopics([...topics, newTopic.trim()]);
      setNewTopic('');
      setIsAddingTopic(false);
    }
  };

  const addExclusion = (e) => {
    if (e.key === 'Enter' && newExclusion.trim()) {
      if (!exclusions.includes(newExclusion.trim())) setExclusions([...exclusions, newExclusion.trim()]);
      setNewExclusion('');
    }
  };

  const addSource = (e) => {
    if (e.key === 'Enter' && newSource.trim()) {
      if (!sources.includes(newSource.trim())) setSources([...sources, newSource.trim()]);
      setNewSource('');
      setIsAddingSource(false);
    }
  };

  if (contextLoading) {
    return (
      <PageShell>
        <p className="font-mono text-[13px] text-on-surface-variant py-16 text-center">Loading preferences…</p>
      </PageShell>
    );
  }

  return (
    <PageShell className="flex flex-col gap-8">
      <PageHeader
        title="Preferences"
        subtitle="What the pipeline boosts, what it drops, and how it reaches you. Changes take effect on the next night's run."
      />

      <SectionCard
        label="Topics"
        description="The ranker adds a fixed boost to anything matching these."
        action={
          isAddingTopic ? (
            <input
              autoFocus
              type="text"
              value={newTopic}
              onChange={e => setNewTopic(e.target.value)}
              onKeyDown={addTopic}
              onBlur={() => setIsAddingTopic(false)}
              placeholder="Type and press Enter…"
              className="font-mono text-xs bg-surface border border-primary rounded-lg px-3 py-2 focus:outline-none text-on-surface"
            />
          ) : (
            <Button variant="ghost" size="sm" onClick={() => setIsAddingTopic(true)}>
              <span className="material-symbols-outlined text-[16px]">add</span> Add
            </Button>
          )
        }
      >
        <div className="flex flex-wrap gap-2">
          {topics.map((topic, i) => (
            <Chip key={i} selected onRemove={() => removeTopic(i)}>{topic}</Chip>
          ))}
          <div className="relative" ref={suggestionsRef}>
            <Chip
              as="button"
              type="button"
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="cursor-pointer border-dashed border-primary/50 text-primary"
            >
              <span className="material-symbols-outlined text-[14px]">explore</span> Suggestions
            </Chip>
            {showSuggestions && (
              <Card className="absolute top-full left-0 mt-2 w-64 z-10 py-2 max-h-64 overflow-y-auto">
                {SUGGESTED_TOPICS.map((topic, i) => {
                  const isAdded = topics.includes(topic);
                  return (
                    <button
                      key={i}
                      onClick={() => {
                        if (!isAdded) setTopics([...topics, topic]);
                        setShowSuggestions(false);
                      }}
                      disabled={isAdded}
                      className={`w-full text-left px-4 py-2 font-reader text-sm flex items-center justify-between transition-colors ${
                        isAdded ? 'text-on-surface-variant/50 cursor-not-allowed' : 'text-on-surface hover:bg-surface-variant/50'
                      }`}
                    >
                      {topic}
                      {isAdded && <span className="material-symbols-outlined text-[16px]">check</span>}
                    </button>
                  );
                })}
              </Card>
            )}
          </div>
        </div>
      </SectionCard>

      <SectionCard
        label="Exclusions"
        description="Matching signals are dropped in the ranker, before the analyzer spends a token on them."
      >
        <TextInput
          icon="block"
          placeholder="Add a term and press Enter…"
          value={newExclusion}
          onChange={e => setNewExclusion(e.target.value)}
          onKeyDown={addExclusion}
          className="max-w-sm"
        />
        {exclusions.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {exclusions.map((exclusion, i) => (
              <Chip key={i} muted onRemove={() => removeExclusion(i)}>{exclusion}</Chip>
            ))}
          </div>
        )}
      </SectionCard>

      <SectionCard
        label="Trusted sources"
        description="Weighted higher when they appear in a run."
        action={
          isAddingSource ? (
            <input
              autoFocus
              type="text"
              value={newSource}
              onChange={e => setNewSource(e.target.value)}
              onKeyDown={addSource}
              onBlur={() => setIsAddingSource(false)}
              placeholder="e.g. arxiv — press Enter"
              className="font-mono text-xs bg-surface border border-primary rounded-lg px-3 py-2 focus:outline-none text-on-surface"
            />
          ) : (
            <Button variant="ghost" size="sm" onClick={() => setIsAddingSource(true)}>
              <span className="material-symbols-outlined text-[16px]">add</span> Add
            </Button>
          )
        }
      >
        {sources.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {sources.map((source, i) => (
              <Chip key={i} onRemove={() => removeSource(i)}>{source}</Chip>
            ))}
          </div>
        ) : (
          <p className="font-reader text-sm text-on-surface-variant">No trusted sources set — all feeds weighted equally.</p>
        )}
      </SectionCard>

      <SectionCard label="Delivery">
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-col gap-1">
            <h4 className="font-reader font-semibold text-on-surface">Daily email briefing</h4>
            <p className="font-reader text-sm text-on-surface-variant leading-relaxed max-w-md">
              Send the briefing to your registered address every morning at 8:00 AM.
            </p>
          </div>
          <label className="relative inline-flex items-center shrink-0 mt-1 cursor-pointer">
            <input
              type="checkbox"
              checked={emailDelivery}
              onChange={(e) => setEmailDelivery(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-surface-variant rounded-full peer peer-checked:bg-primary peer-focus-visible:ring-2 peer-focus-visible:ring-primary peer-focus-visible:ring-offset-2 peer-focus-visible:ring-offset-surface after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full" />
          </label>
        </div>
      </SectionCard>

      <div className="flex justify-end gap-3 pt-2">
        <Button variant="ghost" onClick={() => {
          setTopics(preferences?.preferred_topics || []);
          setExclusions(preferences?.excluded_topics || []);
          setSources(preferences?.preferred_sources || []);
          setEmailDelivery(preferences?.email_delivery_enabled ?? true);
        }}>
          Discard changes
        </Button>
        <Button onClick={savePreferences} disabled={saving}>
          {saving ? 'Saving…' : 'Save preferences'}
        </Button>
      </div>
    </PageShell>
  );
}
