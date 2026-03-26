import type { IAlbum } from '@cue-the-music/core-types';

import { deriveFilterValues, filterAlbums } from './album-filters';

/** Helper to create an album with sensible defaults. */
function makeAlbum(overrides: Partial<IAlbum> = {}): IAlbum {
  return {
    artist: 'Test Artist',
    cover_art_thumbnail_url: null,
    cover_art_url: null,
    created_at: '2026-01-01T00:00:00Z',
    discogs_release_id: '12345',
    genre_tags: ['Rock'],
    id: 1,
    label: null,
    style_tags: ['Punk'],
    title: 'Test Album',
    tracklist: null,
    updated_at: '2026-01-01T00:00:00Z',
    year: 1977,
    ...overrides,
  };
}

const ALBUMS: IAlbum[] = [
  makeAlbum({
    artist: 'Miles Davis',
    genre_tags: ['Jazz'],
    id: 1,
    style_tags: ['Modal'],
    title: 'Kind of Blue',
    year: 1959,
  }),
  makeAlbum({
    artist: 'The Clash',
    genre_tags: ['Rock'],
    id: 2,
    style_tags: ['Punk'],
    title: 'London Calling',
    year: 1979,
  }),
  makeAlbum({
    artist: 'Kraftwerk',
    genre_tags: ['Electronic'],
    id: 3,
    style_tags: ['Synth-pop'],
    title: 'Trans-Europe Express',
    year: 1977,
  }),
  makeAlbum({
    artist: 'Metallica',
    genre_tags: ['Rock', 'Metal'],
    id: 4,
    style_tags: ['Thrash'],
    title: 'Master of Puppets',
    year: 1986,
  }),
];

describe('filterAlbums', () => {
  it('returns all albums when no filters are applied', () => {
    const result = filterAlbums(ALBUMS, {});
    expect(result).toHaveLength(4);
  });

  it('returns empty array for empty album list', () => {
    const result = filterAlbums([], { search: 'test' });
    expect(result).toEqual([]);
  });

  describe('search', () => {
    it('matches artist case-insensitively', () => {
      const result = filterAlbums(ALBUMS, { search: 'miles' });
      expect(result).toHaveLength(1);
      expect(result[0].artist).toBe('Miles Davis');
    });

    it('matches title case-insensitively', () => {
      const result = filterAlbums(ALBUMS, { search: 'KIND OF BLUE' });
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('Kind of Blue');
    });

    it('returns empty when no match', () => {
      const result = filterAlbums(ALBUMS, { search: 'nonexistent' });
      expect(result).toEqual([]);
    });

    it('matches partial strings', () => {
      const result = filterAlbums(ALBUMS, { search: 'trans' });
      expect(result).toHaveLength(1);
      expect(result[0].artist).toBe('Kraftwerk');
    });
  });

  describe('genre filter', () => {
    it('matches genre_tags', () => {
      const result = filterAlbums(ALBUMS, { genres: ['Jazz'] });
      expect(result).toHaveLength(1);
      expect(result[0].artist).toBe('Miles Davis');
    });

    it('matches style_tags', () => {
      const result = filterAlbums(ALBUMS, { genres: ['Punk'] });
      expect(result).toHaveLength(1);
      expect(result[0].artist).toBe('The Clash');
    });

    it('uses OR logic for multiple genres', () => {
      const result = filterAlbums(ALBUMS, { genres: ['Jazz', 'Electronic'] });
      expect(result).toHaveLength(2);
      const artists = result.map((a) => a.artist);
      expect(artists).toContain('Miles Davis');
      expect(artists).toContain('Kraftwerk');
    });

    it('excludes albums with null genre_tags and style_tags', () => {
      const albumsWithNull = [
        ...ALBUMS,
        makeAlbum({
          artist: 'Unknown',
          genre_tags: null,
          id: 99,
          style_tags: null,
          title: 'No Tags',
        }),
      ];
      const result = filterAlbums(albumsWithNull, { genres: ['Rock'] });
      expect(result.find((a) => a.artist === 'Unknown')).toBeUndefined();
    });

    it('excludes albums with empty genre_tags and style_tags', () => {
      const albumsWithEmpty = [
        ...ALBUMS,
        makeAlbum({
          artist: 'Empty',
          genre_tags: [],
          id: 99,
          style_tags: [],
          title: 'Empty Tags',
        }),
      ];
      const result = filterAlbums(albumsWithEmpty, { genres: ['Rock'] });
      expect(result.find((a) => a.artist === 'Empty')).toBeUndefined();
    });
  });

  describe('decade filter', () => {
    it('matches correct year range', () => {
      const result = filterAlbums(ALBUMS, { decades: ['1970'] });
      expect(result).toHaveLength(2);
      const artists = result.map((a) => a.artist);
      expect(artists).toContain('The Clash');
      expect(artists).toContain('Kraftwerk');
    });

    it('uses OR logic for multiple decades', () => {
      const result = filterAlbums(ALBUMS, { decades: ['1950', '1980'] });
      expect(result).toHaveLength(2);
      const artists = result.map((a) => a.artist);
      expect(artists).toContain('Miles Davis');
      expect(artists).toContain('Metallica');
    });

    it('excludes albums with year: null', () => {
      const albumsWithNull = [
        ...ALBUMS,
        makeAlbum({ artist: 'Timeless', id: 99, title: 'No Year', year: null }),
      ];
      const result = filterAlbums(albumsWithNull, { decades: ['1970'] });
      expect(result.find((a) => a.artist === 'Timeless')).toBeUndefined();
    });

    it('includes albums with null year when no decade filter active', () => {
      const albumsWithNull = [
        ...ALBUMS,
        makeAlbum({ artist: 'Timeless', id: 99, title: 'No Year', year: null }),
      ];
      const result = filterAlbums(albumsWithNull, {});
      expect(result).toHaveLength(5);
    });
  });

  describe('combined filters', () => {
    it('uses AND across genre and decade', () => {
      const result = filterAlbums(ALBUMS, {
        decades: ['1970'],
        genres: ['Rock'],
      });
      expect(result).toHaveLength(1);
      expect(result[0].artist).toBe('The Clash');
    });

    it('uses AND for search + genre + decade', () => {
      const result = filterAlbums(ALBUMS, {
        decades: ['1970'],
        genres: ['Rock'],
        search: 'clash',
      });
      expect(result).toHaveLength(1);
      expect(result[0].title).toBe('London Calling');
    });

    it('search narrows within filtered set', () => {
      const result = filterAlbums(ALBUMS, {
        genres: ['Rock'],
        search: 'master',
      });
      expect(result).toHaveLength(1);
      expect(result[0].artist).toBe('Metallica');
    });
  });
});

describe('deriveFilterValues', () => {
  it('returns empty values for empty album list', () => {
    const result = deriveFilterValues([]);
    expect(result.decades).toEqual([]);
    expect(result.genres).toEqual([]);
  });

  it('counts genres across genre_tags and style_tags', () => {
    const result = deriveFilterValues(ALBUMS);
    const rockGenre = result.genres.find((g) => g.genre === 'Rock');
    expect(rockGenre).toBeDefined();
    // Rock appears in genre_tags for The Clash and Metallica
    expect(rockGenre!.count).toBe(2);
  });

  it('deduplicates genres within a single album', () => {
    const albumWithDups = [
      makeAlbum({
        genre_tags: ['Rock', 'Rock'],
        id: 1,
        style_tags: ['Rock'],
      }),
    ];
    const result = deriveFilterValues(albumWithDups);
    const rockGenre = result.genres.find((g) => g.genre === 'Rock');
    // Should count as 1 album, not 3
    expect(rockGenre!.count).toBe(1);
  });

  it('sorts genres by count descending, then name ascending', () => {
    const result = deriveFilterValues(ALBUMS);
    for (let i = 1; i < result.genres.length; i++) {
      const prev = result.genres[i - 1];
      const curr = result.genres[i];
      if (prev.count === curr.count) {
        expect(prev.genre.localeCompare(curr.genre)).toBeLessThanOrEqual(0);
      } else {
        expect(prev.count).toBeGreaterThan(curr.count);
      }
    }
  });

  it('computes decades sorted ascending', () => {
    const result = deriveFilterValues(ALBUMS);
    expect(result.decades).toEqual([...result.decades].sort((a, b) => a - b));
    expect(result.decades).toContain(1950);
    expect(result.decades).toContain(1970);
    expect(result.decades).toContain(1980);
  });

  it('excludes null years from decades', () => {
    const albumsWithNull = [
      ...ALBUMS,
      makeAlbum({ id: 99, year: null }),
    ];
    const result = deriveFilterValues(albumsWithNull);
    // Same decades as without the null-year album
    expect(result.decades).toEqual(deriveFilterValues(ALBUMS).decades);
  });

  it('handles albums with null genre_tags and style_tags', () => {
    const albumsWithNull = [
      makeAlbum({ genre_tags: null, id: 1, style_tags: null }),
    ];
    const result = deriveFilterValues(albumsWithNull);
    expect(result.genres).toEqual([]);
  });
});
