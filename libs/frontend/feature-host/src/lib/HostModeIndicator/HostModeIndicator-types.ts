export interface IHostModeIndicatorProps {
  /** Whether clear queue is currently in progress */
  isClearing: boolean;
  /** Whether sync is currently in progress */
  isSyncing: boolean;
  /** Callback to clear all queue items and now playing */
  onClearQueue: () => void;
  /** Callback to trigger Discogs sync */
  onSync: () => void;
}

export interface IUseHostModeIndicatorReturn {
  /** Handler for clearing the queue */
  handleClearQueue: () => void;
  /** Handler for deactivating host mode */
  handleDeactivate: () => void;
  /** Handler for sync button press */
  handleSync: () => void;
  /** Whether host mode is active */
  isHostMode: boolean;
}
