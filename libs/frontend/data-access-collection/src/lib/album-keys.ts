import type { IAlbumFilters } from '@cue-the-music/core-types';

/** TanStack Query key factory for album-related queries. */
export const albumKeys = {
  all: ['albums'] as const,
  details: () => [...albumKeys.all, 'detail'] as const,
  detail: (id: number) => [...albumKeys.details(), id] as const,
  lists: () => [...albumKeys.all, 'list'] as const,
  list: (filters: IAlbumFilters) => [...albumKeys.lists(), filters] as const,
  filters: () => [...albumKeys.all, 'filters'] as const,
};
