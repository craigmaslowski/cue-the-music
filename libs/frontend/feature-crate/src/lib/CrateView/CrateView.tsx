import { EmptyState } from '@cue-the-music/core-ui';
import {
  deriveFilterValues,
  filterAlbums,
  useAlbums,
} from '@cue-the-music/data-access-collection';
import { useMemo } from 'react';

import { AlbumDetailOverlay } from '../AlbumDetailOverlay';
import { AlbumGrid } from '../AlbumGrid';
import { CollectionSearch } from '../CollectionSearch';
import { noResultsStyles, rootStyles } from './CrateView-elements';
import type { ICrateViewProps } from './CrateView-types';
import { useCrateView } from './useCrateView';

/** Main collection browse view with search, filters, grid, and detail overlay. */
export function CrateView(props: ICrateViewProps) {
  const {
    filters,
    handleCloseOverlay,
    handleDecadesChange,
    handleGenresChange,
    handleOpenOverlay,
    handleSearch,
    selectedAlbumId,
  } = useCrateView(props);

  const { data: albumData } = useAlbums();

  // All albums from the single unfiltered cache entry
  const allAlbums = albumData.albums;

  // Client-side filtering with memoized results
  const filteredAlbums = useMemo(
    () => filterAlbums(allAlbums, filters),
    [allAlbums, filters],
  );

  // Derive filter values (genres with counts, decades) from the full set — static, not reactive
  const filterValues = useMemo(
    () => deriveFilterValues(allAlbums),
    [allAlbums],
  );

  const hasNoCollection = allAlbums.length === 0;
  const hasNoResults = filteredAlbums.length === 0 && !hasNoCollection;

  return (
    <div className={rootStyles}>
      <CollectionSearch
        decades={filterValues.decades.map(String)}
        filteredCount={filteredAlbums.length}
        genres={filterValues.genres}
        onDecadesChange={handleDecadesChange}
        onGenresChange={handleGenresChange}
        onSearch={handleSearch}
        selectedDecades={filters.decades ?? []}
        selectedGenres={filters.genres ?? []}
        totalCount={allAlbums.length}
      />

      {hasNoCollection && (
        <EmptyState
          message="No albums yet."
          submessage="The host hasn't synced their collection."
        />
      )}

      {hasNoResults && (
        <div className={noResultsStyles}>
          <p>No albums match your search. Try different terms or filters.</p>
        </div>
      )}

      {filteredAlbums.length > 0 && (
        <AlbumGrid albums={filteredAlbums} onAlbumPress={handleOpenOverlay} />
      )}

      <AlbumDetailOverlay
        albumId={selectedAlbumId}
        onClose={handleCloseOverlay}
      />
    </div>
  );
}
