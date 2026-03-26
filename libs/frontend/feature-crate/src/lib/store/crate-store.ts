import { create } from 'zustand';

interface ICrateState {
  /** Whether the filter section is expanded */
  isFiltersOpen: boolean;
  /** Current search query */
  search: string;
  /** Selected decade filter values */
  selectedDecades: string[];
  /** Selected genre filter values */
  selectedGenres: string[];
  /** Set filter visibility */
  setIsFiltersOpen: (open: boolean) => void;
  /** Set search query */
  setSearch: (search: string) => void;
  /** Set selected decades */
  setSelectedDecades: (decades: string[]) => void;
  /** Set selected genres */
  setSelectedGenres: (genres: string[]) => void;
  /** Toggle filter section visibility */
  toggleFilters: () => void;
}

/** Zustand store for crate view UI state — persists across tab switches. */
export const useCrateStore = create<ICrateState>((set) => ({
  isFiltersOpen: false,
  search: '',
  selectedDecades: [],
  selectedGenres: [],
  setIsFiltersOpen: (open) => set({ isFiltersOpen: open }),
  setSearch: (search) => set({ search }),
  setSelectedDecades: (selectedDecades) => set({ selectedDecades }),
  setSelectedGenres: (selectedGenres) => set({ selectedGenres }),
  toggleFilters: () => set((s) => ({ isFiltersOpen: !s.isFiltersOpen })),
}));
