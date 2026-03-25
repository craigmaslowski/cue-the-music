import type { ReactNode } from 'react';

export interface IDialogProps {
  /** Content rendered inside the dialog body */
  children: ReactNode;
  /** Accessible description for the dialog */
  description?: string;
  /** Callback when the dialog open state changes */
  onOpenChange?: (details: { open: boolean }) => void;
  /** Whether the dialog is open */
  open: boolean;
  /** Accessible title for the dialog */
  title: string;
}

export interface IUseDialogReturn {
  /** Whether the dialog is currently open */
  open: boolean;
  /** Handler for open state changes */
  handleOpenChange: (details: { open: boolean }) => void;
}
