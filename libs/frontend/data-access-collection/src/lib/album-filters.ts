import type {
  IAlbum,
  IAlbumFilterValues,
  IAlbumFilters,
  IGenreCount,
} from '@cue-the-music/core-types';

/** Derive available filter values (genres with counts, decades) from the full album set. */
export function deriveFilterValues(albums: IAlbum[]): IAlbumFilterValues {
  // Count genres across both genre_tags and style_tags, deduplicating within each album
  const genreCounts = new Map<string, number>();
  for (const album of albums) {
    const allTags = [
      ...(album.genre_tags ?? []),
      ...(album.style_tags ?? []),
    ];
    const unique = new Set(allTags);
    for (const tag of unique) {
      genreCounts.set(tag, (genreCounts.get(tag) ?? 0) + 1);
    }
  }

  const genres: IGenreCount[] = [...genreCounts.entries()]
    .map(([genre, count]) => ({ count, genre }))
    .sort((a, b) => b.count - a.count || a.genre.localeCompare(b.genre));

  // Extract unique decades from album years, excluding nulls
  const decadeSet = new Set<number>();
  for (const album of albums) {
    if (album.year != null) {
      decadeSet.add(Math.floor(album.year / 10) * 10);
    }
  }
  const decades = [...decadeSet].sort((a, b) => a - b);

  return { decades, genres };
}

/** Filter albums by search text, genres, and decades (all client-side). */
export function filterAlbums(
  albums: IAlbum[],
  filters: IAlbumFilters,
): IAlbum[] {
  return albums.filter((album) => {
    // Search: case-insensitive match on artist or title
    if (filters.search) {
      const term = filters.search.toLowerCase();
      if (
        !album.artist.toLowerCase().includes(term) &&
        !album.title.toLowerCase().includes(term)
      ) {
        return false;
      }
    }

    // Genre filter (OR): album must have at least one matching genre/style tag
    if (filters.genres?.length) {
      const albumTags = [
        ...(album.genre_tags ?? []),
        ...(album.style_tags ?? []),
      ];
      if (!filters.genres.some((g) => albumTags.includes(g))) {
        return false;
      }
    }

    // Decade filter (OR): album.year must fall within at least one selected decade
    if (filters.decades?.length) {
      if (album.year == null) return false;
      const albumDecade = Math.floor(album.year / 10) * 10;
      if (!filters.decades.some((d) => Number(d) === albumDecade)) {
        return false;
      }
    }

    return true;
  });
}
