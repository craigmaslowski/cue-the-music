export interface ICollectionSearchProps {
  /** Available decade filter options */
  decades: string[];
  /** Callback when filters change */
  onDecadesChange: (decades: string[]) => void;
  /** Callback when filters change */
  onGenresChange: (genres: string[]) => void;
  /** Callback when search text changes (debounced) */
  onSearch: (value: string) => void;
  /** Available genre filter options */
  genres: string[];
  /** Currently selected decade values */
  selectedDecades: string[];
  /** Currently selected genre values */
  selectedGenres: string[];
}

export interface IUseCollectionSearchReturn {
  /** Whether any filters are active */
  hasActiveFilters: boolean;
}
