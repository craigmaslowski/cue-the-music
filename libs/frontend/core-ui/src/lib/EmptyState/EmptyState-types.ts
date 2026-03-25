import type { ReactNode } from 'react';

export interface IEmptyStateProps {
  /** Icon or illustration rendered above the message */
  icon?: ReactNode;
  /** Primary message describing the empty state */
  message: string;
  /** Optional secondary description text */
  submessage?: string;
}

export interface IUseEmptyStateReturn {
  /** Whether an icon slot is provided */
  hasIcon: boolean;
}
