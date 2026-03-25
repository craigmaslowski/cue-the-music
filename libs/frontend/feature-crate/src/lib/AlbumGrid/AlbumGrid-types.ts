import type { IAlbum } from '@cue-the-music/core-types';

export interface IAlbumGridProps {
  /** Albums to display in the grid */
  albums: IAlbum[];
  /** Callback when an album card is tapped */
  onAlbumPress: (id: number) => void;
}

export interface IUseAlbumGridReturn {
  /** Whether the grid has albums to display */
  hasAlbums: boolean;
}
