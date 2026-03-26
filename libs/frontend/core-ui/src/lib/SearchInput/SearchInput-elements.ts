import { css } from '@styled-system/css';

/** Text input field for search */
export const inputStyles = css({
  backgroundColor: 'surface.containerLow',
  borderRadius: 'full',
  borderWidth: '0',
  color: 'onSurface',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  outline: 'none',
  padding: '3',
  paddingLeft: '5',
  paddingRight: '5',
  width: '100%',
  _placeholder: {
    color: 'onSurface.variant',
  },
  _focus: {
    boxShadow: '0 0 0 2px token(colors.primary.container)',
  },
});

/** Clear button inside the input — absolute positioned right */
export const clearButtonStyles = css({
  alignItems: 'center',
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  display: 'flex',
  fontSize: 'bodyLg',
  justifyContent: 'center',
  padding: '2',
  position: 'absolute',
  right: '5',
  top: '50%',
  transform: 'translateY(-50%)',
});

/** Root container wrapping the input — relative for clear button positioning */
export const rootStyles = css({
  padding: '3',
  position: 'relative',
  width: '100%',
});
