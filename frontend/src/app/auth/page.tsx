'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/authContext';
import { Activity, Lock, User, AlertCircle, Loader2, Mail, Eye, EyeOff } from 'lucide-react';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LandingPage() {
  const [isRightPanelActive, setIsRightPanelActive] = useState(false);

  // Login State
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegPassword, setShowRegPassword] = useState(false);
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isLoginLoading, setIsLoginLoading] = useState(false);

  // Register State
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regError, setRegError] = useState('');
  const [regSuccess, setRegSuccess] = useState('');
  const [isRegLoading, setIsRegLoading] = useState(false);

  const { login } = useAuth();
  const router = useRouter();

  const supabase = createClient();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setIsLoginLoading(true);

    try {
      // Note: Supabase uses email for login by default.
      const { data, error } = await supabase.auth.signInWithPassword({
        email: loginUsername,
        password: loginPassword,
      });

      if (error) throw error;
      
      if (data.session) {
        login(data.session.access_token);
        router.push('/dashboard');
      }
    } catch (err: any) {
      setLoginError(err.message || 'Invalid email or password.');
    } finally {
      setIsLoginLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegError('');
    setRegSuccess('');
    setIsRegLoading(true);

    try {
      const { data, error } = await supabase.auth.signUp({
        email: regEmail,
        password: regPassword,
        options: {
          data: {
            username: regUsername
          }
        }
      });
      
      if (error) throw error;

      if (data.session) {
        login(data.session.access_token);
        router.push('/dashboard');
      } else if (data.user) {
        setRegSuccess('Signup successful! Please check your email to verify your account.');
      }
    } catch (err: any) {
      setRegError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsRegLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'facebook' | 'github' | 'linkedin_oidc') => {
    await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background overflow-hidden relative">
      {/* Dynamic Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#06b6d4]/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-pink-400/20 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Back to Home Button */}
      <Link href="/" className="absolute top-8 left-8 z-[200] flex items-center gap-2 px-5 py-2.5 rounded-full border-2 border-foreground bg-background text-foreground font-medium shadow-[3px_3px_0px_theme(colors.foreground)] hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] transition-all">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        Back to Home
      </Link>

      <div className={`relative w-full max-w-[800px] min-h-[500px] bg-card/60 backdrop-blur-xl border border-border/50 rounded-3xl shadow-2xl overflow-hidden`}>
        
        {/* Sign Up Form */}
        <div className={`absolute top-0 h-full w-1/2 left-0 transition-all duration-700 ease-in-out z-10 ${isRightPanelActive ? 'translate-x-full opacity-100 z-50' : 'opacity-0 z-10 pointer-events-none'}`}>
          <form onSubmit={handleRegister} className="bg-card flex items-center justify-center flex-col px-10 h-full text-center">
            <h1 className="text-3xl font-bold mb-4">Create Account</h1>
            <div className="flex gap-4 my-4">
              <button type="button" onClick={() => handleSocialLogin('google')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#4285F4]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#4285F4] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
              </button>
              <button type="button" onClick={() => handleSocialLogin('facebook')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#1877F2]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#1877F2] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.675 0H1.325C.593 0 0 .593 0 1.325v21.351C0 23.407.593 24 1.325 24H12.82v-9.294H9.692v-3.622h3.128V8.413c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12V24h6.116c.73 0 1.323-.593 1.323-1.325V1.325C24 .593 23.407 0 22.675 0z"/>
                </svg>
              </button>
              <button type="button" onClick={() => handleSocialLogin('github')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#24292e] dark:hover:border-[#ffffff]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#24292e] dark:group-hover:text-[#ffffff] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
                </svg>
              </button>
              <button type="button" onClick={() => handleSocialLogin('linkedin_oidc')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#0A66C2]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#0A66C2] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </button>
            </div>
            <span className="text-sm text-muted-foreground mb-4">or use your email for registration</span>
            
            <div className="w-full space-y-3">
              <div className="relative group">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input type="text" placeholder="Username" autoComplete="username" value={regUsername} onChange={(e) => setRegUsername(e.target.value)} required className="w-full bg-background/50 border border-border px-10 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all" />
              </div>
              <div className="relative group">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input type="email" placeholder="Email" autoComplete="email" value={regEmail} onChange={(e) => setRegEmail(e.target.value)} required className="w-full bg-background/50 border border-border px-10 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all" />
              </div>
              <div className="relative group">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input type={showRegPassword ? "text" : "password"} placeholder="Password" autoComplete="new-password" value={regPassword} onChange={(e) => setRegPassword(e.target.value)} required className="w-full bg-background/50 border border-border px-10 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all" />
                <button type="button" onClick={() => setShowRegPassword(!showRegPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors" tabIndex={-1}>
                  {showRegPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {regError && (
              <div className="mt-4 flex items-center gap-2 text-destructive text-sm bg-destructive/10 p-2 rounded-lg border border-destructive/20 w-full">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span className="text-left leading-tight">{regError}</span>
              </div>
            )}

            {regSuccess && (
              <div className="mt-4 flex items-center gap-2 text-green-600 dark:text-green-400 text-sm bg-green-500/10 p-2 rounded-lg border border-green-500/20 w-full">
                <Mail className="w-4 h-4 shrink-0" />
                <span className="text-left leading-tight">{regSuccess}</span>
              </div>
            )}

            <button type="submit" disabled={isRegLoading} className="mt-6 bg-primary text-primary-foreground font-semibold py-2.5 px-10 rounded-lg shadow hover:bg-primary/90 transition-all active:scale-[0.98] flex items-center justify-center gap-2">
              {isRegLoading ? <><Loader2 className="w-4 h-4 animate-spin"/> Signing Up...</> : 'Sign Up'}
            </button>
          </form>
        </div>

        {/* Sign In Form */}
        <div className={`absolute top-0 h-full w-1/2 left-0 transition-all duration-700 ease-in-out z-20 ${isRightPanelActive ? 'translate-x-full opacity-0 pointer-events-none' : ''}`}>
          <form onSubmit={handleLogin} className="bg-card flex items-center justify-center flex-col px-10 h-full text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-3xl font-bold mb-4">Sign In</h1>
            <div className="flex gap-4 my-4">
              <button type="button" onClick={() => handleSocialLogin('google')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#4285F4]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#4285F4] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
              </button>
              <button type="button" onClick={() => handleSocialLogin('facebook')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#1877F2]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#1877F2] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.675 0H1.325C.593 0 0 .593 0 1.325v21.351C0 23.407.593 24 1.325 24H12.82v-9.294H9.692v-3.622h3.128V8.413c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12V24h6.116c.73 0 1.323-.593 1.323-1.325V1.325C24 .593 23.407 0 22.675 0z"/>
                </svg>
              </button>
              <button type="button" onClick={() => handleSocialLogin('github')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#24292e] dark:hover:border-[#ffffff]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#24292e] dark:group-hover:text-[#ffffff] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
                </svg>
              </button>
              <button type="button" onClick={() => handleSocialLogin('linkedin_oidc')} className="border border-border/50 rounded-full w-10 h-10 flex items-center justify-center transition-colors group hover:border-[#0A66C2]">
                <svg className="w-5 h-5 text-muted-foreground group-hover:text-[#0A66C2] transition-colors" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </button>
            </div>
            <span className="text-sm text-muted-foreground mb-4">or use your account</span>
            
            <div className="w-full space-y-3">
              <div className="relative group">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input type="email" placeholder="Email" autoComplete="email" value={loginUsername} onChange={(e) => setLoginUsername(e.target.value)} required className="w-full bg-background/50 border border-border px-10 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all" />
              </div>
              <div className="relative group">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                <input type={showLoginPassword ? "text" : "password"} placeholder="Password" autoComplete="current-password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} required className="w-full bg-background/50 border border-border px-10 py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all" />
                <button type="button" onClick={() => setShowLoginPassword(!showLoginPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors" tabIndex={-1}>
                  {showLoginPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <Link href="/auth/forgot-password" className="text-sm text-muted-foreground hover:text-foreground mt-4 mb-2 inline-block transition-colors font-medium">Forgot Your Password?</Link>

            {loginError && (
              <div className="mb-4 flex items-center gap-2 text-destructive text-sm bg-destructive/10 p-2 rounded-lg border border-destructive/20 w-full">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span className="text-left leading-tight">{loginError}</span>
              </div>
            )}

            <button type="submit" disabled={isLoginLoading} className="bg-primary text-primary-foreground font-semibold py-2.5 px-10 rounded-lg shadow hover:bg-primary/90 transition-all active:scale-[0.98] flex items-center justify-center gap-2">
              {isLoginLoading ? <><Loader2 className="w-4 h-4 animate-spin"/> Signing In...</> : 'Sign In'}
            </button>
          </form>
        </div>

        {/* Toggle Container */}
        <div className={`absolute top-0 left-1/2 w-1/2 h-full overflow-hidden transition-all duration-700 ease-in-out z-[100] ${isRightPanelActive ? '-translate-x-full rounded-r-[150px] rounded-l-none' : 'rounded-l-[150px] rounded-r-none'}`}>
          <div className={`bg-primary relative -left-full h-full w-[200%] transform transition-all duration-700 ease-in-out text-primary-foreground ${isRightPanelActive ? 'translate-x-1/2' : 'translate-x-0'}`}>
            
            {/* Toggle Left */}
            <div className={`absolute w-1/2 h-full flex items-center justify-center flex-col px-10 text-center top-0 transition-all duration-700 ease-in-out ${isRightPanelActive ? 'translate-x-0' : '-translate-x-[200%]'}`}>
              <h1 className="text-3xl font-bold mb-4">Welcome Back!</h1>
              <p className="text-sm mb-8 px-4 leading-relaxed opacity-90">Enter your personal details to securely access your MedScope AI dashboard.</p>
              <button onClick={() => setIsRightPanelActive(false)} className="bg-transparent border-2 border-primary-foreground text-primary-foreground font-semibold py-2.5 px-10 rounded-lg shadow-sm hover:bg-primary-foreground/10 transition-colors">Sign In</button>
            </div>
            
            {/* Toggle Right */}
            <div className={`absolute w-1/2 h-full flex items-center justify-center flex-col px-10 text-center top-0 right-0 transition-all duration-700 ease-in-out ${isRightPanelActive ? 'translate-x-[200%]' : 'translate-x-0'}`}>
              <h1 className="text-3xl font-bold mb-4">Hello, Colleague!</h1>
              <p className="text-sm mb-8 px-4 leading-relaxed opacity-90">Register with your institutional details to access our digital microscopy analysis platform.</p>
              <button onClick={() => setIsRightPanelActive(true)} className="bg-transparent border-2 border-primary-foreground text-primary-foreground font-semibold py-2.5 px-10 rounded-lg shadow-sm hover:bg-primary-foreground/10 transition-colors">Sign Up</button>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}
