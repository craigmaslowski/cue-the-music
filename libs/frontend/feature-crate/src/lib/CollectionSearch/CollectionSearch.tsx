import { SearchInput } from '@cue-the-music/core-ui';

import { ChipFilter } from '../ChipFilter';
import { GenreFilter } from '../GenreFilter';
import {
  albumCountFiltersToggleStyles,
  countStyles,
  filtersStyles,
  rootStyles,
  toggleButtonStyles,
} from './CollectionSearch-elements';
import type { ICollectionSearchProps } from './CollectionSearch-types';
import { useCollectionSearch } from './useCollectionSearch';

/** Search input combined with genre and decade chip filters. */
export function CollectionSearch(props: ICollectionSearchProps) {
  const {
    decades,
    filteredCount,
    genres,
    onDecadesChange,
    onGenresChange,
    onSearch,
    selectedDecades,
    selectedGenres,
    totalCount,
  } = props;
  const { hasActiveFilters, handleToggleFilters, isFiltersOpen } =
    useCollectionSearch(props);

  const hasFilters = genres.length > 0 || decades.length > 0;
  const countText = hasActiveFilters
    ? `${filteredCount} of ${totalCount} albums`
    : `${totalCount} albums`;

  return (
    <div className={rootStyles}>
      <SearchInput
        onSearch={onSearch}
        placeholder="Search artists and albums..."
      />
      {isFiltersOpen && (
        <div className={filtersStyles}>
          {genres.length > 0 && (
            <GenreFilter
              genres={genres}
              onSelectionChange={onGenresChange}
              selectedGenres={selectedGenres}
            />
          )}
          {decades.length > 0 && (
            <ChipFilter
              label="Decade"
              onSelectionChange={onDecadesChange}
              options={decades}
              selected={selectedDecades}
            />
          )}
        </div>
      )}
      <div className={albumCountFiltersToggleStyles}>
        {totalCount > 0 && <span className={countStyles}>{countText}</span>}
        {hasFilters && (
          <button
            className={toggleButtonStyles}
            onClick={handleToggleFilters}
            type="button"
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: '1.25rem' }}
            >
              {isFiltersOpen ? 'filter_list_off' : 'filter_list'}
            </span>
            {isFiltersOpen ? 'Hide Filters' : 'Show Filters'}
          </button>
        )}
      </div>
    </div>
  );
}
