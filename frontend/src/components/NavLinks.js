"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function NavLinks({ isAdmin }) {
  const pathname = usePathname();

  const links = [
    { name: 'Intelligence Briefing', href: '/' },
    { name: 'History', href: '/history' },
  ];

  if (isAdmin) {
    links.push({ name: 'Mission Control', href: '/admin/mission-control' });
    links.push({ name: 'Analytics', href: '/admin/analytics' });
  }

  return (
    <div className="hidden md:flex gap-6 h-full items-center">
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
  );
}
