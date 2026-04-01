Testing of Use Cases 1-6 used in main menu (option 5) of main.py for easy demonstration

===schema.sql=== 
** trivial blueprint of database tables (preferences, drivers, riders, matching_logs, trips, ratings)

===database_manager.py===
** executescript(table_data) used in create_tables(), as opposed to execute(), to setup multiple databases (tables) simultaneously
** get_connection() returns dict objects via conn.row factory, easing direct access vs. iterating through a tuple
** drop_all_tables() drops all tables using executescript() for clean loading
*** reduces algorithmic complexity (BigO)
*** both get_connection() and drop_all_tables() follow dependency hierarchy for tables to reference other objects as needed (with respect to foreign keys)

===database_model.py===

Creation/Updating:
** INSERT OR REPLACE used in save()

Querying:
** filter() enables querying of data using multiple conditions (e.g., " AND ".join([f"{k} = ?" for k in conditions]) )
** get() enables querying of specific data (e.g., rider_id) 
** all() returns all rows as lists of objects

===matching_log.py===
** records every driver-selection decision — algorithm used, candidates considered, driver chosen

===simulation.py===
** tests functionality of Use Cases 1-6 using data and graph pre-loaded via build_staging_data()

Building the persistence layer forced me to consider which data is truly crucial and needs to be saved after ride completion. 
By storing every trip in the trips table with full lifecycle timestamps—requested_at, accepted_at, started_at, completed_at—the system maintains a complete record of each phase's timeline. 
Combined with the ratings table capturing both rider and driver feedback per trip, the design creates mutual accountability rather than one-sided evaluation. 
Neither party can be misrepresented without a corresponding record.
Before adding the MatchingLog class, the matching algorithm was unclear—you could see who got assigned a driver, but not why. 
Now, every decision is stored with the full candidate list, their computed distances, and the specific algorithm (weighted vs. unweighted). 
During Use Case 5, I was able to query those logs and calculate average distances per algorithm, which confirmed the weighted and unweighted approaches were actually producing different results for transparency. 
Without persistent logs, that kind of audit would be unfeasible. Regarding the mini-ORM, the main tradeoff was simplicity over flexibility. 
Using INSERT OR REPLACE in save() handles both creates and updates in one line, keeping DatabaseModel short and easy to follow. The downside is that it rewrites the entire row every time, which can consume more time with scale. 