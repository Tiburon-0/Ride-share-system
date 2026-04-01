import networkx as nx
import random
from car import SelfDrivenCar
from car import HumanDrivenCar


class Preference:

    '''Intializes Preference Class'''

    def __init__(self, min_rating=0, max_distance=float(), preferred_language=None, prefers_self_driven=False):
        self._min_rating = min_rating
        self._max_distance = max_distance
        self._preferred_language = preferred_language
        self._prefers_self_driven = prefers_self_driven

    # Getter methods

    def get_min_rating(self):
        '''Returns minimum rating for matching'''
        return self._min_rating

    def get_max_distance(self):
        '''Returns maximum distance for matching'''
        return self._max_distance

    def get_preferred_language(self):
        '''Returns preferred language for matching'''
        return self._preferred_language

    def get_prefers_self_driven(self):
        '''Returns self-driven vs human-driven car preference'''
        return self._prefers_self_driven

    # Setter methods

    def set_min_rating(self, min_rating):
        '''Updates minimum rating'''
        self._min_rating = min_rating
        return self._min_rating

    def set_max_distance(self, max_distance):
        '''Updates maximum distance'''
        self._max_distance = max_distance
        return self._max_distance

    # Matching methods

    def matches_driver(self, driver):

        '''Matches rider to driver based on rider's preferences'''

        # Checks that valid preferences have been set

        if self._preferred_language is not None:
            if driver.get_language() != self._preferred_language:
                print(f"Driver language does not match rider's preference...")
                return False

        # Checks that valid car preference has been set and stored
        
        if self._prefers_self_driven is not None:
            car = driver.get_car()

            # Retrieves car for comparison
            if car is not None:
                is_self_driven = isinstance(car, SelfDrivenCar)

            # Checks and compares stored preference against considered driver's car
                if self._prefers_self_driven != is_self_driven:
                    print(f"Car type does not meet rider's preference...")
                    return False

        return True

    def matches_rider(self, rider, driver_location):

        '''Matches driver to rider based on driver's preferences'''

        # Calls User method to determine average rating and stores result
        average_rating = rider.get_average_rating()

        # Checks against driver's minimum rating preference
        if average_rating < self._min_rating:
            print(f"Rider rating falls below driver preference.")
            return False

        # Stores rider's location 
        rider_location = rider.get_current_location()

        # Checks against driver's max distance preference
        if rider_location is not None and driver_location is not None:
            distance = driver_location.distance_to(rider_location)

            if distance > self._max_distance:
                print("Rider's location exceeds driver's preference.")
                return False

        return True

    
