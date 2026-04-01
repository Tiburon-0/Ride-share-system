import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest
import networkx as nx
from graph_model import GraphModel
from ride import Ride
from driver import Driver

class TestGraphModel(unittest.TestCase):
    '''Tests Graph wrapper'''

    def setUp(self):
        self.g = GraphModel()
        self.g.add_edge("A", "B", 5)
        self.g.add_edge("B", "C", 5)
        self.g.add_edge("A", "C", 100)                

    def test_unweighted_shortest_path(self):
        path = self.g.shortest_path("A", "C", weighted=False)
        self.assertEqual(path, ["A", "C"])

    def test_weighted_shortest_path(self):
        path = self.g.shortest_path("A", "C", weighted=True)
        self.assertEqual(path, ["A", "B", "C"])

    def test_unweighted_distance_is_correct(self):
        distance = self.g.shortest_path_length("A", "C", weighted=False)
        self.assertEqual(distance, 1)

    def test_weighted_distance_is_correct(self):
        distance = self.g.shortest_path_length("A", "C", weighted=True)
        self.assertEqual(distance, 10)
    
    def test_unweighted_distance_is_one_hop(self):
        distance = self.g.shortest_path_length("A", "C", weighted=False)
        self.assertEqual(distance, 1)

    def test_weighted_and_unweighted_differ(self):
        unweighted = self.g.shortest_path("A", "C", weighted=False)
        weighted = self.g.shortest_path("A", "C", weighted=True)
        self.assertNotEqual(unweighted, weighted)
    
    def test_unreachable_node_raises(self):
        disconnected = GraphModel()
        disconnected.add_edge("X", "Y", 1)
        disconnected.graph.add_node("Z")
        with self.assertRaises(Exception):
            disconnected.shortest_path("X", "Z")
    
    def test_distance_to_self_is_zero(self):
        distance = self.g.shortest_path_length("A", "A")
        self.assertEqual(distance, 0)


if __name__ == '__main__':
    unittest.main()