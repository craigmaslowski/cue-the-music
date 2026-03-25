import type { ReactNode } from 'react';

export interface IAppShellProps {
  /** Main content area rendered between header and bottom nav */
  children: ReactNode;
}

export interface IUseAppShellReturn {
  /** Current active tab value derived from the URL */
  activeTab: string;
  /** Handler for tab navigation changes */
  handleTabChange: (details: { value: string }) => void;
}
