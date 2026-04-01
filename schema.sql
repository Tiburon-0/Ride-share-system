CREATE TABLE IF NOT EXISTS riders (
    id  TEXT PRIMARY KEY,
    name    TEXT NOT NULL,     
    rating_avg REAL DEFAULT 0.0,
    total_rides INTEGER DEFAULT 0,
    preferences_id  INTEGER,
    FOREIGN KEY (preferences_id) REFERENCES preferences(id)
);

CREATE TABLE IF NOT EXISTS drivers (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    rating_avg     REAL DEFAULT 0.0,
    is_available   INTEGER DEFAULT 1,
    car_type       TEXT,
    preferences_id INTEGER,
    FOREIGN KEY (preferences_id) REFERENCES preferences(id)
);

CREATE TABLE IF NOT EXISTS preferences (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    language         TEXT,
    car_type         TEXT,
    max_distance     REAL,
    min_rider_rating REAL,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS trips (
    id              TEXT PRIMARY KEY,
    rider_id        TEXT NOT NULL,
    driver_id       TEXT NOT NULL,
    start_location  TEXT,
    end_location    TEXT,
    requested_at    TEXT,
    accepted_at     TEXT,
    started_at      TEXT,
    completed_at    TEXT,
    fare            REAL,
    status          TEXT DEFAULT 'requested',
    matching_log_id INTEGER,
    FOREIGN KEY (rider_id)        REFERENCES riders(id),
    FOREIGN KEY (driver_id)       REFERENCES drivers(id),
    FOREIGN KEY (matching_log_id) REFERENCES matching_logs(id)
);

CREATE TABLE IF NOT EXISTS ratings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id     TEXT NOT NULL,
    rater_type  TEXT,    -- "rider" or "driver"
    rater_id    TEXT,
    ratee_type  TEXT,    -- "driver" or "rider"
    ratee_id    TEXT,
    stars       INTEGER,
    comment     TEXT,
    timestamp   TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

CREATE TABLE IF NOT EXISTS matching_logs (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    rider_id (FK) TEXT NOT NULL,
    algorithm TEXT,
    graph_model TEXT,
    candidate_drivers TEXT,
    distances TEXT,
    chosen_driver_id TEXT,
    chosen_distance REAL,
    timestamp TEXT,
    FOREIGN KEY (rider_id) REFERENCES riders(id)
)

