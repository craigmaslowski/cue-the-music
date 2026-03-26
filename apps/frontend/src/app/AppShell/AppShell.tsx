import { HostPinOverlay } from '@cue-the-music/feature-host';
import { Tabs } from '@ark-ui/react';

import {
  contentStyles,
  headerStyles,
  lockIconActiveStyles,
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
  const {
    activeTab,
    handleTabChange,
    isHostMode,
    isPinOverlayOpen,
    handleLockPress,
    handlePinOverlayClose,
  } = useAppShell(props);

  const lockClass = isHostMode
    ? `${lockIconStyles} ${lockIconActiveStyles}`
    : lockIconStyles;

  return (
    <div className={rootStyles}>
      {/* Header with title and host mode lock icon */}
      <header className={headerStyles}>
        <h1 className={titleStyles}>
          <span
            data-icon="album"
            className="material-symbols-outlined text-[#f3ffca]"
          >
            album
          </span>
          Cue The Music
        </h1>
        <button
          aria-label={
            isHostMode ? 'Deactivate host mode' : 'Activate host mode'
          }
          className={lockClass}
          onClick={handleLockPress}
          type="button"
        >
          {isHostMode ? (
            <span className="material-symbols-outlined text-[#f3ffca]">
              lock_open
            </span>
          ) : (
            <span className="material-symbols-outlined text-[#f3ffca]">
              lock
            </span>
          )}
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
            <span
              data-icon="album"
              className="material-symbols-outlined text-[#f3ffca]"
            >
              search
            </span>
            The Crate
          </Tabs.Trigger>
          <Tabs.Trigger className={tabTriggerStyles} value="queue">
            <span
              data-icon="album"
              className="material-symbols-outlined text-[#f3ffca]"
            >
              format_list_bulleted
            </span>
            Queue
          </Tabs.Trigger>
        </Tabs.List>
      </Tabs.Root>

      {/* Host PIN entry overlay */}
      <HostPinOverlay
        isOpen={isPinOverlayOpen}
        onClose={handlePinOverlayClose}
      />
    </div>
  );
}
