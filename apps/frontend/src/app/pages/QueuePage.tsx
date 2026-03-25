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

/** Placeholder page for the Queue — voting and requests come in Phase 7. */
export function QueuePage() {
  return (
    <div className={containerStyles}>
      <h2 className={headingStyles}>Queue</h2>
      <p className={subTextStyles}>
        Request and vote on albums. Coming soon.
      </p>
    </div>
  );
}
