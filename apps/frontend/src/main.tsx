import { SSEProvider } from '@cue-the-music/feature-sse';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { StrictMode } from 'react';
import * as ReactDOM from 'react-dom/client';

import { routeTree } from './routeTree.gen';

// Create a TanStack Query client for server state management
const queryClient = new QueryClient();

// Create the TanStack Router instance with the generated route tree
const router = createRouter({
  routeTree,
  context: { queryClient },
});

// Register the router type for type-safe route references
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement,
);

root.render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <SSEProvider>
        <RouterProvider router={router} />
      </SSEProvider>
    </QueryClientProvider>
  </StrictMode>,
);
