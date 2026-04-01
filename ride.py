import json
from datetime import datetime
from exceptions import RideHailingError, RideLogicError
from database_model import DatabaseModel
from database_manager import execute_query


class Ride(DatabaseModel):
    '''Represents a single trip. Tracks lifecycle timestamps and persists to the trips table'''

    table_name = "trips"

    _ride_counter = 0   # simple counter for generating unique ride IDs

    def __init__(self, rider, driver, destination, payment_method=None, status="requested"):
        Ride._ride_counter += 1
        self._ride_id       = f"TRIP_{Ride._ride_counter:04d}"
        self._rider         = rider
        self._driver        = driver
        self._rider_location = rider.get_current_location() if rider else None
        self._destination   = destination
        self._distance      = None
        self._payment_method = payment_method
        self._fare          = None
        self._status        = status
        self._matching_log_id = None

        # Timestamps — set as each lifecycle event fires
        self._requested_at  = datetime.now().isoformat()
        self._accepted_at   = None
        self._started_at    = None
        self._completed_at  = None

    def __str__(self):
        return f"{self._rider} | {self._driver} | {self._rider_location} | {self._destination}"

    # Getters
    def get_rider(self):          return self._rider
    def get_driver(self):         return self._driver
    def get_rider_location(self): return self._rider_location
    def get_destination(self):    return self._destination
    def get_distance(self):       return self._distance
    def get_status(self):         return self._status
    def get_ride_id(self):        return self._ride_id

    def set_driver(self, driver):
        self._driver = driver
        return self._driver

    def set_locations(self, pickup_location, destination):
        self._rider_location = pickup_location
        self._destination = destination
        return self._rider_location, self._destination

    @property
    def status(self):
        return self._status

    # Lifecycle transitions
    def accept(self):
        self._status = "accepted"
        self._accepted_at = datetime.now().isoformat()
        return f"Ride status: {self._status}..."

    def start(self):
        if self._status != "accepted":
            raise RideLogicError("Ride must be accepted before starting.")
        self._status = "in_progress"
        self._started_at = datetime.now().isoformat()
        print(f"Rider and driver are en route.")
        return f"Ride status: {self._status}..."

    def complete(self):
        if self._status != "in_progress":
            raise RideLogicError("Ride must be in progress before completing.")
        self._status = "complete"
        self._completed_at = datetime.now().isoformat()
        print(f"Ride is complete.")
        return f"Ride status: {self._status}."

    def cancel(self, reason="No reason provided"):
        '''Cancel the trip mid-lifecycle and record the timestamp'''
        self._status = "canceled"
        self._completed_at = datetime.now().isoformat()
        self._cancel_reason = reason
        print(f"Ride canceled: {reason}")
        return f"Ride status: {self._status}."

    def calculate_fare(self, base_fare=2.50):
        if not self._rider_location or not self._destination:
            raise RideLogicError(f"Locations must be set before calculating fare")
        distance_traveled = self._distance
        print(f"Distance traveled: {distance_traveled} units")
        if distance_traveled >= 5:
            fare = float(1.50 * distance_traveled)
        else:
            fare = float(2.00 * distance_traveled)
        self._fare = round(fare, 2)
        return self._fare

    def charge_rider(self):
        if self._fare is None:
            self._fare = self.calculate_fare()
        billing_info = self._rider.get_billing_info()
        if billing_info is None:
            raise RideLogicError(f"Rider has not set billing info.")
        charge_result = billing_info.charge_default_payment_method(
            self._fare, self._destination)
        print(f"Rider has been charged ${self._fare}.")
        return charge_result

    # ── Persistence ───────────────────────────

    def _to_dict(self):
        '''Map Ride fields to the trips table columns, including all lifecycle timestamps'''
        
        rider_id  = self._rider.get_user_id() if self._rider else None
        driver_id = self._driver.get_user_id() if self._driver else None
        start_loc = str(self._rider_location) if self._rider_location else None
        end_loc   = str(self._destination) if self._destination else None
        return {
            "id":              self._ride_id,
            "rider_id":        rider_id,
            "driver_id":       driver_id,
            "start_location":  start_loc,
            "end_location":    end_loc,
            "requested_at":    self._requested_at,
            "accepted_at":     self._accepted_at,
            "started_at":      self._started_at,
            "completed_at":    self._completed_at,
            "fare":            self._fare,
            "status":          self._status,
            "matching_log_id": self._matching_log_id
        }

    @classmethod
    def _from_dict(cls, row):
        '''Rebuild a Ride from a DB row using __new__ to avoid incrementing the ride counter'''

        ride = cls.__new__(cls)   # bypass __init__ to avoid side effects
        ride._ride_id         = row["id"]
        ride._rider           = None        # load separately with Rider.get()
        ride._driver          = None
        ride._rider_location  = row["start_location"]
        ride._destination     = row["end_location"]
        ride._distance        = None
        ride._payment_method  = None
        ride._fare            = row["fare"]
        ride._status          = row["status"]
        ride._matching_log_id = row["matching_log_id"]
        ride._requested_at    = row["requested_at"]
        ride._accepted_at     = row["accepted_at"]
        ride._started_at      = row["started_at"]
        ride._completed_at    = row["completed_at"]
        return ride
