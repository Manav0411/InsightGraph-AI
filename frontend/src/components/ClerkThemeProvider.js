"use client";

import { useTheme } from "next-themes";
import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
import { useEffect, useState } from "react";

export function ClerkThemeProvider({ children }) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <ClerkProvider
      appearance={{
        baseTheme: mounted && resolvedTheme === "dark" ? dark : undefined,
        variables: {
          colorPrimary: mounted && resolvedTheme === "dark" ? "#8ECF9E" : "#4A7C59",
          colorBackground: mounted && resolvedTheme === "dark" ? "#1E201F" : "#F0ECE4",
          colorText: mounted && resolvedTheme === "dark" ? "#E4E0D8" : "#2E3230",
          colorInputBackground: mounted && resolvedTheme === "dark" ? "#121413" : "#FAF6F0",
          colorInputText: mounted && resolvedTheme === "dark" ? "#E4E0D8" : "#2E3230",
          fontFamily: "'Nunito Sans', sans-serif",
          borderRadius: '16px'
        },
        elements: {
          card: "bg-surface-container shadow-2xl border border-outline-variant/30 rounded-[2rem]",
          headerTitle: "font-headline text-4xl font-bold text-on-surface tracking-tight",
          headerSubtitle: "text-on-surface-variant font-body text-lg",
          socialButtonsBlockButton: "bg-surface border border-outline-variant/40 hover:bg-surface-variant text-on-surface transition-colors rounded-xl py-3 shadow-sm",
          socialButtonsBlockButtonText: "font-bold tracking-wide",
          dividerLine: "bg-outline-variant/30",
          dividerText: "text-on-surface-variant uppercase tracking-widest text-[10px]",
          formFieldLabel: "text-on-surface-variant font-bold uppercase tracking-widest text-[10px]",
          formFieldInput: "bg-surface border border-outline-variant/50 text-on-surface focus:ring-2 focus:ring-primary focus:border-transparent rounded-xl py-3",
          formButtonPrimary: "bg-primary hover:bg-primary/90 text-on-primary font-bold transition-colors rounded-xl py-3.5 shadow-md",
          footerActionText: "text-on-surface-variant",
          footerActionLink: "text-primary hover:text-tertiary font-bold",
          identityPreviewText: "text-on-surface",
          identityPreviewEditButton: "text-primary hover:text-tertiary",
          userButtonAvatarBox: "w-10 h-10 rounded-xl border border-outline-variant/40 shadow-sm",
          userButtonPopoverCard: "bg-surface-container shadow-2xl border border-outline-variant/30 rounded-2xl",
          userButtonPopoverActionButton: "hover:bg-surface-variant text-on-surface rounded-xl",
          userButtonPopoverActionButtonText: "text-on-surface font-medium",
          userButtonPopoverActionButtonIcon: "text-on-surface-variant",
          watermark: "hidden",
        }
      }}
      localization={{
        signIn: {
          start: {
            title: "Sign in to InsightGraph",
            subtitle: "Welcome back! Access your intelligence command center.",
          }
        },
        signUp: {
          start: {
            title: "Join InsightGraph",
            subtitle: "Create your account to start synthesizing intelligence.",
          }
        }
      }}
    >
      {children}
    </ClerkProvider>
  );
}
