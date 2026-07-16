'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useActiveImageStore } from '@/store/activeImageStore';
import { Maximize2, ZoomIn, ZoomOut, Hand, MousePointer2, SlidersHorizontal, Map, Ruler, UploadCloud, Microscope, AlertTriangle } from 'lucide-react';
import { analyzeImage } from '@/lib/api';

const PIPELINE_STAGES = [
  'Upload',
  'Quality Check',
  'YOLOv11 Detection',
  'Swin Classification',
  'Report Ready'
];

export function ImageViewer() {
  const { imageUrl, setImageUrl, isExplainabilityMode } = useActiveImageStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [activeTool, setActiveTool] = useState<'pan' | 'select'>('select');
  const [pipelineStage, setPipelineStage] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Simulated drag/drop
  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (!file) return;

    // Display local preview
    const localUrl = URL.createObjectURL(file);
    setImageUrl(localUrl);
    
    setIsAnalyzing(true);
    setPipelineStage(1); // Upload / Quality Check
    
    try {
      // Hardcoded patient for demo purposes (would normally be selected via UI)
      const result = await analyzeImage(file, "P-8472", "Blood Smear");
      
      // Simulate stepping through stages for visual feedback since backend is fast
      setPipelineStage(2); // YOLO
      await new Promise(r => setTimeout(r, 800));
      setPipelineStage(3); // Swin
      await new Promise(r => setTimeout(r, 800));
      setPipelineStage(4); // Report
      
      console.log("Analysis Result:", result);
      // Here we would normally store the result in a Zustand store
      // so other components (like Copilot) can access it
    } catch (error) {
      console.error("Failed to analyze image:", error);
      alert("Failed to analyze image. Please ensure the backend is running.");
    } finally {
      setIsAnalyzing(false);
    }
  }, [setImageUrl]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !imageUrl) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw dummy cell background
    ctx.fillStyle = '#1e1e2f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Only draw annotations if we are past detection phase
    if (pipelineStage >= 3) {
      // Draw simulated bounding box
      ctx.strokeStyle = '#ef4444'; // destructive
      ctx.lineWidth = 2;
      ctx.strokeRect(100, 100, 150, 150);
      
      // Draw label
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(100, 80, 150, 20);
      ctx.fillStyle = '#fff';
      ctx.font = '12px sans-serif';
      ctx.fillText('Abnormal Blast - 98%', 105, 94);
    }
  }, [imageUrl, isExplainabilityMode, pipelineStage]);

  return (
    <div className="flex flex-col h-full bg-card rounded-xl overflow-hidden border border-border shadow-sm relative">
      {imageUrl ? (
        <>
          {/* Clinical Viewer Toolbar */}
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1 bg-card/90 backdrop-blur-md border border-border p-1.5 rounded-lg shadow-md">
            <button 
              onClick={() => setActiveTool('select')}
              className={`p-2 rounded-md transition-all active:scale-95 ${activeTool === 'select' ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
              title="Select / Edit Annotations"
            >
              <MousePointer2 className="w-4 h-4" />
            </button>
            <button 
              onClick={() => setActiveTool('pan')}
              className={`p-2 rounded-md transition-all active:scale-95 ${activeTool === 'pan' ? 'bg-primary/20 text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
              title="Pan Tool"
            >
              <Hand className="w-4 h-4" />
            </button>
            <div className="w-px h-6 bg-border mx-1"></div>
            <button className="p-2 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-all active:scale-95" title="Zoom Out">
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs font-medium text-foreground w-12 text-center" style={{ fontFeatureSettings: '"tnum"' }}>100%</span>
            <button className="p-2 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-all active:scale-95" title="Zoom In">
              <ZoomIn className="w-4 h-4" />
            </button>
            <div className="w-px h-6 bg-border mx-1"></div>
            <button className="p-2 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-all active:scale-95" title="Image Adjustments (Brightness/Contrast)">
              <SlidersHorizontal className="w-4 h-4" />
            </button>
            <button className="p-2 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-all active:scale-95" title="Toggle Scale/Ruler">
              <Ruler className="w-4 h-4" />
            </button>
            <button className="p-2 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-all active:scale-95" title="Toggle Minimap">
              <Map className="w-4 h-4" />
            </button>
          </div>

          {/* Scale Bar Overlay */}
          <div className="absolute bottom-16 right-4 z-10 bg-black/50 backdrop-blur-sm px-3 py-1 rounded text-[10px] text-white font-mono border border-white/20 flex flex-col items-center">
            <div className="w-24 h-px bg-white mb-1 relative">
              <div className="absolute left-0 top-0 w-px h-1.5 -translate-y-1/2 bg-white"></div>
              <div className="absolute right-0 top-0 w-px h-1.5 -translate-y-1/2 bg-white"></div>
            </div>
            100 µm
          </div>

          <div className={`relative w-full h-full flex items-center justify-center overflow-hidden ${activeTool === 'pan' ? 'cursor-grab' : 'cursor-crosshair'}`}>
            <canvas
              ref={canvasRef}
              className="w-full h-full object-contain"
              width={1600}
              height={1200}
            />
          </div>

          {/* AI Pipeline Stepper */}
          <div className="absolute bottom-0 left-0 right-0 border-t border-border bg-card/95 backdrop-blur px-6 py-3 flex items-center justify-between" aria-live="polite">
            <div className="flex items-center gap-2 flex-1">
              {PIPELINE_STAGES.map((stage, idx) => (
                <div key={stage} className="flex items-center gap-2 flex-1">
                  <div className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold transition-all duration-300 ${
                    idx < pipelineStage ? 'bg-green-500/20 text-green-500' :
                    idx === pipelineStage ? (isAnalyzing ? 'bg-primary text-primary-foreground shadow-[0_0_15px_rgba(0,0,0,0.3)] animate-pulse scale-110' : 'bg-primary text-primary-foreground') :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {idx + 1}
                  </div>
                  <span className={`text-xs font-medium whitespace-nowrap ${idx <= pipelineStage ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {stage}
                  </span>
                  {idx < PIPELINE_STAGES.length - 1 && (
                    <div className={`flex-1 h-px mx-2 ${idx < pipelineStage ? 'bg-green-500/50' : 'bg-border'}`}></div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div 
          className="flex flex-col items-center justify-center h-full text-muted-foreground p-8"
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
        >
          <div className={`w-full max-w-xl aspect-video rounded-xl border-2 border-dashed flex flex-col items-center justify-center p-8 transition-all duration-300 ${
            isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-border bg-muted/20 hover:border-primary/50'
          }`}>
            <div className="w-20 h-20 bg-card rounded-full shadow-sm flex items-center justify-center mb-6 relative group">
              <div className="absolute inset-0 bg-primary/20 rounded-full scale-0 group-hover:scale-150 transition-transform duration-500 opacity-0 group-hover:opacity-100"></div>
              <div className="absolute inset-0 border-2 border-primary/30 rounded-full animate-ping opacity-20"></div>
              <Microscope className="w-10 h-10 text-primary relative z-10 hover-lift" />
            </div>
            
            <h3 className="text-xl font-semibold text-foreground mb-2">Upload Slide for Analysis</h3>
            <p className="text-sm text-center mb-6 max-w-sm">
              Drag and drop an image file here, or click to browse. Supported formats: .svs, .tif, .ndpi, .png, .jpg
            </p>
            
            <button className="bg-card border border-border hover:bg-muted text-foreground px-6 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2">
              <UploadCloud className="w-4 h-4" />
              Browse Files
            </button>
            
            <div className="mt-8 flex items-center gap-2 text-xs text-warning bg-warning/10 px-3 py-1.5 rounded-full">
              <AlertTriangle className="w-3.5 h-3.5" />
              Max file size: 2GB per slide
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
