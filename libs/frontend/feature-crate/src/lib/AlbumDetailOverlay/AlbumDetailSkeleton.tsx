import {
  coverArtStyles,
  metadataStyles,
  skeletonLineStyles,
} from './AlbumDetailOverlay-elements';

/** Loading skeleton for the album detail overlay content. */
export function AlbumDetailSkeleton() {
  return (
    <div>
      <div className={coverArtStyles} />
      <div className={metadataStyles}>
        <div className={skeletonLineStyles} style={{ width: '70%' }} />
        <div className={skeletonLineStyles} style={{ width: '50%' }} />
        <div className={skeletonLineStyles} style={{ width: '40%' }} />
      </div>
    </div>
  );
}
