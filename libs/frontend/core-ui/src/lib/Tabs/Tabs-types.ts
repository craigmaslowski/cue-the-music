import type { ReactNode } from 'react';

export interface ITabItem {
  /** Content rendered when this tab is active */
  content: ReactNode;
  /** Whether this tab is disabled */
  disabled?: boolean;
  /** Label shown on the tab trigger */
  label: string;
  /** Unique value identifying this tab */
  value: string;
}

export interface ITabsProps {
  /** Default active tab value */
  defaultValue?: string;
  /** Callback when the active tab changes */
  onValueChange?: (details: { value: string }) => void;
  /** Array of tab definitions */
  tabs: ITabItem[];
  /** Currently active tab value (controlled mode) */
  value?: string;
}

export interface IUseTabsReturn {
  /** Handler for tab value changes */
  handleValueChange: (details: { value: string }) => void;
  /** The tab items to render */
  tabs: ITabItem[];
  /** Currently active tab value */
  value: string | undefined;
}
