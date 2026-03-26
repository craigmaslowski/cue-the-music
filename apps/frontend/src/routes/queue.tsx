import { createFileRoute } from '@tanstack/react-router';

import { QueuePage } from '../app/pages/QueuePage';

/** The Queue — view and vote on requested albums. */
export const Route = createFileRoute('/queue')({
  component: QueuePage,
  errorComponent: QueueErrorComponent,
  pendingComponent: QueuePendingComponent,
});

function QueueErrorComponent() {
  return (
    <div style={{ color: '#ffffff', padding: '2rem', textAlign: 'center' }}>
      <p>Could not load the queue. Please try again.</p>
    </div>
  );
}

function QueuePendingComponent() {
  return (
    <div style={{ color: '#9e9e9e', padding: '2rem', textAlign: 'center' }}>
      Loading queue...
    </div>
  );
}
