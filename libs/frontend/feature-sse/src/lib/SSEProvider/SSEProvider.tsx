import type { ISSEProviderProps } from './SSEProvider-types';
import { useSSEProvider } from './useSSEProvider';

/**
 * SSE provider that opens a single EventSource connection to the backend
 * and invalidates TanStack Query caches when server events arrive.
 * Place at the app root, inside QueryClientProvider.
 */
export function SSEProvider(props: ISSEProviderProps) {
  const { children } = props;
  useSSEProvider(props);

  return <>{children}</>;
}
