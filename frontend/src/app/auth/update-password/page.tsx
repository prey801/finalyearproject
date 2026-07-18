'use client';

import { useState } from 'react';
import { Lock, AlertCircle, Loader2, CheckCircle2, Eye, EyeOff } from 'lucide-react';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';

export default function UpdatePassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const router = useRouter();
  const supabase = createClient();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    
    if (password !== confirmPassword) {
      setStatus('error');
      setErrorMsg('Passwords do not match.');
      return;
    }
    
    if (password.length < 6) {
      setStatus('error');
      setErrorMsg('Password must be at least 6 characters long.');
      return;
    }

    try {
      const { error } = await supabase.auth.updateUser({
        password: password
      });

      if (error) throw error;
      
      setStatus('success');
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message || 'Failed to update password. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#FDFBF7] overflow-hidden relative p-4">
      {/* Brutalist Grid Background */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[repeating-linear-gradient(transparent,transparent_39px,#000_39px,#000_40px),repeating-linear-gradient(90deg,transparent,transparent_39px,#000_39px,#000_40px)]"></div>

      <div className="relative w-full max-w-[500px] min-h-[400px] bg-white border-4 border-foreground shadow-[12px_12px_0px_theme(colors.foreground)] p-10 text-center flex flex-col justify-center animate-fade-in-up">
        
        <h1 className="text-4xl font-black mb-4 uppercase tracking-tighter text-foreground">Set New Password</h1>
        
        {status === 'success' ? (
          <div className="flex flex-col items-center animate-fade-in-up">
            <div className="w-20 h-20 bg-[#06b6d4] text-white flex items-center justify-center mb-6 border-4 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)]">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <div className="border-2 border-foreground p-4 bg-[#FDFBF7] w-full">
              <p className="text-foreground font-black uppercase tracking-widest text-lg leading-relaxed mb-2">
                Successfully Updated!
              </p>
              <p className="text-sm font-bold animate-pulse text-muted-foreground uppercase tracking-widest">
                Redirecting to your dashboard...
              </p>
            </div>
          </div>
        ) : (
          <div className="animate-fade-in-up">
            <p className="text-muted-foreground mb-8 text-sm font-semibold uppercase tracking-widest leading-relaxed">
              Please enter your new password below.
            </p>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
              <div className="relative group text-left">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-foreground transition-colors" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  placeholder="NEW PASSWORD" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                  className="w-full bg-[#FDFBF7] border-4 border-foreground px-12 py-4 focus:outline-none focus:bg-white transition-all font-black text-foreground placeholder:text-muted-foreground/50 shadow-[4px_4px_0px_theme(colors.foreground)] focus:shadow-[6px_6px_0px_theme(colors.foreground)] focus:-translate-y-0.5" 
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors" tabIndex={-1}>
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              <div className="relative group text-left">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground group-focus-within:text-foreground transition-colors" />
                <input 
                  type={showPassword ? "text" : "password"} 
                  placeholder="CONFIRM NEW PASSWORD" 
                  value={confirmPassword} 
                  onChange={(e) => setConfirmPassword(e.target.value)} 
                  required 
                  className="w-full bg-[#FDFBF7] border-4 border-foreground px-12 py-4 focus:outline-none focus:bg-white transition-all font-black text-foreground placeholder:text-muted-foreground/50 shadow-[4px_4px_0px_theme(colors.foreground)] focus:shadow-[6px_6px_0px_theme(colors.foreground)] focus:-translate-y-0.5" 
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
                {status === 'loading' ? <><Loader2 className="w-5 h-5 animate-spin"/> Updating...</> : 'Update Password'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
