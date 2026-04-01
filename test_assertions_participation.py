import sys
import os
import networkx as nx
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from driver import Driver
from rider import Rider
from ride import Ride
from car import Car
from location import Location, RiderLocation


class TestAssertions(unittest.TestCase):

    def setUp(self):
        self.G = nx.Graph()
        self.G.add_node(5)

        self.rider = Rider("Ana", "R1")
        self.rider.set_current_location(Location(node=1))

        self.driver = Driver("Bob", "D1")

    def _make_ride(self, driver=None, destination=Location(node=2)):
        return Ride(self.rider, driver, destination)

    def test_same_node_distance_is_zero(self):
        loc_1 = Location(node=5)
        loc_2 = Location(node=5)
        distance = loc_1.distance_to(self.G, loc_1.get_node(), loc_2.get_node())
        self.assertEqual(distance, 0)

    def test_different_driver_ids(self):
        driver_2 = Driver("Sam", "D2")
        self.assertNotEqual(self.driver._user_id, driver_2._user_id)

    def test_driver_is_available(self):
        driver = Driver("Joe", "D3", is_available=True)
        self.assertTrue(driver.is_available)

    def test_ride_has_not_started(self):
        ride = self._make_ride(driver=self.driver)
        self.assertFalse(ride.get_status() == "In_progress")

    def test_car_same_object(self):
        car_1 = Car(2020, "Toyota", "Camry", "ABC123")
        car_2 = car_1
        self.assertIs(car_1, car_2)

    def test_two_locations_are_distinct_objects(self):
        loc_1 = Location(node=7)
        loc_2 = Location(node=7)
        self.assertIsNot(loc_1, loc_2)

    def test_ride_driver_is_none(self):
        ride = self._make_ride(driver=None)
        self.assertIsNone(ride.get_driver())

    def test_ride_driver_is_assigned(self):
        ride = self._make_ride(driver=self.driver)
        self.assertIsNotNone(ride.get_driver())

    def test_ride_in_ride_history(self):
        ride = self._make_ride(driver=self.driver)
        self.rider.add_ride_to_history(ride)
        self.assertIn(ride, self.rider._ride_history)

    def test_ride_not_in_empty_history(self):
        ride = self._make_ride(driver=self.driver)
        self.assertNotIn(ride, self.rider._ride_history)

    def test_driver_is_instance_of_driver(self):
        self.assertIsInstance(self.driver, Driver)

    def test_location_not_instance_of_ride(self):
        location = Location(node=10)
        self.assertNotIsInstance(location, Ride)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)






