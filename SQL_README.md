# Persistence Layer — SQLite + Mini-ORM

This document covers the database architecture added in Assignment 7, which provides persistent storage for the ride-hailing simulation through a custom ORM pattern built on SQLite.

## Database Schema

Six tables with foreign key relationships model the complete ride lifecycle:

```
┌────────────┐       ┌───────────┐
│ preferences│◄──────│   riders  │
│            │◄──┐   └─────┬─────┘
└────────────┘   │         │
                 │   ┌─────┴──────┐       ┌──────────────┐
                 └───│  drivers   │       │    ratings   │
                     └─────┬──────┘       └──────┬───────┘
                           │                     │
                     ┌─────┴─────────────────────┴───┐
                     │            trips              │
                     └─────────────┬─────────────────┘
                                   │
                         ┌─────────┴────────┐
                         │  matching_logs   │
                         └──────────────────┘
```

| Table | Purpose |
|-------|---------|
| `riders` | Rider profiles with average rating and total ride count |
| `drivers` | Driver profiles with availability flag and car type |
| `preferences` | Shared preference records (language, car type, distance, rating thresholds) |
| `trips` | Full ride lifecycle with four timestamps (requested → accepted → started → completed) |
| `ratings` | Bidirectional feedback — both rider and driver rate each trip |
| `matching_logs` | Audit trail for every driver-selection decision |

## Mini-ORM (`DatabaseModel`)

The `DatabaseModel` base class provides a lightweight Active Record interface. Domain classes inherit from it and implement two serialization methods:

```
DatabaseModel (base)
├── save()           — INSERT OR REPLACE (upsert)
├── get(id)          — Single record by primary key
├── all()            — All rows as domain objects
├── filter(**kwargs)  — Query by column=value conditions
│
├── _to_dict()       — Subclass implements: object → column/value mapping
└── _from_dict()     — Subclass implements: row dict → domain object
```

**Inheriting classes:** `Rider`, `Driver`, `Ride`, `Rating`, `MatchingLog`

Each subclass defines a `table_name` class attribute and overrides `_to_dict()` and `_from_dict()` to handle its specific column mapping.

## Key Design Decisions

**`INSERT OR REPLACE` for upserts** — The `save()` method handles both creation and updates in a single SQL statement. This keeps the ORM simple at the cost of full-row rewrites on every update, which is acceptable at simulation scale.

**`row_factory = sqlite3.Row`** — The connection returns dictionary-like row objects, enabling direct column access by name instead of index-based tuple unpacking.

**`executescript()` for DDL** — Both `create_tables()` and `drop_all_tables()` use `executescript()` to batch multiple DDL statements in one call, respecting foreign key dependency order.

**Four-timestamp trip lifecycle** — Each trip records `requested_at`, `accepted_at`, `started_at`, and `completed_at`, preserving the full timeline of every ride phase.

**Bidirectional ratings** — The `ratings` table captures feedback from both parties per trip (`rater_type` / `ratee_type`), creating mutual accountability rather than one-sided evaluation.

**Matching audit logs** — Every driver assignment is persisted with the complete candidate list, computed distances, chosen driver, and algorithm used (weighted vs. unweighted). This enables post-hoc analysis comparing algorithm performance.

## Database Manager (`database_manager.py`)

| Function | Purpose |
|----------|---------|
| `get_connection()` | Returns a connection with `row_factory` set for dict-style access |
| `create_tables()` | Executes `schema.sql` to initialize all six tables |
| `drop_all_tables()` | Tears down tables in foreign-key-safe order for clean reloads |
| `execute_query()` | Central query runner with optional `fetch` flag for SELECT vs. INSERT |

## Simulation Use Cases

`simulation.py` validates the full persistence layer through six use cases:

| UC | Test |
|----|------|
| 1 | Save and retrieve riders/drivers via `save()` and `get()` |
| 2 | Run a complete trip lifecycle (request → accept → start → complete) |
| 3 | Record and query bidirectional ratings |
| 4 | Load all saved entities and verify state via `all()` |
| 5 | Compare weighted vs. unweighted matching with audit log analysis |
| 6 | Filter queries using `filter()` with multiple conditions |

Run with:

```bash
python simulation.py
```
