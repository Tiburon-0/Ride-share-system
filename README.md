# Ride-Hailing Simulation Platform

A full-stack ride-hailing simulation built iteratively across a graduate-level Python Software Development course (COMP 3006, University of Denver). The system models the complete lifecycle of a ride — from rider request through driver matching, trip execution, payment processing, and mutual rating — using object-oriented design, graph-based routing, greedy matching algorithms, and a custom SQLite persistence layer.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│          Menu system · JSON pipeline · Simulation       │
├──────────┬──────────┬───────────┬───────────────────────┤
│  Domain  │ Matching │   Graph   │     Persistence       │
│  Models  │  Engine  │  Routing  │       Layer           │
├──────────┼──────────┼───────────┼───────────────────────┤
│ User     │ Greedy   │ Barabási- │ DatabaseModel (ORM)   │
│ Rider    │ Weighted │ Albert    │ DatabaseManager       │
│ Driver   │ Unweight │ Dijkstra  │ SQLite via schema.sql │
│ Ride     │          │ NetworkX  │                       │
│ Car      │          │           │                       │
│ Agent    │          │           │                       │
└──────────┴──────────┴───────────┴───────────────────────┘
```

## Key Features

**Object-Oriented Domain Model** — Class hierarchy rooted in `User`, extended by `Rider` and `Driver`. Composition over inheritance for flexible attribute assignment (billing, preferences, cars, locations). Polymorphism demonstrated through `HumanDrivenCar` and `SelfDrivenCar` subclasses.

**Graph-Based Routing** — City map modeled as a Barabási-Albert scale-free network (NetworkX), chosen for its realistic hub-and-spoke topology. Supports both weighted (edge cost) and unweighted (hop count) shortest-path routing via Dijkstra's algorithm.

**Greedy Matching Algorithms** — Two matching strategies assign riders to drivers: unweighted (minimum hops) and weighted (minimum edge cost). Preference filters enforce constraints on rating, distance, language, and car type from both sides. Tie-breaking favors the lower node ID.

**JSON Data Pipeline** — Five loader functions (`load_riders`, `load_drivers`, `load_rides`, `load_billing_info`, `load_locations`) hydrate domain objects from JSON, with three-layer validation: file integrity, field/type checking, and cross-reference verification.

**Custom Exception Hierarchy** — Seven domain-specific exception classes organized under `RideHailingError`, providing granular error handling from data loading through payment processing.

**SQLite Persistence with Mini-ORM** — A `DatabaseModel` base class provides `save()`, `get()`, `all()`, and `filter()` methods. Domain classes inherit this interface and implement `_to_dict()` / `_from_dict()` for serialization. See [SQL_README.md](SQL_README.md) for details.

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point — menu system, JSON loaders, validation, simulation orchestration |
| `user.py` | Base class with name, ID, and rating logic |
| `rider.py` | Extends `User` with billing, ride history, location, preferences |
| `driver.py` | Extends `User` with car, availability, language, location, preferences |
| `ride.py` | Ride lifecycle — state machine from request through completion |
| `car.py` | `Car` base class, `HumanDrivenCar` and `SelfDrivenCar` subclasses |
| `agent.py` | Dispatching agent — creates ride records and maintains event logs |
| `preference.py` | Rider/driver preference constraints (rating, distance, language, car type) |
| `billing_info.py` | Billing management with payment method validation |
| `payment_method.py` | Card and wallet payment processing with expiration/amount validation |
| `location.py` | `RiderLocation` and `DriverLocation` — graph node wrappers |
| `graph_model.py` | NetworkX wrapper — edge management, shortest path, path length |
| `exceptions.py` | Custom exception hierarchy (7 classes) |
| `database_model.py` | Mini-ORM base class (`save`, `get`, `all`, `filter`) |
| `database_manager.py` | Connection management, table creation/teardown, query execution |
| `matching_log.py` | Audit log — records algorithm, candidates, distances, chosen driver |
| `rating.py` | Mutual rating model (rider ↔ driver) |
| `simulation.py` | Use Cases 1–6 integration tests against the persistence layer |
| `schema.sql` | Database schema (6 tables with foreign key relationships) |
| `ride_hailing_sql_queries.py` | Standalone SQL query demonstrations |

## Exception Hierarchy

```
RideHailingError (base)
├── DataLoadError          — JSON file I/O failures
├── DataFormatError        — Invalid JSON structure or types
├── DataReferenceError     — Broken cross-references between entities
├── BillingError           — Billing validation failures
│   └── PaymentError       — Card expiration, invalid amounts, charge failures
└── RideLogicError         — Invalid ride state transitions
```

## Matching Algorithm

The greedy matching engine evaluates every available driver against a requesting rider:

1. **Preference filtering** — Both rider and driver preferences must be mutually satisfied (car type, language, minimum rating, maximum distance).
2. **Distance computation** — Shortest path calculated via Dijkstra's, using either edge weights (traffic-aware) or hop count (uniform cost).
3. **Greedy selection** — The closest qualifying driver is assigned.
4. **Tie-breaking** — If two drivers are equidistant, the lower node ID wins (earlier nodes in the BA graph are more connected hubs).
5. **Audit logging** — Every match decision is persisted with the full candidate list, distances, and algorithm used.

### Why Barabási-Albert?

The BA model generates scale-free networks through preferential attachment — new nodes connect preferentially to high-degree nodes, creating realistic hub structures. This mirrors real cities where major intersections (hubs) carry disproportionate traffic, and weighted edges can represent variable road conditions (highways vs. side streets).

## Tech Stack

- **Python 3** — Core language
- **NetworkX** — Graph generation (BA model) and pathfinding (Dijkstra's)
- **SQLite** (`sqlite3`) — Persistence layer
- **PyUnit** (`unittest`) — Unit testing
- **matplotlib** — Graph visualization
- **Jupyter Notebook** — Interactive matching analysis and map visualization

## How to Run

```bash
# Run the main simulation menu
python main.py

# Run the persistence layer use cases (UC1–UC6)
python simulation.py
```

## Course Progression

This project was built incrementally across seven assignments, each extending the prior week's codebase:

| Assignment | Focus |
|-----------|-------|
| 1–2 | OOP foundations — class hierarchy, composition, properties, state management |
| 3 | JSON data pipeline — loaders, three-layer validation, custom exceptions |
| 4 | Graph integration — BA network, Dijkstra routing, location model |
| 5 | Matching algorithms — greedy weighted/unweighted, preference filtering |
| 6 | Unit testing — PyUnit test suites for drivers, riders, graph, matching, trips |
| 7 | SQLite persistence — mini-ORM, schema design, simulation use cases |
