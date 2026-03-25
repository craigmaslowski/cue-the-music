export interface IToastProps {
  /** Description text providing detail about the notification */
  description?: string;
  /** Callback when the toast is dismissed */
  onClose?: () => void;
  /** Title text of the notification */
  title: string;
  /** Visual variant controlling color scheme */
  variant?: 'error' | 'info' | 'success';
}

export interface IUseToastReturn {
  /** Handler to dismiss the toast */
  handleClose: () => void;
  /** Visual variant for styling */
  variant: 'error' | 'info' | 'success';
}
