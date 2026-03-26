import { useCallback, useMemo, useState } from 'react';

import type {
  IGenreFilterProps,
  IUseGenreFilterReturn,
} from './GenreFilter-types';

const TOP_GENRE_COUNT = 3;

/** Encapsulates GenreFilter state and toggle logic. */
export function useGenreFilter(
  props: IGenreFilterProps,
): IUseGenreFilterReturn {
  const { genres, onSelectionChange, selectedGenres } = props;
  const [isModalOpen, setIsModalOpen] = useState(false);

  const topGenres = useMemo(
    () => genres.slice(0, TOP_GENRE_COUNT),
    [genres],
  );

  const hasSelection = selectedGenres.length > 0;

  const isSelected = useCallback(
    (genre: string): boolean => selectedGenres.includes(genre),
    [selectedGenres],
  );

  const handleToggle = useCallback(
    (genre: string): void => {
      const next = selectedGenres.includes(genre)
        ? selectedGenres.filter((g) => g !== genre)
        : [...selectedGenres, genre];
      onSelectionChange(next);
    },
    [onSelectionChange, selectedGenres],
  );

  const handleClear = useCallback((): void => {
    onSelectionChange([]);
  }, [onSelectionChange]);

  const handleModalOpen = useCallback((): void => {
    setIsModalOpen(true);
  }, []);

  const handleModalClose = useCallback((): void => {
    setIsModalOpen(false);
  }, []);

  return {
    handleClear,
    handleModalClose,
    handleModalOpen,
    handleToggle,
    hasSelection,
    isModalOpen,
    isSelected,
    topGenres,
  };
}
