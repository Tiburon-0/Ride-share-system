===========================[User Class]============================
"user.py" as file:

Parent class for Driver and Rider

*** Instance attributes (name, user_id, [ratings]) ***

Methods: get_rating(), get_average_rating(), and add_rating()

=======[Rider Class]=======
"rider.py" as file:

*** Inherits from User
Instance attributes()
*Uses composition for flexibility
*Instance variables
-Inherited from user (billing_info, [ride_history], current_location, and preference) all passed as instance attributes 
Handled with mutators (e.g. getters & setters) ***

Manual simulation uses populate_riders() to setup load_drivers
{drivers} loaded in main.py from JSON ("riders.json" as file)

=======[Driver Class]======
"driver.py" as file:

*** Inherits from User
-Methods()
-Instance attributes 
--Inherited from user (name, user_id)
--Extends user class by adding language & {objects}: billing_info, is_available, car, current_location, preference passed 
---Handled with mutators (e.g. getters & setters) ***

Uses composition for flexibility

Manual simulation 
-Uses populate_drivers() to setup drivers drivers in main.py 

-Demonstrates composition by assigning and re-assigning cars via populate_drivers() function 


{drivers} loaded in main.py from JSON ("drivers.json" as file)

Error-handling:
Validated 

===========================[Car Class]============================
"car.py" as file:

Car parent class

*** Instance attributes (year, make, model, plate_number) ***

HumanDrivenCar
-Inherited from Car
Polymorphism:
-Overrides get_description() method to display f"Human-driven car description: {human_driven_car_description}"

SelfDrivenCar
-Inherited from Car
Polymorphism:
Overrides get_description() method to display f"Self-driven car description: {self_driven_car_description}"

===========================[Agent Setup]============================
"agent.py" as file:

*** Private instance attributes (self.__agent_id = agent_id) as opposed to protected
Never accessed by driver or rider ***

self.__logs = []

creates ride record (ride) and appends event description to [logs] 

===========================[Ride Setup]============================
"ride.py" as file:

{ride} loaded in main.py from JSON ("ride.json")

===========================[Location Setup]============================

Manual simulation uses populate_riders() to setup load_drivers
{locations} loaded in main.py from JSON ("locations.json" as file)

*** Instance attributes (node_id) ***

Integrates Barabasi-Albert graph as a map generated in Network X

distance_to(): '''Returns the distance between specified points using Djikstra's algorithm'''
-nx.shortest_path_length()



===========================[Preference Setup]=========================
"preference.py" as file:

def __init__(self, min_rating=0, max_distance=float(), preferred_language=None, prefers_self_driven=False):
    self._min_rating = min_rating
    self._max_distance = max_distance
    self._preferred_language = preferred_language
    self._prefers_self_driven = prefers_self_driven

{preferences} loaded in main.py from JSON (driver.json & rider.json)

===========================[Billing Setup]============================
"billing_info.py" as file:

{billing_info} loaded in main.py from billing_info.json
Billing class 
Class attributes 

Validation:

Payment methods represented as an accessible list (e.g. self._payment_methods = [])
add_payment_method() validates that a valid payment method is correctly passed then adds that payment method, while setting default method if necessary
Went with _user as opposed to user_id. Simpler and true to the heart of the mission as user id will be passed in eventually.
Rider has set_billing_info() method allowing for scalable billing history (e.g., addition of more billing methods) without hardcoding. 
Rider exhibits composition via instance attributes. 

==========[Payment Methods Setup]==========
"payment_method.py" as file:




===========================[Preferential Matching Algorithm]============================
find_matching_driver() in main.py

*** Searches for first driver that matches both preferences ***

1. Checks that valid preferences have been set

Stores rider's preferences and location
Stores driver's preferences and location

matches_driver(self, driver) | matches_rider(self, rider, driver_location)
-Checks that valid car preference has been set and stored
-Matches rider to driver based on rider's preferences
-Matches driver to rider based on driver's preferences
-Calls User method to determine average rating and stores result
-Checks against driver's minimum rating preference
-Checks against driver's max distance preference

===========================[Distance Matching Algorithm]============================

-Retrieves rider's location
-Retrieves driver's location
-Assigns driver to rider based on unweighted or weighted distance
-Removes driver
-Implements tie breaker
*If tie, assign driver with lower node.
**Useful because lower number node indicates that node was created sooner, (i.e., more likely logically to be chosen)

==============[Unweighted]===================

-Assigns driver to rider based on unweighted distance
*Counted hops

==============[Weighted]===================

-Assigns driver to rider based on weighted distance
*Sum of weighted edges
===========================[JSON Loaders]============================

load_rides()
load_riders()
load_drivers ()
load_billing_info()
load_locations()

===========================[Network X/Map]============================
Watts–Strogatz - 

**Barabási–Albert (BA): nx.barabasi_albert_graph(100, m)**
-More realistic to actual growth and network modeling
-Scale-free
-Preferential Attachment
-Nodes Rich get richer. Simulate hubs
-Power Law
-Nodes 

===========================[Custom Exceptions]============================

1. RideHailingError (Exception)
   - Base class for all domain-specific errors in the system
   - Allows catching of any system error with a single, general exception type
   - Location: Primarily in main.py, after other specified errors are caught

2. DataLoadError (RideHailingError)
   - Raised when JSON files cannot be opened or read during the loading process
   - Handles: FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError
   - Location: load_json_file() function in main.py

3. DataFormatError (RideHailingError)
   - Raised when JSON structure or field types are invalid
   - Validates required keys and correct data types
   - Location: validate_""_record() functions in main.py

4. DataReferenceError (RideHailingError)
   - Raised when IDs reference non-existent entities, ensuring valid referencing of necessary data 
   - Ensures all cross-references are valid before use
   - Location: validate_""_reference() functions in main.py

5. BillingError (RideHailingError)
   - Base class for billing-related errors 
   - Validates payment methods exist and default payment methods are set for each rider
   - Location: billing_info.py

6. PaymentError (BillingError)
   - Raised when payment processing and charging fails
   - More specific error type inherited from BillingError
   - Validates: card expiration, wallet providers, fare amounts
   - Location: payment_method.py

7. RideLogicError (RideHailingError)
   - Raised when ride operations happen in wrong order (i.e. invalid logic, inconsistent, or incomplete ride state)
   - Validates: locations set before fare calculation, billing exists before charging
   - Location: ride.py

=============================[JSON Validation and Cross-Referencing]=============================

JSON File Loading:
- All JSON loading goes through load_json_file(), which is called by each load_""_file() function
- Catches file errors, encoding errors, and malformed JSON
- Raises appropriate exceptions (DataLoadError or DataFormatError)

Field Validation:
- Implemented in validate_""_record() functions 
- Checks required keys exist and structure of correct data types
- Applied in each load_""_file() function before creating objects

Cross-Reference Validation:
- Implemented in validate_""_reference() functions
- Validates IDs exist before accessing dictionaries
- Applied in:
  - load_riders() 
  - load_drivers() 
  - load_billing_info() 
  - load_rides() 

=====================[Error Detection and Reporting]==============================

Main Program Flow:
- Main menu uses structured try/except/else blocks
- Each menu option wrapped in exception handling
- Exceptions caught in order from most specific -> most general

Error Handling Strategy:
- Specific exceptions caught first (PaymentError before BillingError)
- User-friendly error messages displayed
- Else block confirms successful completion 

Error Messages:
- All exceptions include context about what failed
- Cross-reference errors identify which ID and which entity
- Payment/billing errors explain the specific validation that failed
- Users can immediately understand the errors raised and troubleshoot efficiently


==================[Part 7 Reflection]=================
Question 1:Why did some riders get different drivers when edge weights were added?

Answer 1: Riders received different drivers because of the matching algorithm's functionality.
The matching algorithm accounts for the preferences of both the driver and rider. The driver's preferences include min_rating and max_distance.
Different weights affect the distance between the rider and driver. 

====

Question 2:How does the choice of random graph model (ER, WS, BA) affect routing and distances in your system?

Answer 2: The parameters in BA maps are (n, m). Each node is connected by m edges, so routing and distances become more complex with each node.
Essentially, each additional node adds three additional paths. This means, nodes that are created earlier than others have heavier weights due to the higher number of connections which proliferate from them.

====

Question 3: What real-world ride-hailing behaviors does weighted routing capture that unweighted routing does not?

Answer 3: Weighted routing captures hubs, highways, and streets. 
Highways typically have a higher speed limit and more lanes, so they carry less weight. Streets typically have slower speed limits, so they carry greater weights.

====

Question 4: How did integrating your object-oriented classes (Rider, Driver, Ride, etc.) influence the structure and clarity of your solution? 
Answer 4: