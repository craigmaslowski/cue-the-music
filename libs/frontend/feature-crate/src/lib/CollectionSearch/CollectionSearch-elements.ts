import { css } from '@styled-system/css';

/** Root container for search + filters — sticky at top of scroll area */
export const rootStyles = css({
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(14, 14, 14, 0.9)',
  display: 'flex',
  flexDirection: 'column',
  gap: '3',
  paddingBlock: '3',
  position: 'sticky',
  top: 0,
  zIndex: 5,
});

/** Album count text below filters */
export const countStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelLg',
  paddingInline: '3',
});

/** Toggle button to show/hide filters */
export const toggleButtonStyles = css({
  alignItems: 'center',
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  display: 'flex',
  fontFamily: 'body',
  fontSize: 'labelMd',
  gap: '1',
  paddingInline: '3',
});

/** Filter chips section */
export const filtersStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '3',
  paddingInline: '3',
});

export const albumCountFiltersToggleStyles = css({
  display: 'flex',
  justifyContent: 'space-between',
  width: '100%',
});
