import type { IGenreCount } from '@cue-the-music/core-types';

export interface ICollectionSearchProps {
  /** Available decade filter options */
  decades: string[];
  /** Available genres with album counts */
  genres: IGenreCount[];
  /** Callback when filters change */
  onDecadesChange: (decades: string[]) => void;
  /** Callback when filters change */
  onGenresChange: (genres: string[]) => void;
  /** Callback when search text changes (debounced) */
  onSearch: (value: string) => void;
  /** Currently selected decade values */
  selectedDecades: string[];
  /** Currently selected genre values */
  selectedGenres: string[];
}

export interface IUseCollectionSearchReturn {
  /** Whether any filters are active */
  hasActiveFilters: boolean;
}
