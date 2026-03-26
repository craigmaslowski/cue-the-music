import { css } from '@styled-system/css';

/** Container for host queue controls */
export const rootStyles = css({
  alignItems: 'center',
  display: 'flex',
  gap: '2',
  marginTop: '2',
});

/** Play/promote button — green accent */
export const promoteButtonStyles = css({
  alignItems: 'center',
  background: 'linear-gradient(135deg, token(colors.primary), token(colors.primary.container))',
  borderRadius: 'full',
  borderWidth: '0',
  color: 'primary.onFixed',
  cursor: 'pointer',
  display: 'flex',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 700,
  gap: '1',
  letterSpacing: 'tight',
  padding: '3 5',
  textTransform: 'uppercase',
  transition: 'opacity 0.2s ease',
  _active: {
    opacity: 0.8,
  },
});

/** Remove/skip button — pink/red accent */
export const removeButtonStyles = css({
  alignItems: 'center',
  backgroundColor: 'transparent',
  borderColor: 'rgba(255, 107, 155, 0.3)',
  borderRadius: 'full',
  borderWidth: '1px',
  color: 'secondary',
  cursor: 'pointer',
  display: 'flex',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 700,
  gap: '1',
  letterSpacing: 'tight',
  padding: '3 5',
  textTransform: 'uppercase',
  transition: 'opacity 0.2s ease',
  _active: {
    opacity: 0.8,
  },
});

/** Down-vote count badge — highlighted when skip signal */
export const skipBadgeStyles = css({
  alignItems: 'center',
  backgroundColor: 'rgba(255, 107, 155, 0.15)',
  borderRadius: 'full',
  color: 'secondary',
  display: 'flex',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 700,
  gap: '1',
  padding: '2 3',
});

/** Prominent skip signal highlight */
export const skipSignalStyles = css({
  backgroundColor: 'rgba(255, 107, 155, 0.3)',
  boxShadow: '0 0 8px rgba(255, 107, 155, 0.2)',
});
