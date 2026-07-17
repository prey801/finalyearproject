'use client';

import { useState } from 'react';
import { Save, RefreshCw } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    localInference: true,
    hardwareAcceleration: true,
    confidenceThreshold: 85,
    autoRegionSelect: false,
    viewerHeatmap: true,
    modelSelection: 'medlm-v2'
  });

  const handleToggle = (key: keyof typeof settings) => {
    setSettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings & Configuration</h1>
          <p className="text-muted-foreground mt-1">Manage system preferences and AI model parameters</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Reset to Defaults
          </button>
          <button className="bg-primary hover:bg-primary/90 text-primary-foreground px-5 py-2.5 rounded-md font-medium shadow-sm transition-colors flex items-center gap-2">
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>
      </div>

      <div className="grid gap-6">
        {/* Model Configuration */}
        <fieldset className="bg-card border border-border rounded-xl p-6 shadow-sm">
          <legend className="sr-only">AI Model Configuration</legend>
          <div className="flex items-center gap-2 mb-6 border-b border-border pb-4">
            <RefreshCw className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">AI Model Configuration</h2>
          </div>
          
          <div className="space-y-6">
            <div>
              <label htmlFor="model-select" className="block text-sm font-medium text-foreground mb-1.5">
                Diagnostic Model Version
              </label>
              <select 
                id="model-select"
                value={settings.modelSelection}
                onChange={(e) => setSettings({...settings, modelSelection: e.target.value})}
                className="w-full md:w-1/2 bg-muted/50 border border-border text-foreground rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="medlm-v2">MedLM-v2 (Specialized - Recommended)</option>
                <option value="medlm-v1">MedLM-v1 (Legacy)</option>
                <option value="custom">Custom Fine-tuned Weights</option>
              </select>
              <p className="text-xs text-muted-foreground mt-1.5">Model used for generating primary diagnostic insights.</p>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="confidence-slider" className="flex justify-between items-center text-sm font-medium text-foreground">
                <span>Anomaly Detection Confidence Threshold</span>
                <span className="text-primary font-mono bg-primary/10 px-2 py-0.5 rounded">{settings.confidenceThreshold}%</span>
              </label>
              <input 
                type="range" 
                id="confidence-slider"
                min="50" 
                max="99" 
                value={settings.confidenceThreshold}
                onChange={(e) => setSettings({...settings, confidenceThreshold: parseInt(e.target.value)})}
                className="w-full accent-primary"
              />
              <p className="text-xs text-muted-foreground">Only flag regions with a confidence score above this threshold.</p>
            </div>
          </div>
        </fieldset>

        {/* Hardware & Privacy */}
        <fieldset className="bg-card border border-border rounded-xl p-6 shadow-sm">
          <legend className="sr-only">Hardware & Privacy</legend>
          <div className="mb-6 border-b border-border pb-4">
            <h2 className="text-lg font-semibold text-foreground">Hardware & Privacy</h2>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="pr-8">
                <label htmlFor="toggle-local" className="font-medium text-foreground cursor-pointer">Local Edge Inference</label>
                <p className="text-sm text-muted-foreground mt-0.5">Run all models locally without sending data to the cloud (requires minimum 16GB VRAM).</p>
              </div>
              <button 
                id="toggle-local"
                role="switch"
                aria-checked={settings.localInference}
                onClick={() => handleToggle('localInference')}
                className={`shrink-0 w-11 h-6 rounded-full relative transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-card ${
                  settings.localInference ? 'bg-primary' : 'bg-muted-foreground/30'
                }`}
              >
                <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                  settings.localInference ? 'translate-x-5' : 'translate-x-0'
                }`} />
              </button>
            </div>

            <div className="flex items-center justify-between">
              <div className="pr-8">
                <label htmlFor="toggle-hardware" className="font-medium text-foreground cursor-pointer">Hardware Acceleration</label>
                <p className="text-sm text-muted-foreground mt-0.5">Use GPU for image rendering and tensor processing.</p>
              </div>
              <button 
                id="toggle-hardware"
                role="switch"
                aria-checked={settings.hardwareAcceleration}
                onClick={() => handleToggle('hardwareAcceleration')}
                className={`shrink-0 w-11 h-6 rounded-full relative transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-card ${
                  settings.hardwareAcceleration ? 'bg-primary' : 'bg-muted-foreground/30'
                }`}
              >
                <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                  settings.hardwareAcceleration ? 'translate-x-5' : 'translate-x-0'
                }`} />
              </button>
            </div>
          </div>
        </fieldset>

        {/* Viewer Preferences */}
        <fieldset className="bg-card border border-border rounded-xl p-6 shadow-sm">
          <legend className="sr-only">Viewer Preferences</legend>
          <div className="mb-6 border-b border-border pb-4">
            <h2 className="text-lg font-semibold text-foreground">Viewer Preferences</h2>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="pr-8">
                <label htmlFor="toggle-heatmap" className="font-medium text-foreground cursor-pointer">Default to Heatmap Overlay</label>
                <p className="text-sm text-muted-foreground mt-0.5">Automatically show attention heatmaps when explainability mode is enabled.</p>
              </div>
              <button 
                id="toggle-heatmap"
                role="switch"
                aria-checked={settings.viewerHeatmap}
                onClick={() => handleToggle('viewerHeatmap')}
                className={`shrink-0 w-11 h-6 rounded-full relative transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-card ${
                  settings.viewerHeatmap ? 'bg-primary' : 'bg-muted-foreground/30'
                }`}
              >
                <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                  settings.viewerHeatmap ? 'translate-x-5' : 'translate-x-0'
                }`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="pr-8">
                <label htmlFor="toggle-auto" className="font-medium text-foreground cursor-pointer">Auto-Select Highest Confidence Region</label>
                <p className="text-sm text-muted-foreground mt-0.5">Focus the viewer on the most anomalous region immediately after analysis completes.</p>
              </div>
              <button 
                id="toggle-auto"
                role="switch"
                aria-checked={settings.autoRegionSelect}
                onClick={() => handleToggle('autoRegionSelect')}
                className={`shrink-0 w-11 h-6 rounded-full relative transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-card ${
                  settings.autoRegionSelect ? 'bg-primary' : 'bg-muted-foreground/30'
                }`}
              >
                <span className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${
                  settings.autoRegionSelect ? 'translate-x-5' : 'translate-x-0'
                }`} />
              </button>
            </div>
          </div>
        </fieldset>
      </div>
    </div>
  );
}
