'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useActiveImageStore } from '@/store/activeImageStore';
import { Maximize2, ZoomIn, ZoomOut, Hand, MousePointer2, SlidersHorizontal, Map, Ruler, UploadCloud, Microscope, AlertTriangle, Camera } from 'lucide-react';
import { analyzeImage } from '@/lib/api';
import { X } from 'lucide-react';

const PIPELINE_STAGES = [
  'Upload',
  'Quality Check',
  'YOLOv11 Detection',
  'Swin Classification',
  'Report Ready'
];

const SPECIMEN_TYPES = ['Blood Smear', 'Tissue Section', 'Other'];

function generatePatientId() {
  return `P-${Math.floor(1000 + Math.random() * 9000)}`;
}

export function ImageViewer() {
  const { imageUrl, setImageUrl, isExplainabilityMode, analysisResult, setAnalysisResult } = useActiveImageStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [activeTool, setActiveTool] = useState<'pan' | 'select'>('select');
  const [pipelineStage, setPipelineStage] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [patientId, setPatientId] = useState(generatePatientId);
  const [specimenType, setSpecimenType] = useState(SPECIMEN_TYPES[0]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  // Camera State
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Stop camera helper
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  }, []);

  // Start camera helper
  const startCamera = async () => {
    // If running on insecure context (e.g., HTTP not localhost), getUserMedia might be undefined.
    // In that case, fallback to the native camera input.
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn("getUserMedia is not supported in this browser. Falling back to native camera input.");
      cameraInputRef.current?.click();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      streamRef.current = stream;
      setIsCameraActive(true);
      // Wait for React to render the video element, then attach the stream
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }, 50);
    } catch (err) {
      console.error("Error accessing camera:", err);
      // Fallback if permission is denied or no camera is found
      cameraInputRef.current?.click();
    }
  };

  // Clean up camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

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

    // Clear any previous case's result so the header/report don't show stale
    // data while this new slide is loading and being analyzed.
    setAnalysisResult(null);
    setFileName(file.name);

    // Display local preview then immediately revoke to avoid memory leak
    const localUrl = URL.createObjectURL(file);
    setImageUrl(localUrl);
    // Revoke the blob URL after a short delay — canvas will have rendered by then
    setTimeout(() => URL.revokeObjectURL(localUrl), 5000);

    setIsAnalyzing(true);
    setPipelineStage(1); // Upload / Quality Check

    try {
      const result = await analyzeImage(file, patientId, specimenType);

      // Simulate stepping through stages for visual feedback since backend is fast
      setPipelineStage(2); // YOLO
      await new Promise(r => setTimeout(r, 800));
      setPipelineStage(3); // Swin
      await new Promise(r => setTimeout(r, 800));
      setPipelineStage(4); // Report

      console.log("Analysis Result:", result);
      setAnalysisResult(result);
    } catch (error) {
      console.error("Failed to analyze image:", error);
      const message = error instanceof Error ? error.message : "Please ensure the backend is running.";
      alert(`Failed to analyze image: ${message}`);
    } finally {
      setIsAnalyzing(false);
    }
  }, [setImageUrl, setAnalysisResult, patientId, specimenType]);

  // Capture photo from video stream
  const capturePhoto = useCallback(() => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
          const syntheticEvent = {
            preventDefault: () => {},
            dataTransfer: { files: [file] }
          } as unknown as React.DragEvent;
          onDrop(syntheticEvent);
          stopCamera();
        }
      }, 'image/jpeg', 0.9);
    }
  }, [onDrop, stopCamera]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reuse the drop logic for file processing
    const syntheticEvent = {
      preventDefault: () => {},
      dataTransfer: { files: [file] }
    } as unknown as React.DragEvent;
    
    onDrop(syntheticEvent);
  }, [onDrop]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !imageUrl) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new window.Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#1e1e2f';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Fit the slide image to the canvas, preserving aspect ratio (letterbox)
      const canvasAspect = canvas.width / canvas.height;
      const imgAspect = img.width / img.height;
      let drawWidth: number, drawHeight: number, offsetX: number, offsetY: number;
      if (imgAspect > canvasAspect) {
        drawWidth = canvas.width;
        drawHeight = canvas.width / imgAspect;
        offsetX = 0;
        offsetY = (canvas.height - drawHeight) / 2;
      } else {
        drawHeight = canvas.height;
        drawWidth = canvas.height * imgAspect;
        offsetX = (canvas.width - drawWidth) / 2;
        offsetY = 0;
      }
      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);

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
    };
    img.onerror = () => {
      console.error('Failed to load slide image for preview:', imageUrl);
    };
    img.src = imageUrl;
  }, [imageUrl, isExplainabilityMode, pipelineStage]);

  return (
    <div className="flex flex-col h-full bg-card rounded-xl overflow-hidden border border-border shadow-sm relative">
      {imageUrl ? (
        <>
          {/* Slide Identity Bar — always visible so it's unambiguous which
              slide/patient is currently loaded, whether just uploaded,
              still analyzing, or showing a completed result. */}
          <div className="shrink-0 border-b border-border bg-card px-4 py-2 flex items-center justify-between text-sm z-10 relative">
            <div className="flex items-center gap-3 min-w-0">
              <Microscope className="w-4 h-4 text-primary shrink-0" />
              <span className="font-semibold text-foreground truncate">
                {analysisResult ? analysisResult.sample_id : (fileName || 'Untitled slide')}
              </span>
              <span className="text-muted-foreground">·</span>
              <span className="text-muted-foreground truncate">
                Patient {analysisResult ? analysisResult.patient_id : patientId}
              </span>
              <span className="text-muted-foreground">·</span>
              <span className="text-muted-foreground truncate">
                {analysisResult ? analysisResult.specimen_type : specimenType}
              </span>
            </div>
            {analysisResult && (
              <span className={`shrink-0 text-xs font-bold uppercase px-2 py-0.5 rounded-full ${
                analysisResult.prediction?.toLowerCase() === 'malaria'
                  ? 'bg-destructive/10 text-destructive'
                  : 'bg-green-500/10 text-green-600'
              }`}>
                {analysisResult.prediction}
              </span>
            )}
            {isAnalyzing && !analysisResult && (
              <span className="shrink-0 text-xs font-bold uppercase text-primary animate-pulse">
                Analyzing…
              </span>
            )}
          </div>

          {/* Image viewport — wraps toolbar/scale-bar/canvas/stepper so their
              `absolute` positioning is scoped here, below the identity bar,
              instead of the whole panel. */}
          <div className="relative flex-1 overflow-hidden">
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
          </div>
        </>
      ) : (
        <div 
          className="flex flex-col items-center justify-center h-full text-muted-foreground p-8"
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
        >
          {isCameraActive ? (
            <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-black/95">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                className="w-full max-h-[80%] object-contain"
              />
              <div className="absolute bottom-8 flex gap-4">
                <button 
                  onClick={stopCamera} 
                  className="bg-card/20 hover:bg-card/40 text-white border border-white/20 px-6 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2"
                >
                  <X className="w-4 h-4" />
                  Cancel
                </button>
                <button 
                  onClick={capturePhoto} 
                  className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2"
                >
                  <Camera className="w-5 h-5" />
                  Capture Photo
                </button>
              </div>
            </div>
          ) : (
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

            <div className="flex gap-3 mb-6 w-full max-w-sm" onClick={(e) => e.stopPropagation()}>
              <div className="flex-1">
                <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Patient ID</label>
                <input
                  type="text"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  className="w-full mt-1 px-2.5 py-1.5 text-sm bg-card border border-border rounded-md text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50"
                />
              </div>
              <div className="flex-1">
                <label className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Specimen Type</label>
                <select
                  value={specimenType}
                  onChange={(e) => setSpecimenType(e.target.value)}
                  className="w-full mt-1 px-2.5 py-1.5 text-sm bg-card border border-border rounded-md text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50"
                >
                  {SPECIMEN_TYPES.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-4">
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="bg-card border border-border hover:bg-muted text-foreground px-6 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2"
              >
                <UploadCloud className="w-4 h-4" />
                Browse Files
              </button>
              <button 
                onClick={startCamera}
                className="bg-card border border-border hover:bg-muted text-foreground px-6 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2"
              >
                <Camera className="w-4 h-4" />
                Take Photo
              </button>
            </div>
            
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept=".svs,.tif,.ndpi,.png,.jpg,image/*" 
              onChange={handleFileChange} 
            />
            
            <input 
              type="file" 
              ref={cameraInputRef} 
              className="hidden" 
              accept="image/*" 
              capture="environment"
              onChange={handleFileChange} 
            />
            
            <div className="mt-8 flex items-center gap-2 text-xs text-warning bg-warning/10 px-3 py-1.5 rounded-full">
              <AlertTriangle className="w-3.5 h-3.5" />
              Max file size: 2GB per slide
            </div>
          </div>
          )}
        </div>
      )}
    </div>
  );
}
