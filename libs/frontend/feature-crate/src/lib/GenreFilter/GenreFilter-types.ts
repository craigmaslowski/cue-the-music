import type { IGenreCount } from '@cue-the-music/core-types';

export interface IGenreFilterProps {
  /** All genres with album counts, sorted by count descending */
  genres: IGenreCount[];
  /** Callback when genre selection changes */
  onSelectionChange: (selected: string[]) => void;
  /** Currently selected genre names */
  selectedGenres: string[];
}

export interface IUseGenreFilterReturn {
  /** Clear all genre selections */
  handleClear: () => void;
  /** Close the genre modal */
  handleModalClose: () => void;
  /** Open the genre modal */
  handleModalOpen: () => void;
  /** Toggle a genre in the selection */
  handleToggle: (genre: string) => void;
  /** Whether any genres are selected */
  hasSelection: boolean;
  /** Whether the genre modal is open */
  isModalOpen: boolean;
  /** Check if a genre is selected */
  isSelected: (genre: string) => boolean;
  /** Top N genres by album count for default display */
  topGenres: IGenreCount[];
}
