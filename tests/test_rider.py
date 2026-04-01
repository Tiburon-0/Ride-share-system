import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest
from rider import Rider
from location import RiderLocation
from exceptions import RideLogicError

class TestRiderLifecycle(unittest.TestCase):
    '''Tests rider transition states (lifecycle)'''

    def setUp(self):
        self.r = Rider("Alice", "R1")

    def test_rider_state_transitions(self):
        self.assertEqual(self.r.status, "idle")

        self.r.request_ride("A", "B")
        self.assertEqual(self.r.status, "waiting")

        self.r.start_ride()
        self.assertEqual(self.r.status, "on_trip")

        self.r.complete_ride()
        self.assertEqual(self.r.status, "idle")



class TestRiderBusinessBehavior(unittest.TestCase):
    '''Tests business rules for Rider'''

    def setUp(self):
        self.r = Rider("Alice", "R1")
    
    def test_rider_cannot_request_two_rides(self):
        self.r.request_ride("A", "B")
        with self.assertRaises(Exception):
            self.r.request_ride("A", "C")

    def test_rider_can_request_ride_after_completing_one(self):
        self.r.request_ride("A", "B")
        self.r.complete_ride()
        self.r.request_ride("A", "C")

    def test_request_ride_returns_ride_object(self):

        from ride import Ride
        trip = self.r.request_ride("A", "B")
        self.assertIsInstance(trip, Ride)

    def test_initial_state(self):
        self.assertEqual(self.r.get_name(), "Alice")
        self.assertIsNone(self.r.get_current_location())

    def test_update_location(self):
        self.r.set_current_location(17)
        self.assertEqual(self.r._current_location, 17)

class TestRiderHistory(unittest.TestCase):
    '''Tests accurate tracking of ride history'''

    def setUp(self):
        self.r = Rider("Alice", "R1")

    def test_history_starts_empty(self):
        self.assertEqual(len(self.r.get_ride_history()), 0)

    def test_ride_added_to_hisotry(self):
        self.r.add_ride_to_history("simulated_ride")
        self.assertIn("simulated_ride", self.r._ride_history)

    def test_multiple_rides_in_history(self):
        self.r.add_ride_to_history("trip_1")
        self.r.add_ride_to_history("trip_2")
        self.assertEqual(len(self.r._ride_history), 2)
    
    def test_valid_rating_stored(self):
        self.r.add_rating(4)
        self.assertIn(4, self.r.get_ratings())

    def test_invalid_low_rating_rejected(self):
        low_rating = self.r.add_rating(0)
        self.assertIsNone(low_rating)
    
    def test_invalid_high_rating_rejected(self):
        high_rating = self.r.add_rating(6)
        self.assertIsNone(high_rating)

if __name__ == '__main__':
    unittest.main()