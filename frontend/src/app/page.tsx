"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Microscope, Activity, BrainCircuit, Eraser } from 'lucide-react';
import { RoughNotation, RoughNotationGroup } from 'react-rough-notation';
import { motion } from 'framer-motion';

export default function MarketingLandingPage() {
  const [showNotes, setShowNotes] = useState(false);
  const [drawKey, setDrawKey] = useState(0);
  const [isErasing, setIsErasing] = useState(false);

  useEffect(() => {
    // Show base annotations
    const timer = setTimeout(() => setShowNotes(true), 500);
    
    // Loop the circle animation every 8 seconds
    const loopTimer = setInterval(() => {
      setIsErasing(true); // Start the eraser animation
      
      // After 1.5s (when the eraser is done), reset and redraw
      setTimeout(() => {
        setIsErasing(false);
        setDrawKey(prev => prev + 1);
      }, 1500);
    }, 8000);

    return () => {
      clearTimeout(timer);
      clearInterval(loopTimer);
    };
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-cyan-200/50 relative overflow-hidden">
      {/* Dynamic Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#06b6d4]/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-pink-400/20 blur-[120px] rounded-full pointer-events-none"></div>
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b-2 border-foreground/10 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Microscope className="w-8 h-8 text-foreground" />
            <span className="text-xl font-heading font-bold tracking-tight text-foreground">MedScope AI</span>
          </div>
          <div className="flex items-center gap-8">
            <Link href="#features" className="text-sm font-medium hover:underline decoration-2 underline-offset-4">Features</Link>
            <Link href="/auth" className="px-6 py-2 rounded-full font-medium transition-all border-2 border-foreground bg-primary text-primary-foreground shadow-[3px_3px_0px_theme(colors.foreground)] hover:-translate-y-0.5 hover:shadow-[5px_5px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)]">
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden flex flex-col items-center justify-center text-center">
        <div className="max-w-4xl mx-auto px-6 relative z-10 space-y-8 flex flex-col items-center">
          
            <h1 className="text-5xl lg:text-7xl font-heading font-extrabold tracking-tight text-foreground leading-[1.1] max-w-3xl">
              Universal Clinical Decision Support for{' '}
              <span className="relative inline-block">
                
                {/* The Drawn Circle */}
                <span key={drawKey} className={`absolute inset-0 pointer-events-none flex items-center justify-center transition-opacity duration-1000 ${isErasing ? 'opacity-0' : 'opacity-100'}`}>
                  <RoughNotation 
                    show={showNotes}
                    type="circle" 
                    color="#06b6d4" 
                    strokeWidth={3} 
                    padding={[-5, 15, 5, 15]}
                    iterations={4}
                    animationDuration={2000}
                  >
                    <span className="opacity-0">Microscopy</span>
                  </RoughNotation>
                </span>

                {/* The Eraser Animation */}
                {isErasing && (
                  <motion.div
                    initial={{ opacity: 0, x: -80, y: 0 }}
                    animate={{ 
                      opacity: [0, 1, 1, 1, 0],
                      x: [-80, -40, 0, 40, 80],
                      y: [0, -20, 20, -20, 0],
                      rotate: [0, -15, 15, -15, 0]
                    }}
                    transition={{ duration: 1.5, ease: "easeInOut" }}
                    className="absolute top-1/2 left-1/2 z-20 text-foreground pointer-events-none"
                    style={{ marginTop: '-24px', marginLeft: '-24px' }}
                  >
                    <Eraser size={48} className="text-foreground fill-background" />
                  </motion.div>
                )}

                {/* Actual visible text */}
                <span className="relative z-10">Microscopy</span>
              </span>
              .
            </h1>
          
          <p className="text-xl font-sans text-foreground/80 leading-relaxed max-w-2xl mt-8">
            Unlock faster, more accurate diagnoses. MedScope AI uses state-of-the-art vision models to detect, segment, and classify anomalies across ANY microscopy-based disease pipeline.
          </p>
          
          <div className="relative mt-12 flex flex-col items-center">
            <Link href="/auth" className="px-8 py-4 rounded-full bg-[#06b6d4] text-foreground font-bold text-lg transition-all border-2 border-foreground shadow-[4px_4px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[6px_6px_0px_theme(colors.foreground)] active:translate-y-1 active:translate-x-1 active:shadow-[0px_0px_0px_theme(colors.foreground)] flex items-center gap-2">
              Start Your Journey
            </Link>
            
            {/* Playful Note Arrow */}
            <div className={`absolute -right-32 top-0 transform rotate-12 transition-opacity duration-1000 delay-1000 ${showNotes ? 'opacity-100' : 'opacity-0'}`}>
              <svg width="60" height="60" viewBox="0 0 100 100" className="text-foreground -rotate-45" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10,90 Q40,10 90,50" />
                <path d="M70,40 L90,50 L80,70" />
              </svg>
              <div className="font-heading font-bold text-xl text-foreground transform rotate-12 mt-2">
                It's free!
              </div>
            </div>
          </div>
          
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-32 relative bg-foreground/5 border-t-2 border-foreground/10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20 flex flex-col items-center">
            <h2 className="text-4xl lg:text-5xl font-heading font-bold text-foreground mb-6">
              The Intelligent{' '}
              <RoughNotation type="underline" show={showNotes} color="#06b6d4" strokeWidth={4} padding={[0, 0]}>
                Pipeline
              </RoughNotation>
            </h2>
            <p className="text-foreground/70 max-w-2xl mx-auto text-lg font-sans">
              A seamless workflow from slide ingestion to explainable clinical insights. Built for precision.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Microscope className="w-8 h-8 text-foreground" />}
              title="Universal Detection"
              description="Not just Malaria. Our models are trained to isolate and detect anomalies across blood smears, tissue biopsies, and more."
            />
            <FeatureCard 
              icon={<Activity className="w-8 h-8 text-foreground" />}
              title="Precise Segmentation"
              description="Pixel-perfect boundary mapping. Isolate the exact shape and size of infected cells or tumors with our advanced U-Net architectures."
            />
            <FeatureCard 
              icon={<BrainCircuit className="w-8 h-8 text-foreground" />}
              title="Explainable Copilot"
              description="AI isn't a black box anymore. See exactly why the model made a decision with SHAP and Grad-CAM visual overlays."
            />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-32 relative bg-background z-10">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-heading font-bold text-foreground mb-6">
              Common Questions
            </h2>
            <p className="text-foreground/70 text-lg font-sans">
              Everything you need to know about the product and billing.
            </p>
          </div>
          <div className="space-y-6">
            <div className="p-8 rounded-3xl bg-background border-2 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_theme(colors.foreground)] transition-all">
              <h3 className="text-xl font-heading font-bold text-foreground mb-3">Is it actually free?</h3>
              <p className="text-foreground/70 font-sans">Yes! For academic and personal research use, the base pipeline is completely free. We offer enterprise plans for high-throughput clinical deployment.</p>
            </div>
            <div className="p-8 rounded-3xl bg-background border-2 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_theme(colors.foreground)] transition-all">
              <h3 className="text-xl font-heading font-bold text-foreground mb-3">Does it only detect Malaria?</h3>
              <p className="text-foreground/70 font-sans">No. While we started with Malaria, our U-Net architectures and classification models are trained to detect anomalies across a wide range of blood smears and biopsies.</p>
            </div>
            <div className="p-8 rounded-3xl bg-background border-2 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_theme(colors.foreground)] transition-all">
              <h3 className="text-xl font-heading font-bold text-foreground mb-3">How does the explainable AI work?</h3>
              <p className="text-foreground/70 font-sans">We use Grad-CAM and SHAP values to overlay a heatmap on the slide, showing you the exact pixels that led our model to its diagnosis.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t-2 border-foreground/10 bg-foreground/5 relative z-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <Microscope className="w-6 h-6 text-foreground" />
            <span className="text-lg font-heading font-bold tracking-tight text-foreground">MedScope AI</span>
          </div>
          <div className="flex items-center gap-6 text-sm font-sans font-medium text-foreground/70">
            <Link href="/privacy" className="hover:text-foreground transition-colors">Privacy Policy</Link>
            <Link href="/terms" className="hover:text-foreground transition-colors">Terms of Service</Link>
            <Link href="/contact" className="hover:text-foreground transition-colors">Contact</Link>
          </div>
          <div className="text-sm text-foreground/50 font-sans">
            © {new Date().getFullYear()} MedScope AI. All rights reserved.
          </div>
        </div>
      </footer>

    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-8 rounded-3xl bg-background border-2 border-foreground shadow-[6px_6px_0px_theme(colors.foreground)] hover:-translate-y-1 hover:shadow-[8px_8px_0px_theme(colors.foreground)] transition-all flex flex-col items-start">
      <div className="w-16 h-16 rounded-2xl bg-[#06b6d4]/20 border-2 border-foreground flex items-center justify-center mb-6">
        {icon}
      </div>
      <h3 className="text-2xl font-heading font-bold text-foreground mb-3">{title}</h3>
      <p className="text-foreground/70 leading-relaxed font-sans">{description}</p>
    </div>
  );
}
