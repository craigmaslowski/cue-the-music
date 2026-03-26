import { css } from '@styled-system/css';

/** Root container for the Now Playing section */
export const rootStyles = css({
  alignItems: 'center',
  display: 'flex',
  flexDirection: 'column',
  gap: '3',
  margin: '0 auto',
  padding: '2',
});

/** "NOW PLAYING" badge */
export const badgeStyles = css({
  backgroundColor: 'secondary.container',
  borderRadius: 'full',
  color: 'secondary.onContainer',
  display: 'inline-block',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 700,
  letterSpacing: 'tight',
  paddingBlock: '1',
  paddingInline: '3',
  textTransform: 'uppercase',
  width: 'fit-content',
});

/** Album cover art — prominent display */
export const coverArtStyles = css({
  aspectRatio: '1',
  backgroundColor: 'surface.container',
  borderRadius: 'xl',
  boxShadow: 'neonCyan',
  display: 'block',
  height: 'auto',
  maxWidth: '16rem',
  objectFit: 'cover',
  width: '100%',
});

/** Text info beside the cover art */
export const infoStyles = css({
  alignItems: 'center',
  display: 'flex',
  flex: 1,
  flexDirection: 'column',
  gap: '1',
  justifyContent: 'center',
  minWidth: 0,
});

/** Album title — display-level typography */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
  lineHeight: 1.1,
});

/** Artist name */
export const artistStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'bodyLg',
});

/** Empty state placeholder */
export const emptyStyles = css({
  alignItems: 'center',
  color: 'onSurface.variant',
  display: 'flex',
  flexDirection: 'column',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  gap: '2',
  padding: '8',
  textAlign: 'center',
});

/** Placeholder cover art slot when nothing is playing */
export const placeholderArtStyles = css({
  aspectRatio: '1',
  backgroundColor: 'surface.containerLow',
  borderRadius: 'xl',
  maxWidth: '16rem',
  width: '100%',
});
