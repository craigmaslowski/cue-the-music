export interface IHostModeIndicatorProps {
  /** Callback to trigger Discogs sync */
  onSync: () => void;
  /** Whether sync is currently in progress */
  isSyncing: boolean;
}

export interface IUseHostModeIndicatorReturn {
  /** Whether host mode is active */
  isHostMode: boolean;
  /** Handler for sync button press */
  handleSync: () => void;
  /** Handler for deactivating host mode */
  handleDeactivate: () => void;
}
