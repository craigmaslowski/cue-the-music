export interface IHostPinOverlayProps {
  /** Whether the overlay is currently visible */
  isOpen: boolean;
  /** Callback to close the overlay */
  onClose: () => void;
}

export interface IUseHostPinOverlayReturn {
  /** The digits entered so far (0-4 chars) */
  digits: string;
  /** Whether there's an error (wrong PIN) */
  hasError: boolean;
  /** Whether the verify mutation is in-flight */
  isPending: boolean;
  /** Handler for keypad digit press */
  handleDigitPress: (digit: string) => void;
  /** Handler for backspace press */
  handleBackspace: () => void;
  /** Handler for clear/cancel */
  handleClear: () => void;
}
