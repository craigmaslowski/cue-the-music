import type {
  IAlbum,
  IAlbumFilterValues,
  IAlbumFilters,
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

/** Build query params string from album filters. */
function buildFilterParams(filters: IAlbumFilters): string {
  const params = new URLSearchParams();

  if (filters.search) {
    params.set('search', filters.search);
  }
  if (filters.genres?.length) {
    for (const genre of filters.genres) {
      params.append('genre', genre);
    }
  }
  if (filters.decades?.length) {
    for (const decade of filters.decades) {
      params.append('decade', decade);
    }
  }

  const str = params.toString();
  return str ? `?${str}` : '';
}

/** Query options for the album list — reusable for loaders and hooks. */
export function albumListQueryOptions(filters: IAlbumFilters) {
  return queryOptions({
    queryKey: albumKeys.list(filters),
    queryFn: () =>
      apiFetch<IAlbumListResponse>(
        `/api/albums${buildFilterParams(filters)}`,
      ),
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

/** Query options for available filter values. */
export function albumFiltersQueryOptions() {
  return queryOptions({
    queryKey: albumKeys.filters(),
    queryFn: () => apiFetch<IAlbumFilterValues>('/api/album-filters'),
    staleTime: COLLECTION_STALE_TIME,
  });
}

/** Fetch albums with server-side search, genre, and decade filters. */
export function useAlbums(filters: IAlbumFilters) {
  return useSuspenseQuery(albumListQueryOptions(filters));
}

/** Fetch a single album detail with placeholder data from cache. */
export function useAlbum(id: number) {
  const queryClient = useQueryClient();

  return useSuspenseQuery({
    ...albumDetailQueryOptions(id),
    placeholderData: () => {
      // Try to find this album in any cached list query
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

/** Fetch available filter values (genres and decades). */
export function useAlbumFilters() {
  return useSuspenseQuery(albumFiltersQueryOptions());
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
