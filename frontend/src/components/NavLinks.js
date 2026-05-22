"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function NavLinks() {
  const pathname = usePathname();

  const links = [
    { name: 'Dashboard', href: '/' },
    { name: 'Intelligence Briefings', href: '/briefing' },
    { name: 'Analytics', href: '/analytics' },
  ];

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
                : "text-on-surface-variant hover:text-primary transition-colors hover:bg-surface-variant/30 rounded-lg px-3 py-2"
            }
          >
            {link.name}
          </Link>
        );
      })}
    </div>
  );
}
