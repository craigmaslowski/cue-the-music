export interface IQueueViewProps {
  /** No external props — QueueView is a top-level feature component. */
}

export interface IUseQueueViewReturn {
  /** Number of items in the queue */
  count: number;
  /** Whether the queue has items */
  hasItems: boolean;
}
