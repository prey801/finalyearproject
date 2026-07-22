'use client';

import { use, useEffect, useState } from 'react';
import { ImageViewer } from '@/components/viewer/ImageViewer';
import { CopilotChat } from '@/components/chat/CopilotChat';
import { AnalysisReportPanel } from '@/components/analyze/AnalysisReportPanel';
import { useActiveImageStore } from '@/store/activeImageStore';
import { getAnalysisById, fetchImageAsBlobUrl } from '@/lib/api';

// Dedicated route for reopening a past case (from History/Dashboard/similar
// cases). Kept separate from /dashboard/analyze, which is always a fresh
// "New Analysis" workspace — so neither page has to guess the other's intent.
export default function CaseReportPage({ params }: { params: Promise<{ sampleId: string }> }) {
  const { sampleId } = use(params);
  const { analysisResult, setAnalysisResult, setImageUrl, setExplainabilityMode } = useActiveImageStore();
  const [showReport, setShowReport] = useState(true);

  useEffect(() => {
    let blobUrl: string | null = null;
    let cancelled = false;

    // The GradCAM toggle is global store state and would otherwise carry
    // over from whatever case was viewed previously, silently opening this
    // one in heatmap mode (and hiding its detection boxes) before the user
    // ever touches the toggle.
    setExplainabilityMode(false);

    getAnalysisById(sampleId)
      .then(async (result) => {
        if (cancelled) return;
        setAnalysisResult(result);
        setShowReport(true);

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
  }, [sampleId, setAnalysisResult, setImageUrl, setExplainabilityMode]);

  return (
    <div className="h-full p-4 bg-background">
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
