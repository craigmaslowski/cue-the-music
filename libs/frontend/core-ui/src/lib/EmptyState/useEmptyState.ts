import type { IEmptyStateProps, IUseEmptyStateReturn } from './EmptyState-types';

/** Encapsulates EmptyState derived state. */
export function useEmptyState(props: IEmptyStateProps): IUseEmptyStateReturn {
  return {
    hasIcon: props.icon !== undefined,
  };
}
