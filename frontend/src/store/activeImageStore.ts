import { create } from 'zustand';
import { AnalysisResponse } from '@/lib/api';

interface ActiveImageState {
  imageUrl: string | null;
  setImageUrl: (url: string | null) => void;
  isExplainabilityMode: boolean;
  toggleExplainabilityMode: () => void;
  setExplainabilityMode: (value: boolean) => void;
  analysisResult: AnalysisResponse | null;
  setAnalysisResult: (result: AnalysisResponse | null) => void;
}

export const useActiveImageStore = create<ActiveImageState>((set) => ({
  imageUrl: null,
  setImageUrl: (url) => set({ imageUrl: url }),
  isExplainabilityMode: false,
  toggleExplainabilityMode: () => set((state) => ({ isExplainabilityMode: !state.isExplainabilityMode })),
  setExplainabilityMode: (value) => set({ isExplainabilityMode: value }),
  analysisResult: null,
  setAnalysisResult: (result) => set({ analysisResult: result }),
}));
