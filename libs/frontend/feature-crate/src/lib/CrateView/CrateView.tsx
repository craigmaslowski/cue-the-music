import { EmptyState } from '@cue-the-music/core-ui';
import {
  useAlbumFilters,
  useAlbums,
} from '@cue-the-music/data-access-collection';

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

  const { data: albumData } = useAlbums(filters);
  const { data: filterValues } = useAlbumFilters();

  const albums = albumData.albums;
  const total = albumData.count;
  const hasNoCollection = total === 0 && !filters.search && !filters.genres && !filters.decades;
  const hasNoResults = albums.length === 0 && !hasNoCollection;

  return (
    <div className={rootStyles}>
      <CollectionSearch
        decades={filterValues.decades.map(String)}
        genres={filterValues.genres}
        onDecadesChange={handleDecadesChange}
        onGenresChange={handleGenresChange}
        onSearch={handleSearch}
        selectedDecades={filters.decades ?? []}
        selectedGenres={filters.genres ?? []}
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

      {albums.length > 0 && (
        <AlbumGrid albums={albums} onAlbumPress={handleOpenOverlay} />
      )}

      <AlbumDetailOverlay
        albumId={selectedAlbumId}
        onClose={handleCloseOverlay}
      />
    </div>
  );
}
