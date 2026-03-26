import { css } from '@styled-system/css';

/** Full-size cover art image */
export const coverArtStyles = css({
  aspectRatio: '1',
  backgroundColor: 'surface.container',
  borderRadius: 'xl',
  display: 'block',
  height: 'auto',
  objectFit: 'cover',
  width: '100%',
});

/** Album metadata section below cover art */
export const metadataStyles = css({
  display: 'flex',
  flexDirection: 'column',
  gap: '1',
  marginTop: '4',
});

/** Album title in overlay */
export const titleStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
  lineHeight: '32px',
});

/** Artist name in overlay */
export const artistLineStyles = css({
  color: 'onSurface',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  textTransform: 'uppercase',
});

export const artistStyles = css({
  color: 'primary',
  fontSize: 'bodyXl',
  fontWeight: '700',
});

/** Label and year info line */
export const labelStyles = css({
  color: 'secondary',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  fontWeight: '600',
  letterSpacing: 'tighter',
  textTransform: 'uppercase',
});

/** Container for genre/style chips */
export const chipContainerStyles = css({
  display: 'flex',
  flexWrap: 'wrap',
  gap: '2',
  marginTop: '3',
});

/** Individual genre/style chip in detail view */
export const genreChipStyles = css({
  backgroundColor: 'surface.container',
  borderColor: 'surface.containerHighest',
  borderRadius: 'full',
  borderWidth: '1px',
  color: 'tertiary',
  fontFamily: 'body',
  fontSize: 'labelMd',
  fontWeight: '600',
  paddingBlock: '1',
  paddingInline: '2.5',
  textTransform: 'uppercase',
});

/** Tracklist section */
export const tracklistSectionStyles = css({
  marginTop: '5',
});

/** Tracklist heading */
export const tracklistHeadingStyles = css({
  alignItems: 'center',
  color: 'onSurface',
  display: 'flex',
  fontFamily: 'heading',
  fontSize: 'bodyLg',
  fontWeight: 600,
  gap: '4',
  marginBottom: '3',
});

/** Single track row */
export const trackRowStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '3',
  paddingBlock: '2',
});

/** Track position (A1, B1, etc.) */
export const trackPositionStyles = css({
  color: 'primary',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  fontWeight: '600',
  minWidth: '2rem',
});

/** Track title */
export const trackTitleStyles = css({
  color: 'onSurface',
  flex: 1,
  fontFamily: 'body',
  fontSize: 'bodyLg',
});

/** Track duration */
export const trackDurationStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'labelMd',
});

/** Skeleton line for tracklist loading state */
export const skeletonLineStyles = css({
  animation: 'pulse 1.5s ease-in-out infinite',
  backgroundColor: 'surface.container',
  borderRadius: 'xl',
  height: '1rem',
  marginBottom: '2',
  width: '100%',
});

/** Primary action button — gradient neon style, sticky at bottom of scroll area */
export const requestButtonStyles = css({
  background:
    'linear-gradient(135deg, token(colors.primary), token(colors.primary.container))',
  borderRadius: 'full',
  bottom: 0,
  color: 'primary.onFixed',
  cursor: 'pointer',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  fontWeight: 600,
  marginTop: '5',
  paddingBlock: '3',
  paddingInline: '6',
  position: 'sticky',
  textAlign: 'center',
  transition: 'opacity 0.15s ease',
  width: '100%',
  zIndex: 1,
  _disabled: {
    cursor: 'not-allowed',
    opacity: 0.5,
  },
});

/** Button content wrapper for loading spinner */
export const buttonContentStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '2',
  justifyContent: 'center',
});
