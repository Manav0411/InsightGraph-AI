"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from '../lib/config';
import { useUser as useClerkUser, useAuth } from '@clerk/nextjs';

const UserContext = createContext();

export function UserProvider({ children }) {
  const { user: clerkUser, isLoaded } = useClerkUser();
  const { getToken } = useAuth();
  
  const [user, setUser] = useState(null);
  const [preferences, setPreferences] = useState({
    preferred_topics: [],
    excluded_topics: [],
    preferred_sources: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isLoaded) {
      if (clerkUser) {
        setUser({ id: clerkUser.id, name: clerkUser.fullName || 'Commander' });
      } else {
        setUser(null);
        setLoading(false);
      }
    }
  }, [isLoaded, clerkUser]);

  useEffect(() => {
    if (user?.id) {
      fetchPreferences();
    }
  }, [user?.id]);

  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const email = clerkUser?.primaryEmailAddress?.emailAddress;
      const res = await fetch(`${API_BASE_URL}/users/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          // Lets the backend stamp a brand-new user row with the right email
          // immediately, rather than waiting on the Clerk webhook to catch up.
          ...(email ? { 'X-User-Email': email } : {})
        }
      });
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
      const token = await getToken();
      const res = await fetch(`${API_BASE_URL}/users/${user.id}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
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
    <UserContext.Provider value={{ user, setUser, preferences, updatePreferences, loading, getToken }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}

