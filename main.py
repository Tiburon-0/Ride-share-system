-9
# ==================== IMPORTS ==============================
import unittest
import time
import os
import json
import networkx as nx
import random
from exceptions import (RideHailingError, DataLoadError, DataFormatError,
                        DataReferenceError, BillingError, PaymentError, RideLogicError)
from simulation import simulate_use_cases, run_full_trip
from user import User
from rider import Rider
from driver import Driver
from ride import Ride
from agent import Agent
from car import Car, SelfDrivenCar, HumanDrivenCar
from location import Location, RiderLocation, DriverLocation
from preference import Preference
from payment_method import CreditCardPayment, DigitalWalletPayment
from billing_info import BillingInfo

# ====================[Fix Working Directory]==============================

import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Working directory set to: {script_dir}")

# ====================[Test Data]====================
'''Global lists for reference [Manual Ride Simulation]'''

rider_names = ["Alice", "Marcus", "Priya", "Jordan",
               "Taylor", "Blake", "Cameron", "Dakota", "Ellis", "Larry"]

# Drivers

driver_names = ["Carlos", "Yuki", "Rachel", "Austin", "Morgan",
                "Zach", "Sofia", "Liam", "Emma", "Noah",
                "Olivia", "Ethan", "Ava", "Mason", "Isabella",
                "Lucas", "Mia", "Oliver", "Charlotte", "Elijah",
                "Amelia", "James", "Harper", "Benjamin", "Evelyn",
                "William", "Abigail", "Henry", "Emily", "Alexander",
                "Elizabeth", "Michael", "Mila", "Daniel", "Ella",
                "Matthew", "Avery", "Jackson", "Sofia", "David",
                "Camila", "Joseph", "Aria", "Carter", "Scarlett",
                "Owen", "Victoria", "Wyatt", "Madison", "John"]

# Languages
languages = ["English", "Spanish", "Italian",
             "Japanese", "Mandarin", "French", "Arabic"]

# Collects nodes for separation
location_nodes = []

# Separates nodes for assignment to riders and drivers
rider_nodes = []
driver_nodes = []

# Separates nodes for assignment to destinations
destinations = ["University of Denver", "Kaladi Coffee",
                "Lifetime Fitness", "Whole Foods", "Cherry Creek Mall", "Illegal Pete's"]
destination_nodes = []

list_of_riders = []
list_of_drivers = []
list_of_available_drivers = []

# ====================[Assignment5: Network X]==============================
# ==========[Part 1]==========


def create_map_network():
    '''Generates a Barabasi-Albert graph to model a connected, city-level traffic network'''

    n = 100
    m = 3

    pending_map = True

    while pending_map:

        print(f"Generating map...")

        # Generate network using a Barabasi-Albert graph
        city_map = nx.barabasi_albert_graph(n, m)

        # Checks network connectivity. If connected, returns network properties
        if nx.is_connected(city_map):
            city_map.graph['name'] = "Barabasi-Albert"
            nodes = city_map.nodes()
            number_of_nodes = city_map.number_of_nodes()
            edges = city_map.edges()
            number_of_edges = city_map.number_of_edges()
            print(f"Connected {city_map.graph['name']} map network created...")
            print(f" **Map Properties** ")
            print(f"Nodes:{nodes}")
            print(f"Node count:{number_of_nodes}")
            print(f"Edges:{edges}")
            print(f"Edge count:{number_of_edges}")

            # Assigns random weights to map edges
            for u, v in city_map.edges():
                city_map[u][v]['weight'] = random.randint(1, 10)
            print(f"Random edge weight assignment successful...")

            # Adds nodes to location nodes for reference
            for node in city_map.nodes():
                location_nodes.append(node)

            pending_map = False

            return city_map

# ==============================[Part 2]======================================


# ====================[JSON File Error Handling]==============================

def load_json_file(filepath, expected_top_key=None):
    '''Loader for json files'''

    # Attempt to load and parse JSON file
    try:
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        raise DataLoadError(f"File not found: {filepath}") from e
    except UnicodeDecodeError as e:
        raise DataLoadError(f"Encoding error while reading: {filepath}") from e
    except json.JSONDecodeError as e:
        raise DataFormatError(f"Malformed JSON as file: {filepath}") from e

    # Validates structure after confirmation of top key

    if expected_top_key:
        if not isinstance(data, dict):
            raise DataFormatError(
                f"{filepath}: Expected dictionary at top level; received {type(data).__name__}")
        if expected_top_key not in data:
            raise DataFormatError(
                f"Expected {expected_top_key} at top level in {filepath}")

    return data


def validate_rider_record(rider_dict):
    '''Validates, storing all errors and returning them simultaneously for efficient error-handling'''

    rider_validation_errors = []
    required_keys = ["user_id", "name", "ratings",
                     "current_location_id", "preference"]

    # Validates presence of required 'rider' keys

    for key in required_keys:
        if key not in rider_dict:
            rider_validation_errors.append(
                f"Missing required key: {key} in rider record: {rider_dict}")

    # Validates data type of 'rider' keys

    if "user_id" in rider_dict:
        if not isinstance(rider_dict["user_id"], str):
            rider_validation_errors.append(f"Rider 'user_id' must be a string")
    if "name" in rider_dict:
        if not isinstance(rider_dict["name"], str):
            rider_validation_errors.append(f"Rider 'name' must be a string")
    if "ratings" in rider_dict:
        if not isinstance(rider_dict["ratings"], list):
            rider_validation_errors.append(f"Rider 'ratings' must be a list")
    if "current_location_id" in rider_dict:
        if not isinstance(rider_dict["current_location_id"], int):
            rider_validation_errors.append(
                f"Rider 'current_location_id' must be an integer")

    # Validates structure and data types in 'preferences' nested dict

    if "preference" in rider_dict:
        if not isinstance(rider_dict["preference"], dict):
            rider_validation_errors.append(
                f"Rider 'preference' must be a dict")
        else:
            preferences = rider_dict['preference']
            if 'preferred_language' not in preferences:
                rider_validation_errors.append(
                    f"Rider preference missing 'preferred_language'")
            elif not isinstance(preferences['preferred_language'], str):
                rider_validation_errors.append(
                    f"Rider 'preferred_language' must be a string")

            if 'prefers_self_driven' not in preferences:
                rider_validation_errors.append(
                    f"Rider preference missing 'prefers_self_driven'")
            elif not isinstance(preferences['prefers_self_driven'], bool):
                rider_validation_errors.append(
                    f"Rider 'prefers_self_driven' must be a boolean")

    # Raises DataFormatError if any errors are found within rider_validation_errors list

    if rider_validation_errors:
        raise DataFormatError(
            f"DataFormatError detected: {rider_validation_errors}")


def validate_driver_record(driver_dict):
    '''Validates, storing all errors and returning them simultaneously for efficient error-handling'''

    driver_validation_errors = []
    required_keys = ["user_id", "name", "current_location_id",
                     "car", "ratings", "preference", "language"]

    # Validates presence of required 'driver' keys

    for key in required_keys:
        if key not in driver_dict:
            driver_validation_errors.append(
                f"Missing required key: {key} in driver record: {driver_dict}")

    # Validates structure and data type of 'driver' keys

    if "user_id" in driver_dict:
        if not isinstance(driver_dict["user_id"], str):
            driver_validation_errors.append(
                f"Driver 'user_id' must be a string")
    if "name" in driver_dict:
        if not isinstance(driver_dict["name"], str):
            driver_validation_errors.append(f"Driver 'name' must be a string")
    if "current_location_id" in driver_dict:
        if not isinstance(driver_dict['current_location_id'], int):
            driver_validation_errors.append(
                f"Driver 'current_location_id' must be an integer")
    if "car" in driver_dict:
        if not isinstance(driver_dict['car'], dict):
            driver_validation_errors.append(f"Driver's car must be a dict")
    if "ratings" in driver_dict:
        if not isinstance(driver_dict["ratings"], list):
            driver_validation_errors.append(f"Driver 'ratings' must be a list")
    if "language" in driver_dict:
        if not isinstance(driver_dict['language'], str):
            driver_validation_errors.append(
                f"Driver 'language' must be a string")

    # Validates structure and data types in 'preferences' nested dict

    if "preference" in driver_dict:
        if not isinstance(driver_dict["preference"], dict):
            driver_validation_errors.append(
                f"Driver 'preference' must be a dict")
        else:
            preferences = driver_dict['preference']

            if 'min_rating' not in preferences:
                driver_validation_errors.append(
                    f"Driver preference missing 'min_rating'")
            elif not isinstance(preferences['min_rating'], int):
                driver_validation_errors.append(
                    f"Driver 'min_rating' must be an integer")

            if 'max_distance' not in preferences:
                driver_validation_errors.append(
                    f"Driver preference missing 'max_distance'")
            elif not isinstance(preferences['max_distance'], int):
                driver_validation_errors.append(
                    f"Driver 'max_distance' must be an integer")

    # Raises DataFormatError if any errors are found within driver_validation_errors list

    if driver_validation_errors:
        raise DataFormatError(
            f"Errors detected while formatting data: {driver_validation_errors}")


def validate_locations(location_dict):
    '''Validates, storing all errors and returning them simultaneously for efficient error-handling'''

    location_validation_errors = []
    required_keys = ["node_id", "type", "node"]

    # Validates presence of required 'location' keys

    for key in required_keys:
        if key not in location_dict:
            location_validation_errors.append(
                f"Missing key: {key} in {location_dict}")

    # Validates structure and data type of 'location' keys

    if "node_id" in location_dict:
        if not isinstance(location_dict["node_id"], str):
            location_validation_errors.append(f"'Node_id' must be a string")
    if "type" in location_dict:
        if not isinstance(location_dict["type"], str):
            location_validation_errors.append(
                f"Location 'type' must be a string")
    if "node" in location_dict:
        if not isinstance(location_dict["node"], int):
            location_validation_errors.append(
                f"Location 'node' must be an integer")

    # Raises DataFormatError if any errors are found within location_validation_errors list

    if location_validation_errors:
        raise DataFormatError(
            f"Errors detected while formatting data: {location_validation_errors}")


def validate_payment_methods(payment_method_dict):
    '''Validates, storing all errors and returning them simultaneously for efficient error-handling'''

    payment_validation_errors = []
    required_keys = ["method_id", "type", "owner_user_id", "owner_name"]

    # Validates presence of required 'payment_method' keys

    for key in required_keys:
        if key not in payment_method_dict:
            payment_validation_errors.append(
                f"Missing key: {key} in {payment_method_dict}")

    # Validates top-level key structure (shared by both payment methods)

    if "method_id" in payment_method_dict:
        if not isinstance(payment_method_dict["method_id"], str):
            payment_validation_errors.append(
                f"Payment 'method_id' must be a string")

    if "owner_user_id" in payment_method_dict:
        if not isinstance(payment_method_dict["owner_user_id"], str):
            payment_validation_errors.append(
                f"Payment 'owner_user_id' must be a string")

    if "owner_name" in payment_method_dict:
        if not isinstance(payment_method_dict["owner_name"], str):
            payment_validation_errors.append(
                f"Payment 'owner_name' must be a string")

    # Given valid presence of top-level keys, validates keys specific to each 'payment_method' type

    if "type" in payment_method_dict:

        payment_method = payment_method_dict["type"]

        if not isinstance(payment_method, str):
            payment_validation_errors.append(
                f"Payment method 'type' must be a string")

        else:  # Validates structure of specified payment types:
            if payment_method == "CreditCardPayment":   # CreditCardPayment Validation
                required_cc_keys = ["card_number",
                                    "expiration_date", "billing_address"]

                for key in required_cc_keys:
                    if key not in payment_method_dict:
                        payment_validation_errors.append(
                            f"Missing key: {key} in {payment_method_dict}")

                if "card_number" in payment_method_dict:
                    if not isinstance(payment_method_dict["card_number"], str):
                        payment_validation_errors.append(
                            f"'card_number' must be a string")

                if "expiration_date" in payment_method_dict:
                    if not isinstance(payment_method_dict["expiration_date"], str):
                        payment_validation_errors.append(
                            f"Payment 'expiration_date' must be a string")

                if "billing_address" in payment_method_dict:
                    if not isinstance(payment_method_dict["billing_address"], str):
                        payment_validation_errors.append(
                            f"Payment 'billing_address' must be a string")

            elif payment_method == "DigitalWalletPayment":  # DigitalWalletPayment Validation
                required_dw_keys = ["wallet_provider", "wallet_id"]

                for key in required_dw_keys:
                    if key not in payment_method_dict:
                        payment_validation_errors.append(
                            f"Missing key: {key} in {payment_method_dict}")

                if "wallet_provider" in payment_method_dict:
                    if not isinstance(payment_method_dict["wallet_provider"], str):
                        payment_validation_errors.append(
                            f"Payment 'wallet_provider' must be a string")

                if "wallet_id" in payment_method_dict:
                    if not isinstance(payment_method_dict["wallet_id"], str):
                        payment_validation_errors.append(
                            f"Payment 'wallet_id' must be a string")

    # Raises DataFormatError if any errors are found within payment_validation_errors list

    if payment_validation_errors:
        raise DataFormatError(
            f"Errors detected while formatting data: {payment_validation_errors}")


def validate_billing_info(billing_info_dict):
    '''Validates, storing all errors and returning them simultaneously for efficient error-handling'''

    billing_info_validation_errors = []
    required_keys = ["user_id", "payment_method_ids", "default_method_id"]

    # Validates presence of billing_info keys

    for key in required_keys:
        if key not in billing_info_dict:
            billing_info_validation_errors.append(
                f"Missing key: {key} in {billing_info_dict}")

    # Validates structure and data type of billing_info keys

    if "user_id" in billing_info_dict:
        if not isinstance(billing_info_dict["user_id"], str):
            billing_info_validation_errors.append(
                "Billing info 'user_id' must be a string")

    if "default_method_id" in billing_info_dict:
        if not isinstance(billing_info_dict["default_method_id"], str):
            billing_info_validation_errors.append(
                f"Billing info 'default_method_id' must be a string")

    if "payment_method_ids" in billing_info_dict:
        if not isinstance(billing_info_dict["payment_method_ids"], list):
            billing_info_validation_errors.append(
                f"Billing info 'payment_method_ids' must be a list")

        # Validates payment_method

        else:
            payment_method_ids = billing_info_dict['payment_method_ids']
            for method_id in payment_method_ids:
                if not isinstance(method_id, str):
                    billing_info_validation_errors.append(
                        f"Billing info '{method_id}' must be a string")

    # Raises DataFormatError if any errors are found within billing_info_validation_errors list

    if billing_info_validation_errors:
        raise DataFormatError(
            f"Errors detected while formatting data: {billing_info_validation_errors}")


def validate_rides(ride_dict):
    '''Validates, storing all errors and returning them simultaneously for efficient error-handling'''

    ride_validation_errors = []
    required_keys = ["ride_id", "rider_id", "driver_id",
                     "pickup_location_id", "dropoff_location_id", "status", "fare_amount"]

    # Validates presence of 'ride' keys

    for key in required_keys:
        if key not in ride_dict:
            ride_validation_errors.append(f"Missing key: {key} in {ride_dict}")

    # Given valid presence, validates class of 'ride' keys

    if "ride_id" in ride_dict:
        if not isinstance(ride_dict["ride_id"], str):
            ride_validation_errors.append(f"'Ride 'id' must be a string")

    if "rider_id" in ride_dict:
        if not isinstance(ride_dict["rider_id"], str):
            ride_validation_errors.append(f"'Rider id' must be a string")

    if "driver_id" in ride_dict:
        if not isinstance(ride_dict["driver_id"], str):
            ride_validation_errors.append(f"'Driver id' must be a string")

    if "pickup_location_id" in ride_dict:
        if not isinstance(ride_dict["pickup_location_id"], str):
            ride_validation_errors.append(
                f"'Pickup location id' must be a string")

    if "dropoff_location_id" in ride_dict:
        if not isinstance(ride_dict["dropoff_location_id"], str):
            ride_validation_errors.append(
                f"'Dropoff location 'id' must be a string")

    if "status" in ride_dict:
        if not isinstance(ride_dict["status"], str):
            ride_validation_errors.append(f"'Status' must be a string")

    if "fare_amount" in ride_dict:
        if not isinstance(ride_dict["fare_amount"], float):
            ride_validation_errors.append(f"'Fare amount' must be a float")

    # Raises DataFormatError if any errors are found within ride_validation_errors list

    if ride_validation_errors:
        raise DataFormatError(
            f"Errors detected while formatting data: {ride_validation_errors}")

# ====================[Cross-Reference Validators]==============================


def validate_location_reference(loc_id, location_dict, context):
    '''Location cross-reference validator'''
    if loc_id not in location_dict:
        raise DataReferenceError(
            f"Unknown location_id '{loc_id}' in {context}")


def validate_payment_method_reference(method_id, payment_method_dict, context):
    '''Payment method cross-reference validator'''
    if method_id not in payment_method_dict:
        raise DataReferenceError(
            f"Unknown method_id '{method_id}' in {context}")


def validate_rider_reference(rider_id, rider_dict, context):
    '''Rider cross-reference validator'''
    if rider_id not in rider_dict:
        raise DataReferenceError(f"Unknown rider_id '{rider_id}' in {context}")


def validate_driver_reference(driver_id, driver_dict, context):
    '''Driver cross-reference validator'''
    if driver_id not in driver_dict:
        raise DataReferenceError(
            f"Unknown driver_id '{driver_id}' in {context}")


def validate_billing_info_reference(rider_id, billing_info_dict, context):
    '''Billing info cross-reference validator'''
    if rider_id not in billing_info_dict:
        raise DataReferenceError(f"Unknown user_id '{rider_id}' in {context}")

# ====================[JSON File Handling]==============================


def load_locations(graph):
    '''Loads locations from locations.json and assigns graph nodes with updated error handling'''

    print(f"Loading locations from 'locations.json'")
    location_data = load_json_file(
        "locations.json", expected_top_key="locations")
    location_list = location_data["locations"]

    for loc_dict in location_data["locations"]:

        validate_locations(loc_dict)  # Validator

    location_objects = {}

    for node in graph.nodes():

        location_objects[node] = Location(node)

    print(f"Created {len(location_objects)} location objects from graph.")
    return location_objects


def load_payment_methods():
    '''Loads payment methods from payment_methods.json'''

    print(f"Loading payment methods from 'payment_methods.json'")
    payment_method_data = load_json_file(
        "payment_methods.json", expected_top_key="payment_methods")

    payment_method_list = payment_method_data["payment_methods"]
    payment_method_objects = {}

    for payment_method_dict in payment_method_list:

        validate_payment_methods(payment_method_dict)  # Validator

        method_id = payment_method_dict["method_id"]
        payment_type = payment_method_dict["type"]
        owner_name = payment_method_dict["owner_name"]

        if payment_type == "CreditCardPayment":
            card_number = payment_method_dict["card_number"]
            expiration_date = payment_method_dict["expiration_date"]
            billing_address = payment_method_dict["billing_address"]

            payment_method_obj = CreditCardPayment(
                method_id, owner_name, card_number, expiration_date, billing_address)

        elif payment_type == "DigitalWalletPayment":
            wallet_provider = payment_method_dict["wallet_provider"]
            wallet_id = payment_method_dict["wallet_id"]

            payment_method_obj = DigitalWalletPayment(
                method_id, owner_name, wallet_provider, wallet_id)

        payment_method_objects[method_id] = payment_method_obj
    return payment_method_objects


def load_billing_info(payment_method_objects):
    '''Loads billing info from billing_info.json'''

    print(f"Loading billing info from 'billing_info.json'")
    billing_info_data = load_json_file(
        "billing_info.json", expected_top_key="billing_info")

    billing_info_list = billing_info_data["billing_info"]
    billing_info_objects = {}

    for billing_info_dict in billing_info_list:

        validate_billing_info(billing_info_dict)  # Validator

        user_id = billing_info_dict["user_id"]
        payment_method_ids = billing_info_dict["payment_method_ids"]
        default_method_id = billing_info_dict["default_method_id"]

        billing_info_obj = BillingInfo(user_id)

        for payment_method_id in payment_method_ids:

            # Cross-reference Validator for Payment_methods
            validate_payment_method_reference(
                payment_method_id, payment_method_objects, f"BillingInfo {user_id}")

            payment_method = payment_method_objects[payment_method_id]
            billing_info_obj.add_payment_method(payment_method)

        # Cross-reference Validator for default_payment_methods
        validate_payment_method_reference(
            default_method_id, payment_method_objects, f"BillingInfo {user_id} default")

        default_method = payment_method_objects[default_method_id]
        billing_info_obj.set_default_method(default_method)

        billing_info_objects[user_id] = billing_info_obj

    return billing_info_objects


def load_riders(location_objects, billing_info_objects):
    '''Loads riders from riders.json'''

    print(f"Loading riders from 'riders.json'")
    rider_data = load_json_file("riders.json", expected_top_key="riders")

    rider_list = rider_data["riders"]
    rider_objects = {}

    for i, rider_dict in enumerate(rider_data['riders']):

        validate_rider_record(rider_dict)  # Validator

        # Builds user ids for each rider in JSON list
        user_id = f"R{i}"

        # References lists of names and nodes to randomly assign
        name = random.choice(rider_names)
        # Randomly assigns graph nodes to riders
        node = random.choice(list(location_objects.keys()))

        # Builds location objects using assigned node
        current_location_id = node
        current_location = Location(node)

        ratings = rider_dict["ratings"]
        pref_data = rider_dict["preference"]

        # Cross-reference validators

        validate_location_reference(
            current_location_id, location_objects, f"Rider {user_id}")

        validate_billing_info_reference(
            user_id, billing_info_objects, f"Rider {user_id}")

        billing_info = billing_info_objects[user_id]

        preference_obj = Preference(
            preferred_language=pref_data["preferred_language"], prefers_self_driven=pref_data["prefers_self_driven"])

        rider_obj = Rider(name=name, user_id=user_id, billing_info=billing_info,
                          current_location=current_location, preference=preference_obj)

        for rating in ratings:
            rider_obj.add_rating(rating)

        rider_objects[user_id] = rider_obj

    return rider_objects


def load_drivers(location_objects):
    '''Loads drivers from drivers.json'''

    print(f"Loading drivers from 'drivers.json'")
    driver_data = load_json_file("drivers.json", "drivers")

    driver_list = driver_data["drivers"]
    driver_objects = {}

    for i, driver_dict in enumerate(driver_data['drivers']):

        validate_driver_record(driver_dict)  # Validator

        user_id = f"D{i}"

        # References lists of names and nodes to randomly assign
        name = random.choice(driver_names)
        # Randomly assigns graph nodes to drivers
        current_location_id = random.choice(list(location_objects.keys()))

        # Referencing JSON values for specified keys: (Language, Ratings, and Preference)

        language = random.choice(languages)
        ratings = driver_dict["ratings"]
        preference = driver_dict["preference"]

        # Cross-reference Validator

        validate_location_reference(
            current_location_id, location_objects, f"Driver {user_id}")

        # Assembling car objects (composition: driver has-a car)

        car_data = driver_dict["car"]
        car_type = car_data["type"]
        year = car_data["year"]
        make = car_data["make"]
        model = car_data["model"]
        plate_number = car_data["plate"]

        if car_type == "HumanDrivenCar":
            car = HumanDrivenCar(year, make, model, plate_number)
        elif car_type == "SelfDrivenCar":
            car = SelfDrivenCar(year, make, model, plate_number)

        # Assembling preferences (composition: driver has-a preference)

        pref_data = driver_dict["preference"]
        preference_obj = Preference(
            min_rating=pref_data["min_rating"],
            max_distance=pref_data["max_distance"])

        current_location = location_objects[current_location_id]

        driver_obj = Driver(name=name, user_id=user_id,
                            car=car, current_location=current_location, preference=preference_obj, language=language)

        for rating in ratings:
            driver_obj.add_rating(rating)

        driver_objects[user_id] = driver_obj

    return driver_objects


def load_rides(rider_objects, driver_objects, location_objects):
    '''Loads rides from rides.json'''

    print(f"Loading rides from 'rides.json'")
    ride_data = load_json_file("rides.json", expected_top_key="rides")

    ride_list = ride_data["rides"]
    ride_objects = {}

    for ride_dict in ride_list:

        validate_rides(ride_dict)  # Validator

        ride_id = ride_dict["ride_id"]
        rider_id = ride_dict["rider_id"]
        driver_id = ride_dict["driver_id"]
        pickup_location_id = ride_dict["pickup_location_id"]
        dropoff_location_id = ride_dict["dropoff_location_id"]
        status = ride_dict["status"]
        fare_amount = ride_dict["fare_amount"]

        # Cross-reference Validators

        validate_rider_reference(rider_id, rider_objects, f"Ride {ride_id}")
        validate_driver_reference(driver_id, driver_objects, f"Ride {ride_id}")
        validate_location_reference(
            pickup_location_id, location_objects, f"Ride {ride_id} pickup")
        validate_location_reference(
            dropoff_location_id, location_objects, f"Ride {ride_id} dropoff")

        rider_obj = rider_objects[rider_id]
        driver_obj = driver_objects[driver_id]
        pickup_location = location_objects[pickup_location_id]
        dropoff_location = location_objects[dropoff_location_id]

        ride_obj = Ride(rider=rider_obj, driver=driver_obj,
                        destination=dropoff_location, status=status)

        ride_obj.set_locations(pickup_location, dropoff_location)

        ride_obj._fare = fare_amount

        ride_objects[ride_id] = ride_obj

    return ride_objects

# ======================[Helper Functions]======================


def test_json_loaders():
    '''Tests all JSON loader functions'''

    print(f"Testing JSON Loaders")
    print(f"===========================")

    # Load in dependency order
    print(f"Loading locations...")
    location_objects = load_locations()
    print(f"Loaded {len(location_objects)} locations")

    print(f"Loading payment methods...")
    payment_method_objects = load_payment_methods()
    print(f"Loaded {len(payment_method_objects)} payment methods")

    print(f"Loading billing info...")
    billing_info_objects = load_billing_info(payment_method_objects)
    print(f"Loaded {len(billing_info_objects)} billing info records")

    print(f"Loading riders...")
    rider_objects = load_riders(location_objects, billing_info_objects)
    print(f"Loaded {len(rider_objects)} riders")

    print(f"Loading drivers...")
    driver_objects = load_drivers(location_objects)
    print(f"Loaded {len(driver_objects)} drivers")

    print(f"Loading rides...")
    ride_objects = load_rides(rider_objects, driver_objects, location_objects)
    print(f"Loaded {len(ride_objects)} rides")
    return location_objects, payment_method_objects, billing_info_objects, rider_objects, driver_objects, ride_objects


def find_matching_driver(rider, available_driver_list):
    '''Searches for first driver that matches both preferences'''

    print(f"Searching for preferential match...")

    # Stores rider's preferences and location
    rider_preference = rider.get_preference()
    rider_location = rider.get_current_location()

    # Stores driver's preferences and location
    for driver in available_driver_list:
        driver_preference = driver.get_preference()
        driver_location = driver.get_current_location()

        if rider_preference and rider_preference.matches_driver(driver) and driver_preference and driver_preference.matches_rider(rider, rider_location):
            print(f"{rider.get_name()} and {driver.get_name()} have been matched.")
            driver.go_offline()
            return driver

    return None


def greedy_match_unweighted(graph, riders, drivers):
    '''Matches rider and driver using unweighted distance (counting hops)'''

    print(f"Commencing unweighted greedy match search...")

    matches = []  # Empty list to store matches

    for rider in riders:
        driver_candidates = []
        rider_location = rider.get_current_location().get_node()  # Retrieves rider location
        # Communicates rider location to user
        print(f"Rider location: {rider_location}")

        for potential_driver in drivers:  # Iterates through passed list of driver objects

            if potential_driver.is_available:  # Evaluates boolean availability of indexed driver object
                potential_driver_node = potential_driver.get_current_location(
                ).get_node()  # Retrieves location (node) of driver
                # Evaluates shortest path between rider and driver
                distance = nx.shortest_path_length(
                    graph, rider_location, potential_driver_node)
                # Creates a tuple of driver, driver location, and distance and adds to driver candidate list
                driver_candidates.append(
                    (potential_driver, potential_driver_node, distance))
                # Communicates driver location to user
                print(f"Driver location: {potential_driver_node}")

        if driver_candidates:  # Checks for populated list of driver candidates, then sets driver with the lowest distance
            optimal_candidate = min(
                driver_candidates, key=lambda x: (x[2], x[1]))
            matched_driver = optimal_candidate[0]
            matched_node = optimal_candidate[1]
            matched_distance = optimal_candidate[2]

            print(f"{rider.get_name()} -> Node: {rider_location} matched with {matched_driver.get_name()} -> Node: {matched_node}. Distance: {matched_distance} hops")

            matched_driver.is_available = False

            ride = Ride(rider, matched_driver, destination=None)
            ride._distance = matched_distance
            matches.append((rider, matched_driver, matched_distance))
        else:
            print(f"No available drivers for {rider.get_name()}.")

    return matches


def greedy_match_weighted(graph, riders, drivers, ):
    '''Matches rider and driver using unweighted distance (summing edge weights)'''

    print(f"Commencing weighted greedy match search...")

    matches = []  # Empty list to store matches

    for rider in riders:
        driver_candidates = []
        rider_location = rider.get_current_location().get_node()
        # Communicates rider location to user
        print(f"Rider location: {rider_location}")

        for potential_driver in drivers:
            if potential_driver.is_available:  # Evaluates boolean availability of indexed driver object
                potential_driver_node = potential_driver.get_current_location(
                ).get_node()  # Retrieves location (node) of driver
                # Evaluates shortest path between rider and driver
                distance = nx.shortest_path_length(
                    graph, rider_location, potential_driver_node, weight='weight')
                # Creates a tuple of driver, driver location, and distance and adds to driver candidate list
                driver_candidates.append(
                    (potential_driver, potential_driver_node, distance))
                # Communicates driver location to user
                print(f"Driver location: {potential_driver_node}")

        if driver_candidates:  # Checks for populated list of driver candidates, then sets driver with the lowest distance
            optimal_candidate = min(
                driver_candidates, key=lambda x: (x[2], x[1]))
            matched_driver = optimal_candidate[0]
            matched_location = optimal_candidate[1]
            matched_distance = optimal_candidate[2]

            print(f"{rider.get_name()} -> Node: {rider_location} matched with {matched_driver.get_name()} -> {matched_location}. | Distance: {matched_distance} (weighted)")

            matched_driver.is_available = False

            ride = Ride(rider, matched_driver, destination=None)
            ride._distance = matched_distance
            matches.append((rider, matched_driver, matched_distance))
        else:
            print(
                f"No available drivers within 20 hops for {rider.get_name()}.")

    return matches


def select_driver(rider_node, drivers, graph_model):
    '''Returns the closest available driver to rider_node. Skips unreachable drivers.'''
    candidates = []
    for driver in drivers:
        if driver.is_available:
            try:
                driver_node = driver.get_current_location().get_node()
                distance = nx.shortest_path_length(graph_model.graph, rider_node, driver_node)
                candidates.append((driver, driver_node, distance))
            except nx.NetworkXNoPath:
                pass  # skip unreachable drivers
    if not candidates:
        return None
    return min(candidates, key=lambda x: (x[2], x[1]))[0]

def create_an_agent():
    '''Creates an agent'''
    agent = Agent("Agent_007")
    return agent


def time_ride(func):
    '''Decorator that gives current date and time then measures the ride's execution time'''

    def wrapper(*args, **kwargs):
        current_date = time.ctime(time.time())
        print(f"Today's date: {current_date}.")

        # Measures execution time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Here is the length of your ride: {elapsed} seconds...")
        return result
    return wrapper


def request_ride(rider, pickup_location, destination):
    '''Rider requests ride for agent to log'''

    requested_ride = rider.request_ride(pickup_location, destination)
    print(f"{rider} has requested a ride from {pickup_location} to {destination}.")
    return rider, requested_ride, pickup_location, destination


def driver_go_online(drivers):
    '''Driver goes online for agent to manage'''

    available_drivers = []

    # Sets each driver status to online, referencing list of drivers
    for driver in drivers:
        driver.go_online()
        available_drivers.append(driver)

    return available_drivers


def setup_rider_billing():
    '''Sets billing for each rider'''

    for rider in list_of_riders:
        name = rider.get_name()

        if name == "Alice":
            alice_card = CreditCardPayment(
                "alice_card", "Alice", "**** **** **** 1234", "12/27", "123 University Blvd.")
            alice_wallet = DigitalWalletPayment(
                "alice_wallet", "Alice", "Google", "alice@gmail.com")
            billing_info = BillingInfo(rider)
            billing_info.add_payment_method(alice_card)
            billing_info.add_payment_method(alice_wallet)

        elif name == "Marcus":
            marcus_card = CreditCardPayment(
                "marcus_card", "Marcus", "**** **** **** 2345", "12/27", "456 University Blvd.")
            marcus_wallet = DigitalWalletPayment(
                "marcus_wallet", "Marcus", "Google", "marcus@gmail.com")
            billing_info = BillingInfo(rider)
            billing_info.add_payment_method(marcus_card)
            billing_info.add_payment_method(marcus_wallet)

        elif name == "Priya":
            priya_card = CreditCardPayment(
                "priya_card", "Priya", "**** **** **** 3456", "12/27", "789 University Blvd.")
            priya_wallet = DigitalWalletPayment(
                "priya_wallet", "Priya", "Google", "priya@gmail.com")
            billing_info = BillingInfo(rider)
            billing_info.add_payment_method(priya_card)
            billing_info.add_payment_method(priya_wallet)

        print(f"Card and digital wallet have been created for {name}.")
        rider.set_billing_info(billing_info)

    return list_of_riders


# ==================================[JSON Simulation]====================================
total_rides = 0
saved_rides = []


@time_ride
def simulate_ride_json_preferential():
    '''Simulates ride via integration of JSON loaders and preferential matching'''

    global total_rides

    print(f"Simulating ride via JSON integration and preferential matching...")

    city_map = create_map_network()

    # Loads JSON dicts

    location_objects = load_locations(city_map)
    payment_method_objects = load_payment_methods()
    billing_info_objects = load_billing_info(payment_method_objects)
    rider_objects = load_riders(location_objects, billing_info_objects)
    driver_objects = load_drivers(location_objects)
    # ride_objects = load_rides(
    #    rider_objects, driver_objects, location_objects)

    # Converts JSON dicts to lists
    list_of_riders = list(rider_objects.values())
    list_of_drivers = list(driver_objects.values())
    available_drivers = []

    # Establishes current rider
    current_rider = random.choice(list_of_riders)
    list_of_riders.remove(current_rider)

    # Establishes agent
    agent = Agent("Agent_007")

    # Establishes pickup location
    pickup_node = current_rider.get_current_location().get_node()
    pickup_location = location_objects[pickup_node]

    # Establishes destination
    destination_node = random.choice(list(location_objects.keys()))
    destination = location_objects[destination_node]

    # Requests ride
    request_ride(current_rider, pickup_location, destination)

    # Riders go online for possible pickup
    for driver in list_of_drivers:
        driver.go_online()
        if driver.is_available:
            available_drivers.append(driver)

    # Online drivers are checked for matching preferences
    driver = find_matching_driver(current_rider, available_drivers)
    if driver is None:
        print(
            f"No matching driver for {current_rider.get_name()}. Ride cancelled.")
        return None

    # Ride is created and transitioned through statuses
    created_ride = agent.create_a_ride(current_rider, driver, destination)
    created_ride._distance = nx.shortest_path_length(
        city_map, pickup_node, destination_node)
    created_ride.accept()
    agent.log_ride(created_ride, "Accepted")
    created_ride.start()
    agent.log_ride(created_ride, "In progress")
    created_ride.complete()
    agent.log_ride(created_ride, "Complete")

    # Driver and rider exchange ratings, all logged by agent
    driver_rating = current_rider.rate_driver(driver, 5)
    agent.log_ride(
        created_ride, f"{current_rider.get_name()} rated {driver.get_name()}: {driver_rating} stars")
    rider_rating = driver.rate_rider(current_rider, 4)
    agent.log_ride(
        created_ride, f"{driver.get_name()} rated {current_rider.get_name()}: {rider_rating} stars")

    # Fare is calculated and charged to rider
    fare = created_ride.calculate_fare()
    print(f"Fare: ${fare:.2f}")
    created_ride.charge_rider()
    print(current_rider.get_billing_info())

    total_rides += 1
    saved_rides.append(created_ride)

    # Logs are returned
    agent.show_logs()

    # Opens 'rides.json' to save ride
    try:
        with open("rides.json", "r") as file:
            rides_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        rides_data = {"rides": []}

    # Creates ride record
    ride_record = {
        "ride_id": f"Ride{total_rides}",
        "rider_id": current_rider.get_user_id(),
        "driver_id": driver.get_user_id(),
        "pickup_location_id": pickup_location.get_node(),
        "dropoff_location_id": destination_node,
        "status": created_ride.get_status(),
        "fare_amount": created_ride._fare
    }

    # Saves ride record to JSON
    rides_data['rides'].append(ride_record)

    with open('rides.json', 'w') as file:
        json.dump(rides_data, file, indent=2)

    print(f"{total_rides} tracked...")
    print(f"{len(saved_rides)} rides successfully saved to 'rides.json'")


@time_ride
def simulate_ride_json_greedy():
    '''Simulates ride via integration of JSON loaders w/greedy matching'''

    global total_rides

    print(f"Simulating ride via JSON integration and greedy matching...")

    city_map = create_map_network()

    # Loads JSON dicts

    location_objects = load_locations(city_map)
    payment_method_objects = load_payment_methods()
    billing_info_objects = load_billing_info(payment_method_objects)
    rider_objects = load_riders(location_objects, billing_info_objects)
    driver_objects = load_drivers(location_objects)

    # Converts JSON dicts to lists
    list_of_riders = list(rider_objects.values())
    list_of_drivers = list(driver_objects.values())

    print(f"==========[Rider Locations]===========")
    for rider in list_of_riders:
        print(f"{rider.get_name()} - Rider ID: {rider.get_user_id()} -> {rider.get_current_location().get_node()}")

    print(f"==========[Driver Locations]===========")
    for driver in list_of_drivers:
        print(f"{driver.get_name()} - Driver ID: {driver.get_user_id()} - > {driver.get_current_location().get_node()}")

    # Unweighted Matching
    for driver in list_of_drivers:
        driver.go_online()

    unweighted_matches = greedy_match_unweighted(
        city_map, list_of_riders, list_of_drivers)

    for driver in list_of_drivers:
        driver.is_available = True

    weighted_matches = greedy_match_weighted(
        city_map, list_of_riders, list_of_drivers)

# ====================[Comparison Summary]=====================

    print(f"=================[Comparison Summary]==================")
    changed_riders = []

    for i in range(len(unweighted_matches)):
        rider_unweighted, driver_unweighted, distance_unweighted = unweighted_matches[i]
        rider_weighted, driver_weighted, distance_weighted = weighted_matches[i]

        if distance_unweighted >= 5:
            fare_unweighted = round(1.50 * distance_unweighted, 2)
        else:
            fare_unweighted = round(2.00 * distance_unweighted, 2)

        if distance_weighted >= 5:
            fare_weighted = round(1.50 * distance_weighted, 2)
        else:
            fare_weighted = round(2.00 * distance_weighted, 2)

        if driver_unweighted.get_user_id() != driver_weighted.get_user_id():
            changed_riders.append(rider_unweighted.get_name())
            print(
                f"\n Rider: {rider_unweighted.get_name()}"
                f"\n Unweighted: {driver_unweighted.get_name()} | {distance_unweighted} hops | Fare: ${fare_unweighted}"
                f"\n Weighted: {driver_weighted.get_name()} | {distance_weighted} cost | Fare: ${fare_weighted}"
            )

    print(f"{len(changed_riders)} rider(s) matched to a different driver in unweighted vs weighted.")
    # Opens 'rides.json' to save ride
    try:
        with open("rides.json", "r") as file:
            rides_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        rides_data = {"rides": []}

    for i, (rider, driver, distance) in enumerate(weighted_matches):
        if distance >= 5:
            fare = round(1.50 * distance, 2)
        else:
            fare = round(2.00 * distance, 2)

        # Creates ride record
        ride_record = {
            "ride_id": f"Ride_greedy_{i}",
            "rider_id": rider.get_user_id(),
            "driver_id": driver.get_user_id(),
            "pickup_location_id": rider.get_current_location().get_node(),
            "dropoff_location_id": driver.get_current_location().get_node(),
            "status": "Complete",
            "fare_amount": fare
        }

        # Saves ride record to JSON
        rides_data['rides'].append(ride_record)
        saved_rides.append(ride_record)
        total_rides += 1

    with open('rides.json', 'w') as file:
        json.dump(rides_data, file, indent=2)

    print(f"{len(saved_rides)} ride(s) successfully saved to 'rides.json'")

# ================[Assignment 5 Efficient Data Tracking]==============


def count_json_riders():
    '''Easy way to track number of riders loaded into json'''

    rider_count = 0
    with open("riders.json", "r") as file:
        rider_data = json.load(file)

    for rider in rider_data['riders']:
        rider_count += 1
    print(f"Number of riders: {rider_count}")
    return rider_count


def count_json_drivers():
    '''Easy way to track number of drivers loaded into json'''

    driver_count = 0
    with open("drivers.json", "r") as file:
        driver_data = json.load(file)

    for driver in driver_data['drivers']:
        driver_count += 1
    print(f"Number of drivers: {driver_count}")
    return driver_count


def count_json_locations():
    '''Easy way to track number of locations loaded into json'''

    rider_location_count = 0
    driver_location_count = 0
    destination_count = 0

    with open("locations.json", "r") as file:
        location_data = json.load(file)

    for location in location_data['locations']:
        if location["type"] == "RiderLocation":
            rider_location_count += 1
        elif location["type"] == "DriverLocation":
            driver_location_count += 1
        elif location["type"] == "Destination":
            destination_count += 1
    print(f"Number of rider locations: {rider_location_count}")
    print(f"Number of driver locations: {driver_location_count}")
    print(f"Number of destination locations: {destination_count}")
    return rider_location_count, driver_location_count, destination_count

# ========================================[MAIN MENU]=========================================

if __name__ == '__main__':
    print(f"======[MAIN MENU]======")
    print(f"1. Run ride simulation [JSON loading w/ preferential matching]")
    print(f"2. Run ride simulation [JSON/weighted greedy matching]")
    print(f"3: Track # of riders, drivers, and location counts")
    print(f"4. Run unit tests")
    print(f"5. Test Use Cases")
    print(f"6. Exit and save")

    mob_through_town = True

    while mob_through_town:
        create_an_agent()
        option = input(f"Select an option: ")
        if option == "1":
            errors_detected = False
            try:
                simulate_ride_json_preferential()
            except DataLoadError as d:
                print(f"DataLoadError detected: {d}")
                errors_detected = True
            except DataFormatError as d:
                print(f"DataFormatError detected: {d}")
                errors_detected = True
            except DataReferenceError as d:
                print(f"DataReferenceError detected: {d}")
                errors_detected = True
            except PaymentError as p:
                print(f"PaymentError detected: {p}")
                errors_detected = True
            except BillingError as b:
                print(f"BillingError detected: {b}")
                errors_detected = True
            except RideLogicError as r:
                print(f"RideLogicError detected: {r}")
                errors_detected = True
            except RideHailingError as r:
                print(f"RideHailingError detected: {r}")
                errors_detected = True
            except Exception as e:
                print(f"Error detected: {e}")
                errors_detected = True
            else:
                print(f"-----Simulation completed-----")
            finally:
                if errors_detected:
                    print(f"Correct errors before next simulation run....")
                else:
                    print("No errors detected.")
        elif option == "2":
            simulate_ride_json_greedy()
        elif option == "3":
            count_json_riders()
            count_json_drivers()
            count_json_locations()
        elif option == "4":
            import unittest
            loader = unittest.TestLoader()
            suite = loader.discover(start_dir='tests', pattern='test_*.py')
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        elif option == "5":
            simulate_use_cases()
        elif option == "6":
            print(f"Exiting...")
            mob_through_town = False
