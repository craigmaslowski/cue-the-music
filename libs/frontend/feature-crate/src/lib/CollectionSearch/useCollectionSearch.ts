import type {
  ICollectionSearchProps,
  IUseCollectionSearchReturn,
} from './CollectionSearch-types';

/** Encapsulates CollectionSearch state derivation. */
export function useCollectionSearch(
  props: ICollectionSearchProps,
): IUseCollectionSearchReturn {
  const { selectedDecades, selectedGenres } = props;

  const hasActiveFilters =
    selectedGenres.length > 0 || selectedDecades.length > 0;

  return { hasActiveFilters };
}
