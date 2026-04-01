import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest
from driver import Driver
from location import DriverLocation
from exceptions import RideLogicError

class TestDriverStateTransitions(unittest.TestCase):
    '''Tests transitions of the driver's state (lifecycle)'''

    def setUp(self):
        loc = DriverLocation(node=5)
        self.d = Driver("Zach", "D1", is_available=True, current_location=loc)

    def test_driver_state_transitions(self):
        
        self.assertEqual(self.d.status, "available")

        self.d.assign_to_trip("T1")
        self.assertEqual(self.d.status, "assigned")

        self.d.start_trip()
        self.assertEqual(self.d.status, "on_trip")

        self.d.complete_trip()
        self.assertEqual(self.d.status, "available")

    def test_invalid_transition_start_before_assign_raises(self):
        with self.assertRaises(RideLogicError):
            self.d.start_trip()

    def test_driver_is_unavailable_while_assigned(self):
        self.d.assign_to_trip("T1")
        self.assertFalse(self.d.is_available)

    def test_driver_is_available_again_after_completing(self):
        self.d.assign_to_trip("T1")
        self.d.start_trip()
        self.d.complete_trip()
        self.assertTrue(self.d.is_available)
    
    def test_go_online_sets_available_true(self):

        self.d.go_offline() # takes driver offline
        self.d.go_online() # takes driver online

        self.assertTrue(self.d.is_available) #Checks truthiness of driver availability

    def test_invalid_rating_is_rejected(self):
        result = self.d.add_rating(99)
        self.assertIsNone(result)
    
    def test_start_trip_without_assign_raises_error(self):
        with self.assertRaises(RideLogicError):
            self.d.start_trip()

class TestDriverBehavior(unittest.TestCase):
    '''Tests driver behavioral logic'''
    
    def setUp(self):
        loc = DriverLocation(node=5)
        self.d = Driver("Zach", "D1", is_available=True, current_location=loc)

    def test_driver_cannot_start_trip_without_assignment(self):
        with self.assertRaises(RideLogicError):
            self.d.start_trip()

if __name__ == '__main__':
    unittest.main()