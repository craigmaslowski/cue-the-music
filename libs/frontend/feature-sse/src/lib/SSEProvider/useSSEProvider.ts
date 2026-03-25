import { albumKeys } from '@cue-the-music/data-access-collection';
import { queueKeys } from '@cue-the-music/data-access-queue';
import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useRef, useState } from 'react';

import type { ISSEProviderProps, IUseSSEProviderReturn } from './SSEProvider-types';

const DEFAULT_URL =
  (typeof import.meta !== 'undefined' &&
    import.meta.env?.VITE_API_BASE_URL) ||
  'http://localhost:8000';

const STALENESS_TIMEOUT_MS = 45_000;

/** Encapsulates SSE connection lifecycle, reconnection, and cache invalidation. */
export function useSSEProvider(props: ISSEProviderProps): IUseSSEProviderReturn {
  const { url } = props;
  const sseUrl = `${url ?? DEFAULT_URL}/api/events`;

  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);

  // Track in-flight mutations to defer SSE invalidation
  const inFlightKeysRef = useRef<Set<string>>(new Set());
  const deferredInvalidationsRef = useRef<Set<string>>(new Set());
  const eventSourceRef = useRef<EventSource | null>(null);
  const stalenessTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /** Register that a mutation is in flight for a given key prefix. */
  const registerInflight = useCallback((keyPrefix: string) => {
    inFlightKeysRef.current.add(keyPrefix);
  }, []);

  /** Unregister a mutation and flush any deferred invalidations. */
  const unregisterInflight = useCallback(
    (keyPrefix: string) => {
      inFlightKeysRef.current.delete(keyPrefix);

      if (deferredInvalidationsRef.current.has(keyPrefix)) {
        deferredInvalidationsRef.current.delete(keyPrefix);
        void queryClient.invalidateQueries({ queryKey: [keyPrefix] });
      }
    },
    [queryClient],
  );

  /** Invalidate or defer, depending on in-flight mutation state. */
  const invalidateOrDefer = useCallback(
    (queryKey: readonly string[]) => {
      const prefix = queryKey[0];
      if (inFlightKeysRef.current.has(prefix)) {
        deferredInvalidationsRef.current.add(prefix);
      } else {
        void queryClient.invalidateQueries({ queryKey });
      }
    },
    [queryClient],
  );

  /** Reset staleness timer — called on every SSE message. */
  const resetStalenessTimer = useCallback(() => {
    if (stalenessTimerRef.current) {
      clearTimeout(stalenessTimerRef.current);
    }
    stalenessTimerRef.current = setTimeout(() => {
      // Connection is stale — tear down and reconnect
      eventSourceRef.current?.close();
      setIsConnected(false);
    }, STALENESS_TIMEOUT_MS);
  }, []);

  /** Create and configure an EventSource connection. */
  const connect = useCallback(() => {
    // Clean up any existing connection
    eventSourceRef.current?.close();
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    const es = new EventSource(sseUrl);
    eventSourceRef.current = es;

    es.onopen = () => {
      setIsConnected(true);
      resetStalenessTimer();
    };

    es.addEventListener('queue_update', () => {
      invalidateOrDefer(queueKeys.all);
      resetStalenessTimer();
    });

    es.addEventListener('vote_update', () => {
      invalidateOrDefer(queueKeys.all);
      resetStalenessTimer();
    });

    es.addEventListener('collection_sync', () => {
      invalidateOrDefer(albumKeys.all);
      resetStalenessTimer();
    });

    // Heartbeat / keep-alive events just reset staleness
    es.addEventListener('heartbeat', () => {
      resetStalenessTimer();
    });

    es.onerror = () => {
      setIsConnected(false);
      es.close();

      // Auto-reconnect after a short delay
      reconnectTimerRef.current = setTimeout(() => {
        connect();
      }, 3_000);
    };
  }, [sseUrl, invalidateOrDefer, resetStalenessTimer]);

  // Main connection effect
  useEffect(() => {
    connect();

    return () => {
      eventSourceRef.current?.close();
      if (stalenessTimerRef.current) {
        clearTimeout(stalenessTimerRef.current);
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [connect]);

  // Visibility change: reconnect on tab becoming visible
  useEffect(() => {
    function handleVisibilityChange() {
      if (document.visibilityState === 'visible') {
        // Force reconnect and invalidate SSE-driven keys
        connect();
        void queryClient.invalidateQueries({ queryKey: queueKeys.all });
        void queryClient.invalidateQueries({ queryKey: albumKeys.all });
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [connect, queryClient]);

  // Subscribe to mutation cache for in-flight tracking
  useEffect(() => {
    const unsubscribe = queryClient.getMutationCache().subscribe((event) => {
      if (!event.mutation) return;

      const mutationKey = event.mutation.options.mutationKey;
      if (!mutationKey || mutationKey.length === 0) return;

      const prefix = String(mutationKey[0]);

      if (event.type === 'updated') {
        const state = event.mutation.state;
        if (state.status === 'pending') {
          registerInflight(prefix);
        } else {
          // settled (success or error)
          unregisterInflight(prefix);
        }
      }
    });

    return unsubscribe;
  }, [queryClient, registerInflight, unregisterInflight]);

  return {
    isConnected,
  };
}
