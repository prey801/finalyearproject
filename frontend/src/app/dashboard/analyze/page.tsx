'use client';

import { useEffect, useState } from 'react';
import { ImageViewer } from '@/components/viewer/ImageViewer';
import { CopilotChat } from '@/components/chat/CopilotChat';
import { AnalysisReportPanel } from '@/components/analyze/AnalysisReportPanel';
import { useActiveImageStore } from '@/store/activeImageStore';

export default function AnalyzePage() {
  const { analysisResult } = useActiveImageStore();
  const [showReport, setShowReport] = useState(false);

  // Auto-open the report panel as soon as a new analysis result lands
  useEffect(() => {
    if (analysisResult) setShowReport(true);
  }, [analysisResult]);

  return (
    <div className="h-full p-4 bg-background">
      {/*
        Grid layout:
        - lg (1024px+): 1fr (Viewer) + 320px (Chat)
        - xl (1280px+): 1fr (Viewer) + 380px (Chat)
        - Below lg: Chat collapses or moves below (for now we hide it or stack it, but in clinical apps, 1024px is min)
      */}
      <div className="flex flex-col lg:grid lg:grid-cols-[1fr_320px] xl:grid-cols-[1fr_380px] gap-4 h-full">
        <div className="h-[50vh] lg:h-full min-w-0 flex flex-col relative z-10">
          <ImageViewer />
        </div>
        <div className="h-[50vh] lg:h-full shrink-0 flex flex-col bg-card rounded-xl border border-border shadow-sm overflow-hidden">
          <CopilotChat />
        </div>
      </div>

      {showReport && analysisResult && (
        <AnalysisReportPanel result={analysisResult} onClose={() => setShowReport(false)} />
      )}
    </div>
  );
}
