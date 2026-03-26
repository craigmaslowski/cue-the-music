import type { IAlbumFilters } from '@cue-the-music/core-types';
import { useState } from 'react';

import { useCrateStore } from '../store';
import type { ICrateViewProps, IUseCrateViewReturn } from './CrateView-types';

/** Encapsulates CrateView state management for search, filters, and overlay. */
export function useCrateView(_props: ICrateViewProps): IUseCrateViewReturn {
  // Persistent state from Zustand store (survives tab switches)
  const search = useCrateStore((s) => s.search);
  const selectedDecades = useCrateStore((s) => s.selectedDecades);
  const selectedGenres = useCrateStore((s) => s.selectedGenres);
  const setSearch = useCrateStore((s) => s.setSearch);
  const setSelectedDecades = useCrateStore((s) => s.setSelectedDecades);
  const setSelectedGenres = useCrateStore((s) => s.setSelectedGenres);

  // Overlay state is local — should reset on navigation
  const [selectedAlbumId, setSelectedAlbumId] = useState<number | null>(null);

  const filters: IAlbumFilters = {
    decades: selectedDecades.length > 0 ? selectedDecades : undefined,
    genres: selectedGenres.length > 0 ? selectedGenres : undefined,
    search: search || undefined,
  };

  function handleOpenOverlay(id: number): void {
    setSelectedAlbumId(id);
  }

  function handleCloseOverlay(): void {
    setSelectedAlbumId(null);
  }

  return {
    filters,
    handleCloseOverlay,
    handleDecadesChange: setSelectedDecades,
    handleGenresChange: setSelectedGenres,
    handleOpenOverlay,
    handleSearch: setSearch,
    selectedAlbumId,
  };
}
