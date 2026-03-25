import { apiFetch } from '@cue-the-music/data-access-collection';
import {
  queryOptions,
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';

import { queueKeys } from './queue-keys';
import type { IQueueState, IVoteBody } from './queue-types';

/** Query options for the queue — reusable for loaders and hooks. */
export function queueQueryOptions() {
  return queryOptions({
    queryKey: queueKeys.all,
    queryFn: () => apiFetch<IQueueState>('/api/queue'),
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  });
}

/** Fetch the current queue state. SSE invalidation drives refreshes. */
export function useQueue() {
  return useSuspenseQuery(queueQueryOptions());
}

/** Mutation hook for DELETE /api/queue/{id} — cancel a queue request. */
export function useCancelRequest() {
  const queryClient = useQueryClient();

  return useMutation<unknown, Error, { id: number }>({
    mutationFn: ({ id }) =>
      apiFetch(`/api/queue/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

/** Mutation hook for PUT /api/queue/{id}/vote — cast an up or down vote. */
export function useVote() {
  const queryClient = useQueryClient();

  return useMutation<unknown, Error, { id: number; value: 1 | -1 }>({
    mutationFn: ({ id, value }) => {
      const body: IVoteBody = { value };
      return apiFetch(`/api/queue/${id}/vote`, {
        method: 'PUT',
        body: JSON.stringify(body),
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}

/** Mutation hook for DELETE /api/queue/{id}/vote — remove own vote. */
export function useRemoveVote() {
  const queryClient = useQueryClient();

  return useMutation<unknown, Error, { id: number }>({
    mutationFn: ({ id }) =>
      apiFetch(`/api/queue/${id}/vote`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}
