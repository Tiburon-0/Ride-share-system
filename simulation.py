'''
Assignment 7 — Simulation Script
Covers Use Cases 1–6, as well as the full demonstration (Part 4).
'''

import os, sys, json, networkx as nx
from datetime import datetime

# ── Fix working directory so JSON files load correctly ──
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from database_manager import create_tables, drop_all_tables, execute_query
from rider import Rider
from driver import Driver
from ride import Ride
from location import RiderLocation, DriverLocation
from graph_model import GraphModel
from matching_log import MatchingLog
from rating import Rating

# ────────────────────────────────────────────────────────
# HELPER: run both matching algorithms and return results
# ────────────────────────────────────────────────────────

def select_and_log(rider, drivers, graph, algorithm="weighted"):
    '''
    Finds the closest available driver using the specified algorithm; builds and saves a MatchingLog;
    returns (driver, distance, log)
    '''
    
    candidates = []
    for driver in drivers:
        if driver.is_available:
            try:
                r_node = rider.get_current_location().get_node()
                d_node = driver.get_current_location().get_node()
                if algorithm == "weighted":
                    dist = nx.shortest_path_length(graph, r_node, d_node, weight='weight')
                else:
                    dist = nx.shortest_path_length(graph, r_node, d_node)
                candidates.append((driver, dist))
            except nx.NetworkXNoPath:
                pass

    if not candidates:
        return None, None, None

    candidates.sort(key=lambda x: x[1])
    chosen_driver, chosen_dist = candidates[0]

    log = MatchingLog(
        rider_id          = rider.get_user_id(),
        algorithm         = algorithm,
        graph_model       = "barabasi_albert",
        candidate_drivers = [d.get_user_id() for d, _ in candidates],
        distances         = [dist for _, dist in candidates],
        chosen_driver_id  = chosen_driver.get_user_id(),
        chosen_distance   = chosen_dist
    )
    log.save()

    chosen_driver.is_available = False
    return chosen_driver, chosen_dist, log


def run_full_trip(rider, driver, distance, log_id, start_node, end_node, label=""):
    '''Creates, transitions, and saves a complete trip'''

    print(f"\n  [{label}] {rider.get_name()} -> {driver.get_name()} | dist={distance:.1f}")
    trip = Ride(rider, driver, destination=f"Node {end_node}")
    trip._rider_location = f"Node {start_node}"
    trip._destination    = f"Node {end_node}"
    trip._distance       = distance
    trip._matching_log_id = log_id

    # Save rider/driver first (FK constraint)
    rider.save()
    driver.save()

    trip.accept()
    trip.start()
    trip.complete()

    if trip._fare is None:
        trip._fare = round(1.50 * distance if distance >= 5 else 2.00 * distance, 2)

    trip.save()
    return trip


def save_ratings(trip, rider, driver, rider_stars=5, driver_stars=4):
    '''Saves both rider -> driver and driver -> rider ratings'''

    rating_1 = Rating(trip.get_ride_id(), "rider",  rider.get_user_id(),
                "driver", driver.get_user_id(), rider_stars)
    rating_2 = Rating(trip.get_ride_id(), "driver", driver.get_user_id(),
                "rider",  rider.get_user_id(),  driver_stars)
    rating_1.save()
    rating_2.save()
    return rating_1, rating_2

# ────────────────────────────────────────────────────────
# BUILD SIMULATION DATA
# ────────────────────────────────────────────────────────

def build_staging_data():
    '''Creates a small, deterministic graph + riders + drivers for simulation.'''

    # 6-node graph with intentionally different weighted vs unweighted paths
    g = GraphModel()
    g.add_edge(0, 1, weight=1)
    g.add_edge(1, 2, weight=1)
    g.add_edge(0, 2, weight=10)   # direct but longer and more expensive
    g.add_edge(2, 3, weight=2)
    g.add_edge(3, 4, weight=2)
    g.add_edge(4, 5, weight=1)
    g.add_edge(1, 4, weight=1)

    # Named riders — spread across graph 
    aisha  = Rider("Aisha",  "r_aisha",  current_location=RiderLocation(node=0))
    ben    = Rider("Ben",    "r_ben",    current_location=RiderLocation(node=2))
    carla  = Rider("Carla",  "r_carla",  current_location=RiderLocation(node=3))
    dina   = Rider("Dina",   "r_dina",   current_location=RiderLocation(node=0))

    # Named drivers — spread across graph
    d_alpha = Driver("Alpha", "d_alpha", is_available=True,
                     current_location=DriverLocation(node=1))
    d_beta  = Driver("Beta",  "d_beta",  is_available=True,
                     current_location=DriverLocation(node=2))
    d_charlie = Driver("Charlie", "d_charlie", is_available=True,
                     current_location=DriverLocation(node=4))
    d_delta = Driver("Delta", "d_delta", is_available=True,
                     current_location=DriverLocation(node=5))

    return g, [aisha, ben, carla, dina], [d_alpha, d_beta, d_charlie, d_delta]     # returns graph, list of riders, list of drivers

# ────────────────────────────────────────────────────────
# USE CASE 1 — Weighted vs Unweighted Matching
# ────────────────────────────────────────────────────────

def use_case_1(g, riders, drivers):
    print(f"\n")       
    print(f"  =============================================================  ")    
    print(f"         USE CASE 1 — Weighted vs Unweighted Matching") 
    print(f"  =============================================================  ")
    print(f"\n")

    aisha = riders[0]
    print(f"Ride requested by: {riders[0]}")

    # Reset availability
    for driver in drivers: 
        driver.is_available = True

    # Weighted match
    chosen_weighted, dist_weighted, log_weighted = select_and_log(aisha, drivers, g.graph, algorithm="weighted")
    print(f"  Weighted -> Chosen driver: {chosen_weighted.get_name()} | dist={dist_weighted:.2f}")
    trip_weighted = run_full_trip(aisha, chosen_weighted, dist_weighted, log_weighted.db_id,
                           start_node=0, end_node=5, label="UC1 - Weighted")
    save_ratings(trip_weighted, aisha, chosen_weighted, rider_stars=5, driver_stars=4)

    # Reset and run unweighted
    for driver in drivers: 
        driver.is_available = True

    chosen_unweighted, dist_unweighted, log_unweighted = select_and_log(aisha, drivers, g.graph, algorithm="unweighted")
    print(f"  Unweighted -> {chosen_unweighted.get_name()} | hops = {dist_unweighted} ")
    print(f"  [Comparison only — unweighted log saved, trip not duplicated]  ")

    print(f"\n")    
    print(f"  =============================================================  ")
    print(f"                    Use Case 1 complete...")
    print(f"  =============================================================  ")


# ────────────────────────────────────────────────────────
# USE CASE 2 — Concurrent Requests (Ben and Carla)
# ────────────────────────────────────────────────────────

def use_case_2(g, riders, drivers):
    print(f"\n")
    print("USE CASE 2 — Concurrent Requests")

    ben, carla = riders[1], riders[2]
    for driver in drivers: 
        driver.is_available = True

    # Ben requests first — gets closest available driver
    chosen_ben, dist_ben, log_ben = select_and_log(ben, drivers, g.graph, "weighted")
    print(f"  Ben -> {chosen_ben.get_name()} | dist = {dist_ben:.2f}")

    # Carla requests second — chosen_ben is now unavailable
    chosen_carla, dist_carla, log_carla = select_and_log(carla, drivers, g.graph, "weighted")
    print(f"  Carla -> {chosen_carla.get_name()} | dist = {dist_carla:.2f}")

    trip_ben = run_full_trip(ben, chosen_ben, dist_ben, log_ben.db_id,
                             start_node=2, end_node=5, label="UC2 - Ben")
    
    trip_carla = run_full_trip(carla, chosen_carla, dist_carla, log_carla.db_id,
                               start_node=3, end_node=5, label="UC2 - Carla")

    save_ratings(trip_ben, ben, chosen_ben, 5, 5)
    save_ratings(trip_carla, carla, chosen_carla, 4, 5)
    print(f"\n")
    print(f"  =============================================================  ")
    print(f"                    Use Case 2 complete...")
    print(f"  =============================================================  ")

# ────────────────────────────────────────────────────────
# USE CASE 3 — Preference-Aware Matching
# ────────────────────────────────────────────────────────

def use_case_3(g, riders, drivers):
    print(f"\n")
    print("USE CASE 3 — Preference-Aware Matching")

    dina = riders[3]
    for driver in drivers: 
        driver.is_available = True

    drivers[0].add_rating(3)   # Alpha: avg 3.0
    drivers[1].add_rating(5)   # Beta: avg 5.0
    drivers[2].add_rating(5)   # Charlie: avg 5.0
    drivers[3].add_rating(4)   # Delta: avg 4.0

    min_rating = 4.5
    preferred_drivers = [driver for driver in drivers
                         if driver.is_available and driver.get_average_rating() >= min_rating]

    print(f"  Dina requires driver avg rating ≥ {min_rating}")
    print(f"  Eligible drivers: {[driver.get_name() for driver in preferred_drivers]}")

    chosen, dist, log = select_and_log(dina, preferred_drivers, g.graph, "weighted")
    print(f"  Matched: {chosen.get_name()} | dist={dist:.2f}")

    trip = run_full_trip(dina, chosen, dist, log.db_id,
                         start_node=0, end_node=4, label="UC3 - Dina")
    save_ratings(trip, dina, chosen, 5, 5)

    print(f"\n")
    print(f"  =============================================================  ")
    print(f"                    Use Case 3 complete...")
    print(f"  =============================================================  ")

# ────────────────────────────────────────────────────────
# USE CASE 4 — System Reload
# ────────────────────────────────────────────────────────

def use_case_4():
    print(f"\n")    
    print("USE CASE 4 — System Reload from Database")

    riders  = Rider.all()
    drivers = Driver.all()
    trips   = Ride.all()
    logs    = MatchingLog.all()
    ratings = Rating.all()

    print(f"\n  Riders loaded:        {len(riders)}")
    for rider in riders:
        print(f"    {rider.get_user_id()}: {rider.get_name()}")

    print(f"\n  Drivers loaded:       {len(drivers)}")
    for driver in drivers:
        print(f"    {driver.get_user_id()}: {driver.get_name()} | available={driver.is_available}")

    print(f"\n  Trips loaded:         {len(trips)}")
    for trip in trips:
        print(f"    {trip.get_ride_id()} | status={trip.get_status()} | fare={trip._fare}")

    print(f"\n  Matching logs loaded: {len(logs)}")

    for log in logs:
        print(f"    {log}")

    print(f"\n  Ratings loaded:       {len(ratings)}")
    for rating in ratings:
        print(f"    {rating}")

    print(f"\n")
    print(f"  =============================================================  ")
    print(f"                    Use Case 4 complete...")
    print(f"  =============================================================  ")

# ────────────────────────────────────────────────────────
# USE CASE 5 — Analytics
# ────────────────────────────────────────────────────────

def use_case_5():
    print(f"\n")
    print("USE CASE 5 — Analytics")

    logs = MatchingLog.all()
    if not logs:
        print("  No matching logs found.")
        return

    weighted   = [log for log in logs if log.algorithm == "weighted"]
    unweighted = [log for log in logs if log.algorithm == "unweighted"]

    avg_weighted = sum(log.chosen_distance for log in weighted)   / len(weighted)   if weighted   else 0
    avg_unweighted = sum(log.chosen_distance for log in unweighted) / len(unweighted) if unweighted else 0

    print(f"\n  Total matching logs: {len(logs)}")
    print(f"  Weighted logs: {len(weighted)} | Avg chosen distance: {avg_weighted:.2f}")
    print(f"  Unweighted logs: {len(unweighted)} | Avg chosen hops: {avg_unweighted:.2f}")

    # Driver selection frequency
    freq = {}
    for log in logs:
        freq[log.chosen_driver_id] = freq.get(log.chosen_driver_id, 0) + 1
    print(f"\n  Driver selection frequency:")
    for driver_id, count in sorted(freq.items(), key=lambda x: -x[1]):
        print(f"    {driver_id}: selected {count} time(s)")

    # Average trip rating per algorithm
    ratings = Rating.all()
    trips   = {trip.get_ride_id(): trip for trip in Ride.all()}
    logs_by_trip = {}
    for log in logs:
        # Match log to trip via matching_log_id
        row = execute_query(
            "SELECT id FROM trips WHERE matching_log_id = ?",
            (log.db_id,), fetch=True)
        if row:
            logs_by_trip[row[0]["id"]] = log.algorithm

    print(f"\n  Trip ratings by algorithm:")
    algorithm_ratings = {"weighted": [], "unweighted": []}
    for rating in ratings:
        algorithm = logs_by_trip.get(rating.trip_id)
        if algorithm in algorithm_ratings:
            algorithm_ratings[algorithm].append(rating.stars)

    for algorithm, stars in algorithm_ratings.items():
        avg = sum(stars) / len(stars) if stars else 0
        print(f"    {algorithm}: avg rating: {avg:.2f} ({len(stars)} ratings)")

    print(f"\n")
    print(f"  =============================================================  ")
    print(f"                    Use Case 5 complete...")
    print(f"  =============================================================  ")

# ────────────────────────────────────────────────────────
# USE CASE 6 — Cancellation Scenario
# ────────────────────────────────────────────────────────

def use_case_6(g, riders, drivers):
    print(f"\n")
    print("USE CASE 6 — Cancellation + Re-request")

    # Create a fresh rider for this scenario
    sam = Rider("Sam", "R_SAM", current_location=RiderLocation(node=0))
    for driver in drivers: 
        driver.is_available = True

    # Initial match
    chosen, dist, log = select_and_log(sam, drivers, g.graph, "weighted")
    print(f"  Sam matched with {chosen.get_name()} | dist={dist:.2f}")

    # Start trip but then cancel mid-trip
    sam.save()
    chosen.save()

    trip1 = Ride(sam, chosen, destination="Node 5")
    trip1._rider_location  = "Node 0"
    trip1._destination     = "Node 5"
    trip1._distance        = dist
    trip1._matching_log_id = log.db_id
    trip1.accept()
    trip1.start()
    trip1.cancel(reason="Driver unavailable")   # cancel mid-trip
    trip1._fare = 0.0
    trip1.save()
    print(f"  Trip 1 ({trip1.get_ride_id()}) canceled. Status: {trip1.get_status()}")

    # Driver goes back online after cancellation
    chosen.is_available = True
    chosen.save()

    # Sam re-requests — new MatchingLog + new Trip
    chosen2, dist2, log2 = select_and_log(sam, drivers, g.graph, "weighted")
    print(f"  Sam re-matched with {chosen2.get_name()} | dist={dist2:.2f}")
    trip2 = run_full_trip(sam, chosen2, dist2, log2.db_id,
                          start_node=0, end_node=5, label="UC6 - Rebook")
    save_ratings(trip2, sam, chosen2, 4, 5)

    print(f"  Trip 2 ({trip2.get_ride_id()}) completed. Status: {trip2.get_status()}")
    print(f"\n")
    print(f"  =============================================================  ")    
    print(f"                    Use Case 6 complete...")
    print(f"  =============================================================  ")


# ────────────────────────────────────────────────────────
# MAIN — Part 4 Demonstration
# ────────────────────────────────────────────────────────

def simulate_use_cases():
    print("Assignment 7 — Starting Simulation")

    # Fresh start each run
    drop_all_tables()
    create_tables()

    g, riders, drivers = build_staging_data()

    use_case_1(g, riders, drivers)
    use_case_2(g, riders, drivers)
    use_case_3(g, riders, drivers)
    use_case_4()          # reload from DB
    use_case_5()          # analytics
    use_case_6(g, riders, drivers)

    print("=======================")
    print("All Use Cases Complete")
    print("=======================")  
