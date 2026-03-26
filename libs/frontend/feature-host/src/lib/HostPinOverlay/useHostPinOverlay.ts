import { useVerifyPin } from '@cue-the-music/data-access-host';
import { useCallback, useEffect, useRef, useState } from 'react';

import { useHostStore } from '../store';
import type {
  IHostPinOverlayProps,
  IUseHostPinOverlayReturn,
} from './HostPinOverlay-types';

const PIN_LENGTH = 4;

/** Encapsulates PIN entry logic, verification, and host mode activation. */
export function useHostPinOverlay(
  props: IHostPinOverlayProps,
): IUseHostPinOverlayReturn {
  const { isOpen, onClose } = props;
  const [digits, setDigits] = useState('');
  const [hasError, setHasError] = useState(false);
  const activateHostMode = useHostStore((s) => s.activateHostMode);
  const verifyPin = useVerifyPin();
  const errorTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Reset state when overlay opens/closes
  useEffect(() => {
    if (isOpen) {
      setDigits('');
      setHasError(false);
    }
    return () => {
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }
    };
  }, [isOpen]);

  const submitPin = useCallback(
    (pin: string) => {
      verifyPin.mutate(
        { pin },
        {
          onSuccess: (data) => {
            activateHostMode(data.token);
            setDigits('');
            onClose();
          },
          onError: () => {
            setHasError(true);
            setDigits('');
            errorTimeoutRef.current = setTimeout(() => {
              setHasError(false);
            }, 600);
          },
        },
      );
    },
    [verifyPin, activateHostMode, onClose],
  );

  const handleDigitPress = useCallback(
    (digit: string) => {
      if (verifyPin.isPending) return;

      setDigits((prev) => {
        if (prev.length >= PIN_LENGTH) return prev;
        const next = prev + digit;
        if (next.length === PIN_LENGTH) {
          // Auto-submit when 4 digits entered
          submitPin(next);
        }
        return next;
      });
    },
    [verifyPin.isPending, submitPin],
  );

  const handleBackspace = useCallback(() => {
    if (verifyPin.isPending) return;
    setDigits((prev) => prev.slice(0, -1));
  }, [verifyPin.isPending]);

  const handleClear = useCallback(() => {
    setDigits('');
    onClose();
  }, [onClose]);

  return {
    digits,
    hasError,
    isPending: verifyPin.isPending,
    handleDigitPress,
    handleBackspace,
    handleClear,
  };
}
