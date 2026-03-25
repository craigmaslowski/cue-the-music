import type { IDialogProps, IUseDialogReturn } from './Dialog-types';

/** Encapsulates Dialog state and event handling logic. */
export function useDialog(props: IDialogProps): IUseDialogReturn {
  const { onOpenChange, open } = props;

  function handleOpenChange(details: { open: boolean }): void {
    onOpenChange?.(details);
  }

  return {
    handleOpenChange,
    open,
  };
}
