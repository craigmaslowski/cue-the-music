import { SearchInput } from '@cue-the-music/core-ui';

import { ChipFilter } from '../ChipFilter';
import { filtersStyles, rootStyles } from './CollectionSearch-elements';
import type { ICollectionSearchProps } from './CollectionSearch-types';
import { useCollectionSearch } from './useCollectionSearch';

/** Search input combined with genre and decade chip filters. */
export function CollectionSearch(props: ICollectionSearchProps) {
  const {
    decades,
    genres,
    onDecadesChange,
    onGenresChange,
    onSearch,
    selectedDecades,
    selectedGenres,
  } = props;
  useCollectionSearch(props);

  return (
    <div className={rootStyles}>
      <SearchInput
        onSearch={onSearch}
        placeholder="Search artists and albums..."
      />

      <div className={filtersStyles}>
        {genres.length > 0 && (
          <ChipFilter
            label="Genre"
            onSelectionChange={onGenresChange}
            options={genres}
            selected={selectedGenres}
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
    </div>
  );
}
