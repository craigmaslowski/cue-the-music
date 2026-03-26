import { css } from '@styled-system/css';

/** Root container for a single queue item */
export const rootStyles = css({
  // alignItems: 'center',
  backgroundColor: 'surface.containerLow',
  borderRadius: 'xl',
  display: 'flex',
  flexDirection: 'column',
  gap: '3',
  padding: '3',
});

export const albumMetaStyles = css({
  display: 'flex',
  gap: '4',
});

/** Album thumbnail in the queue item */
export const thumbnailStyles = css({
  backgroundColor: 'surface.container',
  borderRadius: 'xl',
  flexShrink: 0,
  height: '3.5rem',
  objectFit: 'cover',
  width: '3.5rem',
});

/** Text content: title and artist */
export const infoStyles = css({
  display: 'flex',
  flex: 1,
  flexDirection: 'column',
  gap: '0.5',
  minWidth: 0,
});

/** Album title in the queue item */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'bodyLg',
  fontWeight: 600,
  letterSpacing: 'tight',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap',
});

/** Artist name in the queue item */
export const artistStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap',
});

/** Actions column: votes and cancel */
export const actionsStyles = css({
  alignItems: 'center',
  display: 'flex',
  flexShrink: 0,
  gap: '2',
});

/** Cancel button — only visible for own requests */
export const cancelButtonStyles = css({
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontSize: 'labelMd',
  fontFamily: 'body',
  padding: '1',
  transition: 'color 0.15s ease',
  _hover: {
    color: 'secondary',
  },
  _disabled: {
    cursor: 'not-allowed',
    opacity: 0.5,
  },
});
