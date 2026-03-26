import { css } from '@styled-system/css';

/** 2-column responsive grid for album cards */
export const gridStyles = css({
  display: 'grid',
  gap: '4',
  gridTemplateColumns: 'repeat(2, 1fr)',
  padding: '3',
});
