import sqlite3
import json

db_path = "rideshare.db"

def get_connection():
    '''Opens rideshare.db and returns an SQLite connection with dict-style row access'''

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row   # direct access vs. tuple iteration       
    return connection


def create_tables():
    '''Creates all tables if they don't already exist; 
    Respects dependency order (creation hierarchy)'''
    
    connection = get_connection()
    cursor = connection.cursor()

    # executescript runs multiple SQL statements at once
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS preferences (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            language    TEXT,
            car_type    TEXT,
            max_distance    REAL,
            min_rider_rating REAL,
            notes       TEXT
        );

        CREATE TABLE IF NOT EXISTS riders (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            rating_avg  REAL DEFAULT 0.0,
            total_rides INTEGER DEFAULT 0,
            preferences_id INTEGER,
            FOREIGN KEY (preferences_id) REFERENCES preferences(id)
        );

        CREATE TABLE IF NOT EXISTS drivers (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            rating_avg  REAL DEFAULT 0.0,
            is_available INTEGER DEFAULT 1,
            car_type    TEXT,
            preferences_id INTEGER,
            FOREIGN KEY (preferences_id) REFERENCES preferences(id)
        );

        CREATE TABLE IF NOT EXISTS matching_logs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            rider_id         TEXT NOT NULL,
            algorithm        TEXT,
            graph_model      TEXT,
            candidate_drivers TEXT,
            distances        TEXT,
            chosen_driver_id TEXT,
            chosen_distance  REAL,
            timestamp        TEXT,
            FOREIGN KEY (rider_id) REFERENCES riders(id)
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
            rater_type  TEXT,
            rater_id    TEXT,
            ratee_type  TEXT,
            ratee_id    TEXT,
            stars       INTEGER,
            comment     TEXT,
            timestamp   TEXT,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        );
    ''')

    connection.commit()
    connection.close()
    print("All tables created...")
    print(
        "Creation Dependency Order (Highest -> Lowest): "
        "[Preferences -> Riders -> Drivers -> Matching logs -> Trips -> Ratings]")


def execute_query(sql, params=(), fetch=False):
    '''Runs any SQL statement. fetch=True returns rows as dicts; fetch=False returns lastrowid'''

    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute(sql, params)

    if fetch:
        rows=[dict(row) for row in cursor.fetchall()]
        connection.close()
        return rows

    connection.commit()
    last_id=cursor.lastrowid
    connection.close()
    return last_id


def drop_all_tables():
    '''Drops all tables to reset the database between runs (useful during development).
    Respects dependency order (creation hierarchy) while dropping'''

    conn=get_connection()
    cursor=conn.cursor()
    cursor.executescript('''
        DROP TABLE IF EXISTS ratings;
        DROP TABLE IF EXISTS trips;
        DROP TABLE IF EXISTS matching_logs;
        DROP TABLE IF EXISTS drivers;
        DROP TABLE IF EXISTS riders;
        DROP TABLE IF EXISTS preferences;
    ''')
    conn.commit()
    conn.close()
    print("All tables dropped.")
