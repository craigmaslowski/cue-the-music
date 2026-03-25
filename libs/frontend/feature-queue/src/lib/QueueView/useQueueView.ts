import { useQueue } from '@cue-the-music/data-access-queue';

import type { IQueueViewProps, IUseQueueViewReturn } from './QueueView-types';

/** Encapsulates QueueView data fetching and derived state. */
export function useQueueView(_props: IQueueViewProps): IUseQueueViewReturn {
  const { data } = useQueue();

  return {
    count: data.count,
    hasItems: data.queue.length > 0,
  };
}
