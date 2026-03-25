import type { ReactNode } from 'react';

import type { IQueueItem } from '@cue-the-music/core-types';

export interface IQueueViewProps {
  /** Optional render prop to inject per-item actions (e.g., host controls). */
  renderItemActions?: (item: IQueueItem) => ReactNode;
}

export interface IUseQueueViewReturn {
  /** Number of items in the queue */
  count: number;
  /** Whether the queue has items */
  hasItems: boolean;
}
