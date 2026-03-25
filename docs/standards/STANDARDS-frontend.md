# Coding Standards — Frontend

## React Components

### Structure
1. Every component lives in its own folder: `{ComponentName}/index.ts`, `{ComponentName}.tsx`, `{ComponentName}-elements.ts`, `{ComponentName}-types.ts`, `use{ComponentName}.ts`.
2. Component names are PascalCase. File names match the component name exactly.
3. Components are defined with the `function` keyword, not arrow functions — unless using `forwardRef` or similar.
4. No default exports. Ever.
5. `index.ts` barrel-exports the component and its types. Barrel files chain all the way up the folder tree.
6. The component file contains only JSX rendering. All logic, state, handlers, and hook calls live in the accompanying `use{ComponentName}` hook.
7. The hook takes a single parameter: the component's props object.
8. Two TypeScript interfaces per component: `I{ComponentName}Props` for the component, `IUse{ComponentName}Return` for the hook's return value. Both live in the types file.
9. The component and types are exported. The hook and elements are not.

### Decomposition
10. Each component and hook must have a single responsibility. If you have to use "and" to describe what it does, split it.
11. Favor smaller, readable code chunks over large files. No hard line count — the test is readability and single responsibility.
12. Sub-components may live in the parent's folder only when they are specific to that parent and not reused elsewhere. They must be small and focused. If reused or non-trivial, they get their own folder.

### Props and State
13. Props may be drilled at most two levels deep: `A -> B -> C`. If a prop would pass through a third component, use Zustand or context instead — unless the drilling explicitly addresses a performance concern.
14. Event handler naming: `handle{Event}` inside hooks, `on{Event}` for props passed to components.

### JSX Discipline
15. No anonymous functions in JSX — except single-expression callbacks (e.g., `onClick={() => setOpen(true)}`). Anything more complex must be a named handler from the hook.
16. Component styling uses Panda CSS (`css()`). Style definitions live in `{ComponentName}-elements.ts`, not inline in the component file.

## TanStack

### Query
1. Query key factories are required. Each domain/resource gets a factory that produces consistent keys. No hand-written string array keys scattered across components.
   ```typescript
   export const bookKeys = {
     all: ["books"] as const,
     details: () => [...bookKeys.all, "detail"] as const,
     detail: (id: string) => [...bookKeys.details(), id] as const,
     lists: () => [...bookKeys.all, "list"] as const,
     list: (filters: BookFilters) => [...bookKeys.lists(), filters] as const,
   };
   ```
2. Query and mutation definitions live in a dedicated data-access library per domain — not in component hooks. Component hooks consume them, they do not define them.
3. Custom hooks wrap every `useQuery` and `useMutation` call (e.g., `useBooks()`, `useCreateBook()`). Components never call `useQuery` directly.
4. `useSuspenseQuery` is the default. Use Suspense boundaries with fallbacks for loading states. Only fall back to `useQuery` with manual loading/error handling when Suspense doesn't fit.
5. Mutations must define `onSuccess` invalidation — always invalidate the relevant query keys so the cache stays in sync. No manual refetches unless necessary.

### Router
6. File-based routing using TanStack Router's code generation. Route tree is auto-generated, not hand-maintained.
7. Route loaders use `ensureQueryData` to pre-fetch via TanStack Query. Loaders do not fetch independently of the query cache.
8. Route-level error boundaries and pending states are required — no route without an error and loading fallback.

### Table
9. Column definitions live in their own file: `{ComponentName}-columns.tsx`. Not inline in the component.
10. Table configuration (sorting, filtering, pagination) is separate from rendering. The component's hook sets up the table instance; the component file only renders it.

## Zustand

1. Zustand is for client/UI state only. Server state (API data, cache) lives in TanStack Query. If it comes from an API, it does not go in a Zustand store.
2. One store per domain/feature. No single global store. Each feature or domain gets its own store (e.g., `useAuthStore`, `useLayoutStore`). Stores live in the feature library that owns them.
3. Use slices when a store grows beyond a single concern. A store with 2-3 related pieces of state is fine as-is. Once it manages multiple concerns, split into slices that are combined into one store.
4. `useState` or `useReducer` vs Zustand — if the state is used by a single component and its direct children, use `useState` or `useReducer`. Prefer `useReducer` over multiple `useState` calls when a hook manages more than 2-3 related pieces of state. If state is shared across components that are not in a direct parent-child relationship, use Zustand. Never use Zustand for state that only one component cares about.
5. Granular selectors are required. Never subscribe to the entire store. Always select the specific fields a component needs to prevent unnecessary re-renders.
   ```typescript
   // Bad
   const store = useLayoutStore();
   // Good
   const sidebarOpen = useLayoutStore((s) => s.sidebarOpen);
   ```
6. Custom selector hooks for complex derivations. If multiple components need the same derived state, extract it into a named hook rather than duplicating the selector logic.
7. Actions live inside the store, not in components. State mutations are defined as actions in the store definition. Components call actions, they do not call `setState` directly.
8. Use `devtools` middleware in development. Use `persist` middleware only when state genuinely needs to survive page refresh (e.g., user preferences). Use `immer` middleware when updates involve nested state. Do not add middleware by default — add it when the need is clear.

## Panda CSS + ArkUI

### Panda CSS
1. Use `css()` for one-off styles. Use recipes for components with variants (size, color, state). Use slot recipes for multi-part components (e.g., a card with header, body, footer slots). Choosing the right tool prevents style sprawl.
2. Styles live in `{ComponentName}-elements.ts`, not inline in JSX. The component file imports style references, it does not define them.
3. Customize Panda's theme tokens for project colors, spacing, typography, and breakpoints. All design values come from tokens — no magic numbers or raw hex codes in style definitions.
4. Responsive styles use Panda's built-in responsive syntax with token-based breakpoints, mobile-first. No media query strings.
   ```typescript
   css({ fontSize: { base: "sm", md: "md", lg: "lg" } })
   ```
5. Do not use Panda's `styled()` system function. Use `css()` and recipes exclusively. One consistent styling approach, no mixing paradigms.

### ArkUI
6. ArkUI is the default for any interactive UI primitive — modals, menus, tabs, accordions, tooltips, popovers, selects, etc. Do not build these from scratch.
7. Every ArkUI component used in the project must be wrapped in your own component following the standard component anatomy (`{ComponentName}/` folder, hook, types, elements). This gives a consistent API, a single place to apply project-level defaults, and a seam for customization.
8. ArkUI's unstyled components are styled exclusively with Panda CSS recipes/slot recipes. No other styling approach for ArkUI components.
