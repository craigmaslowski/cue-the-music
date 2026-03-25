import type { IQueueItem } from '@cue-the-music/core-types';
import {
  HostModeIndicator,
  HostQueueControls,
} from '@cue-the-music/feature-host';
import { QueueView } from '@cue-the-music/feature-queue';

import { useQueuePage } from './useQueuePage';

/** Page component for the Queue route — mounts host controls at the app layer. */
export function QueuePage() {
  const { handlePromote, handleRemove, handleSync, isHostMode, isSyncing } =
    useQueuePage();

  /* Render prop injected into QueueView -> UpNextList -> QueueItem to show
     host controls per item without feature-queue importing feature-host. */
  const renderItemActions = (item: IQueueItem) =>
    isHostMode ? (
      <HostQueueControls
        downCount={item.votes.down_count}
        onPromote={handlePromote}
        onRemove={handleRemove}
        queueItemId={item.id}
      />
    ) : null;

  return (
    <>
      <HostModeIndicator isSyncing={isSyncing} onSync={handleSync} />
      <QueueView renderItemActions={renderItemActions} />
    </>
  );
}
