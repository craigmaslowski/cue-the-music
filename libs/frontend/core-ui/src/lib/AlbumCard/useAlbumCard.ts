import type { IAlbumCardProps, IUseAlbumCardReturn } from './AlbumCard-types';

/** Encapsulates AlbumCard interaction logic. */
export function useAlbumCard(props: IAlbumCardProps): IUseAlbumCardReturn {
  const { id, onPress } = props;

  function handlePress(): void {
    onPress?.(id);
  }

  return { handlePress };
}
