"use client";

import dynamic from 'next/dynamic';

const Hero3D = dynamic(() => import('@/components/marketing/Hero3D'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[500px] flex items-center justify-center bg-[#050508]">
      <div className="animate-pulse flex flex-col items-center">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-indigo-400 font-mono text-sm">Initializing WebGL Engine...</p>
      </div>
    </div>
  )
});

export default function DynamicHero3D() {
  return <Hero3D />;
}
