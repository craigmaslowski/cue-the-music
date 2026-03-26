import {
  chipRowStyles,
  chipSelectedStyles,
  chipStyles,
  clearButtonStyles,
  labelStyles,
  moreButtonStyles,
  rootStyles,
} from './GenreFilter-elements';
import type { IGenreFilterProps } from './GenreFilter-types';
import { GenreFilterModal } from './GenreFilterModal';
import { useGenreFilter } from './useGenreFilter';

/** Hybrid genre filter: top chips + modal picker with two-state display. */
export function GenreFilter(props: IGenreFilterProps) {
  const { genres } = props;
  const {
    handleClear,
    handleModalClose,
    handleModalOpen,
    handleToggle,
    hasSelection,
    isModalOpen,
    isSelected,
    topGenres,
  } = useGenreFilter(props);

  return (
    <div className={rootStyles}>
      <span className={labelStyles}>Genre</span>
      <div className={chipRowStyles}>
        {hasSelection ? (
          <>
            {props.selectedGenres.map((genre) => (
              <button
                aria-pressed={true}
                className={chipSelectedStyles}
                key={genre}
                onClick={() => handleToggle(genre)}
                type="button"
              >
                {genre}
              </button>
            ))}
          </>
        ) : (
          <>
            {topGenres.map((g) => (
              <button
                aria-pressed={false}
                className={chipStyles}
                key={g.genre}
                onClick={() => handleToggle(g.genre)}
                type="button"
              >
                {g.genre}
              </button>
            ))}
          </>
        )}
        <button
          aria-label="Browse all genres"
          className={moreButtonStyles}
          onClick={handleModalOpen}
          type="button"
        >
          + More
        </button>
        {hasSelection && (
          <button
            aria-label="Clear genre filters"
            className={clearButtonStyles}
            onClick={handleClear}
            type="button"
          >
            ✕ Clear
          </button>
        )}
      </div>

      <GenreFilterModal
        genres={genres}
        isSelected={isSelected}
        onClose={handleModalClose}
        onToggle={handleToggle}
        open={isModalOpen}
      />
    </div>
  );
}
