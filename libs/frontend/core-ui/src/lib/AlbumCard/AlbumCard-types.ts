export interface IAlbumCardProps {
  /** Artist name */
  artist: string;
  /** Thumbnail URL for the album cover art */
  coverArtThumbnailUrl: string | null;
  /** Unique album identifier */
  id: number;
  /** Callback when the card is tapped/clicked */
  onPress?: (id: number) => void;
  /** Album title */
  title: string;
  /** Release year */
  year: number | null;
}

export interface IUseAlbumCardReturn {
  /** Handler for card click/tap */
  handlePress: () => void;
}
