import type { ReactNode } from 'react';

import type { IQueueItem } from '@cue-the-music/data-access-queue';

export interface IQueueItemProps {
  /** Queue item data */
  item: IQueueItem;
  /** Optional render prop to inject actions below the item (e.g., host controls). */
  renderItemActions?: (item: IQueueItem) => ReactNode;
}

export interface IUseQueueItemReturn {
  /** Handler for cancel request button */
  handleCancel: () => void;
  /** Handler for down vote */
  handleDownVote: () => void;
  /** Handler for up vote */
  handleUpVote: () => void;
  /** Whether cancel mutation is in progress */
  isCancelling: boolean;
}
