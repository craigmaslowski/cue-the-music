import { SyncButton } from '../SyncButton';
import {
  actionsStyles,
  deactivateButtonStyles,
  dotStyles,
  labelStyles,
  rootStyles,
  statusStyles,
} from './HostModeIndicator-elements';
import type { IHostModeIndicatorProps } from './HostModeIndicator-types';
import { useHostModeIndicator } from './useHostModeIndicator';

/** "HOST MODE ACTIVE" indicator with sync button and deactivate option. */
export function HostModeIndicator(props: IHostModeIndicatorProps) {
  const { isSyncing } = props;
  const { isHostMode, handleSync, handleDeactivate } =
    useHostModeIndicator(props);

  if (!isHostMode) return null;

  return (
    <div className={rootStyles}>
      <div className={statusStyles}>
        <div className={dotStyles} />
        <span className={labelStyles}>Host Mode Active</span>
      </div>
      <div className={actionsStyles}>
        <SyncButton isSyncing={isSyncing} onSync={handleSync} />
        <button
          className={deactivateButtonStyles}
          onClick={handleDeactivate}
          type="button"
        >
          Exit
        </button>
      </div>
    </div>
  );
}
