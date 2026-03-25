import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';

interface IHostState {
  isHostMode: boolean;
  sessionToken: string | null;
  activateHostMode: (token: string) => void;
  deactivateHostMode: () => void;
}

/** Zustand store for host mode state. Persisted to sessionStorage. */
export const useHostStore = create<IHostState>()(
  persist(
    (set) => ({
      isHostMode: false,
      sessionToken: null,
      activateHostMode: (token: string) =>
        set({ isHostMode: true, sessionToken: token }),
      deactivateHostMode: () =>
        set({ isHostMode: false, sessionToken: null }),
    }),
    {
      name: 'cue-host-mode',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        isHostMode: state.isHostMode,
        sessionToken: state.sessionToken,
      }),
    },
  ),
);
