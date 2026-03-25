import {
  ApiError,
  useAlbum,
  useRequestAlbum,
} from '@cue-the-music/data-access-collection';
import { useCallback, useState } from 'react';

import type { IAlbumDetailOverlayProps } from './AlbumDetailOverlay-types';

/** Return type for the outer overlay hook (controls dialog + request). */
export interface IUseAlbumDetailOverlayReturn {
  buttonText: string;
  handleClose: () => void;
  handleRequest: () => void;
  isOpen: boolean;
  isRequestDisabled: boolean;
  isRequesting: boolean;
}

/** Encapsulates AlbumDetailOverlay request mutation and dialog state. */
export function useAlbumDetailOverlay(
  props: IAlbumDetailOverlayProps,
): IUseAlbumDetailOverlayReturn {
  const { albumId, onClose } = props;
  const isOpen = albumId !== null;

  const [alreadyInQueue, setAlreadyInQueue] = useState(false);
  const [limitReached, setLimitReached] = useState(false);
  const [requestSuccess, setRequestSuccess] = useState(false);

  const requestMutation = useRequestAlbum();

  // Reset state when album changes
  const resetState = useCallback(() => {
    setAlreadyInQueue(false);
    setLimitReached(false);
    setRequestSuccess(false);
    requestMutation.reset();
  }, [requestMutation]);

  function handleClose(): void {
    resetState();
    onClose();
  }

  function handleRequest(): void {
    if (!albumId) return;

    requestMutation.mutate(
      { album_id: albumId },
      {
        onSuccess: () => {
          setRequestSuccess(true);
        },
        onError: (error) => {
          if (error instanceof ApiError) {
            if (error.status === 409) {
              setAlreadyInQueue(true);
            } else if (error.status === 429) {
              setLimitReached(true);
            }
          }
        },
      },
    );
  }

  // Derive button text and disabled state from cache/mutation state
  const isRequesting = requestMutation.isPending;
  let buttonText = 'Request This Album';
  let isRequestDisabled = false;

  if (alreadyInQueue) {
    buttonText = 'Already in queue';
    isRequestDisabled = true;
  } else if (limitReached) {
    buttonText = 'Request limit reached';
    isRequestDisabled = true;
  } else if (requestSuccess) {
    buttonText = 'Requested';
    isRequestDisabled = true;
  } else if (isRequesting) {
    buttonText = 'Requesting...';
    isRequestDisabled = true;
  }

  return {
    buttonText,
    handleClose,
    handleRequest,
    isOpen,
    isRequestDisabled,
    isRequesting,
  };
}

/**
 * Inner hook that fetches album data. Separated so it can be conditionally
 * rendered (only when albumId is non-null and overlay is mounted).
 */
export function useAlbumDetailData(albumId: number) {
  const { data: album, isPlaceholderData } = useAlbum(albumId);

  const isTracklistLoading = isPlaceholderData || album.tracklist === null;

  return { album, isTracklistLoading };
}
