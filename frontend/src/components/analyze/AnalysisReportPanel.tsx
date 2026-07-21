'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { X, FileText, AlertTriangle, CheckCircle2, Microscope, Images } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { AnalysisResponse, SimilarCase, getSimilarCases } from '@/lib/api';

interface AnalysisReportPanelProps {
  result: AnalysisResponse;
  onClose: () => void;
}

const markdownComponents = {
  p: (props: React.ComponentPropsWithoutRef<'p'>) => <p className="leading-relaxed mb-2 last:mb-0" {...props} />,
  strong: (props: React.ComponentPropsWithoutRef<'strong'>) => <strong className="font-bold text-foreground" {...props} />,
  ul: (props: React.ComponentPropsWithoutRef<'ul'>) => <ul className="list-disc pl-4 mb-2 space-y-0.5" {...props} />,
  ol: (props: React.ComponentPropsWithoutRef<'ol'>) => <ol className="list-decimal pl-4 mb-2 space-y-0.5" {...props} />,
  li: (props: React.ComponentPropsWithoutRef<'li'>) => <li className="leading-relaxed" {...props} />,
  h1: (props: React.ComponentPropsWithoutRef<'h1'>) => <h1 className="font-bold text-base mt-3 mb-1 first:mt-0" {...props} />,
  h2: (props: React.ComponentPropsWithoutRef<'h2'>) => <h2 className="font-bold text-sm mt-3 mb-1 first:mt-0" {...props} />,
  h3: (props: React.ComponentPropsWithoutRef<'h3'>) => <h3 className="font-bold text-sm mt-3 mb-1 first:mt-0" {...props} />,
};

export function AnalysisReportPanel({ result, onClose }: AnalysisReportPanelProps) {
  const isAbnormal = result.prediction?.toLowerCase() === 'malaria';
  const isLowConfidence = result.confidence < 70;
  const isAtypical = result.image_typicality != null && result.image_typicality < 0.5;

  const [similarCases, setSimilarCases] = useState<SimilarCase[]>([]);

  useEffect(() => {
    let cancelled = false;
    getSimilarCases(result.sample_id)
      .then((cases) => { if (!cancelled) setSimilarCases(cases); })
      .catch((err) => console.error('Failed to fetch similar cases:', err));
    return () => { cancelled = true; };
  }, [result.sample_id]);

  return (
    <>
      <div
        className="fixed inset-0 bg-background/80 z-40"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-card border-l border-border shadow-2xl flex flex-col">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <div>
            <h2 className="text-xl font-bold text-foreground tracking-tight">Analysis Report</h2>
            <p className="text-sm text-muted-foreground mt-0.5">Sample {result.sample_id}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-muted-foreground hover:bg-muted hover:text-foreground rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Prediction banner */}
          <div className={`flex items-center gap-3 p-4 rounded-lg border ${
            isLowConfidence
              ? 'bg-muted/30 border-border'
              : isAbnormal ? 'bg-destructive/10 border-destructive/30' : 'bg-green-500/10 border-green-500/30'
          }`}>
            {isLowConfidence
              ? <AlertTriangle className="w-6 h-6 text-muted-foreground shrink-0" />
              : isAbnormal
                ? <AlertTriangle className="w-6 h-6 text-destructive shrink-0" />
                : <CheckCircle2 className="w-6 h-6 text-green-600 shrink-0" />}
            <div>
              <p className="font-bold text-foreground">
                {result.prediction}
                {isLowConfidence && <span className="font-normal text-muted-foreground"> — low confidence, not conclusive</span>}
              </p>
              <p className="text-xs text-muted-foreground">
                Confidence: {result.confidence.toFixed(1)}%
                {result.uncertainty != null ? ` · Uncertainty: ${result.uncertainty.toFixed(1)}%` : ''}
              </p>
            </div>
          </div>

          {/* Key figures */}
          <div className="grid grid-cols-2 gap-y-4 gap-x-2">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Patient</span>
              <p className="font-medium text-sm text-foreground">{result.patient_id}</p>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Specimen</span>
              <p className="font-medium text-sm text-foreground">{result.specimen_type}</p>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Image Quality</span>
              <p className="font-medium text-sm text-foreground">{result.quality}</p>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Parasitemia</span>
              <p className="font-medium text-sm text-foreground">{result.parasitemia.toFixed(2)}%</p>
            </div>
            <div className="space-y-1 col-span-2">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Cell Count</span>
              <p className="font-medium text-sm text-foreground">{result.infected_cells} infected / {result.total_cells} total</p>
            </div>
          </div>

          {result.total_cells === 0 && (
            <div className="flex items-center gap-2 text-xs font-medium text-destructive bg-destructive/10 border border-destructive/30 px-3 py-2 rounded-md">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              Cell detection found nothing on this image — parasitemia could not be measured. Treat this as inconclusive, not a negative result.
            </div>
          )}

          {result.review_required && (
            <div className="flex items-center gap-2 text-xs font-medium text-warning bg-warning/10 border border-warning/30 px-3 py-2 rounded-md">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              Flagged for pathologist review
            </div>
          )}

          {isAtypical && (
            <div className="flex items-center gap-2 text-xs font-medium text-warning bg-warning/10 border border-warning/30 px-3 py-2 rounded-md">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              This image looks visually unusual compared to previously processed cases (typicality: {(result.image_typicality! * 100).toFixed(0)}%) — results may be less reliable.
            </div>
          )}

          {/* Report text */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-muted-foreground" />
              Clinical Copilot Report
            </h3>
            <div className="bg-muted/30 rounded-lg p-3.5 border border-border text-sm text-foreground/80">
              <ReactMarkdown components={markdownComponents}>{result.report}</ReactMarkdown>
            </div>
          </div>

          {/* Similar Cases */}
          {similarCases.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                <Images className="w-4 h-4 text-muted-foreground" />
                Similar Past Cases
              </h3>
              <div className="space-y-1.5">
                {similarCases.map((c) => (
                  <Link
                    key={c.sample_id}
                    href={`/dashboard/analyze/${encodeURIComponent(c.sample_id)}`}
                    className="flex items-center justify-between text-sm bg-muted/30 hover:bg-muted/60 border border-border rounded-md px-3 py-2 transition-colors"
                  >
                    <div className="min-w-0">
                      <p className="font-medium text-foreground truncate">{c.sample_id}</p>
                      <p className="text-xs text-muted-foreground">
                        {c.prediction} · Patient {c.patient_id} · {c.parasitemia.toFixed(1)}% parasitemia
                      </p>
                    </div>
                    <span className="shrink-0 text-xs font-mono text-muted-foreground ml-2">
                      {(c.similarity * 100).toFixed(0)}%
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Model versions */}
          {result.model_versions && Object.keys(result.model_versions).length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                <Microscope className="w-4 h-4 text-muted-foreground" />
                Models Used
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(result.model_versions).map(([key, val]) => (
                  <span
                    key={key}
                    className="text-[10px] font-mono bg-muted/50 border border-border rounded px-1.5 py-0.5 text-muted-foreground"
                  >
                    {key}: {val}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
