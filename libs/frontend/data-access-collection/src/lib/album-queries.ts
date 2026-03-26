import type {
  IAlbum,
  IAlbumListResponse,
} from '@cue-the-music/core-types';
import {
  queryOptions,
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';

import { albumKeys } from './album-keys';
import { ApiError, apiFetch } from './api-client';

const COLLECTION_STALE_TIME = 60_000;

/** Query options for the full album list (unfiltered). */
export function albumListQueryOptions() {
  return queryOptions({
    queryKey: albumKeys.lists(),
    queryFn: () => apiFetch<IAlbumListResponse>('/api/albums'),
    staleTime: COLLECTION_STALE_TIME,
  });
}

/** Query options for a single album detail. */
export function albumDetailQueryOptions(id: number) {
  return queryOptions({
    queryKey: albumKeys.detail(id),
    queryFn: () => apiFetch<IAlbum>(`/api/albums/${id}`),
    staleTime: COLLECTION_STALE_TIME,
  });
}

/** Fetch all albums (unfiltered, single cache entry). */
export function useAlbums() {
  return useSuspenseQuery(albumListQueryOptions());
}

/** Fetch a single album detail with placeholder data from cache. */
export function useAlbum(id: number) {
  const queryClient = useQueryClient();

  return useSuspenseQuery({
    ...albumDetailQueryOptions(id),
    initialData: () => {
      // Try to find this album in the cached list query
      const listQueries = queryClient.getQueriesData<IAlbumListResponse>({
        queryKey: albumKeys.lists(),
      });

      for (const [, data] of listQueries) {
        const found = data?.albums.find((album) => album.id === id);
        if (found) {
          return found;
        }
      }

      return undefined;
    },
  });
}

/** Request body for adding an album to the queue. */
interface IRequestAlbumBody {
  album_id: number;
}

/** Mutation result state for the request album action. */
export interface IRequestAlbumResult {
  /** The 409 status means album is already in queue. */
  alreadyInQueue: boolean;
  /** The 429 status means request limit reached. */
  limitReached: boolean;
}

/** Mutation hook for POST /api/queue to request an album. */
export function useRequestAlbum() {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, IRequestAlbumBody>({
    mutationFn: (body: IRequestAlbumBody) =>
      apiFetch('/api/queue', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['queue'] });
    },
  });
}
