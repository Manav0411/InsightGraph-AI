"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button className="text-on-surface-variant hover:text-primary hover:bg-surface-variant/30 rounded-lg p-2 transition-colors flex items-center justify-center opacity-0">
        <span className="material-symbols-outlined">light_mode</span>
      </button>
    );
  }

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="text-on-surface-variant hover:text-primary hover:bg-surface-variant/30 rounded-lg p-2 transition-colors flex items-center justify-center"
      aria-label="Toggle Dark Mode"
    >
      <span className="material-symbols-outlined">
        {theme === "dark" ? "light_mode" : "dark_mode"}
      </span>
    </button>
  );
}
