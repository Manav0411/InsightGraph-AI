"use client";

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function NavLinks({ isAdmin }) {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const links = [
    { name: 'Briefing', href: '/' },
    { name: 'History', href: '/history' },
  ];

  if (isAdmin) {
    links.push({ name: 'Mission Control', href: '/admin/mission-control' });
    links.push({ name: 'Analytics', href: '/admin/analytics' });
  }

  return (
    <>
      <div className="hidden md:flex gap-1 h-full items-center order-first md:mr-2">
        {links.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.name}
              href={link.href}
              className={`font-mono text-[13px] px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? "text-primary"
                  : "text-on-surface-variant hover:text-primary hover:bg-surface-variant/30"
              }`}
            >
              {link.name}
            </Link>
          );
        })}
      </div>

      <div className="md:hidden flex items-center order-last ml-1">
        <button
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Menu"
          className="text-on-surface-variant hover:text-primary p-2 focus:outline-none rounded-lg hover:bg-surface-variant/30 transition-colors flex items-center justify-center"
        >
          <span className="material-symbols-outlined">{isOpen ? 'close' : 'menu'}</span>
        </button>
      </div>

      {isOpen && (
        <div className="absolute top-16 left-0 w-full bg-surface border-b border-outline-variant/20 md:hidden flex flex-col py-4 px-6 gap-1">
          {links.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className={`font-mono text-sm rounded-lg px-4 py-3 transition-colors ${
                  isActive
                    ? "text-primary bg-primary/10"
                    : "text-on-surface-variant hover:text-primary hover:bg-surface-variant/30"
                }`}
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
