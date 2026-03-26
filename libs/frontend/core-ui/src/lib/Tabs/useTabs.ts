import type { ITabsProps, IUseTabsReturn } from './Tabs-types';

/** Encapsulates Tabs state and event handling logic. */
export function useTabs(props: ITabsProps): IUseTabsReturn {
  const { defaultValue, onValueChange, tabs, value } = props;

  function handleValueChange(details: { value: string }): void {
    onValueChange?.(details);
  }

  return {
    handleValueChange,
    tabs,
    value: value ?? defaultValue,
  };
}
