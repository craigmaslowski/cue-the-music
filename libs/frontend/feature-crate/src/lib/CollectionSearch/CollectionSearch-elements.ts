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

/** Filter chips section */
export const filtersStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '3',
  paddingInline: '3',
});
