import type { IQueueItem } from '@cue-the-music/data-access-queue';

export interface IUpNextListProps {
  /** Ordered list of queue items */
  items: IQueueItem[];
}

export interface IUseUpNextListReturn {
  /** Whether the list has items */
  hasItems: boolean;
}
