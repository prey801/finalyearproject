'use client';

import { useState } from 'react';
import { Mail, AlertCircle, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const supabase = createClient();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setStatus('error');
      setErrorMsg('Please enter a valid email address.');
      return;
    }

    setStatus('loading');

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/callback?next=/auth/update-password`,
      });

      if (error) throw error;
      setStatus('success');
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message || 'Failed to send reset link. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FDFBF7] overflow-hidden relative p-4">
      {/* Brutalist Grid Background */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[repeating-linear-gradient(transparent,transparent_39px,#000_39px,#000_40px),repeating-linear-gradient(90deg,transparent,transparent_39px,#000_39px,#000_40px)]"></div>

      <div className="relative w-full max-w-[500px] min-h-[400px] bg-white border-4 border-foreground shadow-[12px_12px_0px_theme(colors.foreground)] p-10 text-center flex flex-col justify-center animate-fade-in-up">
        
        <div className="mb-8 self-start">
          <Link href="/auth" className="inline-flex items-center gap-2 text-sm font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors border-b-2 border-transparent hover:border-foreground pb-0.5">
            <ArrowLeft className="w-4 h-4" />
            Back to Sign In
          </Link>
        </div>

        <h1 className="text-4xl font-black mb-4 uppercase tracking-tighter text-foreground">Reset Password</h1>
        
        {status === 'success' ? (
          <div className="flex flex-col items-center animate-fade-in-up">
            <div className="w-20 h-20 bg-[#06b6d4] text-white flex items-center justify-center mb-6 border-4 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)]">
              <Mail className="w-10 h-10" />
            </div>
            <p className="text-foreground font-medium text-lg leading-relaxed border-2 border-foreground p-4 bg-[#FDFBF7]">
              If an account exists for <span className="font-black">{email}</span>, we have sent a password reset link. Please check your inbox.
            </p>
          </div>
        ) : (
          <div className="animate-fade-in-up">
            <p className="text-muted-foreground mb-8 text-sm font-semibold uppercase tracking-widest leading-relaxed">
              Enter your email and we'll send a reset link.
            </p>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
              <div className="relative group text-left">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-foreground transition-colors" />
                <input 
                  type="email" 
                  placeholder="EMAIL ADDRESS" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  required 
                  className="w-full bg-[#FDFBF7] border-4 border-foreground px-12 py-4 focus:outline-none focus:bg-white transition-all font-black uppercase text-foreground placeholder:text-muted-foreground/50 shadow-[4px_4px_0px_theme(colors.foreground)] focus:shadow-[6px_6px_0px_theme(colors.foreground)] focus:-translate-y-0.5" 
                />
              </div>

              {status === 'error' && (
                <div className="flex items-center gap-3 text-destructive font-bold uppercase tracking-wider text-sm bg-destructive/10 p-4 border-4 border-destructive w-full shadow-[4px_4px_0px_theme(colors.destructive)]">
                  <AlertCircle className="w-5 h-5 shrink-0" />
                  <span className="text-left leading-tight">{errorMsg}</span>
                </div>
              )}

              <button 
                type="submit" 
                disabled={status === 'loading'} 
                className="mt-2 bg-[#06b6d4] text-white font-black uppercase tracking-widest py-4 px-10 shadow-[6px_6px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] transition-all border-4 border-foreground flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status === 'loading' ? <><Loader2 className="w-5 h-5 animate-spin"/> Sending...</> : 'Send Reset Link'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
