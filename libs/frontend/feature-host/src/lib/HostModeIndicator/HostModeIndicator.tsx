import { SyncButton } from '../SyncButton';
import {
  actionsStyles,
  clearAllButtonStyles,
  deactivateButtonStyles,
  dotStyles,
  labelStyles,
  rootStyles,
  statusStyles,
} from './HostModeIndicator-elements';
import type { IHostModeIndicatorProps } from './HostModeIndicator-types';
import { useHostModeIndicator } from './useHostModeIndicator';

/** "HOST MODE ACTIVE" indicator with clear, sync, and deactivate actions. */
export function HostModeIndicator(props: IHostModeIndicatorProps) {
  const { isClearing, isSyncing } = props;
  const { isHostMode, handleClearQueue, handleSync, handleDeactivate } =
    useHostModeIndicator(props);

  if (!isHostMode) return null;

  const isBusy = isClearing || isSyncing;

  return (
    <div className={rootStyles}>
      <div className={statusStyles}>
        <div className={dotStyles} />
        <span className={labelStyles}>Host Mode Active</span>
      </div>
      <div className={actionsStyles}>
        <button
          className={clearAllButtonStyles}
          disabled={isBusy}
          onClick={handleClearQueue}
          type="button"
        >
          Clear All
        </button>
        <SyncButton isSyncing={isSyncing} onSync={handleSync} />
        <button
          className={deactivateButtonStyles}
          disabled={isBusy}
          onClick={handleDeactivate}
          type="button"
        >
          Exit
        </button>
      </div>
    </div>
  );
}
