import { Dialog } from '@cue-the-music/core-ui';
import { Suspense } from 'react';

import type { IAlbumDetailOverlayProps } from './AlbumDetailOverlay-types';
import { AlbumDetailContent } from './AlbumDetailContent';
import { AlbumDetailSkeleton } from './AlbumDetailSkeleton';
import { useAlbumDetailOverlay } from './useAlbumDetailOverlay';

/** Dialog-based overlay showing album detail with request button. */
export function AlbumDetailOverlay(props: IAlbumDetailOverlayProps) {
  const { albumId } = props;
  const {
    buttonText,
    handleClose,
    handleRequest,
    isOpen,
    isRequestDisabled,
    isRequesting,
  } = useAlbumDetailOverlay(props);

  return (
    <Dialog
      onOpenChange={(details) => {
        if (!details.open) handleClose();
      }}
      open={isOpen}
      title=""
    >
      {albumId !== null && (
        <Suspense fallback={<AlbumDetailSkeleton />}>
          <AlbumDetailContent
            albumId={albumId}
            buttonText={buttonText}
            isRequestDisabled={isRequestDisabled}
            isRequesting={isRequesting}
            onRequest={handleRequest}
          />
        </Suspense>
      )}
    </Dialog>
  );
}
