import { createFileRoute } from '@tanstack/react-router';

import { CratePage } from '../app/pages/CratePage';

/** The Crate — browse the host's vinyl collection. */
export const Route = createFileRoute('/crate')({
  component: CratePage,
  errorComponent: CrateErrorComponent,
  pendingComponent: CratePendingComponent,
});

function CrateErrorComponent() {
  return (
    <div style={{ color: '#ffffff', padding: '2rem', textAlign: 'center' }}>
      <p>Could not load the collection. Please try again.</p>
    </div>
  );
}

function CratePendingComponent() {
  return (
    <div style={{ color: '#9e9e9e', padding: '2rem', textAlign: 'center' }}>
      Loading collection...
    </div>
  );
}
