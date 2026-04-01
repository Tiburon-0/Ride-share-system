from user import User
from database_model import DatabaseModel


class Rider(User, DatabaseModel):

    '''Rider inherits from User (business logic) and DatabaseModel (persistence)'''

    table_name = "riders"

    def __init__(self, name, user_id, billing_info=None, current_location=None, preference=None):
        '''Initalize rider'''

        # Call parent constructor: User
        super().__init__(name, user_id)
        self._billing_info = billing_info
        self._ride_history = []
        self._current_location = current_location
        self.preference = preference
        self._on_trip = False
        self.status = "idle"

    def __str__(self):
        '''User-friendly display for Class'''
        return f"Rider: {self._name}, ID: {self._user_id}"

    # Getter methods

    def get_ride_history(self):
        '''Returns rider's history'''
        return self._ride_history

    def get_current_location(self):
        '''Returns rider's current location'''
        return self._current_location

    def get_preference(self):
        '''Returns rider's preference'''
        return self.preference

    def get_billing_info(self):
        '''Returns rider's billing info'''
        return self._billing_info

    # Setter methods

    def set_current_location(self, location):
        '''Updates rider's current location'''
        self._current_location = location
        return self._current_location

    def set_preference(self, preference):
        '''Updates rider's preference'''
        self.preference = preference
        return self.preference

    def set_billing_info(self, billing_info):
        '''Updates rider's billing info'''
        self._billing_info = billing_info
        return self._billing_info

    # Service methods

    def request_ride(self, pickup_location, destination):
        '''Rider picks a destination and requests ride'''
        
        if self.status in ("waiting", "on_trip"):
            raise Exception(f"{self._name} already has an active ride.")
        self.status = "waiting"
        from ride import Ride
        ride = Ride(self, driver=None, destination=destination)
        return ride

    def rate_rider(self, rider, rating):
        '''Driver rates rider'''

        if rating >= 1 and rating <= 5: 
            rider.add_rating(rating)
        else:
            print(f"Rating must be between 1 and 5.")
        print(f"{self._name} rated the rider {rider.get_name()} {rating} stars.")
        return rating    

    def add_ride_to_history(self, ride):
        '''Ride is added to personal ride history (local) and running list of rides (global list)'''
        self._ride_history.append(ride)
        return f"{ride} added to personal rider history."
    
    def start_ride(self):
        '''Transitions rider state from waiting to on_trip'''
        
        self._on_trip = True
        self.status = "on_trip"
        return self._on_trip, self.status

    def complete_ride(self):
        '''Changes rider trip state to False after ride completion'''

        self._on_trip = False
        self.status = "idle"
        return self._on_trip, self.status

    def _to_dict(self):
        '''Maps Rider instance variables to 'riders' table columns'''

        return {
            "id":             self._user_id,
            "name":           self._name,
            "rating_avg":     self.get_average_rating(),
            "total_rides":    len(self._ride_history),
            "preferences_id": None
        }
    
    @classmethod
    def _from_dict(cls, row):
        '''Rebuilds a Rider from a DB row'''
        return cls(name=row["name"], user_id=row["id"])