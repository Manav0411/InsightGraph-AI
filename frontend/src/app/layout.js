import "./globals.css";
import NavLinks from "../components/NavLinks";
import { UserProvider } from "../context/UserContext";
import { ThemeProvider } from "../components/ThemeProvider";
import { ThemeToggle } from "../components/ThemeToggle";
import Link from 'next/link';
import { SignInButton, SignUpButton, UserButton } from '@clerk/nextjs';
import { auth, currentUser } from '@clerk/nextjs/server';
import { ClerkThemeProvider } from '../components/ClerkThemeProvider';
import { Button } from '../components/ui';
import { Agentation } from "agentation";

export const metadata = {
  title: "InsightGraph - Intelligence Command Center",
  description: "AI-powered Intelligence Operations Platform",
};

export default async function RootLayout({ children }) {
  const { userId } = await auth();
  const user = await currentUser();
  const email = user?.emailAddresses?.[0]?.emailAddress?.toLowerCase() || "";
  const adminEmails = process.env.ADMIN_EMAILS ? process.env.ADMIN_EMAILS.split(',') : [];
  const isAdmin = user && adminEmails.includes(email);
  
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
      </head>
      <body className="bg-surface text-on-surface antialiased min-h-screen flex flex-col transition-colors duration-300" suppressHydrationWarning>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <ClerkThemeProvider>
            <UserProvider>
              <nav className="font-mono fixed top-0 w-full z-50 bg-surface-container-low/85 backdrop-blur border-b border-outline-variant/20">
            <div className="flex justify-between items-center px-4 md:px-8 h-16 w-full max-w-7xl mx-auto">
              <div className="flex items-center gap-2 md:gap-8">
                <Link href="/" className="inline-flex items-baseline gap-1 font-mono font-semibold text-[15px] md:text-base text-primary hover:opacity-80 transition-opacity">
                  <span className="text-on-surface-variant">&#9656;</span>insightgraph
                </Link>
              </div>
              <div className="flex items-center gap-2 md:gap-4">
                {userId && <NavLinks isAdmin={isAdmin} />}

                <ThemeToggle />

                {userId ? (
                  <>
                    <Link href="/preferences" aria-label="Preferences" className="text-on-surface-variant hover:text-primary hover:bg-surface-variant/30 rounded-lg p-2 transition-colors flex items-center justify-center">
                      <span className="material-symbols-outlined" data-icon="settings">settings</span>
                    </Link>
                    <UserButton appearance={{ elements: { userButtonAvatarBox: "w-8 h-8 rounded-lg" } }} />
                  </>
                ) : (
                  <>
                    <SignInButton mode="modal" signUpForceRedirectUrl="/onboarding" fallbackRedirectUrl="/">
                      <Button variant="ghost" size="sm">Sign in</Button>
                    </SignInButton>
                    <SignUpButton mode="modal" forceRedirectUrl="/onboarding" fallbackRedirectUrl="/onboarding">
                      <Button variant="primary" size="sm">Get started</Button>
                    </SignUpButton>
                  </>
                )}

              </div>
            </div>
          </nav>

          {/* Every screen owns its own width + padding via <PageShell>. */}
          <main className="flex-1 w-full pt-16">
            {children}
          </main>
          </UserProvider>
        </ClerkThemeProvider>
        </ThemeProvider>
        {process.env.NODE_ENV === "development" && <Agentation />}
      </body>
    </html>
  );
}
