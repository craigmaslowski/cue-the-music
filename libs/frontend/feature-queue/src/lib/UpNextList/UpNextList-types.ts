import type { ReactNode } from 'react';

import type { IQueueItem } from '@cue-the-music/data-access-queue';

export interface IUpNextListProps {
  /** Ordered list of queue items */
  items: IQueueItem[];
  /** Optional render prop to inject per-item actions (e.g., host controls). */
  renderItemActions?: (item: IQueueItem) => ReactNode;
}

export interface IUseUpNextListReturn {
  /** Whether the list has items */
  hasItems: boolean;
}
