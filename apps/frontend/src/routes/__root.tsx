import type { QueryClient } from '@tanstack/react-query';
import {
  Outlet,
  createRootRouteWithContext,
} from '@tanstack/react-router';

import { AppShell } from '../app/AppShell/AppShell';

interface IRouterContext {
  queryClient: QueryClient;
}

/** Root route providing the app shell (header + bottom nav) to all child routes. */
export const Route = createRootRouteWithContext<IRouterContext>()({
  component: RootComponent,
  errorComponent: RootErrorComponent,
  pendingComponent: RootPendingComponent,
});

function RootComponent() {
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

function RootErrorComponent() {
  return (
    <AppShell>
      <div style={{ color: '#ffffff', padding: '2rem', textAlign: 'center' }}>
        <h2>Something went wrong</h2>
        <p>Please refresh the page and try again.</p>
      </div>
    </AppShell>
  );
}

function RootPendingComponent() {
  return (
    <AppShell>
      <div style={{ color: '#9e9e9e', padding: '2rem', textAlign: 'center' }}>
        Loading...
      </div>
    </AppShell>
  );
}
