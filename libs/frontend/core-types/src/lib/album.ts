/**
 * Album API types — derived from the generated OpenAPI schema.
 * Do not hand-write API response types; regenerate from the backend instead.
 */

import type { components } from './generated-api';

/** Album data as returned by the backend API. */
export type IAlbum = components['schemas']['AlbumGetResponse'];

/** Paginated album list response from the API. */
export type IAlbumListResponse = components['schemas']['AlbumListResponse'];

/** A genre tag paired with its album count (client-side derived). */
export interface IGenreCount {
  count: number;
  genre: string;
}

/** Available filter values derived client-side from the full album set. */
export interface IAlbumFilterValues {
  decades: number[];
  genres: IGenreCount[];
}

/** Filters applied when filtering the album collection (client-side). */
export interface IAlbumFilters {
  decades?: string[];
  genres?: string[];
  search?: string;
}
