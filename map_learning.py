import networkx as nx
import random

def create_graph(n, m):

    '''Creates a Barabasi-Albert graph to model traffic network'''

    pending_map = True

    while pending_map:

        print(f"Generating map...")

        # Generate network using a Barabasi-Albert graph
        map = nx.barabasi_albert_graph(n, m)


        # Checks network connectivity. If connected, returns network properties
        if nx.is_connected(map):
            map.graph['name'] = "Barabasi-Albert"
            nodes = map.nodes()        
            number_of_nodes = map.number_of_nodes()    
            edges = map.edges()
            number_of_edges = map.number_of_edges()
            print(f"Connected {map.graph['name']} map network created...") 
            print(f"**{map.graph['name']} Map Properties**")
            print(f"Nodes:{nodes}")
            print(f"Node count:{number_of_nodes}")
            print(f"Edges:{edges}")
            print(f"Edge count:{number_of_edges}")
            
            pending_map = False

            return map

city_map = create_graph(100, 3)

def print_u_v_nodes(graph):
    for u,v in graph.edges():
        print(f"U: {u}")
        print(f"V: {v}")
    for node in graph.nodes():
        print(node)
    return f"Nodes and edges printed"

print_u_v_nodes(city_map)

list_of_riders = []
list_of_drivers = []
list_of_available_drivers = []

# ================[Populate Riders]=============

# Riders
riders = ["Alice", "Marcus", "Priya", "Jordan", "Taylor", "Blake", "Cameron", "Dakota", "Ellis", "Larry"]

rider_nodes = {}

# Drivers
drivers = ["Carlos", "Yuki", "Rachel", "Austin", "Morgan",
"Zach", "Sofia", "Liam", "Emma", "Noah",
"Olivia", "Ethan", "Ava", "Mason", "Isabella",
"Lucas", "Mia", "Oliver", "Charlotte", "Elijah",
"Amelia", "James", "Harper", "Benjamin", "Evelyn",
"William", "Abigail", "Henry", "Emily", "Alexander",
"Elizabeth", "Michael", "Mila", "Daniel", "Ella",
"Matthew", "Avery", "Jackson", "Sofia", "David",
"Camila", "Joseph", "Aria", "Carter", "Scarlett",
"Owen", "Victoria", "Wyatt", "Madison", "John"]

driver_nodes = {}

def assign_driver_rider_data():
    '''Randomly assigns names, ratings, current_location_ids to drivers and riders'''

def populate_riders(rider_list, graph):
# Riders
    riders = ["Alice", "Marcus", "Priya", "Jordan", "Taylor", "Blake", "Cameron", "Dakota", "Ellis", "Larry"]

    rider_nodes = {}

    for rider in rider_list:
        for node in graph.nodes():
            if node % 5 == 0:
                rider

def load_riders(location_objects, billing_info_objects):


    '''Loads riders from riders.json'''


    print(f"Loading riders from 'riders.json'")
    rider_data = load_json_file("riders.json", expected_top_key="riders")


    rider_list = rider_data["riders"]
    rider_objects = {}


    for rider_dict in rider_list:


        validate_rider_record(rider_dict)  # Validator


        user_id = rider_dict["user_id"]
        name = rider_dict["name"]
        ratings = rider_dict["ratings"]
        current_location_id = rider_dict["current_location_id"]
        pref_data = rider_dict["preference"]


        # Cross-reference validators


        validate_location_reference(
            current_location_id, location_objects, f"Rider {user_id}")


        validate_billing_info_reference(
            user_id, billing_info_objects, f"Rider {user_id}")


        current_location = location_objects[current_location_id]


        billing_info = billing_info_objects[user_id]


        preference_obj = Preference(
            preferred_language=pref_data["preferred_language"], prefers_self_driven=pref_data["prefers_self_driven"])


        rider_obj = Rider(name=rider_dict["name"], user_id=rider_dict["user_id"], billing_info=billing_info,
                          current_location=location_objects[current_location_id], preference=preference_obj)


        for rating in ratings:
            rider_obj.add_rating(rating)


        rider_objects[user_id] = rider_obj


    return rider_objects
    
# ================[Populate Drivers]============

# Drivers
drivers = ["Carlos", "Yuki", "Rachel", "Austin", "Morgan",
"Zach", "Sofia", "Liam", "Emma", "Noah",
"Olivia", "Ethan", "Ava", "Mason", "Isabella",
"Lucas", "Mia", "Oliver", "Charlotte", "Elijah",
"Amelia", "James", "Harper", "Benjamin", "Evelyn",
"William", "Abigail", "Henry", "Emily", "Alexander",
"Elizabeth", "Michael", "Mila", "Daniel", "Ella",
"Matthew", "Avery", "Jackson", "Sofia", "David",
"Camila", "Joseph", "Aria", "Carter", "Scarlett",
"Owen", "Victoria", "Wyatt", "Madison", "John"]

languages = ["English", "Spanish", "Italian", "Japanese", "Mandarin", "French", "Arabic"]

location_nodes = []

def load_drivers(location_objects):

    '''Loads drivers from drivers.json'''

    print(f"Loading drivers from 'drivers.json'")
    driver_data = load_json_file("drivers.json", "drivers")

    driver_list = driver_data["drivers"]
    driver_objects = {}

    for i, driver_dict in driver_list:

        validate_driver_record(driver_dict)  # Validator

        user_id = f"D{i}"
        name = random.choice(drivers)
        current_location_id = random.choice(location_nodes)

        ratings = driver_dict["ratings"]
        preference = driver_dict["preference"]
        language = random.choice(languages)

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



# ========



