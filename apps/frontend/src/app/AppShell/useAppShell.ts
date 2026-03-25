import { useLocation, useNavigate } from '@tanstack/react-router';

import type { IAppShellProps, IUseAppShellReturn } from './AppShell-types';

/** Encapsulates AppShell navigation logic, syncing tabs with the URL. */
export function useAppShell(_props: IAppShellProps): IUseAppShellReturn {
  const location = useLocation();
  const navigate = useNavigate();

  // Derive active tab from the current URL path
  const activeTab = location.pathname.startsWith('/queue') ? 'queue' : 'crate';

  function handleTabChange(details: { value: string }): void {
    navigate({ to: `/${details.value}` });
  }

  return {
    activeTab,
    handleTabChange,
  };
}
