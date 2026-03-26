import { useHostStore } from '@cue-the-music/feature-host';
import { useLocation, useNavigate } from '@tanstack/react-router';
import { useCallback, useState } from 'react';

import type { IAppShellProps, IUseAppShellReturn } from './AppShell-types';

/** Encapsulates AppShell navigation logic, syncing tabs with the URL. */
export function useAppShell(_props: IAppShellProps): IUseAppShellReturn {
  const location = useLocation();
  const navigate = useNavigate();
  const isHostMode = useHostStore((s) => s.isHostMode);
  const deactivateHostMode = useHostStore((s) => s.deactivateHostMode);
  const [isPinOverlayOpen, setIsPinOverlayOpen] = useState(false);

  // Derive active tab from the current URL path
  const activeTab = location.pathname.startsWith('/queue') ? 'queue' : 'crate';

  function handleTabChange(details: { value: string }): void {
    navigate({ to: `/${details.value}` });
  }

  const handleLockPress = useCallback(() => {
    if (isHostMode) {
      deactivateHostMode();
    } else {
      setIsPinOverlayOpen(true);
    }
  }, [isHostMode, deactivateHostMode]);

  const handlePinOverlayClose = useCallback(() => {
    setIsPinOverlayOpen(false);
  }, []);

  return {
    activeTab,
    handleTabChange,
    isHostMode,
    isPinOverlayOpen,
    handleLockPress,
    handlePinOverlayClose,
  };
}
