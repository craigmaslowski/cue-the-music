import { css } from '@styled-system/css';

/** Root container for the crate view */
export const rootStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '2',
  minHeight: '100%',
  paddingBottom: '4',
});

/** No-results message container */
export const noResultsStyles = css({
  alignItems: 'center',
  color: 'onSurface.variant',
  display: 'flex',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  justifyContent: 'center',
  padding: '12',
  textAlign: 'center',
});
