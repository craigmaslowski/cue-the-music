import type { IAlbumFilters } from '@cue-the-music/core-types';

export interface ICrateViewProps {
  /** No external props — CrateView is a top-level feature component. */
}

export interface IUseCrateViewReturn {
  /** Currently applied filters */
  filters: IAlbumFilters;
  /** Handler for closing the album detail overlay */
  handleCloseOverlay: () => void;
  /** Handler for selecting decades */
  handleDecadesChange: (decades: string[]) => void;
  /** Handler for selecting genres */
  handleGenresChange: (genres: string[]) => void;
  /** Handler for opening an album detail overlay */
  handleOpenOverlay: (id: number) => void;
  /** Handler for search text changes */
  handleSearch: (value: string) => void;
  /** The album ID currently open in the overlay, or null */
  selectedAlbumId: number | null;
}
