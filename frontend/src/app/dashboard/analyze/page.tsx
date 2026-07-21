'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { ImageViewer } from '@/components/viewer/ImageViewer';
import { CopilotChat } from '@/components/chat/CopilotChat';
import { AnalysisReportPanel } from '@/components/analyze/AnalysisReportPanel';
import { useActiveImageStore } from '@/store/activeImageStore';
import { getAnalysisById, fetchImageAsBlobUrl } from '@/lib/api';

export default function AnalyzePage() {
  return (
    <Suspense fallback={null}>
      <AnalyzePageInner />
    </Suspense>
  );
}

function AnalyzePageInner() {
  const { analysisResult, setAnalysisResult, setImageUrl } = useActiveImageStore();
  const [showReport, setShowReport] = useState(false);
  const searchParams = useSearchParams();
  const sampleId = searchParams.get('sample');

  // "New Analysis" (no ?sample= in the URL): the workspace store is global
  // and outlives navigation, so without this a fresh visit would keep
  // showing whatever case was last open instead of the upload/camera screen.
  useEffect(() => {
    if (sampleId) return;
    setAnalysisResult(null);
    setImageUrl(null);
    setShowReport(false);
  }, [sampleId, setAnalysisResult, setImageUrl]);

  // Reopening a past case from History/Dashboard: load its real result
  // (and slide image, if one was persisted) into the workspace so the
  // report panel and Copilot chat both have full context.
  useEffect(() => {
    if (!sampleId) return;
    let blobUrl: string | null = null;
    let cancelled = false;

    getAnalysisById(sampleId)
      .then(async (result) => {
        if (cancelled) return;
        setAnalysisResult(result);

        if (!result.image_path) {
          setImageUrl(null);
          return;
        }
        try {
          blobUrl = await fetchImageAsBlobUrl(result.image_path);
          if (!cancelled) setImageUrl(blobUrl);
        } catch (err) {
          console.error(`Failed to load slide image for ${sampleId}:`, err);
          if (!cancelled) setImageUrl(null);
        }
      })
      .catch((err) => {
        console.error(`Failed to load case ${sampleId}:`, err);
        alert(`Could not load case ${sampleId}. It may have been deleted.`);
      });

    return () => {
      cancelled = true;
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [sampleId, setAnalysisResult, setImageUrl]);

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
