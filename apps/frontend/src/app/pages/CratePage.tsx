import { css } from '@styled-system/css';

const containerStyles = css({
  alignItems: 'center',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  padding: '12',
});

const headingStyles = css({
  color: 'onSurface',
  fontFamily: 'heading',
  fontSize: 'headlineLg',
  fontWeight: 700,
});

const subTextStyles = css({
  color: 'onSurface.variant',
  fontFamily: 'body',
  fontSize: 'bodyLg',
  marginTop: '4',
});

/** Placeholder page for The Crate — collection browsing comes in Phase 6. */
export function CratePage() {
  return (
    <div className={containerStyles}>
      <h2 className={headingStyles}>The Crate</h2>
      <p className={subTextStyles}>
        Browse the vinyl collection. Coming soon.
      </p>
    </div>
  );
}
