'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Activity, Clock, Settings, Home, Microscope, UserCircle, LogOut } from 'lucide-react';
import { createClient } from '@/lib/supabase/client';
import { useEffect, useState } from 'react';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Analyze', href: '/dashboard/analyze', icon: Activity },
  { name: 'History', href: '/dashboard/history', icon: Clock },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClient();
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const { data: { user }, error } = await supabase.auth.getUser();
        if (error) throw error;
        if (user) {
          setUserEmail(user.email ?? 'Unknown User');
        } else {
          setUserEmail('Test Clinician');
        }
      } catch (err) {
        // Fallback for Colab testing auth bypass when Supabase errors out
        setUserEmail('Test Clinician');
      }
    };
    fetchUser();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/auth');
  };

  return (
    <aside className="w-64 border-r-4 border-foreground bg-[#FDFBF7] flex flex-col h-full shrink-0 relative overflow-hidden">
      {/* Subtle scanline overlay for clinical feel */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[repeating-linear-gradient(transparent,transparent_2px,#000_2px,#000_4px)]"></div>
      
      <div className="p-6 relative z-10 flex items-center gap-3 border-b-4 border-foreground bg-white">
        <div className="p-2 bg-[#06b6d4] border-2 border-foreground rounded-none text-white shadow-[2px_2px_0px_theme(colors.foreground)]">
          <Microscope className="w-5 h-5" />
        </div>
        <h1 className="text-xl font-black tracking-tight text-foreground uppercase">
          MedScope <span className="bg-[#06b6d4] text-white px-1 border-2 border-foreground transform -rotate-2 inline-block">AI</span>
        </h1>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2 relative z-10 bg-[#FDFBF7]">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-3 border-2 transition-all font-bold uppercase tracking-tight ${
                isActive
                  ? 'bg-foreground text-background border-foreground shadow-[3px_3px_0px_theme(colors.foreground)]'
                  : 'bg-transparent border-transparent text-muted-foreground hover:border-foreground hover:bg-white hover:text-foreground hover:shadow-[3px_3px_0px_theme(colors.foreground)] hover:-translate-y-0.5'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile & Logout */}
      <div className="p-4 relative z-10 border-t-4 border-foreground mt-auto bg-white">
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-3 px-2">
            <UserCircle className="w-8 h-8 text-foreground" />
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-bold text-foreground truncate">{userEmail || 'Loading...'}</span>
              <span className="text-xs font-black text-muted-foreground uppercase tracking-widest">Clinician</span>
            </div>
          </div>
          <button 
            onClick={handleSignOut}
            className="flex items-center justify-center gap-2 w-full py-2 border-2 border-foreground bg-[#FDFBF7] text-foreground font-bold uppercase text-sm hover:-translate-y-0.5 hover:shadow-[3px_3px_0px_theme(colors.foreground)] active:translate-y-0 active:shadow-none transition-all"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}
