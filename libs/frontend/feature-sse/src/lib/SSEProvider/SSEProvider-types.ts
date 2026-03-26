import type { ReactNode } from 'react';

export interface ISSEProviderProps {
  /** Child components that benefit from SSE-driven cache invalidation */
  children: ReactNode;
  /** SSE endpoint URL (defaults to VITE_API_BASE_URL + /api/events) */
  url?: string;
}

export interface IUseSSEProviderReturn {
  /** Whether the SSE connection is currently open */
  isConnected: boolean;
}
