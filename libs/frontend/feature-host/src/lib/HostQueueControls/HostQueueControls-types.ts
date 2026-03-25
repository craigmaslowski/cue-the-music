export interface IHostQueueControlsProps {
  /** The queue item ID to control */
  queueItemId: number;
  /** Down-vote count for this queue item */
  downCount: number;
  /** Callback to promote this item to now playing */
  onPromote: (queueItemId: number) => void;
  /** Callback to remove this item from the queue */
  onRemove: (queueItemId: number) => void;
}

export interface IUseHostQueueControlsReturn {
  /** Whether host mode is active */
  isHostMode: boolean;
  /** Whether down-votes are prominent (3+ downvotes) */
  isSkipSignal: boolean;
  /** Handler for promote button */
  handlePromote: () => void;
  /** Handler for remove button */
  handleRemove: () => void;
}
