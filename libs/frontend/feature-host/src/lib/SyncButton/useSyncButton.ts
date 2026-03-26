import { useCallback } from 'react';

import type { ISyncButtonProps, IUseSyncButtonReturn } from './SyncButton-types';

/** Encapsulates SyncButton logic. */
export function useSyncButton(props: ISyncButtonProps): IUseSyncButtonReturn {
  const { isSyncing, onSync } = props;

  const handlePress = useCallback(() => {
    if (!isSyncing) {
      onSync();
    }
  }, [isSyncing, onSync]);

  return {
    isDisabled: isSyncing,
    handlePress,
  };
}
