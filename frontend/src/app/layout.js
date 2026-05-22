import "./globals.css";
import NavLinks from "../components/NavLinks";
import { UserProvider } from "../context/UserContext";

export const metadata = {
  title: "InsightGraph - Intelligence Command Center",
  description: "AI-powered Intelligence Operations Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="light">
      <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
      </head>
      <body className="bg-surface text-on-surface antialiased min-h-screen flex flex-col">
        {/* TopNavBar */}
        <UserProvider>
          <nav className="font-body leading-relaxed fixed top-0 w-full z-50 bg-surface-container-low border-b border-outline-variant/20 shadow-sm transition-all duration-300 ease-in-out">
          <div className="flex justify-between items-center px-8 h-16 w-full max-w-7xl mx-auto">
            <div className="flex items-center gap-8">
              <div className="font-headline text-2xl font-bold text-primary">InsightGraph</div>
              <NavLinks />
            </div>
            <div className="flex items-center gap-4">
              <div className="relative group">
                <a href="/preferences" className="text-on-surface-variant hover:bg-surface-variant/30 hover:text-primary rounded-lg p-2 transition-colors flex items-center justify-center">
                  <span className="material-symbols-outlined" data-icon="settings">settings</span>
                </a>
              </div>
              <button className="text-on-surface-variant hover:text-primary hover:bg-surface-variant/30 rounded-lg p-2 transition-colors flex items-center justify-center">
                <span className="material-symbols-outlined" data-icon="notifications">notifications</span>
              </button>
              <button className="text-on-surface-variant hover:text-primary hover:bg-surface-variant/30 rounded-lg p-2 transition-colors flex items-center justify-center">
                <span className="material-symbols-outlined" data-icon="account_circle">account_circle</span>
              </button>
            </div>
          </div>
        </nav>
        
        {/* Main Content Layout */}
        <div className="flex-1 flex max-w-[1400px] mx-auto w-full relative pt-16">
          <main className="flex-1 p-6 md:p-8 lg:p-10 w-full overflow-y-auto">
            {children}
          </main>
        </div>
        </UserProvider>
      </body>
    </html>
  );
}
