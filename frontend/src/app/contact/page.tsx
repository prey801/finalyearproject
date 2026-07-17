import Link from 'next/link';
import { Mail, MessageSquare } from 'lucide-react';

export default function Contact() {
  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden py-32 px-6">
      {/* Dynamic Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#06b6d4]/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-pink-400/20 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Back to Home Button */}
      <Link href="/" className="absolute top-8 left-8 z-[200] flex items-center gap-2 px-5 py-2.5 rounded-full border-2 border-foreground bg-background text-foreground font-medium shadow-[3px_3px_0px_theme(colors.foreground)] hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] transition-all">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        Back to Home
      </Link>

      <div className="max-w-3xl mx-auto relative z-10 bg-card/60 backdrop-blur-xl border border-border/50 rounded-3xl shadow-2xl p-12 text-center">
        <div className="w-16 h-16 bg-[#06b6d4]/20 border-2 border-foreground rounded-2xl flex items-center justify-center mx-auto mb-6">
          <MessageSquare className="w-8 h-8 text-foreground" />
        </div>
        <h1 className="text-4xl font-heading font-bold mb-6">Get in Touch</h1>
        <p className="text-lg font-sans text-foreground/80 mb-12">
          Have questions about our pipeline, enterprise plans, or academic research partnerships? We'd love to hear from you.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-6">
          <a href="mailto:support@medscope.ai" className="px-8 py-4 rounded-full bg-primary text-primary-foreground font-bold text-lg transition-all border-2 border-foreground shadow-[4px_4px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] flex items-center justify-center gap-2">
            <Mail className="w-5 h-5" />
            support@medscope.ai
          </a>
        </div>
      </div>
    </div>
  );
}
