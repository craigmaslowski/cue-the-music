import { useCallback, useState } from 'react';

import type {
  ICollectionSearchProps,
  IUseCollectionSearchReturn,
} from './CollectionSearch-types';

/** Encapsulates CollectionSearch state derivation. */
export function useCollectionSearch(
  props: ICollectionSearchProps
): IUseCollectionSearchReturn {
  const { selectedDecades, selectedGenres } = props;
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  const hasActiveFilters =
    selectedGenres.length > 0 || selectedDecades.length > 0;

  const handleToggleFilters = useCallback(() => {
    setIsFiltersOpen((prev) => !prev);
  }, []);

  return { hasActiveFilters, handleToggleFilters, isFiltersOpen };
}
