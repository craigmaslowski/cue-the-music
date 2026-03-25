import type { ISyncResponse, IVerifyPinResponse } from '@cue-the-music/core-types';
import { ApiError } from '@cue-the-music/data-access-collection';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { hostFetch } from './host-fetch';
import { queueKeys } from './host-keys';

/** Mutation hook for POST /api/host/verify-pin. */
export function useVerifyPin() {
  return useMutation<IVerifyPinResponse, ApiError, { pin: string }>({
    mutationFn: (body) =>
      hostFetch<IVerifyPinResponse>('/api/host/verify-pin', null, {
        method: 'POST',
        body: JSON.stringify(body),
      }),
  });
}

interface IHostMutationOptions {
  onUnauthorized?: () => void;
  token: string | null;
}

/** Mutation hook for POST /api/host/now-playing — promotes a queue item. */
export function usePromoteToNowPlaying(options: IHostMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, { queue_item_id: number }>({
    mutationFn: (body) =>
      hostFetch(
        '/api/host/now-playing',
        options.token,
        {
          method: 'POST',
          body: JSON.stringify(body),
        },
        options.onUnauthorized,
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

/** Mutation hook for DELETE /api/host/now-playing — clears now playing. */
export function useClearNowPlaying(options: IHostMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, void>({
    mutationFn: () =>
      hostFetch(
        '/api/host/now-playing',
        options.token,
        { method: 'DELETE' },
        options.onUnauthorized,
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

/** Mutation hook for DELETE /api/host/queue/{id} — removes a queue item. */
export function useRemoveQueueItem(options: IHostMutationOptions) {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, { id: number }>({
    mutationFn: ({ id }) =>
      hostFetch(
        `/api/host/queue/${id}`,
        options.token,
        { method: 'DELETE' },
        options.onUnauthorized,
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

/** Mutation hook for POST /api/host/sync — triggers Discogs sync. */
export function useTriggerSync(options: IHostMutationOptions) {
  return useMutation<ISyncResponse, ApiError, void>({
    mutationFn: () =>
      hostFetch<ISyncResponse>(
        '/api/host/sync',
        options.token,
        { method: 'POST' },
        options.onUnauthorized,
      ),
  });
}
