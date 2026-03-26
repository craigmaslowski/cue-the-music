import { useCallback } from 'react';

import {
  useClearQueue,
  usePromoteToNowPlaying,
  useRemoveQueueItem,
  useTriggerSync,
} from '@cue-the-music/data-access-host';
import { useHostStore } from '@cue-the-music/feature-host';

interface IUseQueuePageReturn {
  /** Handler for clearing the entire queue and now playing */
  handleClearQueue: () => void;
  /** Handler for promoting a queue item to now playing */
  handlePromote: (queueItemId: number) => void;
  /** Handler for removing a queue item */
  handleRemove: (queueItemId: number) => void;
  /** Handler for triggering Discogs sync */
  handleSync: () => void;
  /** Whether the clear queue operation is in progress */
  isClearing: boolean;
  /** Whether host mode is active */
  isHostMode: boolean;
  /** Whether a Discogs sync is in progress */
  isSyncing: boolean;
}

/**
 * Owns host-mode wiring for the queue page: store reads, sync/promote/remove
 * mutations, and onUnauthorized handling for expired tokens.
 */
export function useQueuePage(): IUseQueuePageReturn {
  const deactivateHostMode = useHostStore((s) => s.deactivateHostMode);
  const isHostMode = useHostStore((s) => s.isHostMode);
  const sessionToken = useHostStore((s) => s.sessionToken);

  const mutationOptions = {
    onUnauthorized: deactivateHostMode,
    token: sessionToken,
  };

  const clearQueueMutation = useClearQueue(mutationOptions);
  const promoteMutation = usePromoteToNowPlaying(mutationOptions);
  const removeMutation = useRemoveQueueItem(mutationOptions);
  const syncMutation = useTriggerSync(mutationOptions);

  const handleClearQueue = useCallback(() => {
    clearQueueMutation.mutate();
  }, [clearQueueMutation]);

  const handlePromote = useCallback(
    (queueItemId: number) => {
      promoteMutation.mutate({ queue_item_id: queueItemId });
    },
    [promoteMutation],
  );

  const handleRemove = useCallback(
    (queueItemId: number) => {
      removeMutation.mutate({ id: queueItemId });
    },
    [removeMutation],
  );

  const handleSync = useCallback(() => {
    syncMutation.mutate();
  }, [syncMutation]);

  return {
    handleClearQueue,
    handlePromote,
    handleRemove,
    handleSync,
    isClearing: clearQueueMutation.isPending,
    isHostMode,
    isSyncing: syncMutation.isPending,
  };
}
