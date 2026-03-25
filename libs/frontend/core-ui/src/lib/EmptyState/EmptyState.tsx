import {
  iconStyles,
  messageStyles,
  rootStyles,
  submessageStyles,
} from './EmptyState-elements';
import type { IEmptyStateProps } from './EmptyState-types';
import { useEmptyState } from './useEmptyState';

/** Reusable empty state with optional icon slot, message, and submessage. */
export function EmptyState(props: IEmptyStateProps) {
  const { icon, message, submessage } = props;
  const { hasIcon } = useEmptyState(props);

  return (
    <div className={rootStyles}>
      {hasIcon && <div className={iconStyles}>{icon}</div>}
      <p className={messageStyles}>{message}</p>
      {submessage && <p className={submessageStyles}>{submessage}</p>}
    </div>
  );
}
