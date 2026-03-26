import {
  artistStyles,
  buttonContentStyles,
  chipContainerStyles,
  coverArtStyles,
  genreChipStyles,
  infoLineStyles,
  metadataStyles,
  requestButtonStyles,
  skeletonLineStyles,
  titleStyles,
  trackDurationStyles,
  trackPositionStyles,
  trackRowStyles,
  trackTitleStyles,
  tracklistHeadingStyles,
  tracklistSectionStyles,
} from './AlbumDetailOverlay-elements';
import { useAlbumDetailData } from './useAlbumDetailOverlay';

interface IAlbumDetailContentProps {
  albumId: number;
  buttonText: string;
  isRequestDisabled: boolean;
  isRequesting: boolean;
  onRequest: () => void;
}

/** Inner content of the album detail overlay — fetches album data via Suspense. */
export function AlbumDetailContent(props: IAlbumDetailContentProps) {
  const { albumId, buttonText, isRequestDisabled, isRequesting, onRequest } =
    props;
  const { album, isTracklistLoading } = useAlbumDetailData(albumId);

  const allTags = [...(album.genre_tags ?? []), ...(album.style_tags ?? [])];
  const infoSegments: string[] = [];
  if (album.label) infoSegments.push(album.label);
  if (album.year) infoSegments.push(String(album.year));

  return (
    <div>
      {album.cover_art_url ? (
        <img
          alt={`${album.title} by ${album.artist}`}
          className={coverArtStyles}
          src={album.cover_art_url}
        />
      ) : (
        <div className={coverArtStyles} />
      )}

      <div className={metadataStyles}>
        <h3 className={titleStyles}>{album.title}</h3>
        <span className={artistStyles}>{album.artist}</span>
        {infoSegments.length > 0 && (
          <span className={infoLineStyles}>
            {infoSegments.join(' \u00B7 ')}
          </span>
        )}
      </div>

      {allTags.length > 0 && (
        <div className={chipContainerStyles}>
          {allTags.map((tag) => (
            <span className={genreChipStyles} key={tag}>
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className={tracklistSectionStyles}>
        <h4 className={tracklistHeadingStyles}>
          <span className="material-symbols-outlined">
            format_list_bulleted
          </span>{' '}
          Tracklist
        </h4>
        {isTracklistLoading ? (
          <div>
            {Array.from({ length: 6 }, (_, i) => (
              <div className={skeletonLineStyles} key={i} />
            ))}
          </div>
        ) : (
          album.tracklist?.map((track) => (
            <div
              className={trackRowStyles}
              key={`${track.position}-${track.title}`}
            >
              <span className={trackPositionStyles}>{track.position}</span>
              <span className={trackTitleStyles}>{track.title}</span>
              {track.duration && (
                <span className={trackDurationStyles}>{track.duration}</span>
              )}
            </div>
          ))
        )}
      </div>

      <button
        className={requestButtonStyles}
        disabled={isRequestDisabled}
        onClick={onRequest}
        type="button"
      >
        <span className={buttonContentStyles}>
          {isRequesting && <Spinner />}
          {!isRequesting && (
            <span
              data-icon="album"
              className="material-symbols-outlined text-[#f3ffca]"
            >
              album
            </span>
          )}
          {buttonText}
        </span>
      </button>
    </div>
  );
}

/** Simple loading spinner for the request button. */
function Spinner() {
  return (
    <svg
      fill="none"
      height="16"
      stroke="currentColor"
      strokeWidth="2"
      viewBox="0 0 24 24"
      width="16"
    >
      <circle cx="12" cy="12" opacity="0.25" r="10" />
      <path d="M4 12a8 8 0 018-8" opacity="0.75">
        <animateTransform
          attributeName="transform"
          dur="1s"
          from="0 12 12"
          repeatCount="indefinite"
          to="360 12 12"
          type="rotate"
        />
      </path>
    </svg>
  );
}
