---
title: "SQLite async configuration with FastAPI and SQLAlchemy 2.0"
category: configuration-fixes
date: 2026-03-25
tags: [sqlite, aiosqlite, fastapi, sqlalchemy, async, wal-mode, pragmas]
module: Backend
symptom: "MissingGreenlet error when accessing model attributes after commit, or SQLITE_BUSY under concurrent requests"
root_cause: "SQLite requires specific PRAGMA configuration and SQLAlchemy async settings for concurrent web app usage"
---

# SQLite Async Configuration with FastAPI and SQLAlchemy 2.0

## Problem

Two common issues when using SQLite with async FastAPI:

1. **MissingGreenlet error** — Accessing SQLAlchemy model attributes after `session.commit()` triggers a lazy load that fails because sync I/O can't happen inside the async context.
2. **SQLITE_BUSY** — Multiple concurrent requests (e.g., guests voting simultaneously) cause write contention and database lock errors.

## Root Cause

SQLite's default configuration is optimized for single-process, single-thread access. Web applications need:
- WAL mode for concurrent readers during writes
- Busy timeout for write contention retry
- Explicit transaction control to prevent pysqlite's quirky auto-transaction behavior
- `expire_on_commit=False` to prevent lazy loads after commit in async context

## Solution

### Engine and session configuration

```python
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    "sqlite+aiosqlite:///./app.db",
    connect_args={"check_same_thread": False},
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL: prevents MissingGreenlet after commit
)
```

### PRAGMA configuration via engine events

```python
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")       # concurrent reads during writes
    cursor.execute("PRAGMA busy_timeout=5000")       # retry writes for 5 seconds
    cursor.execute("PRAGMA synchronous=NORMAL")      # safe with WAL, faster
    cursor.execute("PRAGMA foreign_keys=ON")         # SQLite disables FK by default!
    cursor.execute("PRAGMA cache_size=-64000")       # 64MB page cache
    cursor.execute("PRAGMA temp_store=MEMORY")       # temp tables in memory
    cursor.close()
```

### Explicit transaction control

```python
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_isolation(dbapi_connection, connection_record):
    dbapi_connection.isolation_level = None  # disable pysqlite auto-transactions

@event.listens_for(engine.sync_engine, "begin")
def do_begin(conn):
    conn.exec_driver_sql("BEGIN")
```

## Key gotchas

- **`expire_on_commit=False` is mandatory** for async sessions. Without it, any attribute access after commit triggers a lazy load → MissingGreenlet.
- **`foreign_keys=ON` must be set per connection** — SQLite disables FK enforcement by default, and the PRAGMA is connection-scoped.
- **`check_same_thread=False` is mandatory** — aiosqlite uses background threads, so connections are always accessed from different threads.
- **WAL mode does NOT enable concurrent writes** — it only allows readers to proceed during writes. Writes are still serialized. `busy_timeout` handles the queueing.
- **Keep sync transactions small** during bulk operations (e.g., commit per page during a Discogs sync, not one giant transaction) to avoid holding the write lock.

## Prevention

- Include this PRAGMA configuration as part of the initial database setup, not as a later fix.
- Always use `expire_on_commit=False` with async SQLAlchemy sessions.
- After `session.flush()`, use `session.refresh(instance)` if you need to access computed columns or updated timestamps.
- Test with concurrent requests early to catch SQLITE_BUSY before production use.
