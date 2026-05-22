"use client";

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../lib/config';
import { useUser } from '../../context/UserContext';

export default function Preferences() {
  const { preferences, updatePreferences, loading: contextLoading } = useUser();
  const [topics, setTopics] = useState([]);
  const [exclusions, setExclusions] = useState([]);
  const [sources, setSources] = useState([]);
  const [newTopic, setNewTopic] = useState('');
  const [newExclusion, setNewExclusion] = useState('');
  const [newSource, setNewSource] = useState('');
  const [isAddingTopic, setIsAddingTopic] = useState(false);
  const [isAddingSource, setIsAddingSource] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (preferences) {
      setTopics(preferences.preferred_topics || []);
      setExclusions(preferences.excluded_topics || []);
      setSources(preferences.preferred_sources || []);
    }
  }, [preferences]);

  const savePreferences = async () => {
    setSaving(true);
    try {
      await updatePreferences({
        preferred_topics: topics,
        excluded_topics: exclusions,
        preferred_sources: sources
      });
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const removeTopic = (index) => {
    setTopics(topics.filter((_, i) => i !== index));
  };

  const removeExclusion = (index) => {
    setExclusions(exclusions.filter((_, i) => i !== index));
  };
  
  const removeSource = (index) => {
    setSources(sources.filter((_, i) => i !== index));
  };

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

  if (contextLoading) return <div className="p-8">Loading Preferences...</div>;

  return (
    <div className="w-full max-w-6xl space-y-8 mx-auto">
      {/* Page Header */}
      <nav className="flex border-b border-outline-variant/20 mb-8 overflow-x-auto">
        <a className="px-6 py-4 text-sm font-semibold text-on-surface-variant hover:text-primary transition-colors whitespace-nowrap" href="#">Security</a>
        <a className="px-6 py-4 text-sm font-semibold text-on-surface-variant hover:text-primary transition-colors whitespace-nowrap" href="#">Data Sources</a>
        <a className="px-6 py-4 text-sm font-semibold text-on-surface-variant hover:text-primary transition-colors whitespace-nowrap" href="#">Integrations</a>
        <a className="px-6 py-4 text-sm font-bold text-primary border-b-2 border-primary transition-colors whitespace-nowrap relative after:absolute after:bottom-0 after:left-0 after:w-full after:h-0.5 after:bg-primary" href="#">Preferences</a>
      </nav>
      
      <header className="mb-10">
        <h1 className="font-headline text-4xl font-bold text-on-surface mb-2">Personalization Preferences</h1>
        <p className="text-on-surface-variant text-lg leading-relaxed max-w-2xl">Tailor your InsightGraph experience by managing what matters most. Your configurations directly influence the intelligence briefings and analytics surfaced to you.</p>
      </header>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 auto-rows-min">
        
        {/* Core Topics Card (Spans 2 columns) */}
        <div className="lg:col-span-2 bg-gradient-to-br from-surface-container-low to-transparent rounded-2xl p-8 border border-outline-variant/30 shadow-sm flex flex-col h-full">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-headline text-xl font-semibold text-primary flex items-center gap-2">
                <span className="material-symbols-outlined text-tertiary">psychology</span>
                Core Topics
              </h3>
              <p className="text-on-surface-variant text-sm mt-1">Define the thematic pillars of your intelligence feed.</p>
            </div>
            {isAddingTopic ? (
              <input 
                autoFocus
                type="text" 
                value={newTopic}
                onChange={e => setNewTopic(e.target.value)}
                onKeyDown={addTopic}
                onBlur={() => setIsAddingTopic(false)}
                className="text-sm font-semibold text-on-surface bg-surface border border-primary focus:outline-none px-4 py-2 rounded-lg"
                placeholder="Type and press Enter..."
              />
            ) : (
              <button onClick={() => setIsAddingTopic(true)} className="text-sm font-semibold text-primary hover:bg-primary/10 px-4 py-2 rounded-lg transition-colors flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">add</span> Add Topic
              </button>
            )}
          </div>
          
          <div className="flex flex-wrap gap-3 mt-auto">
            {topics.map((topic, i) => (
              <div key={i} className={`rounded-full px-5 py-2.5 flex items-center gap-2 text-sm font-semibold transition-colors cursor-pointer border shadow-sm ${i % 2 === 0 ? 'bg-primary-container text-on-primary-fixed-variant hover:bg-primary-fixed border-primary/10' : i % 3 === 0 ? 'bg-tertiary-container/40 text-on-tertiary-fixed-variant hover:bg-tertiary-container/60 border-tertiary/10' : 'bg-surface-container-high text-on-surface hover:bg-surface-variant border-outline-variant/30'}`}>
                {topic}
                <button onClick={() => removeTopic(i)} className="hover:text-error transition-colors flex items-center"><span className="material-symbols-outlined text-[18px]">close</span></button>
              </div>
            ))}
            {/* Add New Pill Button */}
            <button className="rounded-full px-5 py-2.5 flex items-center gap-2 text-sm font-semibold border border-dashed border-primary/50 text-primary hover:bg-primary/5 transition-colors">
              <span className="material-symbols-outlined text-[18px]">add</span> Explore Suggestions
            </button>
          </div>
        </div>

        {/* Exclusions Card (Spans 1 column) */}
        <div className="lg:col-span-1 bg-gradient-to-br from-surface-container-low to-transparent rounded-2xl p-8 border border-outline-variant/30 shadow-sm flex flex-col h-full">
          <div className="mb-6">
            <h3 className="font-headline text-xl font-semibold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary">block</span>
              Exclusions
            </h3>
            <p className="text-on-surface-variant text-sm mt-1">Mute noise by excluding specific terms or entities.</p>
          </div>
          <div className="relative w-full mb-4">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
            <input 
              className="w-full bg-surface border border-outline-variant/50 rounded-lg py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-outline/70" 
              placeholder="Add an exclusion... (press Enter)" 
              type="text"
              value={newExclusion}
              onChange={e => setNewExclusion(e.target.value)}
              onKeyDown={addExclusion}
            />
          </div>
          <div className="flex flex-wrap gap-2 overflow-y-auto max-h-32 pr-2">
            {exclusions.map((exclusion, i) => (
              <div key={i} className="bg-error-container/50 text-on-error-container rounded-md px-3 py-1.5 flex items-center gap-1.5 text-xs font-semibold border border-error/10">
                {exclusion}
                <button onClick={() => removeExclusion(i)} className="hover:text-error flex items-center"><span className="material-symbols-outlined text-[14px]">close</span></button>
              </div>
            ))}
          </div>
        </div>

        {/* Trusted Sources Card */}
        <div className="lg:col-span-1 bg-gradient-to-br from-surface-container-low to-transparent rounded-2xl p-8 border border-outline-variant/30 shadow-sm">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="font-headline text-xl font-semibold text-primary flex items-center gap-2">
                <span className="material-symbols-outlined text-tertiary">verified</span>
                Trusted Sources
              </h3>
              <p className="text-on-surface-variant text-sm mt-1">Weight these publishers higher in your feed.</p>
            </div>
          </div>
          <div className="space-y-4">
            {sources.map((source, i) => (
              <div key={i} className="flex items-center justify-between group p-2 -mx-2 rounded-lg hover:bg-surface-variant/30 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border ${i % 3 === 0 ? 'bg-primary/10 text-primary border-primary/20' : i % 3 === 1 ? 'bg-tertiary/10 text-tertiary border-tertiary/20' : 'bg-secondary/10 text-secondary border-secondary/20'}`}>
                    {source.substring(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-on-surface">{source}</h4>
                    <p className="text-xs text-on-surface-variant">Trusted Source</p>
                  </div>
                </div>
                <button onClick={() => removeSource(i)} className="text-outline opacity-0 group-hover:opacity-100 hover:text-error transition-all p-1">
                  <span className="material-symbols-outlined text-[20px]">delete</span>
                </button>
              </div>
            ))}
          </div>
          {isAddingSource ? (
            <input 
              autoFocus
              type="text" 
              value={newSource}
              onChange={e => setNewSource(e.target.value)}
              onKeyDown={addSource}
              onBlur={() => setIsAddingSource(false)}
              className="w-full mt-6 py-2.5 px-4 text-sm font-semibold text-on-surface bg-surface border border-primary focus:outline-none rounded-lg"
              placeholder="Type domain (e.g. github) and press Enter..."
            />
          ) : (
            <button onClick={() => setIsAddingSource(true)} className="w-full mt-6 py-2.5 text-sm font-semibold text-primary bg-primary/5 hover:bg-primary/10 rounded-lg transition-colors border border-primary/10 flex justify-center items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">manage_search</span> Manage Directory
            </button>
          )}
        </div>

        {/* Behavioral Tuning Card (Spans 2 columns) */}
        <div className="lg:col-span-2 bg-gradient-to-br from-surface-container-low to-transparent rounded-2xl p-8 border border-outline-variant/30 shadow-sm">
          <div className="mb-8">
            <h3 className="font-headline text-xl font-semibold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary">tune</span>
              Behavioral Tuning
            </h3>
            <p className="text-on-surface-variant text-sm mt-1">Adjust how the algorithm processes and presents information to you.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
            {/* Toggle Setting */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-on-surface mb-1">Highlight Contradictions</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">Automatically flag reports from trusted sources that present opposing viewpoints on your core topics.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-outline-variant/30 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            {/* Toggle Setting */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-on-surface mb-1">Aggressive Noise Filtering</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">Strictly limit briefings to explicit matches of core topics, filtering out tangential or related industry news.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-outline-variant/30 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>

            {/* Toggle Setting */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-on-surface mb-1">Prioritize Primary Sources</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">Boost raw data releases, earnings calls, and official statements over secondary journalistic analysis.</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                <input type="checkbox" defaultChecked className="sr-only peer" />
                <div className="w-11 h-6 bg-surface-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-outline-variant/30 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Actions Footer */}
      <div className="flex justify-end gap-4 pt-8 mt-10">
        <button className="px-6 py-3 rounded-xl font-bold text-on-surface hover:bg-surface-variant/50 transition-all duration-300">Discard Changes</button>
        <button onClick={savePreferences} disabled={saving} className="px-6 py-3 rounded-xl font-bold text-on-primary bg-gradient-to-r from-primary to-primary/80 hover:-translate-y-0.5 transition-all duration-300 shadow-[0_4px_12px_rgba(74,124,89,0.3)] hover:shadow-[0_6px_20px_rgba(74,124,89,0.35)] disabled:opacity-70 disabled:hover:translate-y-0 disabled:hover:shadow-none">
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
}
