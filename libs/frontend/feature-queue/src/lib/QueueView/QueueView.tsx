import { EmptyState } from '@cue-the-music/core-ui';
import { useQueue } from '@cue-the-music/data-access-queue';

import { NowPlayingSection } from '../NowPlayingSection';
import { UpNextList } from '../UpNextList';
import {
  countBadgeStyles,
  listContainerStyles,
  rootStyles,
  sectionHeaderStyles,
  sectionTitleStyles,
} from './QueueView-elements';
import type { IQueueViewProps } from './QueueView-types';
import { useQueueView } from './useQueueView';

/** Main queue view: Now Playing, Up Next header with count, and queue list. */
export function QueueView(props: IQueueViewProps) {
  const { count, hasItems } = useQueueView(props);
  const { data } = useQueue();

  return (
    <div className={rootStyles}>
      <NowPlayingSection nowPlaying={data.now_playing} />

      <div className={sectionHeaderStyles}>
        <h2 className={sectionTitleStyles}>Up Next</h2>
        <span className={countBadgeStyles}>
          {count} {count === 1 ? 'album' : 'albums'} in queue
        </span>
      </div>

      {hasItems ? (
        <div className={listContainerStyles}>
          <UpNextList items={data.items} />
        </div>
      ) : (
        <EmptyState
          message="Queue is empty"
          submessage="Browse the crate and request an album to get started."
        />
      )}
    </div>
  );
}
