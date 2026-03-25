import type { IAlbumFilters } from '@cue-the-music/core-types';
import { useCallback, useState } from 'react';

import type { ICrateViewProps, IUseCrateViewReturn } from './CrateView-types';

/** Encapsulates CrateView state management for search, filters, and overlay. */
export function useCrateView(_props: ICrateViewProps): IUseCrateViewReturn {
  const [search, setSearch] = useState('');
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [selectedDecades, setSelectedDecades] = useState<string[]>([]);
  const [selectedAlbumId, setSelectedAlbumId] = useState<number | null>(null);

  const filters: IAlbumFilters = {
    search: search || undefined,
    genres: selectedGenres.length > 0 ? selectedGenres : undefined,
    decades: selectedDecades.length > 0 ? selectedDecades : undefined,
  };

  const handleSearch = useCallback((value: string) => {
    setSearch(value);
  }, []);

  const handleGenresChange = useCallback((genres: string[]) => {
    setSelectedGenres(genres);
  }, []);

  const handleDecadesChange = useCallback((decades: string[]) => {
    setSelectedDecades(decades);
  }, []);

  function handleOpenOverlay(id: number): void {
    setSelectedAlbumId(id);
  }

  function handleCloseOverlay(): void {
    setSelectedAlbumId(null);
  }

  return {
    filters,
    handleCloseOverlay,
    handleDecadesChange,
    handleGenresChange,
    handleOpenOverlay,
    handleSearch,
    selectedAlbumId,
  };
}
