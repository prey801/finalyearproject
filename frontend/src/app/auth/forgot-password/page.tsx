'use client';

import { useState } from 'react';
import { Mail, AlertCircle, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    
    // Simulate API call for now since we don't have the backend route specified
    setTimeout(() => {
      if (email) {
        setStatus('success');
      } else {
        setStatus('error');
        setErrorMsg('Please enter a valid email address.');
      }
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background overflow-hidden relative">
      {/* Dynamic Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#06b6d4]/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-pink-400/20 blur-[120px] rounded-full pointer-events-none"></div>

      <div className="relative w-full max-w-[500px] min-h-[400px] bg-card/60 backdrop-blur-xl border border-border/50 rounded-3xl shadow-2xl p-10 text-center flex flex-col justify-center">
        
        <div className="mb-6 self-start">
          <Link href="/auth" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors font-medium">
            <ArrowLeft className="w-4 h-4" />
            Back to Sign In
          </Link>
        </div>

        <h1 className="text-3xl font-bold mb-4 font-heading">Reset Password</h1>
        
        {status === 'success' ? (
          <div className="flex flex-col items-center animate-fade-in-up">
            <div className="w-16 h-16 bg-[#06b6d4]/20 rounded-2xl flex items-center justify-center mb-6 border-2 border-foreground">
              <Mail className="w-8 h-8 text-foreground" />
            </div>
            <p className="text-muted-foreground leading-relaxed">
              If an account exists for <span className="font-semibold text-foreground">{email}</span>, we have sent a password reset link. Please check your inbox.
            </p>
          </div>
        ) : (
          <div className="animate-fade-in-up">
            <p className="text-muted-foreground mb-8 text-sm leading-relaxed">
              Enter the email address associated with your account and we'll send you a link to reset your password.
            </p>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="relative group text-left">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-foreground transition-colors" />
                <input 
                  type="email" 
                  placeholder="Email Address" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  required 
                  className="w-full bg-background/50 border-2 border-foreground/20 px-10 py-3 rounded-xl focus:outline-none focus:border-foreground transition-all font-medium text-foreground" 
                />
              </div>

              {status === 'error' && (
                <div className="flex items-center gap-2 text-destructive text-sm bg-destructive/10 p-3 rounded-lg border border-destructive/20 w-full">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span className="text-left leading-tight">{errorMsg}</span>
                </div>
              )}

              <button 
                type="submit" 
                disabled={status === 'loading'} 
                className="mt-4 bg-foreground text-background font-semibold py-3 px-10 rounded-xl shadow-[4px_4px_0px_theme(colors.foreground)] hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] transition-all border-2 border-foreground flex items-center justify-center gap-2"
              >
                {status === 'loading' ? <><Loader2 className="w-4 h-4 animate-spin"/> Sending...</> : 'Send Reset Link'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
