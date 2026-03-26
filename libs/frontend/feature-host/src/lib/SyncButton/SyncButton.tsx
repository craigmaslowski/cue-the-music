import { buttonStyles, spinnerStyles } from './SyncButton-elements';
import type { ISyncButtonProps } from './SyncButton-types';
import { useSyncButton } from './useSyncButton';

/** Button to trigger Discogs collection sync with loading state. */
export function SyncButton(props: ISyncButtonProps) {
  const { isSyncing } = props;
  const { isDisabled, handlePress } = useSyncButton(props);

  return (
    <button
      className={buttonStyles}
      disabled={isDisabled}
      onClick={handlePress}
      type="button"
    >
      {isSyncing ? (
        <>
          <span className={spinnerStyles}>&#x21BB;</span>
          Syncing…
        </>
      ) : (
        'Sync'
      )}
    </button>
  );
}
