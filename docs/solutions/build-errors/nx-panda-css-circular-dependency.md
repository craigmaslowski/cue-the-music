---
title: "NX monorepo circular dependency with Panda CSS styled-system"
category: build-errors
date: 2026-03-25
tags: [nx, panda-css, vite, circular-dependency, monorepo, styled-system]
module: Frontend
symptom: "NX graph shows circular dependency between frontend libs and the frontend app"
root_cause: "Panda CSS generates styled-system output in the app directory, but libs import from it via @styled-system path alias"
---

# NX Monorepo Circular Dependency with Panda CSS styled-system

## Problem

When using Panda CSS in an NX monorepo with multiple frontend libraries, NX detects a circular dependency:

```
libs/frontend/core-ui → apps/frontend (via @styled-system imports)
apps/frontend → libs/frontend/core-ui (normal app → lib dependency)
```

This happens because Panda CSS generates its `styled-system/` output directory inside the frontend app (`apps/frontend/styled-system/`), but all frontend libraries need to import from it (`import { css } from '@styled-system/css'`). NX interprets the `@styled-system` path alias (which resolves to `apps/frontend/styled-system/`) as a dependency from the lib back to the app.

## Root Cause

Panda CSS is a build-time CSS engine that generates a `styled-system/` directory containing `css()`, recipes, tokens, and other utilities. In a monorepo, this output lives in the app that runs `panda codegen`. When NX analyzes the dependency graph, it sees libs importing from a path inside the app directory, creating a false circular dependency.

## Solution

Two complementary fixes:

### 1. Externalize @styled-system in library Vite configs

In each lib's `vite.config.mts`, externalize the styled-system imports so Vite doesn't try to bundle them (they're resolved at the app level):

```typescript
// libs/frontend/core-ui/vite.config.mts
export default defineConfig({
  build: {
    lib: { /* ... */ },
    rollupOptions: {
      external: [
        /^@styled-system\/.*/,
        /^@cue-the-music\/.*/,
        // other workspace packages
      ],
    },
  },
});
```

### 2. Add implicit dependency exclusion to lib package.json

Tell NX to ignore the false dependency edge:

```json
// libs/frontend/core-ui/package.json
{
  "nx": {
    "implicitDependencies": ["!@cue-the-music/frontend"]
  }
}
```

### 3. Configure Panda CSS importMap for monorepo

In `panda.config.ts`, set the `importMap` so Panda CSS knows the canonical import path:

```typescript
export default defineConfig({
  importMap: '@styled-system',
  // ...
});
```

And in the app's `vite.config.mts`, add a resolve alias:

```typescript
resolve: {
  alias: {
    '@styled-system': path.resolve(__dirname, 'styled-system'),
  },
},
```

## Prevention

- When setting up Panda CSS in an NX monorepo, configure the externalization and implicit dependency exclusion as part of the initial setup, not after the circular dependency appears.
- Consider whether a shared `core-theme` library could own the Panda config and codegen output instead of the app. This would make the dependency direction correct (libs → core-theme, app → core-theme) but requires Panda CSS to support generating output outside the app directory.
- Disable `@nx/js:typescript-sync` in `nx.json` if it keeps re-introducing circular references in tsconfig files.
