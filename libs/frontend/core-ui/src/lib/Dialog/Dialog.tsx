import { Dialog as ArkDialog, Portal } from '@ark-ui/react';

import {
  backdropStyles,
  closeTriggerStyles,
  contentStyles,
  descriptionStyles,
  positionerStyles,
  scrollBodyStyles,
  titleStyles,
} from './Dialog-elements';
import type { IDialogProps } from './Dialog-types';
import { useDialog } from './useDialog';

/** Wrapped Ark UI Dialog with project theme styling. */
export function Dialog(props: IDialogProps) {
  const { children, description, title } = props;
  const { handleOpenChange, open } = useDialog(props);

  return (
    <ArkDialog.Root onOpenChange={handleOpenChange} open={open}>
      <Portal>
        <ArkDialog.Backdrop className={backdropStyles} />
        <ArkDialog.Positioner className={positionerStyles}>
          <ArkDialog.Content className={contentStyles}>
            <ArkDialog.Title className={titleStyles}>{title}</ArkDialog.Title>
            {description && (
              <ArkDialog.Description className={descriptionStyles}>
                {description}
              </ArkDialog.Description>
            )}
            <div className={scrollBodyStyles}>{children}</div>
            <ArkDialog.CloseTrigger className={closeTriggerStyles}>
              ✕
            </ArkDialog.CloseTrigger>
          </ArkDialog.Content>
        </ArkDialog.Positioner>
      </Portal>
    </ArkDialog.Root>
  );
}
