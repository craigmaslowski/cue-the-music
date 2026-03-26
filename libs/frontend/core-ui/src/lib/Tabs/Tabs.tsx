import { Tabs as ArkTabs } from '@ark-ui/react';

import {
  contentStyles,
  listStyles,
  rootStyles,
  triggerStyles,
} from './Tabs-elements';
import type { ITabsProps } from './Tabs-types';
import { useTabs } from './useTabs';

/** Wrapped Ark UI Tabs styled as a bottom navigation bar. */
export function Tabs(props: ITabsProps) {
  const { handleValueChange, tabs, value } = useTabs(props);

  return (
    <ArkTabs.Root
      className={rootStyles}
      onValueChange={handleValueChange}
      value={value}
    >
      {/* Tab content panels rendered above the tab bar */}
      {tabs.map((tab) => (
        <ArkTabs.Content
          className={contentStyles}
          key={tab.value}
          value={tab.value}
        >
          {tab.content}
        </ArkTabs.Content>
      ))}

      {/* Bottom navigation tab triggers */}
      <ArkTabs.List className={listStyles}>
        {tabs.map((tab) => (
          <ArkTabs.Trigger
            className={triggerStyles}
            disabled={tab.disabled}
            key={tab.value}
            value={tab.value}
          >
            {tab.label}
          </ArkTabs.Trigger>
        ))}
      </ArkTabs.List>
    </ArkTabs.Root>
  );
}
