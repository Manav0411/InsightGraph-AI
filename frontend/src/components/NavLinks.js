"use client";

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function NavLinks({ isAdmin }) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const links = [
    { name: 'Intelligence Briefing', href: '/' },
    { name: 'History', href: '/history' },
  ];

  if (isAdmin) {
    links.push({ name: 'Mission Control', href: '/admin/mission-control' });
    links.push({ name: 'Analytics', href: '/admin/analytics' });
  }

  return (
    <>
      <div className="hidden md:flex gap-6 h-full items-center order-first md:mr-4">
        {links.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.name}
              href={link.href}
              className={
                isActive
                  ? "text-primary border-b-2 border-primary pb-1 h-full flex items-center font-semibold"
                  : "text-on-surface-variant hover:text-primary transition-colors hover:bg-surface-variant/30 rounded-lg px-3 py-2 flex items-center"
              }
            >
              {link.icon ? (
                <span className="material-symbols-outlined text-[24px]">{link.icon}</span>
              ) : (
                link.name
              )}
            </Link>
          );
        })}
      </div>

      <div className="md:hidden flex items-center order-last ml-2">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-on-surface-variant hover:text-primary p-2 focus:outline-none rounded-lg hover:bg-surface-variant/30 transition-colors flex items-center justify-center"
        >
          <span className="material-symbols-outlined">{isOpen ? 'close' : 'menu'}</span>
        </button>
      </div>

      {isOpen && (
        <div className="absolute top-16 left-0 w-full bg-surface border-b border-outline-variant/20 shadow-lg md:hidden flex flex-col py-4 px-6 gap-2 animate-in slide-in-from-top-2 duration-200">
          {links.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className={
                  isActive
                    ? "text-primary font-bold bg-primary/10 rounded-lg px-4 py-3"
                    : "text-on-surface-variant hover:text-primary hover:bg-surface-variant/30 rounded-lg px-4 py-3 transition-colors font-medium"
                }
              >
                {link.name}
              </Link>
            );
          })}
        </div>
      )}
    </>
  );
}
