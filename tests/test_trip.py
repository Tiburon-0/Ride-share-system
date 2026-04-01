import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from rider import Rider
from driver import Driver
from ride import Ride
from graph_model import GraphModel
from location import RiderLocation, DriverLocation
from main import select_driver
from exceptions import RideLogicError

class TestRideStateTransitions(unittest.TestCase):
    '''Tests proper transition of Ride state'''
    
    def setUp(self):
        self.r = Rider("Zach", "R1", current_location=RiderLocation(node=0))
        self.d = Driver("Lee", "D1", is_available=True, current_location=DriverLocation(node=7))
        self.trip = Ride(self.r, self.d, destination=10)

    def test_new_ride_status_is_requested(self):
        self.assertEqual(self.trip.get_status(), "requested")

    def test_accept_updated_status(self):
        self.trip.accept()
        self.assertEqual(self.trip.get_status(), "accepted")

    def test_start_updates_status(self):
        self.trip.accept()
        self.trip.start()
        self.assertEqual(self.trip.get_status(), "in_progress")

    def test_complete_updates_status(self):
        self.trip.accept()
        self.trip.start()
        self.trip.complete()
        self.assertEqual(self.trip.get_status(), "complete")

class TestRideErrorHandling(unittest.TestCase):
    '''Tests that invalid transitions raise the correct error'''

    def setUp(self):
        self.r = Rider("Zach", "R1", current_location=RiderLocation(node=0))
        self.d = Driver("Lee", "D1", is_available=True, current_location=DriverLocation(node=7))

    def test_complete_before_start_raises(self):
        trip = Ride(self.r, self.d, destination=30)
        with self.assertRaises(Exception):
            trip.complete()
    
    def test_start_before_accept_raises(self):
        trip = Ride(self.r, self.d, destination=30)
        with self.assertRaises(Exception):
            trip.start()
    
    def test_fare_with_no_locations_raises(self):
        rider_no_loc = Rider("Tom", "R2")
        trip = Ride(rider_no_loc, self.d, destination=None)
        with self.assertRaises(Exception):
            trip.calculate_fare()

class TestFullRideIntegration(unittest.TestCase):
    '''Simulates a full ride mini-scenario'''

    def test_full_ride_flow(self):
        graph = GraphModel()
        graph.add_edge("A", "B", 1)

        rider = Rider("Alice", "R1", current_location=RiderLocation(node="A"))
        driver = Driver("Jerry", "D1", is_available=True, current_location=DriverLocation(node="B"))

        matched = select_driver("A", [driver], graph)
        self.assertIsNotNone(matched)

        trip = Ride(rider, matched, destination=DriverLocation(node="B"))
        trip._distance = 1
        trip.accept()
        trip.start()
        trip.complete()

        rider.add_ride_to_history(trip)

        self.assertEqual(trip.get_status(), "complete")
        self.assertEqual(len(rider.get_ride_history()), 1)
        self.assertEqual(driver.status, "available")

if __name__ == '__main__':
    unittest.main()