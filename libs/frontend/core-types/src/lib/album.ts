/** Album data as returned by the backend API. */
export interface IAlbum {
  artist: string;
  cover_art_thumbnail_url: string | null;
  cover_art_url: string | null;
  created_at: string;
  discogs_release_id: string;
  genre_tags: string[];
  id: number;
  label: string | null;
  style_tags: string[];
  title: string;
  tracklist: ITrack[] | null;
  updated_at: string;
  year: number | null;
}

/** Individual track within an album tracklist. */
export interface ITrack {
  duration: string;
  position: string;
  title: string;
}
