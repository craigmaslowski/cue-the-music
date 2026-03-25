export interface IAlbumDetailOverlayProps {
  /** Album ID to display, or null when closed */
  albumId: number | null;
  /** Callback when the overlay should close */
  onClose: () => void;
}
