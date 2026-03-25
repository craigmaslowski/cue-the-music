import {
  countStyles,
  downCountActiveStyles,
  downIconActiveStyles,
  downIconStyles,
  rootStyles,
  upCountActiveStyles,
  upIconActiveStyles,
  upIconStyles,
  voteButtonStyles,
} from './VoteControls-elements';
import type { IVoteControlsProps } from './VoteControls-types';
import { useVoteControls } from './useVoteControls';

/** Up/down vote buttons with counts. Active votes are highlighted with neon accents. */
export function VoteControls(props: IVoteControlsProps) {
  const { downCount, isDownVoted, isUpVoted, upCount } = props;
  const { handleDownVote, handleUpVote } = useVoteControls(props);

  return (
    <div className={rootStyles}>
      <button
        aria-label={isUpVoted ? 'Remove up vote' : 'Vote up'}
        className={voteButtonStyles}
        onClick={handleUpVote}
        type="button"
      >
        <span className={isUpVoted ? upIconActiveStyles : upIconStyles}>
          &#x25B2;
        </span>
        <span className={isUpVoted ? upCountActiveStyles : countStyles}>
          {upCount}
        </span>
      </button>

      <button
        aria-label={isDownVoted ? 'Remove down vote' : 'Vote down'}
        className={voteButtonStyles}
        onClick={handleDownVote}
        type="button"
      >
        <span className={isDownVoted ? downIconActiveStyles : downIconStyles}>
          &#x25BC;
        </span>
        <span className={isDownVoted ? downCountActiveStyles : countStyles}>
          {downCount}
        </span>
      </button>
    </div>
  );
}
