import type { IToastProps, IUseToastReturn } from './Toast-types';

/** Encapsulates Toast state and event handling logic. */
export function useToast(props: IToastProps): IUseToastReturn {
  const { onClose, variant = 'info' } = props;

  function handleClose(): void {
    onClose?.();
  }

  return {
    handleClose,
    variant,
  };
}
