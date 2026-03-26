import { css } from '@styled-system/css';

/** Close button for the toast notification */
export const closeTriggerStyles = css({
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontSize: 'bodyLg',
  padding: '1',
});

/** Description text below the title */
export const descriptionStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  marginTop: '1',
});

/** Root toast container — floats in corner with themed background */
export const rootStyles = css({
  backgroundColor: 'surface.containerHighest',
  borderRadius: 'xl',
  boxShadow: 'ambient',
  display: 'flex',
  gap: '3',
  justifyContent: 'space-between',
  maxWidth: '360px',
  minWidth: '280px',
  padding: '4',
});

/** Title text of the toast */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'bodyLg',
  fontWeight: 600,
});

/** Accent bar color per variant — applied as a left border */
export const variantAccent = {
  error: css({ borderLeftColor: 'secondary', borderLeftWidth: '3px' }),
  info: css({ borderLeftColor: 'tertiary', borderLeftWidth: '3px' }),
  success: css({ borderLeftColor: 'primary.container', borderLeftWidth: '3px' }),
} as const;
