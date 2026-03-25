# Coding Standards — General

This is a living document. Add to it after every project as new standards emerge or existing ones are refined. Every rule here is an enforceable constraint, not a suggestion. If a rule needs to be broken, document the exception and the reason in a comment.

## NX Monorepo

1. Top-level workspace folders: `apps/`, `libs/`, `tools/`, `docs/`, `infrastructure/`. No other top-level source folders.
2. `libs/` contains frontend libraries under `libs/frontend/`.
3. All project and library names are kebab-case. Scoped with the workspace designator (e.g., `@myorg/feature-name`).
4. Apps are as thin as possible — `main.tsx`, `App.tsx`, and nothing else unless it genuinely cannot live in a library. If code can live in a library, it must live in a library.
5. Shared types, constants, and utilities live in dedicated `core` libraries (e.g., `core-types`, `core-utils`), not in feature libraries.
6. `core` libraries must never import from `feature` libraries. Dependency direction is strictly: `app -> feature -> core`. Never the reverse.
7. When creating new functionality, default to creating it in a library, not in an app. The burden of proof is on keeping code in an app, not on extracting it.
8. **IMPORTANT** ALWAYS usee NX generators to scaffold new apps and libs.

- @nx/react for frontend libs
- @nxlv/python

## General Discipline

### Typing

1. TypeScript: `strict: true` in tsconfig. No `any` — ever. If a type is unknown, use `unknown` and narrow it.
2. Python: Type hints on all function signatures — parameters and return types. No untyped `**kwargs` or `*args` in service, repository, or any business logic functions. If flexible arguments are needed, define a typed model or `TypedDict`.

### Naming

3. TypeScript files: `camelCase.ts` (non-component). Component files: `PascalCase.tsx` as defined in the frontend standards.
4. Python files: idiomatic `snake_case.py`.
5. Config files: descriptive names, no strict convention beyond clarity.

### Ordering

6. All lists must be alphabetized: interface fields, object keys, function parameters, destructured bindings, CSS properties, class fields, enum members, imports within a group — across all languages. Only exception: idiomatic language reasons (e.g., `model_config` at top of a Pydantic model).

### Imports

7. Import order: external libraries -> internal/workspace libraries -> relative imports (furthest to closest). Alphabetized within each group.

### Error Handling

8. Users must never see technical errors, stack traces, or developer-facing messages in the UI. All errors surfaced to users must be friendly, human-readable messages. Technical details are for logs, not for end users.

### Comments

9. Light comments describing what the code does and why, especially on AI-generated code. Not every line — but enough that a reader can follow the intent without deep analysis.

### Testing

10. Target 90%+ code coverage. Test what makes sense to catch errors early — no rigid rules about unit vs integration vs e2e ratios, but all three should exist where appropriate.

### Environment

11. `.env` files for local development. Never commit secrets. Production config is architecture-dependent.

### Anti-laziness

12. No lazy coding. If a human reviewer would call it lazy — oversized files, missing types, skipped extraction, shortcuts that trade maintainability for speed — it is wrong. Fix it before committing.

## Never Do This

This is the most important section. These are the rules you follow on day one.

1. **Never use `any` in TypeScript.** Use `unknown` and narrow, or define a proper type.
2. **Never use untyped `**kwargs`or`\*args`** in Python service, repository, or business logic functions. Define typed parameters, a Pydantic model, or a `TypedDict`.
3. **Never use default exports.** Named exports only, everywhere.
4. **Never put business logic in route handlers.** Routes call services. Period.
5. **Never put database queries in services.** Services call repositories.
6. **Never return raw dicts or untyped data from API endpoints.** Every endpoint has explicit Pydantic request and response models.
7. **Never put component logic in the component file.** Logic, state, and handlers live in the `use{ComponentName}` hook.
8. **Never define styles inline in a component file.** Styles live in `{ComponentName}-elements.ts`.
9. **Never write a single-file agent.** Agents must be decomposed into separate concerns.
10. **Never hardcode prompts, model config, or tool definitions inline in agent orchestration code.**
11. **Never drill props more than two levels deep** (`A -> B -> C` max) unless explicitly addressing a performance concern.
12. **Never use anonymous functions in JSX** beyond single-expression callbacks.
13. **Never use raw `useQuery` or `useMutation` in a component.** Wrap them in custom hooks. Components never call TanStack Query directly.
14. **Never subscribe to an entire Zustand store.** Always use granular selectors.
15. **Never put server state in Zustand.** API/server data lives in TanStack Query.
16. **Never write hand-crafted query key strings.** Use query key factories.
17. **Never skip alphabetical ordering** of properties, keys, parameters, destructured bindings, CSS properties, imports within groups, or any similar list — in any language.
18. **Never show technical errors to users in the UI.** Stack traces, raw exception messages, and developer jargon are for logs, not for end users.
19. **Never create code in an app that could live in a library.** Apps are thin shells.
20. **Never import a feature library from a core library.** Dependency direction is `app -> feature -> core`. Never reversed.
21. **Never raise raw `HTTPException` with bare string messages.** Use custom exception classes.
22. **Never build interactive UI primitives from scratch** when ArkUI provides one (modals, menus, tabs, etc.).
23. **Never write lazy code.** If a human reviewer would call it lazy — oversized files, missing types, skipped extraction, shortcuts that trade maintainability for speed — it is wrong. Fix it before committing.
