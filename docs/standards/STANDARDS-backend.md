# Coding Standards — Backend

## FastAPI

1. Use FastAPI's `Depends()` for dependency injection. Dependencies live in their own modules, not inline.
2. Custom exception classes are required. Exceptions must carry enough context for the frontend to display a user-friendly error. Never raise raw `HTTPException` with bare string messages.
3. Every endpoint must define explicit Pydantic request and response models. No returning raw dicts, lists, or untyped data.
4. OpenAPI schema is the contract — frontend types are generated from it. Response models must be accurate because they drive codegen.
5. Endpoints must be thin. Business logic lives in a service layer, never in route handlers. A route handler receives input, calls a service, and returns the response.
6. One router file per resource/domain (e.g., `users.py`, `projects.py`). Routers are registered in a central location.
7. Service layer lives in its own module/folder alongside routers — not nested inside them.
8. Dependencies that are reused across routers (e.g., `get_db`, `get_current_user`) live in a shared `dependencies` module.

## SQLAlchemy

1. Session management via FastAPI's `Depends()`. Session-per-request pattern.
2. Alembic for all migrations. No manual DDL.
3. One model per file. No monolithic `models.py`.
4. Models live in a persistence layer alongside other persistence-related code (repositories, queries, etc.) — not scattered across feature modules.
5. Use SQLAlchemy 2.0 declarative style with `Mapped[]` type annotations. No legacy 1.x `Column()` style.
6. Define a shared `Base` class with common mixins — at minimum a `TimestampMixin` providing `created_at` and `updated_at` columns, and an `id` primary key convention.
7. Both sides of a relationship must be defined explicitly. No implicit back-references.
8. SQLAlchemy models and Pydantic schemas are strictly separate. No SQLModel or hybrid classes. The persistence layer must not leak into the API layer.
9. Alembic migrations are auto-generated as a starting point but must be reviewed and edited before committing. Migration file names must be descriptive, not just the auto-generated hash.
10. Repository pattern — database queries live in repository classes/functions in the persistence layer, not in services or route handlers. Services call repositories, not the session directly.

## Pydantic

1. Schema naming convention: `{Entity}{Action}{Request|Response}` — e.g., `BookCreateRequest`, `BookCreateResponse`, `UserUpdateRequest`, `UserGetResponse`.
2. Base schema inheritance is a per-project judgment call — use when it reduces duplication, skip when it doesn't.
3. Schemas live in a dedicated schemas module, separate from both routers and persistence.
4. Validation lives in the Pydantic model via validators and `Field()` constraints. Services rely on schemas being validated on arrival — they do not re-validate.
5. Use `model_config = ConfigDict(from_attributes=True)` on response schemas. This allows passing SQLAlchemy model instances directly to response schemas without manual dict conversion.
6. No use of `Any` in schema fields. Every field must have an explicit type. This ensures clean OpenAPI output and clean generated frontend types.
7. Use `Enum` classes for any field with a fixed set of values — never bare strings. Enums flow through OpenAPI into generated frontend types as union literals.
8. Schemas must not import from the persistence layer. Conversion between SQLAlchemy models and Pydantic schemas happens in the service or repository layer, never inside the schema itself.
