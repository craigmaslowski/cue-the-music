import { Dialog } from '@cue-the-music/core-ui';

import { chipSelectedStyles, chipStyles } from './GenreFilter-elements';
import { chipGridStyles } from './GenreFilterModal-elements';
import type { IGenreFilterModalProps } from './GenreFilterModal-types';

/** Full-screen modal for browsing and selecting genres. */
export function GenreFilterModal(props: IGenreFilterModalProps) {
  const { genres, isSelected, onClose, onToggle, open } = props;

  return (
    <Dialog
      onOpenChange={(details) => {
        if (!details.open) onClose();
      }}
      open={open}
      title="Browse Genres"
    >
      <div className={chipGridStyles}>
        {genres.map((g) => (
          <button
            aria-pressed={isSelected(g.genre)}
            className={isSelected(g.genre) ? chipSelectedStyles : chipStyles}
            key={g.genre}
            onClick={() => onToggle(g.genre)}
            type="button"
          >
            {g.genre}
          </button>
        ))}
      </div>
    </Dialog>
  );
}
