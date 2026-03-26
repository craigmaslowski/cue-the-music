export interface IVoteControlsProps {
  /** Down-vote count */
  downCount: number;
  /** Whether the current user voted down */
  isDownVoted: boolean;
  /** Whether the current user voted up */
  isUpVoted: boolean;
  /** Callback when down vote is pressed */
  onDownVote: () => void;
  /** Callback when up vote is pressed */
  onUpVote: () => void;
  /** Up-vote count */
  upCount: number;
}

export interface IUseVoteControlsReturn {
  /** Handler for down vote button press */
  handleDownVote: () => void;
  /** Handler for up vote button press */
  handleUpVote: () => void;
}
