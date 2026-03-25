import { QueueItem } from '../QueueItem';
import { rootStyles } from './UpNextList-elements';
import type { IUpNextListProps } from './UpNextList-types';

/** Ordered list of upcoming queue items. */
export function UpNextList(props: IUpNextListProps) {
  const { items } = props;

  return (
    <div className={rootStyles}>
      {items.map((item) => (
        <QueueItem item={item} key={item.id} />
      ))}
    </div>
  );
}
