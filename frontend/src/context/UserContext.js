"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from '../lib/config';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [user, setUser] = useState({ id: 'default_user', name: 'Commander' });
  const [preferences, setPreferences] = useState({
    preferred_topics: [],
    excluded_topics: [],
    preferred_sources: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPreferences();
  }, [user.id]);

  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/users/${user.id}`);
      if (res.ok) {
        const json = await res.json();
        if (json.profile?.preferences) {
          setPreferences(json.profile.preferences);
        }
      }
    } catch (err) {
      console.error("Failed to fetch user preferences:", err);
    } finally {
      setLoading(false);
    }
  };

  const updatePreferences = async (newPrefs) => {
    try {
      const res = await fetch(`${API_BASE_URL}/users/${user.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPrefs)
      });
      if (res.ok) {
        setPreferences({ ...preferences, ...newPrefs });
        return true;
      }
    } catch (err) {
      console.error("Failed to update preferences:", err);
    }
    return false;
  };

  return (
    <UserContext.Provider value={{ user, setUser, preferences, updatePreferences, loading }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
