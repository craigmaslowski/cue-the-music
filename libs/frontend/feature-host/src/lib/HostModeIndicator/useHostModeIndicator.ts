import { useCallback } from 'react';

import { useHostStore } from '../store';
import type {
  IHostModeIndicatorProps,
  IUseHostModeIndicatorReturn,
} from './HostModeIndicator-types';

/** Encapsulates HostModeIndicator logic. */
export function useHostModeIndicator(
  props: IHostModeIndicatorProps,
): IUseHostModeIndicatorReturn {
  const { onClearQueue, onSync } = props;
  const isHostMode = useHostStore((s) => s.isHostMode);
  const deactivateHostMode = useHostStore((s) => s.deactivateHostMode);

  const handleClearQueue = useCallback(() => {
    onClearQueue();
  }, [onClearQueue]);

  const handleSync = useCallback(() => {
    onSync();
  }, [onSync]);

  const handleDeactivate = useCallback(() => {
    deactivateHostMode();
  }, [deactivateHostMode]);

  return {
    handleClearQueue,
    handleDeactivate,
    handleSync,
    isHostMode,
  };
}
