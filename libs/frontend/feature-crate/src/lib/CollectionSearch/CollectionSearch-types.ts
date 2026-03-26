import type { IGenreCount } from '@cue-the-music/core-types';

export interface ICollectionSearchProps {
  /** Available decade filter options */
  decades: string[];
  /** Number of albums matching current filters */
  filteredCount: number;
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
  /** Total number of albums in the collection */
  totalCount: number;
}

export interface IUseCollectionSearchReturn {
  /** Whether any filters are active */
  hasActiveFilters: boolean;
  /** Handler to toggle filter section visibility */
  handleToggleFilters: () => void;
  /** Whether the filter section is expanded */
  isFiltersOpen: boolean;
}
