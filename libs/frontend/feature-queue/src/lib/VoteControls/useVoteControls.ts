import type { IUseVoteControlsReturn, IVoteControlsProps } from './VoteControls-types';

/** Encapsulates VoteControls event handlers. */
export function useVoteControls(props: IVoteControlsProps): IUseVoteControlsReturn {
  const { onUpVote, onDownVote } = props;

  function handleUpVote(): void {
    onUpVote();
  }

  function handleDownVote(): void {
    onDownVote();
  }

  return {
    handleDownVote,
    handleUpVote,
  };
}
