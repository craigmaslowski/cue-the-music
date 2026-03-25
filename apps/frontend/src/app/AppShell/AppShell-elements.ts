import { css } from '@styled-system/css';

/** Main content area between header and bottom nav */
export const contentStyles = css({
  flex: 1,
  overflow: 'auto',
});

/** Header bar with app title and host mode lock icon */
export const headerStyles = css({
  alignItems: 'center',
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(14, 14, 14, 0.9)',
  display: 'flex',
  justifyContent: 'space-between',
  padding: '4',
  position: 'sticky',
  top: 0,
  zIndex: 10,
});

/** Lock icon button placeholder for host mode */
export const lockIconStyles = css({
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontSize: 'bodyLg',
  padding: '2',
});

/** App root container — full viewport, dark background */
export const rootStyles = css({
  backgroundColor: 'surface',
  color: 'onSurface',
  display: 'flex',
  flexDirection: 'column',
  fontFamily: 'body',
  height: '100dvh',
  overflow: 'hidden',
  width: '100%',
});

/** Tab list container — bottom navigation bar */
export const tabListStyles = css({
  backdropFilter: 'blur(token(blurs.glass))',
  backgroundColor: 'rgba(26, 26, 26, 0.9)',
  display: 'flex',
  justifyContent: 'space-around',
  paddingBottom: 'env(safe-area-inset-bottom)',
  width: '100%',
});

/** Tabs root — flexbox column filling remaining space */
export const tabRootStyles = css({
  display: 'flex',
  flex: 1,
  flexDirection: 'column',
  overflow: 'hidden',
});

/** Individual tab trigger in the bottom nav */
export const tabTriggerStyles = css({
  backgroundColor: 'transparent',
  borderWidth: '0',
  color: 'onSurface.variant',
  cursor: 'pointer',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 600,
  letterSpacing: 'tight',
  padding: '3',
  textTransform: 'uppercase',
  transition: 'color 0.2s ease',
  width: '50%',
  _selected: {
    color: 'primary',
  },
});

/** App title in the header */
export const titleStyles = css({
  color: 'primary',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
  letterSpacing: 'tight',
});
