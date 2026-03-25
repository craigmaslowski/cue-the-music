import {
  promoteButtonStyles,
  removeButtonStyles,
  rootStyles,
  skipBadgeStyles,
  skipSignalStyles,
} from './HostQueueControls-elements';
import type { IHostQueueControlsProps } from './HostQueueControls-types';
import { useHostQueueControls } from './useHostQueueControls';

/** Inline host controls for a queue item: Play, Remove, and skip signal badge. */
export function HostQueueControls(props: IHostQueueControlsProps) {
  const { downCount } = props;
  const { isHostMode, isSkipSignal, handlePromote, handleRemove } =
    useHostQueueControls(props);

  if (!isHostMode) return null;

  return (
    <div className={rootStyles}>
      <button
        className={promoteButtonStyles}
        onClick={handlePromote}
        type="button"
      >
        &#x25B6; Play
      </button>
      <button
        className={removeButtonStyles}
        onClick={handleRemove}
        type="button"
      >
        &#x2715; Remove
      </button>
      {downCount > 0 && (
        <span
          className={`${skipBadgeStyles}${isSkipSignal ? ` ${skipSignalStyles}` : ''}`}
        >
          &#x25BC; {downCount}
        </span>
      )}
    </div>
  );
}
