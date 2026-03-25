import type { IUpNextListProps, IUseUpNextListReturn } from './UpNextList-types';

/** Encapsulates UpNextList logic. */
export function useUpNextList(props: IUpNextListProps): IUseUpNextListReturn {
  return {
    hasItems: props.items.length > 0,
  };
}
