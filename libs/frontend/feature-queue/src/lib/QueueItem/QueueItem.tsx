import { VoteControls } from '../VoteControls';
import {
  actionsStyles,
  artistStyles,
  cancelButtonStyles,
  infoStyles,
  rootStyles,
  thumbnailStyles,
  titleStyles,
} from './QueueItem-elements';
import type { IQueueItemProps } from './QueueItem-types';
import { useQueueItem } from './useQueueItem';

/** Single queue item with album info, vote controls, and optional cancel. */
export function QueueItem(props: IQueueItemProps) {
  const { item } = props;
  const { handleCancel, handleDownVote, handleUpVote, isCancelling } =
    useQueueItem(props);

  const { album } = item;

  return (
    <div className={rootStyles}>
      {album.cover_art_thumbnail_url ? (
        <img
          alt={`${album.title} by ${album.artist}`}
          className={thumbnailStyles}
          height={56}
          loading="lazy"
          src={album.cover_art_thumbnail_url}
          width={56}
        />
      ) : (
        <div className={thumbnailStyles} />
      )}

      <div className={infoStyles}>
        <span className={titleStyles}>{album.title}</span>
        <span className={artistStyles}>{album.artist}</span>
      </div>

      <div className={actionsStyles}>
        <VoteControls
          downCount={item.votes.down_count}
          isDownVoted={item.votes.my_vote === -1}
          isUpVoted={item.votes.my_vote === 1}
          onDownVote={handleDownVote}
          onUpVote={handleUpVote}
          upCount={item.votes.up_count}
        />

        <button
          aria-label="Cancel request"
          className={cancelButtonStyles}
          disabled={isCancelling}
          onClick={handleCancel}
          type="button"
        >
          &#x2715;
        </button>
      </div>
    </div>
  );
}
