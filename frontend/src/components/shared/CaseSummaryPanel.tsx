import { X, Activity, ImageIcon, FileText, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export interface CaseData {
  id: string;
  date: string;
  patient: string;
  type: string;
  status: string;
  findings: string;
}

interface CaseSummaryPanelProps {
  data: CaseData | null;
  onClose: () => void;
}

export function CaseSummaryPanel({ data, onClose }: CaseSummaryPanelProps) {
  if (!data) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-background/80 z-40 fade-backdrop"
        onClick={onClose}
      />
      
      {/* Slide-over panel */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-card border-l border-border shadow-2xl flex flex-col slide-panel">
        <div className="flex items-center justify-between p-5 border-b border-border">
          <div>
            <h2 className="text-xl font-bold text-foreground tracking-tight">Case {data.id}</h2>
            <p className="text-sm text-muted-foreground mt-0.5">{data.date}</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-muted-foreground hover:bg-muted hover:text-foreground rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Status & Patient Info */}
          <div className="grid grid-cols-2 gap-y-4 gap-x-2">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Patient</span>
              <p className="font-medium text-sm text-foreground">{data.patient}</p>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Type</span>
              <p className="font-medium text-sm text-foreground">{data.type}</p>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Status</span>
              <div className="flex items-center gap-1.5 mt-0.5">
                <div className={`w-1.5 h-1.5 rounded-full ${data.status === 'Completed' ? 'bg-green-500' : 'bg-warning'}`}></div>
                <span className="font-medium text-foreground text-sm">{data.status}</span>
              </div>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">AI Findings</span>
              <div className="mt-0.5">
                <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                  data.findings.includes('Abnormal') ? 'bg-destructive/10 text-destructive' :
                  data.findings.includes('Normal') ? 'bg-green-500/10 text-green-500' :
                  'bg-warning/10 text-warning'
                }`}>
                  {data.findings}
                </span>
              </div>
            </div>
          </div>

          {/* Slide Preview Mockup */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
              <ImageIcon className="w-4 h-4 text-muted-foreground" />
              Slide Overview
            </h3>
            <div className="aspect-[16/9] bg-muted/30 rounded-lg border border-border flex items-center justify-center relative overflow-hidden group">
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-white text-sm font-medium">Click to open full viewer</span>
              </div>
              <Activity className="w-8 h-8 text-muted-foreground/30" />
            </div>
          </div>

          {/* AI Report Summary Mockup */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-muted-foreground" />
              Automated Summary
            </h3>
            <div className="bg-muted/30 rounded-lg p-3.5 border border-border text-sm text-foreground/80 leading-relaxed">
              {data.findings.includes('Abnormal') 
                ? "The AI model detected high-confidence anomalies consistent with atypical cell structures. Two distinct regions were flagged for immediate pathologist review. Nuclear pleomorphism is prominent."
                : "The analysis completed successfully. No significant anomalies were detected by the model. Cell morphology appears within normal limits for the specified specimen type."}
            </div>
          </div>
        </div>

        <div className="p-5 border-t border-border bg-muted/10">
          <Link 
            href="/analyze" 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center justify-center gap-2"
          >
            Open in Analyze Workspace
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </>
  );
}
