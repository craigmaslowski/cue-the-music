import { useCallback } from 'react';

import { useHostStore } from '../store';
import type {
  IHostQueueControlsProps,
  IUseHostQueueControlsReturn,
} from './HostQueueControls-types';

const SKIP_SIGNAL_THRESHOLD = 3;

/** Encapsulates HostQueueControls logic. */
export function useHostQueueControls(
  props: IHostQueueControlsProps,
): IUseHostQueueControlsReturn {
  const { queueItemId, downCount, onPromote, onRemove } = props;
  const isHostMode = useHostStore((s) => s.isHostMode);

  const handlePromote = useCallback(() => {
    onPromote(queueItemId);
  }, [queueItemId, onPromote]);

  const handleRemove = useCallback(() => {
    onRemove(queueItemId);
  }, [queueItemId, onRemove]);

  return {
    isHostMode,
    isSkipSignal: downCount >= SKIP_SIGNAL_THRESHOLD,
    handlePromote,
    handleRemove,
  };
}
