export interface ISyncButtonProps {
  /** Whether sync is currently in progress */
  isSyncing: boolean;
  /** Callback to trigger sync */
  onSync: () => void;
}

export interface IUseSyncButtonReturn {
  /** Whether the button is disabled */
  isDisabled: boolean;
  /** Handler for button press */
  handlePress: () => void;
}
