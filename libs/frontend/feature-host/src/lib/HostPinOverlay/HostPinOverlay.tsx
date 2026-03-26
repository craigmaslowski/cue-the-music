import {
  actionKeyStyles,
  clearKeyStyles,
  dotContainerStyles,
  dotErrorStyles,
  dotFilledStyles,
  dotStyles,
  keyStyles,
  keypadStyles,
  lockIconStyles,
  overlayStyles,
  shakeStyles,
  subtitleStyles,
  titleStyles,
} from './HostPinOverlay-elements';
import type { IHostPinOverlayProps } from './HostPinOverlay-types';
import { useHostPinOverlay } from './useHostPinOverlay';

const DIGITS = ['1', '2', '3', '4', '5', '6', '7', '8', '9'];
const PIN_LENGTH = 4;

/** Full-screen PIN entry overlay for host mode activation. */
export function HostPinOverlay(props: IHostPinOverlayProps) {
  const { isOpen } = props;
  const {
    digits,
    hasError,
    handleDigitPress,
    handleBackspace,
    handleClear,
  } = useHostPinOverlay(props);

  if (!isOpen) return null;

  return (
    <div className={overlayStyles}>
      {/* Lock icon */}
      <div className={lockIconStyles}>
        <span role="img" aria-label="Lock">
          &#x1F513;
        </span>
      </div>

      {/* Title */}
      <h2 className={titleStyles}>Host Access</h2>
      <p className={subtitleStyles}>
        Unlock host controls for the party queue.
      </p>

      {/* PIN dots */}
      <div
        className={`${dotContainerStyles}${hasError ? ` ${shakeStyles}` : ''}`}
      >
        {Array.from({ length: PIN_LENGTH }).map((_, i) => {
          const isFilled = i < digits.length;
          const dotClass = hasError
            ? `${dotStyles} ${dotErrorStyles}`
            : isFilled
              ? `${dotStyles} ${dotFilledStyles}`
              : dotStyles;
          return <div key={i} className={dotClass} />;
        })}
      </div>

      {/* Numeric keypad */}
      <div className={keypadStyles}>
        {DIGITS.map((digit) => (
          <button
            key={digit}
            className={keyStyles}
            onClick={() => handleDigitPress(digit)}
            type="button"
          >
            {digit}
          </button>
        ))}

        {/* Bottom row: clear, 0, backspace */}
        <button
          className={`${actionKeyStyles} ${clearKeyStyles}`}
          onClick={handleClear}
          type="button"
        >
          &#x2715;
        </button>
        <button
          className={keyStyles}
          onClick={() => handleDigitPress('0')}
          type="button"
        >
          0
        </button>
        <button
          className={actionKeyStyles}
          onClick={handleBackspace}
          type="button"
          aria-label="Backspace"
        >
          &#x232B;
        </button>
      </div>
    </div>
  );
}
