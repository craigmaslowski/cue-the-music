import { Tabs } from '@ark-ui/react';

import {
  contentStyles,
  headerStyles,
  lockIconStyles,
  rootStyles,
  tabListStyles,
  tabRootStyles,
  tabTriggerStyles,
  titleStyles,
} from './AppShell-elements';
import type { IAppShellProps } from './AppShell-types';
import { useAppShell } from './useAppShell';

/**
 * App shell providing the header with app title, main content area,
 * and bottom navigation tabs for Crate and Queue views.
 */
export function AppShell(props: IAppShellProps) {
  const { children } = props;
  const { activeTab, handleTabChange } = useAppShell(props);

  return (
    <div className={rootStyles}>
      {/* Header with title and host mode lock icon */}
      <header className={headerStyles}>
        <h1 className={titleStyles}>Cue The Music</h1>
        <button
          aria-label="Host mode"
          className={lockIconStyles}
          type="button"
        >
          &#x1F512;
        </button>
      </header>

      {/* Bottom navigation tabs wrapping the main content */}
      <Tabs.Root
        className={tabRootStyles}
        onValueChange={handleTabChange}
        value={activeTab}
      >
        {/* Main content area — child routes render here */}
        <div className={contentStyles}>{children}</div>

        {/* Bottom tab bar */}
        <Tabs.List className={tabListStyles}>
          <Tabs.Trigger className={tabTriggerStyles} value="crate">
            The Crate
          </Tabs.Trigger>
          <Tabs.Trigger className={tabTriggerStyles} value="queue">
            Queue
          </Tabs.Trigger>
        </Tabs.List>
      </Tabs.Root>
    </div>
  );
}
