import { css } from '@styled-system/css';

/** Sync button with neon accent */
export const buttonStyles = css({
  alignItems: 'center',
  background:
    'linear-gradient(135deg, token(colors.primary), token(colors.primary.container))',
  borderRadius: 'full',
  borderWidth: '0',
  color: 'primary.onFixed',
  cursor: 'pointer',
  display: 'flex',
  fontFamily: 'heading',
  fontSize: 'labelMd',
  fontWeight: 700,
  gap: '1.5',
  letterSpacing: 'tight',
  paddingBottom: '0.25rem',
  paddingLeft: '0.5rem',
  paddingRight: '0.5rem',
  paddingTop: '0.25rem',
  textTransform: 'uppercase',
  transition: 'opacity 0.2s ease',
  _disabled: {
    cursor: 'not-allowed',
    opacity: 0.7,
  },
});

/** Spinning loader icon */
export const spinnerStyles = css({
  animationDuration: '0.8s',
  animationIterationCount: 'infinite',
  animationName: 'spin',
  animationTimingFunction: 'linear',
  display: 'inline-block',
  fontSize: 'labelMd',
});
