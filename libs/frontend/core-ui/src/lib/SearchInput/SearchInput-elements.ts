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

/** Root container wrapping the input */
export const rootStyles = css({
  padding: '3',
  width: '100%',
});
