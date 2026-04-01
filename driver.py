from exceptions import RideLogicError
from user import User
from database_model import DatabaseModel


class Driver(User, DatabaseModel):

    table_name = "drivers"

    def __init__(self, name, user_id, is_available=False, car=None,
                 current_location=None, preference=None, language="English", rating=5):
        super().__init__(name, user_id)
        self.is_available = is_available
        self._car = car
        self._current_location = current_location
        self.preference = preference
        self.language = language
        self.rating = rating
        self.status = "available"

    def __str__(self):
        status = "online" if self.is_available else "offline"
        return f"{self._name} | {self.rating} stars | Car: {self._car} | {status}"

    # Getters
    def get_name(self):              return self._name
    def get_car(self):               return self._car
    def get_current_location(self):  return self._current_location
    def get_preference(self):        return self.preference
    def get_language(self):          return self.language
    def get_rating(self):            return self.rating

    # Setters
    def set_car(self, car):
        self._car = car
        return self._car

    def set_current_location(self, location):
        self._current_location = location
        return self._current_location

    def set_preference(self, preference):
        self.preference = preference
        return self.preference

    def set_language(self, language):
        self.language = language
        return self.language

    def assign_car(self, car):
        self._car = car
        print(f"{self._name} has been assigned: {car.get_description()}")
        return self._car

    def check_availability(self):
        if self.is_available:
            return f"{self._name} is available for pickups."
        return f"{self._name} is unavailable for pickups."

    def go_online(self):
        self.is_available = True
        return f"{self._name} is online and available for pickups."

    def go_offline(self):
        self.is_available = False
        return f"{self._name} is now offline."

    # State transitions
    def assign_to_trip(self, trip_id=None):
        self.status = "assigned"
        self.is_available = False

    def start_trip(self):
        if self.status != "assigned":
            raise RideLogicError("Driver must be assigned before starting trip...")
        self.status = "on_trip"
        return self.status

    def complete_trip(self):
        self.status = "available"
        self.is_available = True

    def accept_ride(self, rider_name, destination):
        return f"{self._name} accepted the ride with {rider_name} to {destination}."

    def rate_rider(self, rider, rating):
        if rating >= 1 and rating <= 5:
            rider.add_rating(rating)
        print(f"{self._name} rated the rider {rider.get_name()} {rating} stars.")
        return rating

    # ── Persistence ───────────────────────────

    def _to_dict(self):
        '''Maps Driver instance variables to 'drivers' table columns.'''

        car_type = None
        if self._car is not None:
            car_type = type(self._car).__name__   # returns simple description of complex car object (e.g., "SelfDrivenCar" or "HumanDrivenCar")
        return {
            "id":             self._user_id,
            "name":           self._name,
            "rating_avg":     self.get_average_rating(),
            "is_available":   1 if self.is_available else 0,
            "car_type":       car_type,
            "preferences_id": None
        }

    @classmethod
    def _from_dict(cls, row):
        '''Reconstructs a Driver object from a DB row.'''
        
        driver = cls(
            name=row["name"],
            user_id=row["id"],
            is_available=bool(row["is_available"])
        )
        return driver
