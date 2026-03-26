/**
 * Album API types — derived from the generated OpenAPI schema.
 * Do not hand-write API response types; regenerate from the backend instead.
 */

import type { components } from './generated-api';

/** Album data as returned by the backend API. */
export type IAlbum = components['schemas']['AlbumGetResponse'];

/** Available filter values returned by the album-filters endpoint. */
export type IAlbumFilterValues = components['schemas']['AlbumFilterGetResponse'];

/** Paginated album list response from the API. */
export type IAlbumListResponse = components['schemas']['AlbumListResponse'];

/** Filters applied when fetching the album collection (client-side type). */
export interface IAlbumFilters {
  decades?: string[];
  genres?: string[];
  search?: string;
}
