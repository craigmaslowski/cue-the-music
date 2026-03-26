import { css } from '@styled-system/css';

/** Artist name below the title */
export const artistStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  whiteSpace: 'nowrap',
});

/** Album cover art image — 1:1 aspect ratio with lazy loading */
export const coverArtStyles = css({
  aspectRatio: '1',
  backgroundColor: 'surface.container',
  borderRadius: 'xl',
  display: 'block',
  height: 'auto',
  objectFit: 'cover',
  width: '100%',
});

/** Card root — uses ambient shadow, scale-down press animation */
export const rootStyles = css({
  backgroundColor: 'surface.containerHighest',
  borderRadius: 'xl',
  boxShadow: 'ambient',
  cursor: 'pointer',
  overflow: 'hidden',
  transition: 'transform 0.15s ease',
  _active: {
    transform: 'scale(0.98)',
  },
});

/** Text container below the cover art */
export const textContainerStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5',
  padding: '3',
});

/** Album title */
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

/** Release year label */
export const yearStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
});
