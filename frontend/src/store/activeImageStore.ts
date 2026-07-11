import { create } from 'zustand';

interface ActiveImageState {
  imageUrl: string | null;
  setImageUrl: (url: string | null) => void;
  isExplainabilityMode: boolean;
  toggleExplainabilityMode: () => void;
}

export const useActiveImageStore = create<ActiveImageState>((set) => ({
  imageUrl: null,
  setImageUrl: (url) => set({ imageUrl: url }),
  isExplainabilityMode: false,
  toggleExplainabilityMode: () => set((state) => ({ isExplainabilityMode: !state.isExplainabilityMode })),
}));
