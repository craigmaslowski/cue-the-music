import { useCrateStore } from '../store';
import type {
  ICollectionSearchProps,
  IUseCollectionSearchReturn,
} from './CollectionSearch-types';

/** Encapsulates CollectionSearch state derivation. */
export function useCollectionSearch(
  _props: ICollectionSearchProps,
): IUseCollectionSearchReturn {
  const isFiltersOpen = useCrateStore((s) => s.isFiltersOpen);
  const toggleFilters = useCrateStore((s) => s.toggleFilters);

  return { handleToggleFilters: toggleFilters, isFiltersOpen };
}
