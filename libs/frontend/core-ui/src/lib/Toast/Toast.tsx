import { Toast as ArkToast } from '@ark-ui/react';

import {
  closeTriggerStyles,
  descriptionStyles,
  rootStyles,
  titleStyles,
  variantAccent,
} from './Toast-elements';
import type { IToastProps } from './Toast-types';
import { useToast } from './useToast';

/** Themed toast notification with variant accent colors. */
export function Toast(props: IToastProps) {
  const { description, title } = props;
  const { handleClose, variant } = useToast(props);

  return (
    <ArkToast.Root className={`${rootStyles} ${variantAccent[variant]}`}>
      <div>
        <ArkToast.Title className={titleStyles}>{title}</ArkToast.Title>
        {description && (
          <ArkToast.Description className={descriptionStyles}>
            {description}
          </ArkToast.Description>
        )}
      </div>
      <ArkToast.CloseTrigger
        className={closeTriggerStyles}
        onClick={handleClose}
      >
        ✕
      </ArkToast.CloseTrigger>
    </ArkToast.Root>
  );
}
