import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from driver import Driver
from rider import Rider
from graph_model import GraphModel
from location import RiderLocation, DriverLocation
from main import greedy_match_unweighted, greedy_match_weighted, select_driver

def make_driver(name, user_id, node, available=True):
    return Driver(name, user_id, is_available=available, current_location=DriverLocation(node=node))

def make_rider(node):
    return Rider("Alice", "R1", current_location=RiderLocation(node=node))

class TestSelectDriver(unittest.TestCase):
    '''Tests the select_driver function'''

    def test_select_closest_driver(self):
        created_graph = GraphModel()
        created_graph.add_edge("A", "B", 1)
        created_graph.add_edge("B", "C", 1)

        d1 = make_driver("D1", "D1", node="A")
        d2 = make_driver("D2", "D2", node="C")
        drivers = [d1, d2]

        selected = select_driver("B", drivers, created_graph)
        self.assertEqual(selected.get_user_id(), "D1")
    
    def test_no_available_drivers_returns_none(self):
        created_graph = GraphModel()
        created_graph.add_edge("A", "B", 1)

        d1 = make_driver("Carlos", "D1", node="A", available=False)
        result = select_driver("B", [d1], created_graph)
        self.assertIsNone(result)
    
    def test_unreachable_driver_is_skipped(self):
        created_graph = GraphModel()
        created_graph.add_edge("A", "B", 1)
        created_graph.graph.add_node("Z")

        d1 = make_driver("Carlos", "D1", node="B") # reachable
        d2 = make_driver("Yuki", "D2", node="Z") # unreachable

        selected = select_driver("A", [d1, d2], created_graph)
        self.assertEqual(selected.get_user_id(), "D1")

class TestGreedyMatchUnweighted(unittest.TestCase):
    '''Tests unweighted greedy matching (counts hops)'''

    def setUp(self):
        self.graph = GraphModel()
        self.graph.add_edge("A", "B", 1)
        self.graph.add_edge("B", "C", 1)
        self.graph.add_edge("C", "D", 1)

        self.rider = make_rider(node="A")
        self.d1 = make_driver("Carlos", "D1", node="B")
        self.d2 = make_driver("Yuki", "D2", node="D")
    
    def test_closer_driver_selected(self):
        matches = greedy_match_unweighted(self.graph.graph, [self.rider], [self.d1, self.d2])
        matched_rider, matched_driver, matched_distance = matches[0]
        self.assertEqual(matched_driver.get_name(), "Carlos")

    def test_matched_driver_goes_unavailable(self):
        greedy_match_unweighted(self.graph.graph, [self.rider], [self.d1, self.d2])
        self.assertFalse(self.d1.is_available)
    
    def test_no_available_drivers_returns_empty(self):
        self.d1.go_offline()
        self.d2.go_offline()
        matches = greedy_match_unweighted(self.graph.graph, [self.rider], [self.d1, self.d2])
        self.assertEqual(len(matches), 0)

    def test_driver_not_reused_across_riders(self):
        rider_2 = make_rider(node="A")
        matches = greedy_match_unweighted(self.graph.graph, [self.rider, rider_2], [self.d1])
        self.assertEqual(len(matches), 1)
    
class TestWeightedVsUnweighted(unittest.TestCase):
    '''Tess weighted vs unweighted'''

    def setUp(self):
        self.graph = GraphModel()
        self.graph.add_edge("A", "B", 100)
        self.graph.add_edge("A", "C", 1)

        self.rider = make_rider(node="A")
        self.d1 = make_driver("Carlos", "D1", node="B")
        self.d2 = make_driver("Yuki", "D2", node="C")
    
    def test_weighted_selects_cheaper_driver(self):
        matches = greedy_match_weighted(self.graph.graph, [self.rider], [self.d1, self.d2])
        matched_rider, matched_driver, matched_distance = matches[0]
        self.assertEqual(matched_driver.get_name(), "Yuki") 

    def test_weighted_and_unweighted_pick_different_drivers(self):
        weighted = greedy_match_weighted(self.graph.graph, [self.rider], [self.d1, self.d2])
        weighted_rider, weighted_winner, weighted_distance = weighted[0]

        # Reset availability before running the second algorithm
        self.d1.is_available = True
        self.d2.is_available = True

        unweighted = greedy_match_unweighted(self.graph.graph, [self.rider], [self.d1, self.d2])
        unweighted_rider, unweighted_winner, unweighted_distance = unweighted[0]

        self.assertNotEqual(weighted_winner.get_name(), unweighted_winner.get_name())

if __name__ == '__main__':
    unittest.main()