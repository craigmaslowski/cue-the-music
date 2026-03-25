import {
  useCancelRequest,
  useRemoveVote,
  useVote,
} from '@cue-the-music/data-access-queue';

import type { IQueueItemProps, IUseQueueItemReturn } from './QueueItem-types';

/** Encapsulates QueueItem state: voting and cancel mutations. */
export function useQueueItem(props: IQueueItemProps): IUseQueueItemReturn {
  const { item } = props;
  const cancelMutation = useCancelRequest();
  const voteMutation = useVote();
  const removeVoteMutation = useRemoveVote();

  function handleCancel(): void {
    cancelMutation.mutate({ id: item.id });
  }

  function handleUpVote(): void {
    if (item.my_vote === 1) {
      removeVoteMutation.mutate({ id: item.id });
    } else {
      voteMutation.mutate({ id: item.id, value: 1 });
    }
  }

  function handleDownVote(): void {
    if (item.my_vote === -1) {
      removeVoteMutation.mutate({ id: item.id });
    } else {
      voteMutation.mutate({ id: item.id, value: -1 });
    }
  }

  return {
    handleCancel,
    handleDownVote,
    handleUpVote,
    isCancelling: cancelMutation.isPending,
  };
}
