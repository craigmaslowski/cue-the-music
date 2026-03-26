import type { IGenreCount } from '@cue-the-music/core-types';

export interface IGenreFilterModalProps {
  /** All genres with album counts */
  genres: IGenreCount[];
  /** Check if a genre is selected */
  isSelected: (genre: string) => boolean;
  /** Callback when the modal is closed */
  onClose: () => void;
  /** Toggle a genre in the selection */
  onToggle: (genre: string) => void;
  /** Whether the modal is open */
  open: boolean;
}
