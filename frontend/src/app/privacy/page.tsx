'use client';

import Link from 'next/link';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background text-foreground relative overflow-hidden">
      {/* Dynamic Background Gradients */}
      <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#06b6d4]/10 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-pink-400/10 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Back to Home Button */}
      <Link href="/" className="fixed top-8 left-8 z-[200] flex items-center gap-2 px-5 py-2.5 rounded-full border-2 border-foreground bg-background text-foreground font-medium shadow-[3px_3px_0px_theme(colors.foreground)] hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] transition-all">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        Back to Home
      </Link>

      <div className="max-w-6xl mx-auto px-6 pt-32 pb-24 relative z-10">
        <header className="mb-16">
          <h1 className="text-5xl lg:text-7xl font-heading font-extrabold tracking-tight mb-4">
            Privacy Policy
          </h1>
          <p className="text-xl font-sans text-foreground/60 font-medium">
            Effective Date: {new Date().toLocaleDateString()}
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          
          {/* Sticky Table of Contents Sidebar */}
          <aside className="lg:col-span-4 sticky top-12 hidden md:block">
            <div className="p-8 rounded-3xl bg-background border-2 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)]">
              <h3 className="font-heading font-bold text-2xl mb-6">Contents</h3>
              <nav className="flex flex-col gap-3 font-sans font-medium text-foreground/70">
                <a href="#information" className="hover:text-foreground hover:translate-x-1 transition-all">1. Information We Collect</a>
                <a href="#compliance" className="hover:text-foreground hover:translate-x-1 transition-all">2. Healthcare Compliance</a>
                <a href="#sharing" className="hover:text-foreground hover:translate-x-1 transition-all">3. Data Sharing</a>
                <a href="#rights" className="hover:text-foreground hover:translate-x-1 transition-all">4. Your Rights</a>
              </nav>
            </div>
          </aside>

          {/* Long-form Content Column */}
          <article className="lg:col-span-8 font-sans text-lg text-foreground/80 leading-loose space-y-12">
            
            <section id="information" className="scroll-mt-32">
              <h2 className="text-3xl font-heading font-bold text-foreground mb-6">1. Information We Collect</h2>
              <p className="mb-4">
                At MedScope AI, we believe in minimizing data collection to only what is strictly necessary to run our models securely and effectively. We collect two primary categories of information:
              </p>
              <ul className="list-disc pl-6 space-y-2 mb-4">
                <li><strong className="text-foreground">Account Data:</strong> We collect information you provide directly to us when you register for an account, such as your name, institutional email address, and authentication credentials.</li>
                <li><strong className="text-foreground">Clinical Data:</strong> Microscopic slide images, metadata, and user-provided annotations uploaded during your workflow. All clinical data is strictly anonymized before processing.</li>
                <li><strong className="text-foreground">Usage Data:</strong> Telemetry on how our explainability features (such as SHAP visual overlays) are used. This helps us refine our UI/UX and algorithmic transparency.</li>
              </ul>
            </section>

            <section id="compliance" className="scroll-mt-32">
              <h2 className="text-3xl font-heading font-bold text-foreground mb-6">2. Healthcare Compliance & HIPAA</h2>
              <p className="mb-4">
                We handle medical imagery, meaning we adhere to the strictest healthcare compliance frameworks. MedScope AI employs end-to-end encryption for all data in transit and at rest.
              </p>
              <p className="mb-4">
                Before any image reaches our inference servers, our ingestion pipeline strips all Protected Health Information (PHI) from DICOM headers and image metadata. For Enterprise clinical deployment, we offer fully executed Business Associate Agreements (BAAs).
              </p>
            </section>

            <section id="sharing" className="scroll-mt-32">
              <h2 className="text-3xl font-heading font-bold text-foreground mb-6">3. Data Sharing & Third Parties</h2>
              <p className="mb-4">
                Your data is your data. <strong>We do not sell your data.</strong> 
              </p>
              <p className="mb-4">
                We only share data with essential infrastructure providers (such as secure cloud hosting environments) under strict confidentiality agreements. For free or academic users, heavily anonymized image patches may be used to further train our universal detection models, ensuring the global medical community benefits from collective intelligence.
              </p>
            </section>

            <section id="rights" className="scroll-mt-32">
              <h2 className="text-3xl font-heading font-bold text-foreground mb-6">4. Your Rights</h2>
              <p className="mb-4">
                You retain complete control over your account. At any time, you may request a complete export of your uploaded data, annotations, and generated heatmaps. 
              </p>
              <p>
                You may also request total account deletion, which physically purges your information from our active databases within 30 days. To exercise these rights, please contact our support team.
              </p>
            </section>

          </article>
        </div>
      </div>
    </div>
  );
}
