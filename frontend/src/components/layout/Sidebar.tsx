'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, Clock, Settings, Home, Microscope, UserCircle } from 'lucide-react';

const navItems = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Analyze', href: '/analyze', icon: Activity },
  { name: 'History', href: '/history', icon: Clock },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-sidebar-border bg-sidebar flex flex-col h-full shrink-0 text-sidebar-foreground relative overflow-hidden">
      {/* Subtle scanline overlay for clinical feel */}
      <div className="absolute inset-0 pointer-events-none opacity-5 bg-[repeating-linear-gradient(transparent,transparent_2px,#000_2px,#000_4px)]"></div>
      
      <div className="p-6 relative z-10 flex items-center gap-3">
        <div className="p-2 bg-primary/20 rounded-md text-primary">
          <Microscope className="w-5 h-5" />
        </div>
        <h1 className="text-xl font-bold tracking-tight text-foreground">
          MedScope AI
        </h1>
      </div>

      <nav className="flex-1 px-4 space-y-1 relative z-10">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-md transition-colors duration-150 ${
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                  : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile Chip */}
      <div className="p-4 relative z-10 border-t border-sidebar-border mt-auto">
        <div className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-sidebar-accent/50 cursor-pointer transition-colors">
          <UserCircle className="w-8 h-8 text-sidebar-foreground/70" />
          <div className="flex flex-col">
            <span className="text-sm font-medium text-sidebar-foreground">Dr. Sarah Chen</span>
            <span className="text-xs text-sidebar-foreground/50">Lead Pathologist</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
